#!/usr/bin/env python3
"""The digest a gate prints from its own saved output, so reading a result never means running the gate again.

    gate_report.py axioms  <this run's log> <previous run's log, or ''> <CLAUDE.md>
    gate_report.py vacuity <this run's log> <previous run's log, or ''> <CLAUDE.md>

`scripts/axioms.sh` and `scripts/vacuity.sh` save their Lean tool's complete output (`scripts/gate-log.sh`) and call this to print,
from that file and the previous complete run's file:

* every count the tool computed, including the ones the gate does not decide on;
* whether those counts still match the line `CLAUDE.md` records (§ Trust ledger: `axiom audit: clean=…`; § The gate: `vacuity:
  declarations=…`), one line per count — a drifted record is **flagged, never failed**, because counts move at every landing and the
  implementer's drafts refile them at the close;
* every row that changed since the previous complete run, which answers "which declarations are the new ones?" without a second run.

It decides nothing about the scan: pass and fail stay in the shell scripts. It refuses, loudly, in two cases, because each is a check
that could not run:
* exit 2 — the tool's output is not the shape it reads (an accounting line missing, a listing that disagrees with its own totals): a
  digest that silently printed less than the run computed would be the failure this file exists to remove;
* exit 3 — the recorded line could not be read (missing, or present twice): a comparison that could not run must never read as one
  that passed. The digest is printed in full first, with the line to record.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))


def lines_of(path: str) -> list[str]:
    if not path or not Path(path).exists():
        return []
    return [x.strip() for x in Path(path).read_text(encoding="utf-8", errors="replace").splitlines()]


def recorded(claude: str, prefix: str) -> dict | None:
    """The counts on the one line of `claude` that starts with the backticked `prefix`; None if absent or doubled."""
    text = Path(claude).read_text(encoding="utf-8")
    hits = re.findall(r"`" + re.escape(prefix) + r"([^`]*)`", text)
    if len(hits) != 1:
        return None
    return {k: int(v) for k, v in re.findall(r"([\w-]+)=(\d+)", hits[0])}


def compare(label: str, rec: dict | None, now: dict, prefix: str) -> int:
    line = prefix + " ".join(f"{k}={v}" for k, v in now.items())
    if rec is None:
        print(f"REFUSED  {label}: the line `{prefix}…` is missing or present twice; record exactly one: `{line}`")
        return 3
    drift = [f"{k} {rec.get(k)} -> {v}" for k, v in now.items() if rec.get(k) != v]
    if drift:
        print(f"DRIFT    {label} records other counts ({'; '.join(drift)}); refile it as `{line}`")
    else:
        print(f"match    {label}: every count it records was compared and agrees")
    return 0


def axioms(cur: str, prev: str, claude: str) -> int:
    from axioms_check import REC, check
    text = Path(cur).read_text(encoding="utf-8", errors="replace")
    fails, counts = check(text, "")
    if not counts:
        print("REFUSED  the axiom audit's output has no SUMMARY line: nothing to digest")
        return 2
    print("axioms: " + " ".join(f"{k}={v}" for k, v in counts.items()))

    def recs(ls):
        return {m.group(1): m.group(3) for m in (REC.match(x) for x in ls) if m}
    now, before = recs(lines_of(cur)), recs(lines_of(prev))
    for x in lines_of(cur):
        if x.startswith(("DECLARED IMPORT ", "LIBRARY AXIOM ")):
            print("  " + x)
    for n, a in sorted(now.items()):
        if a not in ("-",) and set(a.split(",")) - {"propext", "Classical.choice", "Quot.sound"}:
            print(f"  beyond the standard three: {n}: {a}")
    if prev:
        added = sorted(set(now) - set(before))
        gone = sorted(set(before) - set(now))
        moved = sorted(n for n in set(now) & set(before) if now[n] != before[n])
        print(f"since the previous run: {len(added)} new, {len(gone)} gone, {len(moved)} changed their axioms")
        for n in added:
            print(f"  new      {n}: {now[n]}")
        for n in gone:
            print(f"  gone     {n}")
        for n in moved:
            print(f"  changed  {n}: {before[n]} -> {now[n]}")
    else:
        print("since the previous run: no previous complete run to compare against")
    keep = {k: counts[k] for k in ("clean", "imported", "purchased", "axiom-free")}
    return compare("CLAUDE.md § Trust ledger", recorded(claude, "axiom audit: "), keep, "axiom audit: ")


VAC_KEYS = ("declarations", "refutations-skipped", "sites", "vacuous", "stale", "declared", "witnessed", "generic", "unknown")


def read_vacuity(ls: list[str]) -> tuple[dict, list[str]] | None:
    counts, sites = {}, []
    for x in ls:
        if x.startswith(("=== SCANNED ===", "=== TOTALS ===")):
            counts.update({k: int(v) for k, v in re.findall(r"([\w-]+)=(\d+)", x)})
        elif x.startswith("SITE "):
            sites.append(x)
    if not all(k in counts for k in VAC_KEYS) or counts["sites"] != len(sites):
        return None
    return counts, sites


def vacuity(cur: str, prev: str, claude: str) -> int:
    got = read_vacuity(lines_of(cur))
    if got is None:
        print("REFUSED  the vacuity scan's output lacks its accounting lines, or its SITE lines disagree with its own total")
        return 2
    counts, sites = got
    print("vacuity: " + " ".join(f"{k}={counts[k]}" for k in VAC_KEYS) + f" untelescoped={counts.get('untelescoped', 0)}")
    for x in lines_of(cur):
        if x.startswith(("DECLARED ", "VACUOUS ", "STALE ", "UNKNOWN ")):
            print("  " + x)
    old = read_vacuity(lines_of(prev)) if prev else None
    if old is not None:
        a, b = set(old[1]), set(sites)
        print(f"since the previous run: {len(b - a)} site rows new, {len(a - b)} gone")
        for x in sorted(b - a):
            print(f"  new   {x}")
        for x in sorted(a - b):
            print(f"  gone  {x}")
    else:
        print("since the previous run: no previous complete run to compare against")
    return compare("CLAUDE.md § The gate", recorded(claude, "vacuity: "), {k: counts[k] for k in VAC_KEYS}, "vacuity: ")


def main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[1] == "axioms":
        return axioms(argv[2], argv[3], argv[4])
    if len(argv) == 5 and argv[1] == "vacuity":
        return vacuity(argv[2], argv[3], argv[4])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
