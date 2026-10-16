#!/usr/bin/env python3
"""Hold the vendored identities to what was vendored, and each lane's copy of its identity to its skill.

Two things can drift, and this script checks both.

* **A vendored skill.** The identity cores and their companions (`keryx`, `poros*`, `ephodos*`, `debruijn*`) and the two stance
  skills the coordinator borrows (`decompress`, `peer-delegation`) are imported, never edited here. Every file under them is listed
  with its SHA-256 in `scripts/identities.manifest`. `check` fails on a file whose hash differs, a listed file that is missing, and a
  file that is present and not listed.
* **A lane's copy of its identity.** Agent files and output styles cannot import another file (an `@` line in either reaches the
  model as text), so each lane's file carries its identity as a copy: the skill's body, then the lane's workflow, which starts at a
  heading of the form `# <who> in this project — the workflow`. `check` fails when the copy differs from the skill by one byte.

    python3 scripts/identities.py check                 # both checks; non-zero exit on any drift
    python3 scripts/identities.py sync --from <forge>   # copy each identity skill from <forge>/identities/*/skills/<name>/,
                                                        # re-record the manifest, re-copy every identity block, then check
    python3 scripts/identities.py sync                  # re-copy every identity block from the skills as they stand, then check
    python3 scripts/identities.py record                # re-record the manifest from the tree as it stands (after a deliberate
                                                        # update of a skill by hand); prints every file whose hash changed
    python3 scripts/identities.py --self-test           # plant each drift in a copy of the tree; each must fail, the faithful
                                                        # copy must pass

`<forge>` is a checkout of the repository the identities are forged in, laid out as `identities/<identity>/skills/<skill>/`. Copy from
its committed tree, not a working copy with edits in it. Standard library only.
"""
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = "scripts/identities.manifest"
IDENTITY_SKILLS = [
    "keryx",
    "poros", "poros-anomaly-hunt", "poros-reframing",
    "ephodos", "ephodos-invention", "ephodos-recognition", "ephodos-verification",
    "debruijn", "debruijn-debugging", "debruijn-domain-modeling", "debruijn-experience-modeling", "debruijn-init",
    "debruijn-meta", "debruijn-obligation-modeling",
]
STANCE_SKILLS = ["decompress", "peer-delegation"]   # not in the forge: updated by hand, then `record`
VENDORED = IDENTITY_SKILLS + STANCE_SKILLS
TARGETS = [  # (the file a mind loads, the skill whose body is its identity)
    (".claude/output-styles/keryx.md", "keryx"),
    (".claude/agents/poros.md", "poros"),
    (".claude/agents/ephodos.md", "ephodos"),
    (".claude/agents/ephodos-verifier.md", "ephodos"),
    (".claude/agents/debruijn.md", "debruijn"),
    (".claude/agents/debruijn-implementer.md", "debruijn"),
]
MARKER = re.compile(r"^# .+ in this project — the workflow$", re.M)
SKIP = {"__pycache__"}


def vendored_files(root: Path) -> dict[str, str]:
    """{path relative to the root: sha256} for every file under the vendored skills."""
    out = {}
    for name in VENDORED:
        base = root / ".claude/skills" / name
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if f.is_file() and not (SKIP & set(f.relative_to(base).parts)):
                out[f.relative_to(root).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def read_manifest(root: Path) -> dict[str, str]:
    path = root / MANIFEST
    if not path.exists():
        raise ValueError(f"{MANIFEST} is missing: nothing to hold the vendored skills to (run `record` once, deliberately)")
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        out[rel.strip()] = digest
    if not out:
        raise ValueError(f"{MANIFEST} lists no file: a manifest that holds nothing checks nothing")
    return out


def write_manifest(root: Path) -> dict[str, str]:
    files = vendored_files(root)
    lines = ["# The vendored skills, one line per file: its SHA-256, then its path. Written by `scripts/identities.py record`",
             "# or `sync --from`; never edited by hand. `scripts/identities.py check` fails on any difference.", ""]
    lines += [f"{h}  {p}" for p, h in sorted(files.items())]
    (root / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return files


def split_front(text: str, where: str) -> tuple[str, str]:
    """(the frontmatter with both `---` lines, the body)."""
    if not text.startswith("---\n"):
        raise ValueError(f"{where}: no frontmatter")
    end = text.index("\n---\n", 4) + len("\n---\n")
    return text[:end], text[end:]


def skill_body(root: Path, name: str) -> str:
    path = root / ".claude/skills" / name / "SKILL.md"
    return split_front(path.read_text(encoding="utf-8"), str(path))[1].strip("\n")


def parse(root: Path, rel: str) -> tuple[str, str, str]:
    """(frontmatter, identity block, workflow from its heading on)."""
    front, body = split_front((root / rel).read_text(encoding="utf-8"), rel)
    m = MARKER.search(body)
    if not m:
        raise ValueError(f"{rel}: no '# … in this project — the workflow' heading after the identity")
    return front, body[: m.start()].strip("\n"), body[m.start():]


def check(root: Path, quiet: bool = False) -> int:
    say = (lambda *a: None) if quiet else print
    failures = 0
    try:
        want = read_manifest(root)
        have = vendored_files(root)
    except (OSError, ValueError) as e:
        say(f"FAIL  {e}")
        want, have, failures = {}, {}, 1
    for rel in sorted(set(want) | set(have)):
        if rel not in have:
            say(f"FAIL  {rel}: listed in the manifest and missing from the tree")
            failures += 1
        elif rel not in want:
            say(f"FAIL  {rel}: in a vendored skill and not in the manifest")
            failures += 1
        elif have[rel] != want[rel]:
            say(f"FAIL  {rel}: its hash differs from the manifest's ({have[rel][:12]} against {want[rel][:12]})")
            failures += 1
    if want:
        say(f"{'ok   ' if not failures else 'FAIL '} the vendored skills: {len(have)} files against {len(want)} listed")
    for rel, name in TARGETS:
        try:
            _, identity, workflow = parse(root, rel)
            body = skill_body(root, name)
        except (OSError, ValueError) as e:
            say(f"FAIL  {e}")
            failures += 1
            continue
        if identity != body:
            a, b = identity.split("\n"), body.split("\n")
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            say(f"FAIL  {rel}: the identity differs from .claude/skills/{name}/SKILL.md at its line {i + 1}: "
                f"{(a[i] if i < len(a) else '<end>')[:80]!r} against {(b[i] if i < len(b) else '<end>')[:80]!r}")
            failures += 1
        else:
            say(f"ok    {rel}: identity = {name} ({len(body.encode()):,} bytes), workflow {len(workflow.encode()):,} bytes")
    say("IDENTITIES: " + ("FAIL" if failures else "PASS"))
    return 1 if failures else 0


def sync_blocks(root: Path) -> None:
    for rel, name in TARGETS:
        front, _, workflow = parse(root, rel)
        (root / rel).write_text(front + skill_body(root, name) + "\n\n" + workflow, encoding="utf-8")
        print(f"synced {rel} <- .claude/skills/{name}/SKILL.md")


def sync_from(root: Path, forge: Path) -> int:
    found = {p.name: p for p in forge.glob("identities/*/skills/*") if p.is_dir()}
    missing = [n for n in IDENTITY_SKILLS if n not in found]
    if missing:
        print(f"FAIL  {forge} has no identities/*/skills/ folder for: {', '.join(missing)}; nothing copied")
        return 1
    before = vendored_files(root)
    for name in IDENTITY_SKILLS:
        dst = root / ".claude/skills" / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(found[name], dst, ignore=shutil.ignore_patterns(*SKIP))
    after = write_manifest(root)
    for rel in sorted(set(before) | set(after)):
        if before.get(rel) != after.get(rel):
            print(f"changed {rel}")
    sync_blocks(root)
    return check(root)


def record(root: Path) -> int:
    before = {}
    try:
        before = read_manifest(root)
    except ValueError:
        pass
    after = write_manifest(root)
    for rel in sorted(set(before) | set(after)):
        if before.get(rel) != after.get(rel):
            print(f"recorded change: {rel}")
    print(f"manifest: {len(after)} files")
    return check(root)


def self_test() -> int:
    """Plant each drift in a copy of the tree; each must fail, and the faithful copy must pass."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in [MANIFEST] + [r for r, _ in TARGETS]:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, root / rel)
        for name in VENDORED:
            shutil.copytree(REPO / ".claude/skills" / name, root / ".claude/skills" / name,
                            ignore=shutil.ignore_patterns(*SKIP))
        results.append(("the faithful copy passes", check(root, quiet=True) == 0))

        def planted(what: str, path: Path, mutate) -> None:
            saved = path.read_bytes()
            mutate(path)
            results.append((what, check(root, quiet=True) == 1))
            path.write_bytes(saved)
            results.append((what + " — and the restored copy passes again", check(root, quiet=True) == 0))

        def one_byte(p: Path) -> None:
            b = bytearray(p.read_bytes())
            i = len(b) // 2
            b[i] = ord("X") if b[i] != ord("X") else ord("Y")
            p.write_bytes(bytes(b))

        planted("a one-byte change in a vendored companion fails",
                root / ".claude/skills/ephodos-verification/SKILL.md", one_byte)
        planted("a one-byte change in a gate script fails", root / ".claude/skills/keryx/scripts/brief_gate.py", one_byte)
        lane = root / TARGETS[2][0]
        text = lane.read_text(encoding="utf-8")
        cut = text.index("\n", text.index("<identity>")) + 5
        planted("a one-character drift in a lane's identity block fails", lane,
                lambda p: p.write_text(text[:cut] + ("X" if text[cut] != "X" else "Y") + text[cut + 1:], encoding="utf-8"))
        planted("a missing workflow heading fails", lane,
                lambda p: p.write_text(MARKER.sub("## the workflow", text), encoding="utf-8"))
        extra = root / ".claude/skills/poros/notes.md"
        extra.write_text("an unlisted file\n", encoding="utf-8")
        results.append(("an unlisted file in a vendored skill fails", check(root, quiet=True) == 1))
        extra.unlink()
        gone = root / ".claude/skills/debruijn-init/SKILL.md"
        saved = gone.read_bytes()
        gone.unlink()
        results.append(("a missing vendored file fails", check(root, quiet=True) == 1))
        gone.write_bytes(saved)
        manifest = root / MANIFEST
        msaved = manifest.read_bytes()
        manifest.write_text("# nothing listed\n", encoding="utf-8")
        results.append(("an empty manifest fails", check(root, quiet=True) == 1))
        manifest.write_bytes(msaved)
        results.append(("the copy passes at the end", check(root, quiet=True) == 0))
    for what, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  self-test: {what}")
    ok = all(ok for _, ok in results)
    print("SELF-TEST " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "check"
    if cmd == "check":
        sys.exit(check(REPO))
    if cmd == "sync":
        if len(args) == 3 and args[1] == "--from":
            sys.exit(sync_from(REPO, Path(args[2]).expanduser().resolve()))
        if len(args) == 1:
            sync_blocks(REPO)
            sys.exit(check(REPO))
    if cmd == "record" and len(args) == 1:
        sys.exit(record(REPO))
    if cmd == "--self-test":
        sys.exit(self_test())
    print(__doc__)
    sys.exit(2)
