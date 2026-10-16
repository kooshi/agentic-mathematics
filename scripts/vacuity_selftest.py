#!/usr/bin/env python3
"""The vacuity scan's planted controls: each verdict planted in a copy of `scripts/Vacuity.lean`, run through the gate's own decision
(`vacuity_check.check`), must come out as expected, with a partner that passes beside each failure. Run by `./scripts/vacuity.sh
--self-test`, from the repository root, one Lean process at a time. Copies live under `build/vacuity-selftest/` and are kept.

The load-bearing control is `UNKNOWN`: a concrete carrier nothing refutes or witnesses must read UNKNOWN, never VACUOUS and never
WITNESSED, or the scan is deciding what it cannot know.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from vacuity_check import check  # noqa: E402

MARKER = "-- VACUITY CONTROLS END"
BASE = '''namespace VacuityControls
/-- The control carrier: a predicate on naturals, true exactly below 2. -/
structure Carrier (n : Nat) : Prop where
  small : n < 2
/-- Evidence: `Carrier 0` is inhabited. -/
theorem carrier_zero : Carrier 0 := ⟨by decide⟩
/-- Evidence: `Carrier 5` is empty. -/
theorem not_carrier_five : ¬ Carrier 5 := fun h => absurd h.small (by decide)
end VacuityControls
'''
C = "VacuityControls.Carrier"
# (name, the theorem planted, a baseline line, the site verdict wanted on the planted declaration, the gate's verdict wanted)
CONTROLS = [
    ("the control carrier alone (partner)", "", "", None, "pass"),
    ("a binder over an empty carrier", f"/-- Planted. -/\ntheorem Ctl.vac (h : {C} 5) : (1 : Nat) = 2 := absurd h.small (by decide)\n",
     "", "VACUOUS", "fail:vacuous"),
    ("the same, declared", f"/-- Planted.\nVACUITY DECLARED: a planted control. -/\ntheorem Ctl.vac (h : {C} 5) : (1 : Nat) = 2 := absurd h.small (by decide)\n",
     "", "DECLARED", "pass"),
    ("a declaration on an inhabited carrier", f"/-- Planted.\nVACUITY DECLARED: a false claim. -/\ntheorem Ctl.stale (h : {C} 0) : True := trivial\n",
     "", "STALE", "fail:stale"),
    ("a binder over an inhabited carrier", f"/-- Planted. -/\ntheorem Ctl.wit (h : {C} 0) : True := trivial\n", "", "WITNESSED", "pass"),
    ("a binder over a carrier with a free parameter", f"/-- Planted. -/\ntheorem Ctl.gen (n : Nat) (h : {C} n) : True := trivial\n",
     "", "GENERIC", "pass"),
    ("a concrete carrier nothing decides", f"/-- Planted. -/\ntheorem Ctl.unk (h : {C} 7) : True := trivial\n", "", "UNKNOWN", "fail:unknown"),
    ("the same, in the baseline (partner)", f"/-- Planted. -/\ntheorem Ctl.unk (h : {C} 7) : True := trivial\n", "UNKNOWN Ctl.unk",
     "UNKNOWN", "pass"),
    ("a baseline entry that no longer holds", "", "UNKNOWN Ctl.gone", None, "fail:baseline-stale"),
    ("a refutation over an empty carrier is skipped", f"/-- Planted. -/\ntheorem Ctl.ref (h : {C} 5) : False := absurd h.small (by decide)\n",
     "", "SKIPPED", "pass"),
]


def site_verdict(out: str, decl: str) -> str:
    hits = re.findall(r"^SITE (\w+) " + re.escape(decl) + r" ::", out, re.M)
    return hits[0] if len(hits) == 1 else ("none" if not hits else "several")


def main() -> int:
    src = (REPO / "scripts/Vacuity.lean").read_text(encoding="utf-8")
    if src.count(MARKER) != 1 or "`VacuityControls.Carrier" not in src:
        print("FAIL  self-test: the plant site or the control carrier's entry in trackedProps is missing")
        return 1
    out = REPO / "build/vacuity-selftest"
    out.mkdir(parents=True, exist_ok=True)
    bad, refutations = 0, {}
    for i, (name, plant, bline, want_site, want) in enumerate(CONTROLS):
        lean = out / f"control{i:02d}.lean"
        lean.write_text(src.replace(MARKER, BASE + plant + MARKER), encoding="utf-8")
        r = subprocess.run(["lake", "env", "lean", "-DautoImplicit=false", "-DrelaxedAutoImplicit=false", str(lean.relative_to(REPO))],
                           cwd=REPO, capture_output=True, text=True)
        text = r.stdout + r.stderr
        (out / f"control{i:02d}.log").write_text(text, encoding="utf-8")
        if r.returncode != 0:
            print(f"FAIL  control {i:02d}: {name}: the copy did not elaborate (lean exit {r.returncode})")
            bad += 1
            continue
        fails = check(text, bline + "\n")
        got = "pass" if not fails else "fail"
        m = re.search(r"refutations-skipped=(\d+)", text)
        refutations[i] = int(m.group(1)) if m else -1
        decl = re.search(r"theorem (Ctl\.\w+)", plant).group(1) if plant else None
        site = site_verdict(text, decl) if decl else None
        ok = (got == want or (want.startswith("fail:") and any(f.startswith(f"FAIL {want[5:]} ") for f in fails)))
        if want_site == "SKIPPED":
            ok = ok and site == "none" and refutations[i] == refutations.get(0, -2) + 1
        elif want_site:
            ok = ok and site == want_site
        if i == 0:
            ok = ok and site_verdict(text, "VacuityControls.carrier_zero") == "WITNESSED"
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  control {i:02d}: {name}: site {site}, gate {got} (wanted {want_site}, {want})"
              + (f" — {fails[0]}" if fails else ""))
    print("SELF-TEST " + ("PASSED" if not bad else f"FAILED ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
