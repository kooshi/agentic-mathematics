#!/usr/bin/env python3
"""Zero `sorry`, checked on the source, and every module reached by the audits.

    python3 scripts/nosorry.py              # the check; exit 1 on any finding
    python3 scripts/nosorry.py --self-test  # plant each finding in a scratch library and watch it fire

Two findings, each a hole the axiom audit cannot see on its own:
* **a `sorry` token** in a module under `Proofs/`, outside comments and string literals. The axiom audit catches `sorryAx` in every
  declaration it reads; this catches one in a declaration it does not read (an `example`, a `#eval`, a module outside the root) and
  names the line.
* **a module not reached from `Proofs.lean`.** The audits import only the root, so a module the root does not import, directly or
  through another module, is checked by nothing — the build compiles it, and nothing audits it.
Standard library only.
"""
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMPORT = re.compile(r"^import\s+(Proofs[\w.]*)", re.M)


def code_only(src: str) -> str:
    """The source with comments (line, block — nested — and doc) and string literals blanked, line structure kept."""
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if depth == 0 and src.startswith("--", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/-", i):
            depth += 1
            out.append("  ")
            i += 2
        elif depth > 0 and src.startswith("-/", i):
            depth -= 1
            out.append("  ")
            i += 2
        elif depth == 0 and src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(re.sub(r"[^\n]", " ", src[i:j + 1]))
            i = j + 1
        else:
            out.append(src[i] if depth == 0 or src[i] == "\n" else " ")
            i += 1
    return "".join(out)


def module_name(root: Path, f: Path) -> str:
    return ".".join(f.relative_to(root).with_suffix("").parts)


def check(root: Path) -> list[str]:
    findings = []
    files = sorted((root / "Proofs").rglob("*.lean"))
    rootfile = root / "Proofs.lean"
    if not rootfile.exists():
        return ["Proofs.lean is missing: nothing is reached, so nothing is audited"]
    for f in files + [rootfile]:
        code = code_only(f.read_text(encoding="utf-8", errors="replace"))
        for k, line in enumerate(code.split("\n"), 1):
            if re.search(r"(?<![\w.'])sorry(?![\w'])", line):
                findings.append(f"sorry {f.relative_to(root)}:{k}")
    graph = {module_name(root, f): set(IMPORT.findall(code_only(f.read_text(encoding="utf-8")))) for f in files}
    reached, todo = set(), list(IMPORT.findall(code_only(rootfile.read_text(encoding="utf-8"))))
    while todo:
        m = todo.pop()
        if m not in reached:
            reached.add(m)
            todo += list(graph.get(m, ()))
    for m in sorted(set(graph) - reached):
        findings.append(f"unreached {m}: Proofs.lean does not import it, directly or through another module, so no audit reads it")
    return findings


def self_test() -> int:
    results = []
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "Proofs").mkdir()
        (root / "Proofs.lean").write_text("import Proofs.A\n", encoding="utf-8")
        a = root / "Proofs/A.lean"

        def run(what, text, extra=None, want=None):
            a.write_text(text, encoding="utf-8")
            if extra:
                (root / "Proofs/B.lean").write_text(extra, encoding="utf-8")
            got = check(root)
            ok = (not got) if want is None else any(g.startswith(want) for g in got)
            results.append((what, ok, got))
            if extra:
                (root / "Proofs/B.lean").unlink()

        run("a clean module passes (partner)", "theorem t : True := trivial\n")
        run("a sorry in a proof fails", "theorem t : True := by\n  sorry\n", want="sorry Proofs/A.lean:2")
        run("a sorry in an example fails", "example : True := sorry\n", want="sorry")
        run("'sorry' in a line comment passes", "-- no sorry here\ntheorem t : True := trivial\n")
        run("'sorry' in a nested block comment and a docstring passes",
            "/- outer /- sorry -/ still sorry -/\n/-- says sorry -/\ntheorem t : True := trivial\n")
        run("'sorry' in a string passes", 'def s : String := "sorry"\n')
        run("an identifier containing sorry passes", "def sorryCount : Nat := 0\n")
        run("a module the root does not reach fails", "theorem t : True := trivial\n", extra="theorem u : True := trivial\n",
            want="unreached Proofs.B")
        run("the same module, imported by A, passes (partner)", "import Proofs.B\ntheorem t : True := trivial\n",
            extra="theorem u : True := trivial\n")
    for what, ok, got in results:
        print(f"{'PASS' if ok else 'FAIL'}  self-test: {what}" + ("" if ok else f" — got {got}"))
    bad = sum(not ok for _, ok, _ in results)
    print("SELF-TEST " + ("PASSED" if not bad else f"FAILED ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    found = check(REPO)
    for f in found:
        print("FAIL  " + f)
    print("==> nosorry: " + ("FAIL" if found else "OK — no sorry, and every module is reached from Proofs.lean"))
    sys.exit(1 if found else 0)
