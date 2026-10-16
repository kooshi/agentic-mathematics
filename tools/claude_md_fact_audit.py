#!/usr/bin/env python3
"""Fact audit for an edit of the loaded and the addressed front files: which fact tokens were in the old version and are NOWHERE in
the new one, and whether the files are within their size budgets.

The corpus is `CLAUDE.md` joined with every file its sections point to as a home (`--also`: the grokkings, the retired grokkings and
their instances, `LEDGER.md`, `LEAN.md`, `RUNNING.md`, the ranked stubs), each only where it exists. *Why one corpus:* the one-home
rule moves a fact from one file to another, and an audit of one file would read every such move as a loss. A token may also leave
the corpus for an EXTERNAL_HOMES file, which is then checked to hold it on every run.

Usage (standard library only; run from the repository root):

    python3 tools/claude_md_fact_audit.py                 # git HEAD's corpus against the working tree's
    python3 tools/claude_md_fact_audit.py --base <rev>    # any git revision as the old version: the previous filing's commit
    python3 tools/claude_md_fact_audit.py --dupes         # literally repeated 10-word runs: the one-home rule's tripwire
    python3 tools/claude_md_fact_audit.py --self-test     # plant each fault in a built-in corpus and watch each one fire

What FAILS the run (exit status 1):
  * a fact token of the old version that occurs nowhere in the new one -- dates, bibliography keys, backticked spans, identifiers
    (M-nn, Gnn, row nn, ...), theorem references, numbers, grade tags, proper names, and every chunk holding a digit or a
    mathematical character -- because a fact dropped in a rewrite reads afterwards as never having been known;
  * a grokking's status tag changed (a reading silently promoted), a grokking or a ledger row gone (they are demoted, never deleted);
  * a PROTECTED region not byte-identical (a region is the blank-line-delimited block holding the tag "[PROTECTED — never compress,
    trim" plus the blocks after it, up to the next block that opens with "**" or "#");
  * a recorded counts line that scripts/gate_report.py reads gone or doubled;
  * a heading gone (other files cite sections by name), or a `row N` / `GN` pointer to nothing;
  * `CLAUDE.md` over 80,000 bytes or the grokkings over 200,000: both load whole at every launch.
It prints bytes per section before and after.

Deliberate re-spellings go in NORMALISE (applied to BOTH versions before extraction, so old and new spellings meet); tokens
deliberately allowed to vanish go in ALLOW with the reason; tokens moved to a file outside the corpus go in EXTERNAL_HOMES. All three
are printed on every run: an allowance is a reviewed decision, never a silent one.

WHAT THIS CANNOT SEE: a number can survive while the sentence that gave it meaning is gone, and a small number that occurs a hundred
times hides the loss of one occurrence. This audit is the floor, not the check: the filing is still read.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

# (regex, replacement, reason) -- applied to BOTH versions before token extraction.
NORMALISE: list[tuple[str, str, str]] = [
    (r"(?<=\d),(?=\d{3}(?!\d))", "", "thousands separators: 1,581 and 1581 are one number"),
    (r"`(axiom audit: |vacuity: )[^`]*`", r"`\1…`",
     "the recorded counts lines move at every close; scripts/gate_report.py reviews their numbers, and the counts-line check keeps "
     "the line itself"),
]
# token -> reason: tokens deliberately allowed to vanish.
ALLOW: dict[str, str] = {}
# token -> (path, reason): tokens moved to a file outside the corpus, which must hold them.
EXTERNAL_HOMES: dict[str, tuple[str, str]] = {}
# the recorded counts lines scripts/gate_report.py reads (CLAUDE.md § Trust ledger and § The gate)
COUNT_LINES = ("axiom audit: ", "vacuity: ")
PROTECTED_TAG = "[PROTECTED — never compress, trim"
MATH = set("αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩℚℝℤℂℕ𝔽√≤≥≠≡≈∈∉⊆⊂⊇⊄∣∤∀∃∧∨¬⟹⟸⟺→↦×·∞∅∩∪⌈⌉⌊⌋₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ⁻⁺′±−½∑∏")
STRIP = ".,;:!?\"'“”‘’—–-*`|…~"
ALSO = (".claude/skills/grokkings/SKILL.md", "plans/GROKKINGS-RETIRED.md", "plans/GROKKING-INSTANCES.md", "LEDGER.md", "LEAN.md",
        "RUNNING.md", "plans/FRONTIER-STUBS.md")
BUDGETS = (("CLAUDE.md", 80_000), (".claude/skills/grokkings/SKILL.md", 200_000))


def normalise(text: str, table=None) -> str:
    for pat, rep, _ in (NORMALISE if table is None else table):
        text = re.sub(pat, rep, text)
    return text


def _balance(tok: str) -> str:
    for o, c in ("()", "[]", "{}"):
        while tok.startswith(o) and tok.count(o) > tok.count(c):
            tok = tok[1:]
        while tok.endswith(c) and tok.count(c) > tok.count(o):
            tok = tok[:-1]
    if len(tok) > 2 and tok[0] + tok[-1] in ("()", "[]") and not any(c in tok[1:-1] for c in "()[]"):
        tok = tok[1:-1]                                         # "(161)" and "161" are one token
    return tok


def chunks(text: str):
    for raw in text.replace("`", " ").split():
        tok = raw
        for _ in range(4):
            tok = _balance(tok.strip(STRIP))
        tok = re.sub(r"-[A-Za-z][A-Za-z-]*$", "", tok)          # 1581-vertex -> 1581
        tok = re.sub(r"^[A-Za-z]+-(?=\d)", "", tok)              # disc-316 -> 316 (identifiers are the id class's business)
        if re.fullmatch(r"\d+(?:\.\d+)?", tok):
            continue                                            # a bare number is the num class's business
        if tok and (any(ch.isdigit() for ch in tok) or any(ch in MATH for ch in tok)):
            yield tok


def facts(text: str) -> dict[str, Counter]:
    """Token classes of one text (already normalised)."""
    out: dict[str, Counter] = defaultdict(Counter)
    out["date"].update(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text))
    out["bib"].update(re.findall(r"`(\[[A-Za-z][A-Za-z0-9]+\])`", text))
    # backticked identifiers, paths and commands; backticked MATHEMATICS is covered chunk by chunk below
    out["code"].update(c for c in re.findall(r"`([^`\n]+)`", text) if not any(ch in MATH for ch in c))
    out["id"].update(re.findall(r"\b(?:M-\d+|arXiv:[\d.]+|[A-Z]{1,2}(?:-[A-Z]{1,2})?-?\d+(?:\.\d+)?[a-z]?)\b", text))
    for m in re.finditer(r"\b[Rr]ows?\s+((?:\d+(?:[–-]\d+)?)(?:(?:,\s*|\s+and\s+|,\s+and\s+)\d+(?:[–-]\d+)?)*)", text):
        for n in re.findall(r"\d+", m.group(1)):
            out["row"][f"row {n}"] += 1
    out["ref"].update(re.sub(r"\s+", " ", r) for r in re.findall(
        r"(?:Thms?\.?|Theorems?|Props?\.|Lemma|Table|Remark|Cor\.|Example|Open Problem|OP|§|¶)\s*[\dA-Z][\w.]*(?:\([ivx]+\))?", text))
    out["num"].update(re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text))
    out["tag"].update(m.group(0) for m in re.finditer(r"(?<!`)\[[a-z][^\]\n]{1,90}\]", text))
    out["chunk"].update(chunks(text))
    lower = set(re.findall(r"\b[a-z][a-zé'’-]+\b", text))
    for w in re.findall(r"\b[A-Z][A-Za-zéúöü'’]+\b", text):
        if w.lower() not in lower:
            out["name"][w] += 1
    return out


def words(text: str) -> Counter:
    return Counter(w for w in re.findall(r"\b[a-zé][a-zé'’-]{4,}\b", text.lower()))


def entries(text: str) -> dict[str, str]:
    """Split into named entries: ledger rows, grokkings, numbered items, stub rows, else the enclosing heading."""
    out: dict[str, list[str]] = defaultdict(list)
    heading, key = "(top)", "(top)"
    for line in text.split("\n"):
        if re.match(r"^#{1,4} ", line):
            heading = key = line.lstrip("# ").strip()
        elif m := re.match(r"^\| [\d–]+ \| \*{0,2}(M-\d+)", line):
            key = f"paths {m.group(1)}"
        elif m := re.match(r"^\| (\d+) \|", line):
            key = f"row {m.group(1)}"
        elif m := re.match(r"^\* \*\*(G\d+) ", line):
            key = m.group(1)
        elif (m := re.match(r"^(\d+)\. \*\*", line)) and "problem stands" in heading:
            key = f"stands item {m.group(1)}"
        elif line.startswith("|") and not key.startswith(("row", "paths")):
            key = heading
        elif not line.strip() and not key.startswith("G"):
            key = heading
        out[key].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def protected_regions(text: str) -> list[str]:
    blocks = re.split(r"\n[ \t]*\n", text)
    regions, i = [], 0
    while i < len(blocks):
        if PROTECTED_TAG in blocks[i]:
            j = i + 1
            while j < len(blocks) and not blocks[j].lstrip().startswith(("**", "#")):
                j += 1
            regions.append("\n\n".join(blocks[i:j]))
            i = j
        else:
            i += 1
    return regions


def token_proxy(text: str) -> int:
    """A PROXY for model tokens (no tokenizer is available offline): an ASCII word costs ceil(len/6), a digit run ceil(len/3),
    every other ASCII non-space character 1, and a non-ASCII character 1 per 2 bytes of its UTF-8 form rounded up (so α is 1,
    ≤ and ₂ are 2, 𝔽 is 2). Good for comparing two versions of one file; not a count."""
    n = 0
    for m in re.finditer(r"[A-Za-z]+|\d+|\S", text):
        g = m.group(0)
        if g[0].isascii() and g[0].isalpha():
            n += -(-len(g) // 6)
        elif g[0].isdigit():
            n += -(-len(g) // 3)
        elif g.isascii():
            n += 1
        else:
            n += -(-len(g.encode()) // 2)
    return n


def section_bytes(text: str) -> list[tuple[str, int]]:
    out, cur, size = [], "(preamble)", 0
    for line in text.split("\n"):
        if re.match(r"^#{1,3} ", line):
            out.append((cur, size))
            cur, size = line.strip(), 0
        size += len(line.encode()) + 1
    out.append((cur, size))
    return out


STRONG = ("date", "bib", "code", "id", "row", "ref", "num", "tag", "chunk", "name")


def audit(old: str, new: str, *, table=None, allow=None, homes=None, moves: str | None = None, show_words=False, quiet=False) -> list[str]:
    """Return the list of failures (empty = pass). Prints the report unless quiet."""
    say = (lambda *a: None) if quiet else print
    allow = ALLOW if allow is None else allow
    homes = EXTERNAL_HOMES if homes is None else homes
    home_text: dict[str, str] = {}
    fails: list[str] = []
    o_n, n_n = normalise(old, table), normalise(new, table)
    fo, fn = facts(o_n), facts(n_n)
    if sum(len(c) for c in fo.values()) < 30:
        fails.append("the extractor found almost nothing in the OLD version: the audit is blind, not green")
    say(f"bytes: {len(old.encode()):,} -> {len(new.encode()):,}  ({len(new.encode()) - len(old.encode()):+,})")
    say(f"token PROXY (see token_proxy; not a tokenizer): {token_proxy(old):,} -> {token_proxy(new):,}  ({token_proxy(new) - token_proxy(old):+,})")
    for cls in STRONG:
        lost = sorted(t for t in fo[cls] if t not in fn[cls] and t not in allow)
        if cls == "name":   # a name survives inside a bibliography key: Cranston in [CranstonRabern2015]
            lost = [t for t in lost if re.sub(r"['’]s$", "", t) not in n_n]
        homed = [t for t in lost if t in homes]
        lost = [t for t in lost if t not in homes]
        say(f"[{cls}] {len(fo[cls])} distinct before, {len(fn[cls])} after, LOST {len(lost)}, homed outside the corpus {len(homed)}")
        for t in homed:
            path = homes[t][0]
            if path not in home_text:
                home_text[path] = normalise(Path(path).read_text(encoding="utf-8"), table) if Path(path).exists() else ""
            if t in home_text[path]:
                say(f"    HOMED {cls}: {t!r} in {path}")
            else:
                fails.append(f"external home {path} lacks {cls} token {t!r}")
        for t in lost:
            say(f"    LOST {cls}: {t!r}  (was ×{fo[cls][t]})")
            fails.append(f"lost {cls} token {t!r}")
    # grokking status tags
    eo, en = entries(o_n), entries(n_n)
    for k, body in eo.items():
        if re.fullmatch(r"G\d+", k):
            head = re.match(r"\* \*\*G\d+ — .*?\*\*", body, re.S)
            tag_o = re.search(r"\[[^\]]+\]", head.group(0)) if head else None
            nb = en.get(k)
            if nb is None:
                fails.append(f"grokking {k} is gone")
                continue
            head_n = re.match(r"\* \*\*G\d+ — .*?\*\*", nb, re.S)
            tag_n = re.search(r"\[[^\]]+\]", head_n.group(0)) if head_n else None
            a = re.sub(r"\s+", " ", tag_o.group(0)) if tag_o else None
            b = re.sub(r"\s+", " ", tag_n.group(0)) if tag_n else None
            if a != b and f"{k}:{a}" not in allow:
                fails.append(f"grokking {k} status tag changed: {a} -> {b}")
    for k in eo:
        if k.startswith("row ") and k not in en:
            fails.append(f"ledger {k} is gone")
    # pointers: a file that points instead of retelling must not point at nothing
    rows_n = {k[4:] for k in en if k.startswith("row ")}
    groks_n = {k for k in en if re.fullmatch(r"G\d+", k)}
    dangling = sorted({t for t in fn["row"] if t[4:] not in rows_n}
                      | {g for g in re.findall(r"\bG\d{1,2}\b", n_n) if g not in groks_n})
    say(f"pointers: {len(fn['row'])} distinct row references, {len(groks_n)} grokkings; dangling: {dangling or 'none'}")
    for d in dangling:
        if d not in allow:
            fails.append(f"dangling pointer: {d} is cited and no such entry exists")
    # protected regions: every old region must survive byte-identical; a NEW region (the principal may protect new text) is
    # allowed and reported
    po, pn = protected_regions(old), protected_regions(new)
    say(f"PROTECTED regions: {len(po)} before ({', '.join(str(len(p.encode())) for p in po)} bytes), {len(pn)} after")
    if any(p not in pn for p in po):
        fails.append("a PROTECTED region is not byte-identical")
    added = [p for p in pn if p not in po]
    if added:
        say(f"PROTECTED regions added: {len(added)} ({', '.join(p.split(chr(10))[0][:60] for p in added)})")
    # the recorded counts lines scripts/gate_report.py reads: each must survive (its numbers may move; the gate report reviews them)
    for prefix in COUNT_LINES:
        had = len(re.findall("`" + re.escape(prefix), old))
        has = len(re.findall("`" + re.escape(prefix), new))
        if had and has != 1:
            fails.append(f"the recorded counts line `{prefix}…` that scripts/gate_report.py reads is gone or doubled ({has} copies)")
        say(f"counts line `{prefix}…`: {has} cop{'y' if has == 1 else 'ies'}")
    # headings
    ho = [l for l in old.split("\n") if re.match(r"^#{1,4} ", l)]
    hn = set(l for l in new.split("\n") if re.match(r"^#{1,4} ", l))
    for h in ho:
        if h not in hn and h not in allow:
            fails.append(f"heading disappeared (other files cite sections by name): {h!r}")
    # sections
    so, sn = section_bytes(old), dict(section_bytes(new))
    say("\nbytes per section (before -> after):")
    for name, b in so:
        a = sn.pop(name, None)
        say(f"  {b:8,} -> {a if a is None else format(a, '8,')}  {('' if a is None else format(a - b, '+,')):>8}  {name}")
    for name, a in sn.items():
        say(f"  {'new':>8} -> {a:8,}  {'':>8}  {name}")
    if show_words:
        wo, wn = words(o_n), words(n_n)
        gone = sorted(w for w in wo if w not in wn)
        say(f"\nvocabulary that vanished ({len(gone)} words; a reading aid, never a failure):")
        say("  " + " ".join(gone))
    if moves:
        lines = []
        where: dict[tuple[str, str], list[str]] = defaultdict(list)
        f_en = {k: facts(v) for k, v in en.items()}
        for k, f in f_en.items():
            for cls in STRONG:
                for t in f[cls]:
                    where[(cls, t)].append(k)
        for k, body in eo.items():
            f_old, f_new = facts(body), f_en.get(k, defaultdict(Counter))
            left = [(cls, t) for cls in ("date", "bib", "code", "id", "row", "ref", "num", "chunk", "name")
                    for t in f_old[cls] if t not in f_new[cls] and not (cls == "num" and len(t) < 2)]
            if left:
                lines.append(f"== {k}: {len(left)} tokens left this entry")
                for cls, t in sorted(set(left)):
                    homes = where.get((cls, t), [])
                    lines.append(f"   {cls:5} {t!r} -> {', '.join(homes[:5]) if homes else 'NOWHERE'}{' …' if len(homes) > 5 else ''}")
        Path(moves).write_text("\n".join(lines) + "\n", encoding="utf-8")
        say(f"\nrelocation map: {len(lines)} lines -> {moves}")
    say("\nnormalisations in force:")
    for pat, rep, why in (NORMALISE if table is None else table):
        say(f"  {pat!r} -> {rep!r}: {why}")
    say(f"external homes in force: {len(homes)}")
    for t, (path, why) in homes.items():
        say(f"  {t!r} -> {path}: {why}")
    say(f"allowances in force: {len(allow)}")
    for t, why in allow.items():
        say(f"  {t!r}: {why}")
    say("")
    for f in fails:
        say("FAIL:", f)
    say("AUDIT " + ("FAILED" if fails else "PASSED") + f" ({len(fails)} failure(s))")
    return fails


def corpus_files(main: str, also: tuple = ALSO, root: Path = Path(".")) -> str:
    """The corpus as the audit reads it from disk: the main file, then each home file that exists."""
    text = (root / main).read_text(encoding="utf-8")
    for extra in also:
        if (root / extra).exists():
            text += "\n\n" + (root / extra).read_text(encoding="utf-8")
    return text


SAMPLE = """# A sample corpus

## Notation

- **The standard three axioms**: `[propext, Classical.choice, Quot.sound]`.

## Frontier

*Last updated: 2026-01-05 — the filing of M-3, which proved the bound 4817 at radius √7 (row 2; `[Smith2020]` Theorem 4).*

The kernel holds the count 90313 at level 12 (row 1, G1), and the lemma `Proofs.Sample.bound_le` closes it.

**Every long-running phase checkpoints.** **[PROTECTED — never compress, trim or paraphrase this paragraph.]** A run expected to
exceed fifteen minutes persists its progress at natural acceptance points and resumes from that state after a kill, because a
process whose state lives only in memory loses every hour it ran when it dies; the resume command is written beside the path.

**The next rule.** It opens with two stars, so the region above ends here.

### Paths forward

| rank | stub | the question |
|---|---|---|
| 1 | **M-4 the next bound** | does 5203 hold? |

## Trust ledger

`axiom audit: clean=12 imported=1 purchased=0 axiom-free=3`

## The gate

`vacuity: declarations=40 refutations-skipped=1 sites=6 vacuous=0 stale=0 declared=1 witnessed=4 generic=1 unknown=0`

## The ledger

| row | result |
|---|---|
| 1 | the count 90313 at level 12 |
| 2 | the bound 4817 at radius √7, ϱ-free |

## Grokkings

* **G1 — Counts are layered. [reading]** The count grows by one layer per level, 7517 at level 9. *Do: when a count appears,
  look for the layers. Killing test: a level whose count is not a layer sum.*
* **G2 — Bounds come from layers. [kernel]** The bound 4817 follows from G1's layers. *Do: when a bound is wanted, sum layers.
  Nothing kills it; it kills any larger bound.*

A long prose block that holds a once-only number, 6151, and enough words around it to be an ordinary paragraph of the kind that
gets moved between files when the one-home rule sends an instance to the instances file, which is exactly what the three-file
plants exercise, so it must be longer than two hundred characters.
"""


def self_test() -> int:
    """Plant one fault at a time in a copy of the built-in sample; each must fire for its own reason, and each partner must pass."""
    text = SAMPLE
    region = protected_regions(text)[0]
    plants = [
        ("faithful copy (partner)", text, None, None, False),
        ("one number deleted", text.replace("90313", "", 2), None, "lost num", True),
        ("one bibliography key deleted", text.replace("`[Smith2020]`", "[x]"), None, "lost bib", True),
        ("one PROTECTED byte changed", text.replace(region, region[:100] + "x" + region[101:]), None, "PROTECTED", True),
        ("the axiom counts line deleted", text.replace("`axiom audit: clean=12 imported=1 purchased=0 axiom-free=3`", ""), None,
         "counts line", True),
        ("the axiom counts changed (partner: counts move at every close)", text.replace("clean=12", "clean=13"), None, "lost", True),
        ("a heading renamed", text.replace("### Paths forward", "### Paths ahead"), None, "heading disappeared", True),
        ("a pointer to a row that does not exist", text.replace("(row 2;", "(row 9;"), None, "dangling pointer", True),
        ("a grokking promoted", text.replace("Counts are layered. [reading]", "Counts are layered. [kernel]"), None,
         "status tag changed", True),
        ("a grokking deleted", text.replace(text[text.index("* **G2"):text.index("A long prose")], ""), None, "grokking G2 is gone",
         True),
        ("a re-spelling WITHOUT a normalisation entry", text.replace("√7", "sqrt7"), None, "lost", True),
        ("the same re-spelling WITH its entry (partner)", text.replace("√7", "sqrt7"), NORMALISE + [(r"√7", "sqrt7", "self-test")],
         None, False),
    ]
    bad = 0
    for name, planted, table, needle, must_fail in plants:
        fails = audit(text, planted, table=table, allow={}, homes={}, quiet=True)
        if "partner: counts move" in name:   # a count changing at a close is reviewed by the gate report, not failed here
            ok = not fails
        else:
            ok = bool(fails) == must_fail and ((not must_fail) or any(needle in x for x in fails))
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'}  {name}: {'fired' if fails else 'passed'}" + (f" -- {fails[0]}" if fails else ""))
    # the files: a block moved to a home file passes; the same move with a fact dropped, or with the home not joined, fails
    pick = text[text.index("A long prose"):].strip()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "plans").mkdir()
        (root / "CLAUDE.md").write_text(text.replace(pick, "moved: see the instances file"), encoding="utf-8")
        for name, inst, joined, needle, must_fail in [
            ("a block moved to the instances file, verbatim (partner)", pick, True, None, False),
            ("the same move with 6151 deleted from the copy", pick.replace("6151", ""), True, "lost num", True),
            ("the same move with the instances file NOT joined", pick, False, "lost", True),
        ]:
            (root / "plans/GROKKING-INSTANCES.md").write_text(inst, encoding="utf-8")
            new = corpus_files("CLAUDE.md", ALSO if joined else (), root)
            fails = audit(text, new, allow={}, homes={}, quiet=True)
            ok = bool(fails) == must_fail and (not must_fail or any(needle in x for x in fails))
            bad += not ok
            print(f"  {'ok ' if ok else 'BAD'}  {name}: {'fired' if fails else 'passed'}" + (f" -- {fails[0]}" if fails else ""))
        base_n = dupes(text, quiet=True)
        both_n = dupes(text + "\n\n" + pick, quiet=True)
        ok = both_n > base_n
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'}  a block told twice raises --dupes: {base_n} -> {both_n}")
    print("SELF-TEST " + ("FAILED" if bad else "PASSED"))
    return 1 if bad else 0


def dupes(text: str, n: int = 10, quiet: bool = False) -> int:
    """List every run of n words that occurs twice or more, outside the PROTECTED regions, merged into maximal runs:
    the one-home-per-fact rule's tripwire at a milestone close (it sees literal retelling only, never paraphrase)."""
    for r in protected_regions(text):
        text = text.replace(r, "")
    w = text.split()
    seen: dict[tuple, int] = {}
    hit = [False] * len(w)
    for i in range(len(w) - n + 1):
        k = tuple(w[i:i + n])
        if k in seen:
            for j in range(i, i + n):
                hit[j] = True
        else:
            seen[k] = i
    runs, i = [], 0
    while i < len(w):
        if hit[i]:
            j = i
            while j < len(w) and hit[j]:
                j += 1
            runs.append(" ".join(w[i:j]))
            i = j
        else:
            i += 1
    total = sum(len(r.encode()) for r in runs)
    if quiet:
        return len(runs)
    print(f"{len(runs)} repeated runs of >= {n} words, {total:,} bytes in second and later tellings:")
    for r in sorted(runs, key=len, reverse=True):
        print(f"  {len(r.encode()):5,} B  {r[:150]}{'…' if len(r) > 150 else ''}")
    return len(runs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="HEAD", help="git revision holding the old version (default HEAD)")
    ap.add_argument("--old", help="read the old corpus from this file instead of git")
    ap.add_argument("--new", default="CLAUDE.md")
    ap.add_argument("--also", nargs="*", default=list(ALSO), help="home files joined to the corpus (each only if present)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dupes", action="store_true", help="list literally repeated 10-word runs in the new corpus, then exit")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.dupes:
        dupes(corpus_files(a.new, tuple(a.also)))
        return 0

    def corpus_rev(rev: str) -> str | None:
        r = subprocess.run(["git", "show", f"{rev}:{a.new}"], capture_output=True)
        if r.returncode != 0:
            print(f"AUDIT COULD NOT RUN: git show {rev}:{a.new} failed: {r.stderr.decode().strip()}", file=sys.stderr)
            return None
        text = r.stdout.decode("utf-8")
        for extra in a.also:
            r2 = subprocess.run(["git", "show", f"{rev}:{extra}"], capture_output=True)
            if r2.returncode == 0:
                text += "\n\n" + r2.stdout.decode("utf-8")
        return text

    old = Path(a.old).read_text(encoding="utf-8") if a.old else corpus_rev(a.base)
    if old is None:
        return 2
    print(f"corpus: {a.new} + {' + '.join(a.also)} (each joined if present)")
    new = corpus_files(a.new, tuple(a.also))
    failed = bool(audit(old, new))
    for f, cap in BUDGETS:
        if Path(f).exists():
            n = len(Path(f).read_bytes())
            print(f"size: {f} {n:,} of {cap:,} bytes")
            if n > cap:
                print(f"FAIL: {f} is {n:,} bytes, over its {cap:,}-byte budget")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
