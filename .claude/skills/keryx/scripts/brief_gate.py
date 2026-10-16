#!/usr/bin/env python3
"""brief_gate.py — the Keryx gate: a brief checked before it leaves.

Conventions checked (see SKILL.md <the_brief>; example-brief.md beside this file passes, example-dirty.md fails by
design, one planted defect per failure):

  quotation  a blockquote — consecutive lines starting with ">" — whose last line is "> — source: <path>" (the word
             "source" in any case). After the path, "§ <heading>" or "row <id>" is an address: the quoted text must
             occur verbatim inside that heading's section (up to the next heading of its level) or inside the table
             row whose first cell is <id>. A heading matches when its text starts with the anchor and the anchor ends a
             word: first as written, and only if no heading matches so, with leading numbers set aside on both sides —
             never a heading whose number differs from a number the anchor gives.
             Anything else after the path is kept for the reader and ignored. Runs of whitespace and blockquote markers
             are ignored. A quotation found verbatim, every "…" in it included, passes: a "…" the source has at that
             point is its text. Otherwise "…" and "[…]" are elisions, and the pieces between them must occur in order —
             except in the statements section, where a statement carries no elision. Every blockquote in a brief is a
             quotation: one with no source line fails, and so do a source that does not resolve, is a directory, or is
             a path the brief's own fence closes (a blind mind must be able to read back what it was sent).
  brief      a line "brief: <id>" at column 0, then indented "field: value" lines, a value continuing on further
             indented lines. The fields:
               identity:        the identity the recipient loads, and the skills it loads fresh
               role:            what it is
               launch:          when it launches: "now", or after which hand-back or commit
               mission:         "§ <heading>" — why the job exists
               statements:      "§ <heading>" holding at least one quotation, or "none — <reason>"
               acceptance:      "§ <heading>" — what done looks like, stated before the work
               yours:           "§ <heading>" — the decisions that are the recipient's
               fences:          "§ <heading>", or "none — <reason>" — never none for a role that names blind, a verifier,
                                a second mind or derivation, a competitor, or independence
               channel:         how the recipient reaches you mid-flight, and where its report goes
               standing rules:  a file that exists (the first path the field names, in the order written) with a paragraph
                                that forbids starting agents — a negation at most three words before a word for it
                                (spawn, subagent, fork, delegate, the Agent tool, agents of your own, start another
                                agent), or that word called forbidden — and gives a reason: a word such as because,
                                reason, why, since, so that, or a clause after a colon or a dash
               record:          the recipient's record; it must be one of the touches, or under one, or match one
               touches:         the paths the recipient may write
               budget:          the size, as guidance, and the hand-back line
             Every "§ <heading>" must name a heading in the brief with text under it. A fence section must name at
             least one path. Every path the brief names outside its quotations must exist, except those in the fence
             section and those the recipient will create: the record, the touches, the channel's paths, and anything
             under a touches directory or matching a touches pattern. A backticked token counts as a path when it ends
             in "/", starts with "~/", has a file extension, or its first directory exists. In a bare name, with no
             "/", the extension counts only when it is a common file type (.md, .py, .lean, .json, …) or the name
             could not be a Lean name (it has a "-" or starts with a digit), so `Finset.card` and `Real.log` are names,
             not missing files. A token whose only "/" leads it, such as a command like `/loop`, names no directory.

What the gate proves, and only this: each quotation is verbatim in its source, at its address when it names one; a
statement carries no elision; no quotation's source is fenced; the fields are present; the sections they name exist and
are not empty; the backticked paths outside quotations exist or are the recipient's to write; a role that names a second
mind has a fence section that names paths; the standing rules have a paragraph that forbids starting agents and gives a
reason. It warns, and does not fail, when a fence names no git history, no shared scratch, or no session transcripts —
the three channels a harness most often leaves open — and when a fenced brief, outside its quotations and its fence, says
"prove" or "confirm" or reports an outcome: decided, settled, established, proved, confirmed, verified, refuted,
succeeded, landed, showed, reduced to, is true or false, or produced, found or gave a result. Each can hand the recipient
the verdict.

What it cannot see: a paraphrase in prose beside the quotation; a statement cut short with no elision mark; a path
written without backticks; a bare file name whose extension it does not list and that could be a Lean name (`run.log`);
a path under the touches that the brief means as an input; a channel that names no real way
to reach you; a verdict given as a grade ("held"), a present tense ("holds"), a confidence, or in words not listed above;
a negation that does not govern the spawning word beside it ("do not hesitate to spawn"); whether the quotation is the
statement that should have been sent; whether the why is the real one; whether the fence names every channel the
recipient can reach.

Subcommands: quotes | brief | all          (all = brief, then quotes, on every file)
Paths resolve from --root (default: the current directory), then from the brief's own directory.
Exit status is non-zero when a check fails. Standard library only.
"""
import fnmatch
import os
import re
import sys

FIELDS = ["identity", "role", "launch", "mission", "statements", "acceptance", "yours", "fences", "channel",
          "standing rules", "record", "touches", "budget"]
SECTION_FIELDS = ["mission", "statements", "acceptance", "yours", "fences"]
MAY_BE_NONE = {"statements", "fences"}
NEW_PATH_FIELDS = ["record", "touches", "channel"]
SOURCE = re.compile(r"^\s*(?:—|--)\s*source:\s*`?([^`\s]+)`?(.*)$", re.I)
ELISION = re.compile(r"\s*(?:\[…\]|\[\.\.\.\]|…)\s*")
TICKED = re.compile(r"`([^`\s]+)`")
EXT = re.compile(r"\.[A-Za-z][A-Za-z0-9]{0,5}$")
# The extensions that make a bare name (no "/") a file. None ends a Lean name in Lean's or Mathlib's code, so `Basic.lean`
# is a file and `Finset.card` is not; log, out, sum, step, set, diff, zip, go, c, h, lock and patch are left out because
# they do (`Real.log`, `Fact.out`, `Finset.sum`, `Array.zip`).
FILE_EXT = set("""md txt rst org tex bib pdf html htm css xml svg png jpg jpeg gif webp py ipynb lean sh bash zsh js mjs ts
                  tsx jsx rs java kt cc cpp hpp cs rb pl lua ml jl swift json jsonl yaml yml toml ini cfg conf csv tsv
                  parquet npy npz pkl h5 sqlite db sql tar gz tgz bz2 xz docx xlsx pptx odt scad stl dxf cir gp dat drat
                  inp msh sta tjp err tmpl""".split())
LEAN_NAME = re.compile(r"^[^\W\d][\w'.]*$")
SECOND_MIND = re.compile(r"\bblind\b|verif|second (?:mind|derivation)|competitor|independen", re.I)
SPAWN = (r"(?:spawn\w*|sub-?agents?|child agents?|children|forks?|forking|delegat\w*|agents? of (?:your|its) own|"
         r"the agent tool|(?:start|launch|run|creat)\w* (?:another|an?|any|other|more) (?:sub)?agents?|other agents)")
FORBIDS_SPAWN = re.compile(r"\b(?:no|not|never|nor|don't|do not|may not|must not|cannot|can't)\b"
                           r"(?:[\s,*]+[\w'’-]+){0,3}?[\s,*]+" + SPAWN + r"|" + SPAWN +
                           r"[^.;:!?]{0,40}?\b(?:forbidden|prohibited|not allowed|not permitted|banned)\b", re.I)
REASON = re.compile(r"\bbecause\b|\breason\b|\bwhy\b|\bso that\b|\bsince\b|:\s+\S|\s—\s", re.I)
VERDICT_WORDS = re.compile(r"(?<!\bor )\b(?:prove|confirm|proved|proven|confirmed|decided|settled|established|showed|"
                           r"verified|refuted|disproved|succeeded|landed|reduced to|"
                           r"(?:is|are|was|were|turned out|came out) (?:true|false))\b(?!\s+or\b)"
                           r"|\b(?:produced|found|yielded|obtained|gave)\b[^.;:]{0,60}?\bresults?\b", re.I)
CHANNELS = [("git history", re.compile(r"git log|git show|commit (?:subject|bod|histor)|git histor", re.I)),
            ("shared scratch", re.compile(r"scratch", re.I)),
            ("session transcripts", re.compile(r"transcript", re.I))]

FAIL, WARN = [], []


def fail(f, msg):
    FAIL.append(f"FAIL  {f}: {msg}")


def warn(f, msg):
    WARN.append(f"warn  {f}: {msg}")


def norm(s):
    s = re.sub(r"(?m)^[ \t]*>[ \t]?", "", s)
    return re.sub(r"\s+", " ", s).strip()


def resolve(p, base, root):
    p = os.path.expanduser(p)
    for c in (os.path.join(root, p), os.path.join(base, p)):
        if os.path.exists(c):
            return c
    return None


def is_path(tok, base, root):
    """A backticked token is a path when it ends in "/", starts with "~/", has an extension, or its first directory
    exists. A bare name's extension counts only when it is a file type in FILE_EXT or the name could not be a Lean name
    (it has a "-" or starts with a digit): `Finset.card` is a name, `fs116-v4.out` a file. "/loop" has no directory."""
    if any(c in tok for c in "<>") or tok.startswith("http"):
        return False
    if tok.startswith("~/") or tok.endswith("/"):
        return True
    if "/" in tok or "." in tok:
        ext = EXT.search(tok.rstrip("*"))
        if ext and not re.match(r"^[\d./]+$", tok) and (
                "/" in tok or ext.group(0)[1:] in FILE_EXT or not LEAN_NAME.match(tok.rstrip("*"))):
            return True
    lead = "/" if tok.startswith("/") else ""
    segs = tok[len(lead):].split("/")
    return len(segs) > 1 and segs[0] != "" and resolve(lead + segs[0], base, root) is not None


def covered(path, patterns):
    """path is one of patterns, lies under one (a directory, written with or without its "/"), or matches one (a glob)."""
    p = re.sub(r"^(?:\./)+", "", path)
    for q in patterns:
        q = re.sub(r"^(?:\./)+", "", q)
        if p == q or p.startswith(q.rstrip("/") + "/") or fnmatch.fnmatch(p, q):
            return True
    return False


def quotations(text):
    """Yield (line number, quoted text, source line or None, character offset) for every blockquote."""
    lines = text.split("\n")
    offs, off = [], 0
    for l in lines:
        offs.append(off)
        off += len(l) + 1
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith(">"):
            start, body = i, []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                body.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            src = None
            if body and SOURCE.match(body[-1]):
                src = body.pop()
            yield start + 1, "\n".join(body), src, offs[start], offs[i - 1] + len(lines[i - 1]) + 1
        else:
            i += 1


def starts(h, a):
    """h begins with a, and a ends at a word boundary: "3" matches "3. The gap", never "30"."""
    return h.startswith(a) and (len(h) == len(a) or not h[len(a)].isalnum())


def heading_name(h):
    return re.sub(r"^[\d.]+\s+", "", h.strip()).strip().lower()


def heading_number(h):
    m = re.match(r"^([\d.]*\d)\.?(?:\s|$)", h.strip())
    return m.group(1) if m else None


def addressed(src_text, raw_anchor):
    """The (start, end) of the section a "§ <anchor>" names, or None. A heading that starts with the anchor as written
    wins; only if none does, the anchor and the headings are compared with their numbers set aside, and a heading whose
    number differs from the anchor's is never taken: "§ 14. Added at round 4" is not "## 12. Added at round 4"."""
    secs = sections(src_text)
    exact = [(a, b) for _, _, a, b, raw in secs if starts(raw, raw_anchor)]
    if exact:
        return exact[0]
    anchor, num = heading_name(raw_anchor), heading_number(raw_anchor)
    named = [(a, b) for nm, _, a, b, raw in secs
             if anchor and starts(nm, anchor) and not (num and heading_number(raw) not in (None, num))]
    return named[0] if named else None


def sections(text):
    """[(heading name, level, body start, body end, raw heading)] for every markdown heading."""
    heads = [(m.start(), len(m.group(1)), heading_name(m.group(2)), m.end(), m.group(2).strip().lower())
             for m in re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", text)]
    out = []
    for j, (s, lvl, name, e, raw) in enumerate(heads):
        end = next((h[0] for h in heads[j + 1:] if h[1] <= lvl), len(text))
        out.append((name, lvl, e, end, raw))
    return out


def section_body(text, name):
    for n, _, a, b, _ in sections(text):
        if n == name:
            return text[a:b], a, b
    return None, 0, 0


def diverges(piece, hay):
    """Where piece leaves hay: the longest word-prefix found, what the brief has next, and what the source has next."""
    words = piece.split(" ")
    k = 0
    while k < len(words) and " ".join(words[:k + 1]) in hay:
        k += 1
    if k == 0:
        return None
    at = hay.find(" ".join(words[:k])) + len(" ".join(words[:k]))
    return " ".join(words[max(0, k - 4):k]), " ".join(words[k:k + 4]), " ".join(hay[at:].split(" ")[1:5])


def find_in_order(pieces, hay):
    pos = 0
    for piece in pieces:
        at = hay.find(piece, pos)
        if at < 0:
            return piece, pos
        pos = at + len(piece)
    return None, pos


def check_quotes(f, text, root, whole_region=None):
    base = os.path.dirname(os.path.abspath(f))
    n = 0
    for line, body, src, off, _ in quotations(text):
        if src is None:
            fail(f, f"line {line}: a quotation with no source line — write \"> — source: <path>\" under it")
            continue
        m = SOURCE.match(src)
        path, rest = m.group(1), m.group(2)
        real = resolve(path, base, root)
        if not real:
            fail(f, f"line {line}: source {path} does not exist")
            continue
        if os.path.isdir(real):
            fail(f, f"line {line}: source {path} is a directory, not a file")
            continue
        n += 1
        src_text = open(real, encoding="utf-8", errors="replace").read()
        hay_all = norm(src_text)
        scope, where = hay_all, None
        sec = re.search(r"§\s*([^;,()]+)", rest)
        row = re.search(r"\brow\s+([A-Za-z0-9_.-]+)", rest)
        if sec:
            hit = addressed(src_text, sec.group(1).strip().lower())
            if not hit:
                fail(f, f"line {line}: source {path} has no heading § {sec.group(1).strip()}")
                continue
            scope, where = norm(src_text[hit[0]:hit[1]]), f"§ {sec.group(1).strip()}"
        elif row:
            rid = row.group(1)
            rows = [l for l in src_text.split("\n")
                    if l.lstrip().startswith("|") and l.strip().strip("|").split("|")[0].strip(" *`") == rid]
            if not rows:
                fail(f, f"line {line}: source {path} has no table row {rid}")
                continue
            scope, where = norm(rows[0]), f"row {rid}"
        q = norm(body)
        if q in scope:
            continue
        if where and q in hay_all:
            fail(f, f"line {line}: in {path}, but not under {where} — the address is a claim too")
            continue
        if whole_region and whole_region[0] <= off < whole_region[1] and ELISION.search(q):
            fail(f, f"line {line}: a statement is quoted whole — no elision inside the statements section")
            continue
        pieces = [p for p in ELISION.split(q) if p]
        missing, pos = find_in_order(pieces, scope)
        if missing is None:
            continue
        if where and find_in_order(pieces, hay_all)[0] is None:
            fail(f, f"line {line}: in {path}, but not under {where} — the address is a claim too")
            continue
        d = diverges(missing, scope[pos:])
        if scope.find(missing) >= 0:
            what = f"\"{missing[:60]}\" is in the source, but before the text the quotation puts ahead of it"
        elif d:
            what = f"agrees up to \"…{d[0]}\", where the brief has \"{d[1]} …\" and the source \"{d[2]} …\""
        else:
            what = f"\"{missing[:60]}\" is not in the source"
        fail(f, f"line {line}: not verbatim in {path}{' ' + where if where else ''} — {what}")
    return n


def header(text):
    """(id, fields, (start, end) character span of the block), or (None, {}, (0, 0))."""
    lines = text.split("\n")
    for i, l in enumerate(lines):
        m = re.match(r"^brief:\s*(\S+)\s*$", l)
        if not m:
            continue
        fields, key, end = {}, None, len(lines)
        for j in range(i + 1, len(lines)):
            l2 = lines[j]
            if not l2.strip() or not l2[0].isspace():
                end = j
                break
            fm = re.match(r"^\s{2,}([a-z][a-z ]*?):\s*(.*)$", l2)
            if fm and fm.group(1) in FIELDS:
                key = fm.group(1)
                fields[key] = fm.group(2).strip()
            elif key:
                fields[key] += " " + l2.strip()
        span = (sum(len(x) + 1 for x in lines[:i]), sum(len(x) + 1 for x in lines[:end]))
        return m.group(1), fields, span
    return None, {}, (0, 0)


def paths_in(v):
    """The paths a field names: its backticked tokens, or, when it has none, its words."""
    return TICKED.findall(v) or [t for t in re.split(r"[,\s]+", v) if t]


def check_brief(f, text, root):
    base = os.path.dirname(os.path.abspath(f))
    bid, fields, (h0, h1) = header(text)
    if bid is None:
        fail(f, "no \"brief: <id>\" block")
        return None, None
    for k in FIELDS:
        if not fields.get(k):
            fail(f, f"brief {bid}: no {k}: field")
    body_of, region = {}, {}
    for k in SECTION_FIELDS:
        v = fields.get(k, "")
        if not v:
            continue
        if k in MAY_BE_NONE and re.match(r"^none\s+—\s+\S", v):
            continue
        m = re.match(r"^§\s*(.+)$", v)
        if not m:
            fail(f, f"brief {bid}: {k}: is not \"§ <heading>\"" + (" or \"none — <reason>\"" if k in MAY_BE_NONE else ""))
            continue
        b, a, e = section_body(text, heading_name(m.group(1)))
        if b is None:
            fail(f, f"brief {bid}: {k}: names § {m.group(1).strip()}, which is not a heading here")
        elif not b.strip():
            fail(f, f"brief {bid}: {k}: § {m.group(1).strip()} is empty")
        else:
            body_of[k], region[k] = b, (a, e)
    if "statements" in body_of and not any(True for _ in quotations(body_of["statements"])):
        fail(f, f"brief {bid}: statements: the section holds no quotation — quote the statements, never paraphrase them")
    if SECOND_MIND.search(fields.get("role", "")) and fields.get("fences", "").startswith("none"):
        fail(f, f"brief {bid}: the role names a second mind and fences: is none")
    fb, fence_paths = body_of.get("fences"), []
    if fb is not None:
        fence_paths = [t for t in TICKED.findall(fb) if "*" in t or is_path(t, base, root)]
        if not fence_paths:
            fail(f, f"brief {bid}: fences: § names no path — a fence is a list of paths, never \"don't look\"")
        else:
            for name, rx in CHANNELS:
                if not rx.search(fb):
                    warn(f, f"brief {bid}: the fence does not mention {name}")
    for line, _, src, _, _ in quotations(text):
        if src and fence_paths and covered(SOURCE.match(src).group(1), fence_paths):
            fail(f, f"line {line}: quotes {SOURCE.match(src).group(1)}, which the fence closes — the recipient cannot "
                    f"read back what it was sent; put the statements in a file outside every fence")
    sr = fields.get("standing rules", "")
    if sr:
        words = [w.strip("`").rstrip(",;:.") for w in sr.split()]
        name = next((w for w in words if w and (is_path(w, base, root) or resolve(w, base, root))), words[0])
        p = resolve(name, base, root)
        if not p or os.path.isdir(p):
            fail(f, f"brief {bid}: standing rules: {name} does not exist")
        else:
            paras = re.split(r"\n\s*\n", open(p, encoding="utf-8", errors="replace").read())
            if not any(FORBIDS_SPAWN.search(x) and REASON.search(x) for x in paras):
                fail(f, f"brief {bid}: standing rules: no paragraph names spawning agents, forbids it, and gives a reason")
    rec = paths_in(fields.get("record", ""))
    if rec and not covered(rec[0], paths_in(fields.get("touches", ""))):
        fail(f, f"brief {bid}: record: {rec[0]} is not among touches:, so the recipient may not write its own record")
    new = [t for k in NEW_PATH_FIELDS for t in paths_in(fields.get(k, ""))]
    cut = [(h0, h1)] + [(a, b) for _, _, _, a, b in quotations(text)]
    if "fences" in region:
        cut.append(region["fences"])
    cut.sort()
    prose, pos = [], 0
    for a, b in cut:
        if a > pos:
            prose.append((pos, text[pos:a]))
        pos = max(pos, b)
    prose.append((pos, text[pos:]))
    missing = set()
    for _, chunk in prose:
        for p in TICKED.findall(chunk):
            if "*" in p or p in missing or covered(p, new) or not is_path(p, base, root):
                continue
            if not resolve(p, base, root):
                missing.add(p)
                fail(f, f"brief {bid}: names {p}, which does not exist — a brief's paths are claims too")
    if fb is not None:
        said = {}
        for at, chunk in prose:
            for m in VERDICT_WORDS.finditer(chunk):
                said.setdefault(text.count("\n", 0, at + m.start()) + 1, " ".join(m.group(0).split()))
        for ln, w in sorted(said.items()):
            warn(f, f"brief {bid}: line {ln}: a fenced brief says \"{w}\" — an outcome, in any words, hands the recipient "
                    f"the verdict")
    return bid, region.get("statements")


def statements_region(text):
    """The statements section's span, for a quotes-only run."""
    _, fields, _ = header(text)
    m = re.match(r"^§\s*(.+)$", fields.get("statements", ""))
    if not m:
        return None
    b, a, e = section_body(text, heading_name(m.group(1)))
    return (a, e) if b is not None else None


def main(argv):
    root = "."
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) < 2 or argv[0] not in ("quotes", "brief", "all"):
        print(__doc__.split("\n\n")[0])
        print("usage: brief_gate.py quotes|brief|all [--root DIR] BRIEF.md ...")
        return 2
    cmd, files = argv[0], argv[1:]
    nq, nb = 0, 0
    for f in files:
        if not os.path.isfile(f):
            fail(f, "no such file")
            continue
        text = open(f, encoding="utf-8", errors="replace").read()
        if cmd in ("brief", "all"):
            bid, region = check_brief(f, text, root)
            nb += bid is not None
        else:
            region = statements_region(text)
        if cmd in ("quotes", "all"):
            nq += check_quotes(f, text, root, region)
    for line in FAIL + WARN:
        print(line)
    tally = []
    if cmd in ("brief", "all"):
        tally.append(f"briefs: {nb}")
    if cmd in ("quotes", "all"):
        tally.append(f"quotations checked: {nq}")
    tally += [f"failures: {len(FAIL)}", f"warnings: {len(WARN)}"]
    print("  ".join(tally))
    print("GATE: " + ("FAIL" if FAIL else "PASS"))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
