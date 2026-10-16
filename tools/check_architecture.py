#!/usr/bin/env python3
"""Check `ARCHITECTURE.md` § 3's module map against the code.

    python3 tools/check_architecture.py [ARCHITECTURE.md]   # exit 1 on any mismatch
    python3 tools/check_architecture.py --self-test         # plant each mismatch in a copy and watch it fire

It shares no code with whatever wrote the map: the import graph comes from `scripts/build_order.py`'s fresh scan of `Proofs/`. A
module is named relative to `Proofs/` without `.lean` (`Example`, `Sub/Part`); its imports cell lists the library modules it imports,
each in backticks, or `—`. *Why:* the map is how a fresh mind finds where a result lives, and a map that has drifted behind the code
sends it to the wrong module with confidence. Checked: every module has exactly one row; every row names a module that exists; every
row's imports are the module's own.
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def graph() -> dict[str, set[str]]:
    spec = importlib.util.spec_from_file_location("bo", REPO / "scripts/build_order.py")
    bo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bo)

    def short(k: str) -> str:
        return k[len("Proofs."):].replace(".", "/")
    return {short(k): {short(i) for i in v} for k, v in bo.modules().items() if k != "Proofs"}


def check(arch: str, mods: dict[str, set[str]]) -> list[str]:
    fails = []
    m = re.search(r"^## 3\. .*?\n(.*?)(?=^## |\Z)", arch, re.S | re.M)
    if not m:
        return ["ARCHITECTURE.md has no § 3 (the module map)"]
    rows: dict[str, set[str]] = {}
    for line in m.group(1).splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        name = cells[0].strip("`")
        if name in rows:
            fails.append(f"module named in two rows: {name}")
        rows[name] = set() if len(cells) < 2 or cells[1] == "—" else set(re.findall(r"`([^`]+)`", cells[1]))
    for name in sorted(set(mods) - set(rows)):
        fails.append(f"module with no row in § 3: {name}")
    for name in sorted(set(rows) - set(mods)):
        fails.append(f"row for a module that does not exist: {name}")
    for name in sorted(set(rows) & set(mods)):
        if rows[name] != mods[name]:
            fails.append(f"{name}: the map says it imports {sorted(rows[name]) or '—'}, the code says {sorted(mods[name]) or '—'}")
    return fails


def self_test() -> int:
    arch = (REPO / "ARCHITECTURE.md").read_text(encoding="utf-8")
    mods = graph()
    if not mods:
        print("FAIL  self-test: the library has no module, so the plants would be vacuous")
        return 1
    one = sorted(mods)[0]
    row = next(x for x in arch.splitlines() if x.startswith(f"| `{one}` |"))
    plants = [
        ("the map as it stands (partner)", arch, None),
        ("a module's row deleted", arch.replace(row + "\n", ""), "module with no row"),
        ("a row for a module that does not exist", arch.replace(row, row + "\n| `Ghost` | — | nothing |"), "does not exist"),
        ("a row with a wrong import", arch.replace(row, row.replace(" | — | ", " | `Ghost` | ", 1) if " | — | " in row else
                                               row.replace(" | `", " | `Ghost`, `", 1)), "the map says"),
        ("a module named twice", arch.replace(row, row + "\n" + row), "two rows"),
    ]
    bad = 0
    for what, text, needle in plants:
        got = check(text, mods)
        ok = (not got) if needle is None else any(needle in g for g in got)
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  self-test: {what}" + ("" if ok else f" — got {got}"))
    print("SELF-TEST " + ("PASSED" if not bad else f"FAILED ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "ARCHITECTURE.md"
    found = check(path.read_text(encoding="utf-8"), graph())
    for f in found:
        print("FAIL  " + f)
    print("==> architecture: " + ("FAIL" if found else "OK — every module has its row, and every row's imports are the code's"))
    sys.exit(1 if found else 0)
