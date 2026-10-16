# Running things here — the toolchain, processes, and instruments that must fail loudly

*Every brief for a job that runs a solver, a build or a long process, or builds a checker, names this file as part of it; the rules
every job needs are `plans/STANDING-RULES.md` rule 9. It is not loaded at launch, because most jobs never run a process. Two paragraphs
of § Building are **PROTECTED**: each states a rule whose loss costs real work, and the fact audit holds them byte-identical. Keryx is
this file's writer.*

## Toolchain

‹PRINCIPAL / Keryx: the machine or machines this project runs on (cores, RAM, whether `/tmp` and swap are RAM), the solvers and
computer-algebra systems installed with their versions, and anything about the environment a job must know before it runs a
process. One line each, current state only.›

- **Python's multiprocessing**: set the start method explicitly (`spawn` or `fork`) in every tool that uses it, because the default
  differs across Python versions and platforms and a pool that silently changes method changes what each worker inherits.
- **`scripts/slot.py`** needs Linux with a systemd user session (`systemd-run --user`) and `taskset`; `scripts/slot.py --self-test`
  checks that this machine has them before any job relies on it.

## Building

The Lean build — `./scripts/build.sh`, never `lake build`; `lake env lean`; the batch and the cap; edits and invalidation — is the
kernel lane's: `LEAN.md` § Building. What follows binds every job that runs a process.

**On any unexplained process crash, from any process: HALT and report.** Do not diagnose, retry, or work past it. *Why:* a crash with no
known cause can be the machine failing — a filesystem or memory fault — and every job that keeps working on a failing machine turns
the fault into lost or corrupted work.

**RAM is the discriminator; threads are not rationed.** Every thread can and should be used, jobs pinned to disjoint cores; RAM is
rationed because exhausting it takes the machine down for every job at once. Where `/tmp` or swap is RAM, large outputs (over about
1 GiB) go to disk under the repository's `data/`, never to `/tmp`. **The enforcement is `scripts/slot.py`:** `scripts/slot.py --mem
<GiB> [--cpus N] -- <cmd>` reserves RAM in a shared ledger, admitting the job only while the reservations stay within the budget and
the kernel's available memory keeps a reserve free; runs it under a hard memory cap with no swap, so an over-cap job is killed inside
its own scope and never takes the machine; pins it to free cores, one thread per physical core first; and exits 75, loudly, if not
admitted within `--wait`. `--status` shows the ledger; `--self-test` plants an over-cap job and a full ledger and watches both
refused. A job under about 2 GiB and 2 minutes may run without a slot; anything bigger or longer declares an honest `--mem`, since an
under-declared job is killed by its cap. **An unknown binary is never probed outside a slot**: a `--help` it does not know is a guess,
and a replay tool run with no target can walk its whole search path on every thread. **A job that calls `systemd-run` itself escapes
the slot's cap** (the new scope is a sibling, not a child), so a Lean build reserves and caps at the same number (`LEAN.md` §
Building).

**Every long-running phase checkpoints and resumes exactly.** **[PROTECTED — never compress, trim or paraphrase this paragraph;
rewrite it only to add an instance.]** A run expected to exceed about fifteen minutes persists its progress at natural acceptance
points (a verdict, a wave, an accepted deletion, a solver's iterate) and resumes from that state after a kill; a long phase whose state
lives only in a process's memory is a **bug, not a style choice** — it is a bet against the machine's crash rate. The audit question at
every phase design: *if this process dies at any instant, what does the relaunch redo?* — and the answer is written in the plan,
beside the checkpoint's path and the **resume command**, never discovered at the loss; a checkpoint nobody knows how to resume from
is a file, not a recovery. The clauses of the rule, each learned from a loss:
1. **State only in a parent process is lost with any child.** A long reduction kept its state in the parent while workers ran; one
   worker died, the pool waited forever, and the whole run was lost.
2. **The checkpoint must not live where another agent is told to clean.** A tidy-up of a scratch tree deleted a live job's only
   resume file. Recoverable state one cleanup away from unrecoverable is not recoverable: checkpoints live outside the scratch tree.
3. **A wall is not a checkpoint, and a tool that cannot be interrupted is not a tool for a long run.** Solves run under `timeout`
   walls with the solver's iterate in memory only were lost when the walls fired, and killing a `timeout` wrapper kills its child
   too. Drive a solver through its own interface in warm-started chunks, the iterate saved after every chunk, never under a wall —
   and test a claim about how processes behave on `sleep` before acting on it.

**A run that blocks something is presumed killable.** **[PROTECTED — never compress, trim or paraphrase this paragraph; rewrite it
only to add an instance.]** When a live job stands in the way of anything — an edit to a module it imports, a core another task
needs, a fix it would invalidate — weigh **the value of the run against the value of what it blocks, and the default is to kill the
run.** The burden of proof is on keeping it, never on stopping it. Because every long run checkpoints (above), **the cost of being
wrong is the time to redo, never the result** — so weigh the cost of being wrong, not the hours already spent. Three shapes that
look like reasons to wait and are not:
- **The run is blocking its own replacement.** A slow run holds open the code its faster replacement must change, so "wait for it
  to finish" makes the slow path self-perpetuating. Ask by name: *is the thing I am waiting on the thing preventing the fix?*
  Measuring the replacement is not a precondition for stopping the run: with checkpoints the redo is cheap.
- **The run is producing records under code you are about to fix.** Finishing banks results from the broken version and forces the
  redo anyway — and those records are the ones a later reader trusts.
- **The fix makes the redo cheaper than the run being protected.** Then waiting costs twice.

Two obligations when you do it. **Capture the run's state into the record before signalling** — a verdict written only at the end is
lost, and the log is not the record. And **name what the kill forfeits, out loud**: a forfeited instrument or prediction must not
disappear quietly merely because the decision was otherwise right.

**Kill by PID or process group, never by matching a command line.** `pkill -f <pattern>` matches the shell that runs it and every
other process whose command line mentions the pattern — another agent's run or monitor included. `setsid` the job, write its pgid to a
file, signal that. **And the pid you hold may not be the process you mean**: `nohup <binary> … &` followed by `$!` can report an
intermediate shell rather than the binary, and killing that pid leaves the binary running, still writing. **A kill is verified by what
stopped changing, never by the exit status of the kill**: after signalling, confirm that no process of that pid is in `ps`, and that
the file it was writing is unchanged across ten seconds. A hand-rolled scan of `/proc/*/cmdline` is `pkill -f` in a different
costume; find a process by the file it holds open instead.

**A pipe can kill the producer, and `| tail` can hide that it did.** A harness piped into `head` dies of `SIGPIPE` when `head` closes
the pipe — possibly before its cleanup restores what it planted — and a verification piped into `tail` reports `tail`'s exit status,
which is always zero. A command whose cleanup matters is never piped into `head`, and a gate's exit status is read from the gate,
never through a pipeline (`set -o pipefail`, or capture to a file and read it).

**Never edit a shell script while it is running.** Bash reads a script lazily, by byte offset, so a live process resumes mid-token
and fails with a message that looks like corruption. Launch long runs from a snapshot copy under `build/`.

## Make the gate fail, and watch it fail

**Run every check's negative control at every milestone.** Break the thing it guards on purpose, confirm it goes red and names the
culprit, then put it back. A check is not known to work until it has been seen to fail.

Every check that fails, fails the same way: **it reports nothing when it could not run** — a comparison never actually performed; an
audit that aborted under `set -e` with no output and read as a pass through a pipe; a harness that re-read a stale file and scored it
as a pass; negative controls the instrument could not see. A trust receipt that fails open is worse than none, because it is
believed. So make a check's failure path louder than its success path, never let a shell pipeline swallow an exit status the gate
depends on, and give every discriminating claim a partner that goes red.

**Every check needs a positive signal for the thing that did not happen.** A wall that could not fire, an exception swallowed in a
timer thread, a control asking the same question twice, a silent search, a trust receipt returning a benign verdict while checking
nothing — each is quiet exactly when it has something to report, because each reacts to an event instead of asserting an absence. An
exit-waiter can tell you a thing has ended, never that it is late.
- **Arm a waiter on a file the success path always writes**, even if that file says "nothing found": a waiter on a file that a good
  outcome prevents from existing reads like a hung run.
- **A waiter's condition must be false at the moment you arm it — check that.** A condition that already holds, or that can never
  match (a pattern that matches nothing, a pattern that matches the waiting shell itself), fails toward "done" or toward "never". Arm
  a waiter on the live job's pid, which cannot self-match.

**State the uninformative outcome and confirm it is reachable, before believing a control's pass.** A planted fault that can never
fire, or a discriminator that cannot separate its two cases, passes review and has tested nothing. **Confirm that both outcomes are
reachable — the one that would teach you nothing and the one you predict**; a prediction whose target region the apparatus cannot
enter is a formality that will read as a finding. **The rule is symmetric: a control going red is not evidence either, until you can
name what a wrong-reason red would look like.** The repair is a **pair**: the stub that must fail beside a faithful stub that must
pass, so the refusal is seen to come from the cause and not the scaffolding.

**Pre-decide how you will respond to your own gate failing — before it fails.** A check you tune until it agrees with you has stopped
being a check; settle the policy while the number under dispute is not yours.

**When you replace a broad instrument with a sharp one, you lose coverage you were not measuring.** State what the old instrument saw
that the new one does not, at the moment you swap them.

**When you put a measured number into a decision, carry what it measures, never just its value** — its units, its conditions and its
population. **When two numbers are compared, exactly one thing may differ between them**: write both as fractions with the
denominators spelled out in words. A comparison that differs in two things and credits one usually credits the change being advocated,
so the error flatters the work.

**A measured half and a derived half fail in opposite directions.** Where an object's relations are *measured* (a float proposes,
exact arithmetic decides), the error is a missed relation, which makes the object easier; where they are *derived from a law*, the
error is an invented relation, which makes refusals faster and looks exactly like success. Before trusting either verdict, ask which
half of the object produced it.

**A check must read the value the code ships, never a copy of it**, and **the failure path's formatting is part of the check**: a
rounding that renders a failing ratio as a passing one is inside the trust boundary.

**Bound a plant's effect on both sides**, so the control reports when it has gone blind:

```
0 < (guarded_result − planted_result) < threshold
```

The lower bound fails when the plant has stopped firing; the upper when it fires too much.

**To compare policies, replay them over a recorded decision sequence rather than re-running**: one run, one population, one thing
differing, with the control that the replay reproduces the original run's cost.

**A cost measured on a failing run understates a succeeding one** — the cheap steps are often the failures. Before costing an
iterative process from a sample, check which regime the sample's cheap steps were in.

**A caveat you write and then step over is worse than one you never wrote**: after writing a scope qualifier, re-read the summary
sentence against it, because the caveat is what made the headline look audited.

**Count your generator's free parameters against the problem's.** A search over a one-parameter family of a two-parameter space looks
at a slice of measure zero, and its positive control can still pass. **A positive control proves an instrument finds things of the
shape its generator can represent**, and says nothing about shapes it excludes: before believing any zero over a family, write down
the generator's image and check the target is inside it. **Enumerate the parameter first and screen the objects against it second**:
an enumeration that never generates a candidate leaves no row to audit, and an omission is worse than a miscount.

**A true explanation that fully accounts for an observation will stop you looking for a second one — and the second may be about
your own apparatus.** A candidate that fails one gate must be checked against all of them before it is used as a test case, because
the first failure makes it feel already understood; re-read every hypothesis against the test instance immediately before believing
an out-of-sample result.

**A mutation harness must verify its own restore**, and **mutate the constant, not only the logic**. A same-size edit written inside
one second can leave a bytecode cache serving the mutated code against a restored source; re-run the controls after the restore and
assert the guarded state comes back. A check that loads two versions of something and identifies them by name — module caches,
registries, environment lookups — can silently compare one version with itself; provoke that failure deliberately.

**Do not mistake a one-sided filter for an inverted monotonicity**, and whenever a one-sided filter judges something you are
building, enumerate the ways to make it inapplicable before the ways to make it fail: a `not-applicable` on the same footing as a
silence is a pass nobody earned.

**These rules are scars, not foresight.** Reasoning finds the controls you thought about; planting faults routinely finds the ones you
did not.
