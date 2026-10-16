#!/usr/bin/env python3
"""The axiom audit's planted controls: each fault the gate exists to catch, planted in a copy of `scripts/Axioms.lean`, must fail for
its own reason, and each partner must pass. Run by `./scripts/axioms.sh --self-test`, from the repository root, one Lean process at a
time (each loads the library). Copies live under `build/axioms-selftest/` and are kept, so a surprising verdict can be read.

Why a control per kind: a check is not known to work until it has been seen to fail, and a control is only evidence when its partner
— the same file without the fault — passes, so the refusal is seen to come from the fault and not the scaffolding.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from axioms_check import check  # noqa: E402

MARKER = "-- DECLARED IMPORTS END"
IMP = '/-- A planted import: `[Example2020]` Theorem 1, p. 1. -/\naxiom Ctl.imp : (2 : Nat) + 2 = 4\n'
USE = '/-- Rests on the planted import. -/\ntheorem Ctl.onImp : (2 : Nat) + 2 = 4 := Ctl.imp\n'
DECL = '#eval AxiomAudit.declareImport ``Ctl.imp\n'
ARCH_LINE = "\n- `Ctl.imp` — a planted import\n"
# (name, the text planted above the marker, a line added to ARCHITECTURE.md § 5, the expected verdict)
#   expected: "pass", "fail:<kind>" (that kind among the FAIL lines), or "lean-fail" (the copy must not elaborate)
CONTROLS = [
    ("faithful copy", "", "", "pass"),
    ("a sorry", '/-- Planted. -/\ntheorem Ctl.planted : (1 : Nat) = 1 := sorry\n', "", "fail:sorry"),
    ("a sorry in a private theorem", '/-- Planted. -/\nprivate theorem Ctl.hidden : (1 : Nat) = 1 := sorry\n', "", "fail:sorry"),
    ("an undeclared axiom, used", '/-- Planted. -/\naxiom Ctl.ax : (1 : Nat) = 2\n/-- Planted. -/\ntheorem Ctl.usesAx : (1 : Nat) = 2 := Ctl.ax\n',
     "", "fail:undeclared-axiom"),
    ("an undeclared axiom nothing uses", '/-- Planted. -/\naxiom Ctl.unused : (1 : Nat) = 2\n', "", "fail:undeclared-library-axiom"),
    ("a declared import, named in ARCHITECTURE.md (partner)", IMP + DECL + USE, ARCH_LINE, "pass"),
    ("the same import, not named in ARCHITECTURE.md", IMP + DECL + USE, "", "fail:arch-missing"),
    ("the same import, declared and used by nothing", IMP + DECL, ARCH_LINE, "fail:unused-import"),
    ("an import whose docstring has no bibliography key",
     '/-- A planted import with no key. -/\naxiom Ctl.nokey : True\n#eval AxiomAudit.declareImport ``Ctl.nokey\n', "", "lean-fail"),
    ("native_decide with no purchase docstring", '/-- Planted. -/\ntheorem Ctl.nat : (2 : Nat) + 2 = 4 := by native_decide\n',
     "", "fail:undeclared-purchase"),
    ("native_decide with its purchase docstring (partner)",
     '/-- **Trust purchase: native evaluation.** Planted. -/\ntheorem Ctl.nat : (2 : Nat) + 2 = 4 := by native_decide\n', "", "pass"),
    ("a purchase docstring with no native axiom",
     '/-- **Trust purchase: native evaluation.** Planted. -/\ntheorem Ctl.notNat : (2 : Nat) + 2 = 4 := rfl\n', "", "fail:stale-purchase"),
]


def main() -> int:
    src = (REPO / "scripts/Axioms.lean").read_text(encoding="utf-8")
    arch = (REPO / "ARCHITECTURE.md").read_text(encoding="utf-8")
    if src.count(MARKER) != 1 or "## 5. Trust" not in arch:
        print(f"FAIL  self-test: the plant site is missing ({MARKER!r} in Axioms.lean, § 5 Trust in ARCHITECTURE.md)")
        return 1
    out = REPO / "build/axioms-selftest"
    out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for i, (name, plant, arch_line, want) in enumerate(CONTROLS):
        lean = out / f"control{i:02d}.lean"
        lean.write_text(src.replace(MARKER, plant + MARKER), encoding="utf-8")
        a = out / f"control{i:02d}-ARCHITECTURE.md"
        a.write_text(arch.replace("## 5. Trust\n", "## 5. Trust\n" + arch_line, 1), encoding="utf-8")
        r = subprocess.run(["lake", "env", "lean", "-DautoImplicit=false", "-DrelaxedAutoImplicit=false", str(lean.relative_to(REPO))],
                           cwd=REPO, capture_output=True, text=True)
        (out / f"control{i:02d}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode != 0:
            got, detail = "lean-fail", f"lean exit {r.returncode}"
        else:
            fails, counts = check(r.stdout + r.stderr, a.read_text(encoding="utf-8"))
            got = "pass" if not fails else "fail"
            detail = "; ".join(fails) if fails else f"COUNTS {counts}"
        ok = (got == want) or (want.startswith("fail:") and got == "fail" and f"FAIL {want[5:]} " in detail + " ")
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  control {i:02d}: {name}: wanted {want}, got {got} — {detail[:200]}")
    print("SELF-TEST " + ("PASSED" if not bad else f"FAILED ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
