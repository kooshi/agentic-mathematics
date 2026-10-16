#!/usr/bin/env python3
"""Helpers for a brief generator: quotations by command, the shared header lines, and a job id that is new.

A milestone's briefs are best written by a small generator (`data/mNN/briefs/mk_<job>.py`) that imports this module, so that every
quotation is copied by script from its source and the next brief is a fill of slots, not a re-derivation (the `keryx` identity's
`<philosophy>`). Typical use, from the repository root:

    import sys; sys.path.insert(0, "scripts"); from mkbrief import *
    fresh("M03-E1")                                   # refuses an id already used anywhere
    stmt = Q("data/m03/claims.md", "> **C03-ONE.")    # one line, quoted whole with its source
    open("data/m03/briefs/M03-E1-derivation.md", "w").write(f\"\"\"...{stmt}...{NOSPAWN}\"\"\")

Then run the gate: `python3 .claude/skills/keryx/scripts/brief_gate.py all <brief>`.

    python3 scripts/mkbrief.py --example    # writes data/briefs/example-brief.md, a brief that passes the gate

Standard library only.
"""
import glob
import subprocess
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent) + "/"

STAND = "plans/STANDING-RULES.md — part of this brief; read it in full"
STAND_LEAN = STAND + ". Also `LEAN.md` in full, and `RUNNING.md` § Building and § Make the gate fail, and watch it fail"
NOSPAWN = ("You start no agents of your own (standing rule 1: delegation is one level\n"
           "deep, because the coordinator can only review work it knows exists).")


def line(path: str, prefix: str, contains: str | None = None) -> str:
    """The one line of `path` that starts with `prefix` (and holds `contains`); fails unless exactly one does, because a quotation
    chosen from several candidates is a guess."""
    full = path if path.startswith("/") else ROOT + path
    lines = [x.rstrip("\n") for x in open(full, encoding="utf-8")]
    hits = [x for x in lines if x.startswith(prefix) and (contains is None or contains in x)]
    assert len(hits) == 1, (path, prefix, len(hits))
    return hits[0]


def Q(path: str, prefix: str, heading: str | None = None, contains: str | None = None) -> str:
    """A blockquote of that line with its source line, in the form the brief gate checks."""
    text = line(path, prefix, contains)
    if text.startswith("> "):
        text = text[2:]
    return "> " + text + "\n> — source: " + path + ((" " + heading) if heading else "") + "\n"


def fresh(job: str) -> None:
    """A job id must be new: no record, report, data folder, brief or commit subject of that id anywhere. Call it in every generator
    before writing the brief: an id issued twice once had two jobs writing one record, and neither could tell."""
    hits = [p for pat in (f"plans/{job}-*", f"plans/{job}.md", f"data/*/reports/{job}.md", f"data/*/briefs/{job}-*")
            for p in glob.glob(ROOT + pat)]
    log = subprocess.run(["git", "-C", ROOT, "log", "--all", "--format=%s", "--fixed-strings", "--grep", job + ":"],
                         capture_output=True, text=True).stdout
    assert not hits and not log.strip(), (job, "is taken", hits[:3], log.splitlines()[:2])


def example() -> str:
    """A brief for Poros's first ranking job, quoting one standing rule by command."""
    rule = Q("plans/STANDING-RULES.md", "4. **Every outcome counts.**")
    return f"""# Brief M01-P1 — the first ranking (an example brief; delete it once a real one exists)

*Written by Keryx. Launch line: "Your brief is on disk: read it in full first."*

brief: M01-P1
  identity: Poros — your agent file (`.claude/agents/poros.md`) is your identity and your lane's workflow
  role: the first re-rank of the frontier, and the first milestone's question
  launch: now
  mission: § Why this job
  statements: § The rule this job is judged by
  acceptance: § Done means
  yours: § What is yours to decide
  fences: none — nothing here is blind, because no derivation has run yet
  channel: message the coordinator ("main") for a question you cannot work around; the report goes to `data/m01/reports/M01-P1.md` and to "main" as your hand-back
  standing rules: {STAND}
  record: `plans/POROS-first-ranking.md`
  touches: `plans/POROS-first-ranking.md`, `data/m01/reports/M01-P1.md`
  budget: about 200k by the harness's count, as guidance; hand back at a saved stage before about 300k

## Why this job

The principal has stated the problem in `CLAUDE.md` § The mission and listed the first stubs in `plans/FRONTIER-STUBS.md`. Nothing is
ranked yet, and the first milestone opens on your card.

## The rule this job is judged by

{rule}
## Done means

1. Stage 1, the readback: the quotation above checked against its source, logged in your record.
2. A draft re-rank of every stub, each row with its bearing on the answer, under `## Draft re-rank` in your record.
3. The top stub's question card, with its existence and structural forms, drafted in your record for Keryx to file.

## What is yours to decide

The ranking, the choice of milestone, and whether any stub's question is the wrong one: say so, and why.

{NOSPAWN}
"""


if __name__ == "__main__":
    if sys.argv[1:] == ["--example"]:
        out = Path(ROOT) / "data/briefs/example-brief.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(example(), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
