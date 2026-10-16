#!/usr/bin/env python3
"""Every decision of the axiom audit, read from the output of `scripts/Axioms.lean`.

    python3 scripts/axioms_check.py <the audit's output> <ARCHITECTURE.md>

Prints one `FAIL <kind> <detail>` line per failure, then one `COUNTS …` line, and exits 1 on any failure. `scripts/axioms.sh` runs it
on the gate's run and on every planted control, so the self-test exercises exactly what the gate decides.

The rule — **every axiom a declaration rests on must be one its class allows** — checked axiom by axiom on each record's set:
  sorry                     `sorryAx` anywhere: a proof is missing.
  undeclared-axiom          an axiom outside the standard three, the declared imports and native evaluation.
  undeclared-purchase       a native-evaluation axiom on a declaration whose docstring does not open with the purchase line.
  stale-purchase            the purchase line on a declaration with no native axiom: the ledger says a purchase exists that does not.
  undeclared-library-axiom  an `axiom` the library declares that no `declareImport` names, whether or not anything uses it.
  arch-missing              a declared import `ARCHITECTURE.md` § 5 Trust does not name in backticks (`LEAN.md` § Assumptions item 4).
  unused-import             a declared import no record rests on: the declaration list has drifted from the library.
  malformed                 the output is not the shape this reads: no SUMMARY line, or counts that disagree with the lines — a
                            check that could not run must never read as one that passed.
Counts: clean (a non-empty subset of the standard three), imported, purchased, axiom-free.
"""
import re
import sys
from pathlib import Path

STD = {"propext", "Classical.choice", "Quot.sound"}
REC = re.compile(r"^RECORD (\S+) PURCHASE-DOC ([01]) AXIOMS (\S+)$")


def native(a: str) -> bool:
    return "._native." in a or a in ("Lean.ofReduceBool", "Lean.trustCompiler")


def trust_section(arch: str) -> str:
    m = re.search(r"^## 5\. Trust\n(.*?)(?=^## |\Z)", arch, re.S | re.M)
    return m.group(1) if m else ""


def check(log_text: str, arch_text: str) -> tuple[list[str], dict]:
    fails, declared, libaxioms, records, summary = [], set(), [], [], None
    for raw in log_text.splitlines():
        line = raw.strip()
        if line.startswith("DECLARED IMPORT "):
            declared.add(line.split(" ", 2)[2])
        elif line.startswith("LIBRARY AXIOM "):
            libaxioms.append(line.split(" ", 2)[2])
        elif m := REC.match(line):
            axs = set() if m.group(3) == "-" else set(m.group(3).split(","))
            records.append((m.group(1), m.group(2) == "1", axs))
        elif line.startswith("SUMMARY "):
            summary = dict(kv.split("=") for kv in line.split()[1:])
    if summary is None:
        return ["FAIL malformed the audit printed no SUMMARY line: it did not run to its end"], {}
    if int(summary.get("records", -1)) != len(records) or int(summary.get("library-axioms", -1)) != len(libaxioms):
        fails.append(f"FAIL malformed SUMMARY says {summary}, the lines say records={len(records)} library-axioms={len(libaxioms)}")
    counts = {"clean": 0, "imported": 0, "purchased": 0, "axiom-free": 0}
    used = set()
    for name, doc, axs in records:
        if "sorryAx" in axs:
            fails.append(f"FAIL sorry {name}")
        other = {a for a in axs if a not in STD and a not in declared and not native(a) and a != "sorryAx"}
        if other:
            fails.append(f"FAIL undeclared-axiom {name}: {', '.join(sorted(other))}")
        nat = any(native(a) for a in axs)
        if nat and not doc:
            fails.append(f"FAIL undeclared-purchase {name}: native evaluation with no 'Trust purchase' docstring")
        if doc and not nat:
            fails.append(f"FAIL stale-purchase {name}: a 'Trust purchase' docstring and no native axiom")
        used |= axs & declared
        if nat:
            counts["purchased"] += 1
        elif axs & declared:
            counts["imported"] += 1
        elif not axs:
            counts["axiom-free"] += 1
        else:
            counts["clean"] += 1
    for a in libaxioms:
        if a not in declared:
            fails.append(f"FAIL undeclared-library-axiom {a}: no declareImport line names it")
    trust = trust_section(arch_text)
    for a in sorted(declared):
        if f"`{a}`" not in trust:
            fails.append(f"FAIL arch-missing {a}: ARCHITECTURE.md § 5 Trust does not name it in backticks")
        if a not in used:
            fails.append(f"FAIL unused-import {a}: declared, and no record rests on it")
    counts["records"] = len(records)
    return fails, counts


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    fails, counts = check(Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"),
                          Path(sys.argv[2]).read_text(encoding="utf-8"))
    for f in fails:
        print(f)
    print("COUNTS " + " ".join(f"{k}={v}" for k, v in counts.items()))
    sys.exit(1 if fails else 0)
