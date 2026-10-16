#!/usr/bin/env python3
"""Every decision of the vacuity gate, read from the output of `scripts/Vacuity.lean` and the baseline.

    python3 scripts/vacuity_check.py <the scan's output> <scripts/vacuity-baseline.txt>

Prints one `FAIL <kind> <detail>` line per failure and exits 1 on any:
  vacuous        a site whose carrier is provably empty, undeclared — never baselinable, because a suppression list able to hide
                 this is exactly what the gate exists to prevent;
  stale          a `VACUITY DECLARED:` docstring on a site whose emptiness is not proved — the marker is a claim, not a `noqa`;
  unknown        an UNKNOWN site the baseline does not hold: the baseline is a ratchet, so anything new fails;
  baseline-stale a baseline entry that is no longer UNKNOWN: the baseline only shrinks, and an entry left behind would hide the next
                 site of that name;
  untelescoped   a declaration the scan could not read: a check that cannot run fails loud;
  malformed      no TOTALS line, or SITE rows that disagree with it.
"""
import re
import sys
from pathlib import Path


def baseline_entries(text: str) -> set[str]:
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def check(scan: str, baseline: str) -> list[str]:
    lines = [x.strip() for x in scan.splitlines()]
    totals = next((x for x in lines if x.startswith("=== TOTALS ===")), None)
    if totals is None or not any(x.startswith("=== SCANNED ===") for x in lines):
        return ["FAIL malformed the scan printed no TOTALS or SCANNED line: it did not run to its end"]
    t = {k: int(v) for k, v in re.findall(r"([\w-]+)=(\d+)", totals)}
    sites = [x for x in lines if x.startswith("SITE ")]
    fails = []
    if t.get("sites") != len(sites):
        fails.append(f"FAIL malformed TOTALS says sites={t.get('sites')}, and {len(sites)} SITE rows were printed")
    flagged = [x for x in lines if re.match(r"^(VACUOUS|STALE|UNKNOWN) \S+$", x)]
    base = baseline_entries(baseline)
    unknown_now = set()
    for x in flagged:
        kind, decl = x.split(" ", 1)
        if kind == "VACUOUS":
            fails.append(f"FAIL vacuous {decl}: its carrier is provably empty and its docstring does not declare it")
        elif kind == "STALE":
            fails.append(f"FAIL stale {decl}: it declares emptiness that is not proved")
        else:
            unknown_now.add(x)
            if x not in base:
                fails.append(f"FAIL unknown {decl}: undecided at a concrete carrier, and not in the baseline")
    for b in sorted(base - unknown_now):
        fails.append(f"FAIL baseline-stale {b}: no longer UNKNOWN; remove it (the baseline only shrinks)")
    if t.get("untelescoped", 0):
        fails.append(f"FAIL untelescoped {t['untelescoped']} declaration(s) could not be read; see the UNTELESCOPED warnings")
    return fails


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    b = Path(sys.argv[2])
    if not b.exists():
        print(f"FAIL malformed the baseline {b} is missing: a missing baseline is a failure, never a free pass")
        sys.exit(1)
    fails = check(Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"), b.read_text(encoding="utf-8"))
    for f in fails:
        print(f)
    sys.exit(1 if fails else 0)
