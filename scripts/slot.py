#!/usr/bin/env python3
"""slot.py -- run a job inside the machine's RAM budget, on pinned cores.

THE RULE.  Threads are not rationed: every thread can and should be used, with jobs pinned to disjoint cores.  RAM is the
discriminator, because exhausting it takes the machine down for every job at once.  The budget for reservations defaults to 75% of
the machine's memory, leaving the rest for the kernel, the desktop and the agents themselves (`SLOT_BUDGET_GB` overrides it).

HOW THIS ENFORCES IT.
  * A shared ledger of reservations (one line per running job: its RAM in GiB and its pinned CPUs) under a lock.  A job is admitted
    only if (a) the ledger's reservations plus its own stay within the budget, and (b) the kernel's MemAvailable minus its request
    stays at least the reserve (default 15% of the machine's memory; `SLOT_RESERVE_GB`), which catches usage no slot tracks.
  * The job runs under `systemd-run --user --scope -p MemoryMax=<mem>G -p MemorySwapMax=0`: a hard cap enforced by the kernel.  A job
    that exceeds its reservation is OOM-killed inside its own scope; the machine is untouched.  The reservation is therefore a ceiling
    the job cannot pass, never an estimate it is trusted to keep.
  * The job is pinned with `taskset` to CPUs no other slot holds, one thread per physical core first, then the sibling threads.
  * Liveness is by pid AND start time, for this process and for its child, so a crashed wrapper cannot leak a reservation (its line is
    pruned when both are gone) and a killed wrapper cannot hide a running job (the child keeps its line alive).

/tmp AND SWAP MAY BE RAM.  Where /tmp is a tmpfs (agents' scratch directories often live there) or swap is compressed RAM, a job's
/tmp writes are charged to its own capped scope while it runs, and files left in /tmp after it exits keep holding RAM, which the
MemAvailable reserve sees.  Slots forbid swap (MemorySwapMax=0).  So large outputs (over about 1 GiB) go to disk under the
repository's data/, never to /tmp or a scratch directory.

UNTRACKED WORK.  A job under about 2 GiB and 2 minutes (a checker run, a small script) may run without a slot; the reserve leaves
room for it.  Anything bigger or longer goes through a slot, with an honest --mem: an under-declared job is killed by its cap.

USAGE
  scripts/slot.py --mem GIB [--cpus N] [--wait SECONDS] [--name LABEL] -- CMD [ARGS...]
      exit status: the job's own; 75 if not admitted within --wait (default 1800 s) -- a LOUD failure, never a silent non-run.
  scripts/slot.py --status          the live reservations, the totals and MemAvailable
  scripts/slot.py --self-test       the controls: a job over its cap is killed; a full ledger refuses; a dead holder is pruned

Needs Linux, a systemd user session and taskset.  Standard library only.  Ledger: $SLOT_DIR (default /run/user/<uid>/agent-slots,
shared by every repository on the machine, because the machine's memory is shared), which lives exactly as long as the boot does, as
do the jobs it describes.
"""
import argparse
import fcntl
import os
import signal
import subprocess
import sys
import time

def _mem_total_gb():
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    return int(line.split()[1]) / 1024 / 1024
    except OSError:
        pass
    return 0.0


SLOT_DIR = os.environ.get('SLOT_DIR', f'/run/user/{os.getuid()}/agent-slots')
BUDGET_GB = float(os.environ.get('SLOT_BUDGET_GB', f'{_mem_total_gb() * 0.75:.1f}'))
RESERVE_GB = float(os.environ.get('SLOT_RESERVE_GB', f'{max(2.0, _mem_total_gb() * 0.15):.1f}'))
LEDGER = os.path.join(SLOT_DIR, 'ledger')
LOCK = os.path.join(SLOT_DIR, 'ledger.lock')
NOT_ADMITTED = 75


def cpu_order():
    """one thread per physical core first, then the siblings: [first thread of each core] + [the rest]"""
    firsts, rest, seen = [], [], set()
    cpus = sorted(int(c[3:]) for c in os.listdir('/sys/devices/system/cpu') if c[3:].isdigit() and c.startswith('cpu'))
    for c in cpus:
        try:
            with open(f'/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list') as f:
                sib = f.read().strip()
        except OSError:
            sib = str(c)
        if sib in seen:
            rest.append(c)
        else:
            seen.add(sib)
            firsts.append(c)
    return firsts + rest


def starttime(pid):
    try:
        with open(f'/proc/{pid}/stat') as f:
            return f.read().rsplit(')', 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def alive(pid, st):
    return pid > 0 and starttime(pid) == st


def mem_available_gb():
    with open('/proc/meminfo') as f:
        for line in f:
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) / 1024 / 1024
    raise RuntimeError('no MemAvailable in /proc/meminfo')


class Ledger:
    """line format: wrapper_pid wrapper_start child_pid child_start mem_gb cpulist name start_epoch"""

    def __enter__(self):
        os.makedirs(SLOT_DIR, exist_ok=True)
        self.fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o644)
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        self.rows = []
        if os.path.exists(LEDGER):
            with open(LEDGER) as f:
                for line in f:
                    p = line.split()
                    if len(p) != 8:
                        continue
                    wp, ws, cp, cs = int(p[0]), p[1], int(p[2]), p[3]
                    if alive(wp, ws) or alive(cp, cs):      # pruned only when BOTH are gone
                        self.rows.append(p)
        return self

    def write(self):
        tmp = LEDGER + '.tmp'
        with open(tmp, 'w') as f:
            for p in self.rows:
                f.write(' '.join(p) + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LEDGER)

    def __exit__(self, *a):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)

    def used(self):
        mem = sum(float(p[4]) for p in self.rows)
        cpus = set()
        for p in self.rows:
            if p[5] != '-':
                cpus.update(int(c) for c in p[5].split(','))
        return mem, cpus


def status():
    with Ledger() as L:
        L.write()
        mem, cpus = L.used()
        print(f'budget {BUDGET_GB:g} GiB reserved-by-slots, reserve {RESERVE_GB:g} GiB of MemAvailable kept free')
        print(f'reserved {mem:g} GiB in {len(L.rows)} slot(s); pinned CPUs {len(cpus)} of {len(cpu_order())}; '
              f'MemAvailable {mem_available_gb():.1f} GiB')
        for p in L.rows:
            age = int(time.time() - float(p[7]))
            print(f'  {p[6]:<28} mem {p[4]:>6} GiB  cpus {p[5]:<24} wrapper {p[0]} child {p[2]}  age {age}s')


def reserve(mem, ncpu, name, wait):
    deadline = time.time() + wait
    me, my_st = os.getpid(), starttime(os.getpid())
    order = cpu_order()
    if ncpu > len(order):
        sys.exit(f'slot: --cpus {ncpu} exceeds the machine\'s {len(order)} CPUs')
    if mem > BUDGET_GB:
        sys.exit(f'slot: --mem {mem:g} exceeds the whole budget {BUDGET_GB:g} GiB; it can never be admitted')
    last_why = ''
    while True:
        with Ledger() as L:
            used_mem, used_cpus = L.used()
            free = [c for c in order if c not in used_cpus]
            avail = mem_available_gb()
            why = []
            if used_mem + mem > BUDGET_GB:
                why.append(f'ledger {used_mem:g} + {mem:g} > budget {BUDGET_GB:g} GiB')
            if avail - mem < RESERVE_GB:
                why.append(f'MemAvailable {avail:.1f} - {mem:g} < reserve {RESERVE_GB:g} GiB')
            if len(free) < ncpu:
                why.append(f'{len(free)} free CPUs < {ncpu}')
            if not why:
                cpus = sorted(free[:ncpu])
                row = [str(me), my_st, '0', '-', f'{mem:g}', ','.join(map(str, cpus)) if cpus else '-', name, f'{time.time():.0f}']
                L.rows.append(row)
                L.write()
                return cpus
            L.write()           # persists the pruning
        why = '; '.join(why)
        if why != last_why:
            print(f'slot: waiting ({why})', file=sys.stderr, flush=True)
            last_why = why
        if time.time() > deadline:
            print(f'slot: NOT ADMITTED after {wait:g} s ({why}); the job did NOT run', file=sys.stderr, flush=True)
            sys.exit(NOT_ADMITTED)
        time.sleep(5)


def set_child(child_pid):
    with Ledger() as L:
        for p in L.rows:
            if p[0] == str(os.getpid()):
                p[2], p[3] = str(child_pid), starttime(child_pid) or '-'
        L.write()


def release():
    with Ledger() as L:
        L.rows = [p for p in L.rows if p[0] != str(os.getpid())]
        L.write()


def run(mem, ncpu, name, wait, cmd):
    cpus = reserve(mem, ncpu, name, wait)
    # --expand-environment=no: systemd-run otherwise rewrites `$VAR` and `$$` in the job's own arguments (`bash -c '... $$ ...'`
    # arrives as `$`), silently changing any command that carries a `$`; the self-test plants exactly that
    argv = ['systemd-run', '--user', '--scope', '-q', '--expand-environment=no', '-p', f'MemoryMax={mem:g}G', '-p', 'MemorySwapMax=0',
            '--']
    if cpus:
        argv += ['taskset', '-c', ','.join(map(str, cpus))]
    argv += cmd
    print(f'slot: admitted {name}: mem {mem:g} GiB (hard cap), cpus {",".join(map(str, cpus)) or "unpinned"}', file=sys.stderr,
          flush=True)
    try:
        child = subprocess.Popen(argv)
    except BaseException:
        release()
        raise
    set_child(child.pid)

    def forward(sig, _frame):
        try:
            child.send_signal(sig)
        except ProcessLookupError:
            pass
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, forward)
    try:
        rc = child.wait()
    finally:
        release()
    if rc < 0:
        rc = 128 - rc
    if rc == 137:
        print(f'slot: {name} exited 137 -- killed, most likely by its {mem:g} GiB cap (MemoryMax); raise --mem honestly or shrink '
              'the job', file=sys.stderr, flush=True)
    return rc


def _cpus(spec):
    out = set()
    for part in spec.split(','):
        a, _, b = part.partition('-')
        out.update(range(int(a), int(b or a) + 1))
    return out


def self_test():
    """Each control must go the way it says, or the test fails loudly.  Uses a private ledger directory so it never touches the
    live one, and small numbers so it is safe beside real jobs."""
    import tempfile
    d = tempfile.mkdtemp(prefix='slot-selftest-')
    env = dict(os.environ, SLOT_DIR=d, SLOT_BUDGET_GB='3', SLOT_RESERVE_GB='0')
    me = [sys.executable, os.path.abspath(__file__)]
    fails = 0

    def check(label, ok, detail=''):
        nonlocal fails
        print(f'{"PASS" if ok else "FAIL"}  {label}' + (f'  ({detail})' if detail else ''))
        fails += (not ok)

    # 1. a job within its cap runs, is pinned, and sits in its own scope
    r = subprocess.run(me + ['--mem', '1', '--cpus', '2', '--name', 'st-pin', '--', 'bash', '-c',
                             'grep Cpus_allowed_list /proc/self/status; cat /proc/self/cgroup; echo "dollar:$$:"'], env=env,
                       capture_output=True, text=True, timeout=60)
    allowed = [x.split(':', 1)[1].strip() for x in r.stdout.splitlines() if x.startswith('Cpus_allowed_list')]
    check('a job within its cap runs, pinned to 2 CPUs, in a transient scope',
          r.returncode == 0 and allowed and allowed[0] != '' and len(_cpus(allowed[0])) == min(2, len(cpu_order()))
          and '.scope' in r.stdout, r.stdout.strip().replace('\n', ' | ')[:160])
    dollar = [x for x in r.stdout.splitlines() if x.startswith('dollar:')]
    check('a `$` in the job\'s arguments reaches the job unexpanded by systemd-run', bool(dollar) and dollar[0] != 'dollar:$:'
          and dollar[0][7:-1].isdigit(), dollar[0] if dollar else 'no output')
    # 2. THE PLANT: a job allocating 2 GiB under a 1 GiB cap must be killed by the kernel, not the machine
    r = subprocess.run(me + ['--mem', '1', '--name', 'st-oom', '--', sys.executable, '-c',
                             'a = bytearray(2 * 1024**3); print("ALLOCATED")'], env=env, capture_output=True, text=True, timeout=120)
    check('a job over its cap is killed (the plant)', r.returncode != 0 and 'ALLOCATED' not in r.stdout, f'exit {r.returncode}')
    # 3. a full ledger refuses loudly within --wait, and the refused job never runs
    marker = os.path.join(d, 'ran')
    hold = subprocess.Popen(me + ['--mem', '2.5', '--name', 'st-hold', '--', 'sleep', '20'], env=env, stderr=subprocess.DEVNULL)
    time.sleep(2)
    t0 = time.time()
    r = subprocess.run(me + ['--mem', '1', '--wait', '4', '--name', 'st-full', '--', 'touch', marker], env=env, capture_output=True,
                       text=True, timeout=60)
    check('a job that does not fit is refused with exit 75 and does not run',
          r.returncode == NOT_ADMITTED and not os.path.exists(marker) and 'NOT ADMITTED' in r.stderr and time.time() - t0 < 20,
          f'exit {r.returncode}')
    r = subprocess.run(me + ['--mem', '0.5', '--wait', '4', '--name', 'st-fits', '--', 'true'], env=env, capture_output=True, text=True,
                       timeout=60)
    check('a job that fits beside the holder is admitted', r.returncode == 0, f'exit {r.returncode}')
    # 4. a SIGKILLed wrapper does not hide its running child: the reservation stays until the child is gone
    hold.send_signal(signal.SIGKILL)
    hold.wait()
    time.sleep(1)
    r = subprocess.run(me + ['--mem', '1', '--wait', '3', '--name', 'st-after-kill', '--', 'true'], env=env, capture_output=True,
                       text=True, timeout=60)
    check('after the wrapper is SIGKILLed, its still-running child keeps the reservation', r.returncode == NOT_ADMITTED,
          f'exit {r.returncode}')
    with open(os.path.join(d, 'ledger')) as f:                            # kill the orphaned child BY ITS RECORDED PID, never a pattern
        orphans = [int(x.split()[2]) for x in f if x.split()[6] == 'st-hold']
    for pid in orphans:
        os.kill(pid, signal.SIGKILL)
    time.sleep(1)
    check('the orphaned child was found in the ledger by pid', len(orphans) == 1, f'{orphans}')
    r = subprocess.run(me + ['--mem', '1', '--wait', '10', '--name', 'st-pruned', '--', 'true'], env=env, capture_output=True,
                       text=True, timeout=60)
    check('once wrapper and child are both gone, the reservation is pruned', r.returncode == 0, f'exit {r.returncode}')
    # 5. over-budget and over-CPU requests are refused at once
    r = subprocess.run(me + ['--mem', '4', '--', 'true'], env=env, capture_output=True, text=True, timeout=30)
    check('a request above the whole budget is refused at once', r.returncode != 0 and 'exceeds the whole budget' in r.stderr)
    with open(os.path.join(d, 'ledger')) as f:
        left = f.read().strip()
    check('the ledger is empty at the end', left == '', repr(left))
    print('SELF-TEST ' + ('OK' if not fails else f'FAILED ({fails})'))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--mem', type=float, help='GiB reserved, and the hard cap (MemoryMax)')
    ap.add_argument('--cpus', type=int, default=1, help='CPUs to pin (default 1; 0 = no pinning)')
    ap.add_argument('--wait', type=float, default=1800, help='seconds to wait for admission (default 1800)')
    ap.add_argument('--name', default=None)
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('cmd', nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.status:
        return status()
    if a.self_test:
        return self_test()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == '--' else a.cmd
    if a.mem is None or not cmd:
        ap.error('--mem and a command (after --) are required')
    if a.mem <= 0:
        ap.error('--mem must be positive')
    name = a.name or os.path.basename(cmd[0])
    return run(a.mem, a.cpus, name, a.wait, cmd)


if __name__ == '__main__':
    sys.exit(main() or 0)
