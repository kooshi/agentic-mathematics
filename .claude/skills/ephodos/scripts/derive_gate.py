#!/usr/bin/env python3
"""derive_gate.py — the Ephodos gate: a text-level lint of derivation entries, a verbatim check of statements
quoted across files, and a re-run of every control with its planted fault.

Conventions checked (see SKILL.md <the_entry>; a gate-clean example is example-clean.md beside this file, and
example-dirty.md fails by design, one planted defect per block):

  derivation   a line "derivation: <name>" at column 0 (a leading "- " is allowed), <name> one token of letters,
               digits, dots, hyphens or underscores; then indented "field: value" lines, a value continuing on further
               indented lines; a blank line ends the block. Blocks sit outside code fences — a header inside a fence
               is warned about and not checked. The fields:
                 statement:    the claim, fixed before the argument
                 uses only:    the hypotheses the argument actually consumed — never the statement repeated
                 not claimed:  the nearest statement a reader will think was proved — never the statement repeated
                 converse:     where the second argument is written ("§ <heading>" or "<path> § <heading>");
                               required for a STRICT two-way statement (if and only if, if, and only if, iff, ⟺, ⇔, ↔,
                               exactly when / the / those, precisely when / the / those, just when, all and only,
                               necessary and sufficient, determine all); for a POSSIBLE one (the only, equivalent,
                               characterizes) "one-way — <reason>" is accepted; "owed" is accepted only when the
                               verdict is not derived
                 argument:     an address — "§ <heading>" in this file, "<path> § <heading>", or an existing path —
                               and never only "clearly", "obviously", "trivial", "standard", "it is easy to see"
                 verdict:      derived | stalls at: <step> | gap: <step> | refuted: <counterexample>
                 grade:        hand | derived from: <entries> | computed over: <set> | certified by: <checker> |
                               kernel: <declaration> | measured   (measured is a candidate: its verdict is never
                               derived; an entry derived from another governs no higher than it — a cited entry that
                               is not derived, or is measured, fails)
                 minds:        <n> — at 2 or more, "blind to: …" is required and "method: …" is expected
                 model:        an object satisfying every hypothesis (for a law, the target object and its regime number)
                 prior art:    new | known: <source> | partly: <source> | owed — "new" names at least two queries,
                               each written "<query>" (<hits>)
                 handoff:      the arbiter the result goes to and what crosses, or "none — <reason>"
               A derived entry needs every field; a stalled, gapped, or refuted one needs statement, argument, verdict.
  verification a line "verification: <name>", the record a second mind files in its own file. The fields:
                 statement:       the entry of that name, quoted verbatim (pass the entry's file too)
                 given:           what this mind saw before it committed its verdict — the statement only, or more
                 committed:       when the verdict was committed: a date (YYYY-MM-DD) or a commit id
                 predicted:       the verdict it expected and its probability, "<verdict> — <p>", registered before
                                  deriving; scored against the verdict, and the Brier score over every verification
                                  printed
                 verdict:         the entry vocabulary, derived by this mind
                 method:          how its route differed from the first derivation's, or that it could not know
                 attack:          an address — where the statement itself was attacked, not only its steps
                 divergences:     an address to a table with a "class" column (truth | route | wording) and a
                                  "resolution" column that says, on every truth row, which mind is wrong or that a third
                                  was sent for; or "none — <reason>" (warned: the disagreement has not started)
                 counterexamples: "none — <what was searched>", or items "<class>: <object> — <where it is local>"
                                  separated by ";" or ",", class refutation | monster | thin truth; a refuted verdict
                                  names a refutation or a monster, and a refutation is never beside a derived one
                 minds, grade:    as for an entry; "blind to: nothing" is one mind, and a given: that names the
                                  argument, proof, sketch, lemmas, or verdict is warned as a checking reading
               Across files: an entry is FAILED when a verification refutes it with a placed counterexample and it still
               says derived — and everything derived from it with it — and when it claims more minds than any
               verification of it counts; it is warned when a verification's verdict differs, or counts more minds.
               A line that opens a block in any other form — capitalized, bold, backticked, or with a note after the
               name — is FAILED as a block the gate cannot read, never skipped in silence.
  invention    a line "invention: <name>", the record of a made description (ephodos-invention): revises: (the
               premise, as the premises section lists it), licence: and premises: (addresses), model:, recovery:,
               consequence:, dissolved: (derived entries, or for model and dissolved an address; or "none — <reason>"),
               old premise planted: (a control, which must fire; or "none — <reason>"). The gate prints the grade the
               receipts carry — secured, or a conjecture naming the receipts it lacks — and cannot see whether a model is
               one or whether the planted fault is the old premise.
  control      a line "control: <name>" with indented of: (the entry, then " — " and the direction), run: (a
               command), expect: (its standard output; compared with runs of whitespace as one space, so a multi-line
               output is written on continuation lines), fault: (the same check with one fault planted — it must run
               cleanly, exit 0, and print something other than expect). Commands run through the shell with the
               document's own directory as working directory: running the gate on a document runs its code.

What the gate proves, and only this: the fields are present and on the ladder; a strict two-way statement carries a
converse with an address that resolves; no scope rider rides inside a statement; the argument is an address that
resolves; an entry derived from others cites derived, unmeasured entries; an entry named in several places carries
one statement, spacing aside; each control prints what its entry says, and its fault runs cleanly and prints
something else. What it prints as CLAIMS and cannot check: the mind count and its independence, what a second mind was given, the
novelty search, the planted fault itself. It scores each registered prediction against its verdict and cannot see
whether the prediction was written first. What it cannot see at all: whether the statement is the one meant, whether "not claimed" is
the nearest false generalization, whether an instance was filed where the class was carried, whether the fault is
the one worth planting.

Subcommands: entries | quotes | controls | all          (all = entries, quotes, then controls)
Exit status is non-zero when a check fails. Standard library only.
"""
import difflib
import os
import re
import subprocess
import sys

FAIL = 0
WARN = 0
WARNED = set()
REFUTED_BY_V = {}   # entry name -> the counterexample a verification placed against it
FIRED = {}          # control name -> True if it printed its expect and its fault printed something else


def say(msg):
    print(msg)


def fail(msg):
    global FAIL
    FAIL += 1
    say(f"  FAIL  {msg}")


def warn(msg):
    global WARN
    WARN += 1
    say(f"  warn  {msg}")


def warn_once(key, msg):
    if key not in WARNED:
        WARNED.add(key)
        warn(msg)


def claim(msg):
    say(f"  claim {msg}")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_fences(text):
    """Blank out fenced code; return (lines, fenced) where fenced holds (line_no, line) for every line inside a fence."""
    out, inside, fenced = [], False, []
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            inside = not inside
            out.append("")
            continue
        if inside:
            fenced.append((i, line))
            out.append("")
        else:
            out.append(line)
    return out, fenced


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().rstrip(".").lower()


def ws(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


# ---------------------------------------------------------------- parsing

HEAD = re.compile(r"^(?:[-*]\s+)?(derivation|control|verification|invention):\s*([\w.-]+)\s*$")
HEAD_LOOSE = re.compile(r"^\s*(?:[-*]\s+)?(derivation|control|verification|invention):\s*[\w.-]+\s*$")
FIELDS = {
    "derivation": ["statement", "uses only", "not claimed", "converse", "argument", "verdict", "grade", "minds",
                   "model", "prior art", "handoff"],
    "verification": ["statement", "given", "committed", "predicted", "verdict", "method", "attack", "divergences",
                     "counterexamples", "minds", "grade"],
    "control": ["of", "run", "expect", "fault"],
    "invention": ["revises", "licence", "premises", "model", "recovery", "consequence", "dissolved", "old premise planted"],
}
KV = re.compile(r"^\s+(?:[-*]\s+)?([A-Za-z][A-Za-z ]*?)\s*:\s?(.*?)\s*$")


def blocks(lines, path):
    """Yield dicts {kind, name, line, path, fields}; an indented line whose key is not a field of the block continues
    the previous field's value; a blank or unindented line ends the block."""
    i, n = 0, len(lines)
    while i < n:
        m = HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        kind, name = m.group(1), m.group(2)
        start, fields, last = i + 1, {}, None
        i += 1
        while i < n and lines[i].strip() and lines[i][0] in " \t":
            kv = KV.match(lines[i])
            key = kv.group(1).strip().lower() if kv else None
            if kv and key in FIELDS[kind]:
                fields[key] = kv.group(2)
                last = key
            elif last:
                fields[last] = (fields[last] + " " + lines[i].strip()).strip()
            i += 1
        yield {"kind": kind, "name": name, "line": start, "path": path, "fields": fields}


ANY_FIELD = {k for v in FIELDS.values() for k in v}
NEAR_HEAD = re.compile(r"^(?:[-*]\s+)?[*_`]*\s*(derivation|control|verification|invention)\s*[*_`]*\s*:", re.I)


def unread_heads(lines):
    """Unindented lines that open a block the gate cannot read: a header word in any case, bold or backticked, or with a
    trailing note, over an indented line whose key is a known field. Prose paragraphs have no such line under them."""
    out = []
    for i, ln in enumerate(lines[:-1]):
        if not ln or ln[0] in " \t" or HEAD.match(ln) or not NEAR_HEAD.match(ln):
            continue
        kv = KV.match(lines[i + 1])
        if kv and kv.group(1).strip().lower() in ANY_FIELD:
            out.append((i + 1, ln.strip()))
    return out


def load(paths):
    docs = []
    for p in paths:
        text = read(p)
        lines, fenced = strip_fences(text)
        docs.append({"path": p, "text": text, "lines": lines, "fenced": fenced, "blocks": list(blocks(lines, p)),
                     "unread": unread_heads(lines)})
    return docs


# ---------------------------------------------------------------- the vocabulary

STRICT = re.compile(
    r"\bif,?\s+and\s+only\s+if\b|\biff\b|⟺|⇔|↔|\b(?:exactly|precisely)\s+(?:when|the|those)\b|\ball and only\b"
    r"|\bjust when\b|\bnecessary and sufficient\b|\bdetermine all\b", re.I)
POSSIBLE = re.compile(r"\bthe only\b|\bequivalent\b|\bcharacteri[sz]", re.I)
RIDER = re.compile(r"\bmore generally\b|\bthe same (?:holds|is true)\b|\bsimilarly\b|\blikewise\b", re.I)
BARE = re.compile(r"^(?:clearly|obvious(?:ly)?|trivial(?:ly)?|it is (?:easy|straightforward|routine) to "
                  r"(?:see|show|check|verify)|immediate(?:ly)?|standard|well[- ]known|left to the reader|by inspection"
                  r"|omitted|n/?a|none|tbd|todo|-|—)\b", re.I)
EMPTY_WORDS = {"", "none", "n/a", "na", "-", "—", "tbd", "todo", "owed", "not claimed", "vacuous"}
VERDICT = re.compile(r"^(derived|stalls at:\s*\S.*|gap:\s*\S.*|refuted:\s*\S.*)$", re.I)
GRADE = re.compile(r"^(hand|measured|derived from|computed over|certified by|kernel)\b\s*:?\s*(.*)$", re.I)
MINDS = re.compile(r"^(\d+)\b\s*(.*)$")
PRIOR = re.compile(r"^(new|known|partly|owed)\b\s*[:—–-]?\s*(.*)$", re.I)
QUERY = re.compile(r"[\"“]([^\"”]{2,})[\"”]\s*\(\s*(\d[\d,]*)\s*(?:hits?)?\s*\)")
SECTION = re.compile(r"§\s*(.+?)\s*$")
PREDICTED = re.compile(r"^(derived|stalls at|gap|refuted)\b(.*)$", re.I)
PROB = re.compile(r"(\d{1,3}(?:\.\d+)?\s*%|0?\.\d+|1(?:\.0+)?|0)")
CX_CLASSES = ("refutation", "monster", "thin truth")
CX_SPLIT = re.compile(r"\s*[;,]\s*(?=(?:refutation|monster|thin truth)\s*:)", re.I)
CX_ITEM = re.compile(r"^(refutation|monster|thin truth)\s*:\s*(\S.*?)\s+[—–]\s+(\S.*)$", re.I)
DIV_CLASSES = ("truth", "route", "wording")
DENIED = re.compile(r"^(?:unresolved|open|pending|undecided|unknown|tbd|todo|\?+)(?:\W|$)|^\?", re.I)
DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b[0-9a-f]{7,40}\b")
CHECKING = re.compile(r"\b(sketch|verdict|argument|proof|lemma(?:s| statements)?)\b", re.I)
NEGATED = re.compile(r"\b(?:not|no|nothing of|without|never|neither|nor)\b[^.;]{0,40}$", re.I)
PATHLIKE = re.compile(r"(?<![\w/])((?:[\w.-]+/)*[\w-][\w.-]*\.[A-Za-z][A-Za-z0-9]{0,5})(?![\w/])")


def headings(lines):
    return [re.sub(r"^#+\s*", "", ln).strip().lower() for ln in lines if re.match(r"^#{1,6}\s", ln)]


def heading_matches(want, heads):
    """Exactly, or as a prefix followed by a character that is not a letter or digit ('Lemma 1' is not 'Lemma 12')."""
    for h in heads:
        if h == want or (h.startswith(want) and not h[len(want)].isalnum()):
            return True
    return False


def resolve(value, doc, label, what="argument"):
    """Resolve an address. Returns True if it resolves, False if it fails, None if the value carries no address."""
    base = os.path.dirname(os.path.abspath(doc["path"]))
    m = SECTION.search(value)
    before = value[: m.start()] if m else value
    target_lines, where = doc["lines"], "this file"
    for cand in PATHLIKE.findall(before):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            if m:
                target_lines, where = strip_fences(read(p))[0], cand
            break
        if "/" in cand or re.search(r"\.(?:md|txt|tex|pdf|lean|py|r|jl|sage|g|m2|m|nb|ipynb|gp|c|cpp|h|rs|hs|v|thy|sh"
                                    r"|csv|json|ml|mag|gap)$", cand, re.I):
            fail(f"{label}: {what} names `{cand}`, which does not exist")
            return False
    else:
        if not m:
            return None
    if m:
        want = m.group(1).strip().strip('"“”').lower()
        if not heading_matches(want, headings(target_lines)):
            fail(f"{label}: {what} names § {m.group(1)!r}, and {where} has no such heading — a conclusion with no chain")
            return False
    return True


def section(value, doc):
    """The lines under the heading an address names (in this file or the named one), up to the next heading."""
    base = os.path.dirname(os.path.abspath(doc["path"]))
    m = SECTION.search(value)
    if not m:
        return []
    lines = doc["lines"]
    for cand in PATHLIKE.findall(value[: m.start()]):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            lines = strip_fences(read(p))[0]
            break
    want, out, level = m.group(1).strip().strip('"“”').lower(), [], 0
    for ln in lines:
        h = re.match(r"^(#{1,6})\s", ln)
        if h and level and len(h.group(1)) <= level:
            break
        if h and not level:
            if heading_matches(want, [re.sub(r"^#+\s*", "", ln).strip().lower()]):
                level = len(h.group(1))
            continue
        if level:
            out.append(ln)
    return out


def table(lines):
    """The first pipe table in these lines, as a header and rows of cells."""
    rows = [[re.sub(r"[*_`]", "", c).replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]
            for ln in lines if ln.strip().startswith("|")]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
    return (rows[0], rows[1:]) if rows else ([], [])


def ladder(block):
    """(verdict_ok, grade_rung) for a cited entry."""
    f = block["fields"]
    g = GRADE.match(f.get("grade", "").strip())
    ok = f.get("verdict", "").strip().lower() == "derived" and block["name"] not in REFUTED_BY_V
    return ok, (g.group(1).lower() if g else "")


# ---------------------------------------------------------------- checks

def check_fenced_headers(docs):
    for d in docs:
        for ln, line in d["fenced"]:
            if HEAD_LOOSE.match(line):
                warn(f"{os.path.basename(d['path'])}:{ln}: {line.strip()!r} sits inside a code fence and is not checked — "
                     f"write entries and controls unfenced")
        for ln, line in d["unread"]:
            if ("unread", d["path"], ln) not in WARNED:
                WARNED.add(("unread", d["path"], ln))
                fail(f"{os.path.basename(d['path'])}:{ln}: {line!r} opens a block the gate cannot read — write "
                     f"'derivation:', 'control:', 'verification:' or 'invention:' in lower case at column 0, then one token of a name")


def check_entries(docs):
    say("entry lint")
    check_fenced_headers(docs)
    entries = [b for d in docs for b in d["blocks"] if b["kind"] == "derivation"]
    for b in (b for d in docs for b in d["blocks"] if b["kind"] == "verification"):
        if re.match(r"^refuted\b", b["fields"].get("verdict", "").strip(), re.I):
            items, _ = cx_items(b["fields"].get("counterexamples", ""))
            placed = [obj for cls, obj, _where in items if cls == "refutation"]
            if placed:
                REFUTED_BY_V.setdefault(b["name"], placed[0])
    if not entries and not any(b["kind"] == "verification" for d in docs for b in d["blocks"]):
        if not any(d["unread"] for d in docs):
            fail("no derivation entry — a result that lives only in prose has not been stated")
        return
    by_name = {}
    for b in entries:
        by_name.setdefault(b["name"], b)
    counts = {"derived": 0, "stalled": 0}
    for b in entries:
        doc = next(d for d in docs if d["path"] == b["path"])
        f, label = b["fields"], f"{os.path.basename(b['path'])}:{b['line']} ({b['name']})"
        st = f.get("statement", "")
        if not st.strip():
            fail(f"{label}: no statement — fix it before the argument")
        verdict = f.get("verdict", "").strip()
        if not VERDICT.match(verdict):
            fail(f"{label}: verdict {verdict!r} is not derived | stalls at: <step> | gap: <step> | refuted: <counterexample>")
        derived = verdict.lower() == "derived"
        counts["derived" if derived else "stalled"] += 1
        arg = f.get("argument", "").strip()
        if not arg:
            fail(f"{label}: no argument — a conclusion with no chain")
        else:
            r = resolve(arg, doc, label)
            if r is None:
                if BARE.match(arg):
                    fail(f"{label}: argument {arg!r} is a bare conclusion, not an address")
                else:
                    warn(f"{label}: argument {arg!r} carries no address (a § heading or a path)")
        if st and RIDER.search(st):
            fail(f"{label}: statement carries a scope rider ({RIDER.search(st).group(0)!r}) — a second claim; give it its own entry")
        strict, possible = STRICT.search(st or ""), POSSIBLE.search(st or "")
        if strict or possible:
            word = (strict or possible).group(0)
            conv = f.get("converse", "").strip()
            one_way = re.match(r"^one-way\s*[—–:-]\s*\S", conv, re.I)
            owed = norm(conv) in EMPTY_WORDS or re.match(r"^(owed|not claimed|none)\b", conv, re.I)
            if conv and not owed and not one_way:
                if resolve(conv, doc, label, "converse") is None:
                    warn(f"{label}: converse {conv!r} carries no address")
            elif one_way and strict:
                fail(f"{label}: converse declared one-way, but the statement says {word!r} — rewrite the statement one way")
            elif one_way:
                pass
            elif not derived:
                pass  # a stalled or refuted two-way conjecture may owe its converse; the verdict says nothing is carried
            elif strict:
                fail(f"{label}: the statement is two-way ({word!r}) and converse is {conv or 'absent'!r} — the sentence "
                     f"conveys a converse the entry does not carry; derive it or state one way")
            else:
                warn(f"{label}: {word!r} may be two-way — give the converse an address, or write converse: one-way — <reason>")
        if not derived:
            continue
        for key in ("uses only", "not claimed", "grade", "minds", "model", "prior art", "handoff"):
            if key not in f or not f[key].strip():
                fail(f"{label}: no {key}: — a derived entry carries every field")
        uo, nc = f.get("uses only", ""), f.get("not claimed", "")
        if uo and norm(uo) == norm(st):
            fail(f"{label}: uses only: repeats the statement — read it off the argument")
        if nc and norm(nc) == norm(st):
            fail(f"{label}: not claimed: repeats the statement — name the nearest thing a reader will think was proved")
        model = f.get("model", "")
        if "model" in f and norm(model) in EMPTY_WORDS:
            fail(f"{label}: model {model!r} — a statement no object satisfies carries nothing")
        grade = f.get("grade", "").strip()
        g = GRADE.match(grade)
        if grade and not g:
            fail(f"{label}: grade {grade!r} is not on the ladder (hand | derived from | computed over | certified by | kernel | measured)")
        elif g:
            rung, rest = g.group(1).lower(), g.group(2).strip()
            if rung == "measured":
                fail(f"{label}: grade measured with verdict derived — a measurement is a candidate; only a derivation concludes")
            elif rung == "derived from":
                cited = [c.strip(" `") for c in re.split(r"[,;]|\s+and\s+", rest) if c.strip(" `")]
                if not cited:
                    fail(f"{label}: derived from names no entry")
                for c in cited:
                    if c not in by_name:
                        warn(f"{label}: derived from {c!r}, which is not an entry in these files — its grade cannot be read")
                        continue
                    ok, crung = ladder(by_name[c])
                    if c in REFUTED_BY_V:
                        fail(f"{label}: derived from {c!r}, which a verification refutes ({REFUTED_BY_V[c]}) — the weakest "
                             f"input governs, and it carries nothing now")
                    elif not ok:
                        fail(f"{label}: derived from {c!r}, whose verdict is {by_name[c]['fields'].get('verdict', '')!r} — "
                             f"the weakest input governs, and it carries nothing yet")
                    elif crung == "measured":
                        fail(f"{label}: derived from {c!r}, graded measured — a candidate cannot carry a derivation")
                    else:
                        cm = (by_name[c]["fields"].get("minds") or "?").split()[0]
                        claim(f"{b['name']}: governed by {c} ({crung}, minds {cm})")
            elif rung == "computed over" and not re.search(r"\d|[≤<{∈]", rest):
                warn(f"{label}: computed over {rest!r} states no set — a computed statement quantifies over exactly the set computed")
            elif rung in ("certified by", "kernel") and not rest:
                fail(f"{label}: grade {rung} names nothing")
        minds = f.get("minds", "").strip()
        if minds:
            check_minds(label, b["name"], minds)
        prior = f.get("prior art", "").strip()
        pm = PRIOR.match(prior)
        if prior and not pm:
            fail(f"{label}: prior art {prior!r} is not new | known: <source> | partly: <source> | owed")
        elif pm:
            verdict_p, rest = pm.group(1).lower(), pm.group(2)
            queries = QUERY.findall(prior)
            if verdict_p == "new" and len({q[0].lower() for q in queries}) < 2:
                fail(f"{label}: prior art new with {len(queries)} counted quer{'y' if len(queries) == 1 else 'ies'} — "
                     f"'new' is a claim about a search: name two, each \"query\" (hits)")
            elif verdict_p in ("known", "partly") and not rest.strip():
                fail(f"{label}: prior art {verdict_p} names no source")
            elif verdict_p == "owed":
                warn(f"{label}: prior art owed — novelty unmeasured; a standing finding")
            claim(f"{b['name']}: prior art {verdict_p}" + (f", {len(queries)} counted queries" if queries else ""))
        ho = f.get("handoff", "").strip()
        if ho and re.match(r"^none\b", ho, re.I) and not re.search(r"none\s*[—–:-]\s*\S", ho, re.I):
            fail(f"{label}: handoff none with no reason")
    seen = set()
    for b in entries:
        key = (b["path"], b["name"])
        if key in seen:
            fail(f"{os.path.basename(b['path'])}:{b['line']} ({b['name']}): a second entry with this name in the same file")
        seen.add(key)
    say(f"  entries: {len(entries)}  derived: {counts['derived']}  stalled, gapped or refuted: {counts['stalled']}")
    check_verifications(docs)


def check_minds(label, name, minds, given=None, prefix=""):
    """Lint a minds: line. Returns (count, trusted): trusted is False when the line cannot carry the count it claims."""
    mm = MINDS.match(minds)
    if not mm:
        fail(f"{label}: minds {minds!r} is not a count — say how many minds, and on what terms")
        return None, False
    n, rest, trusted = int(mm.group(1)), mm.group(2), True
    blind = re.search(r"blind to\s*:\s*([^;]*)", rest, re.I)
    if n >= 2 and not blind:
        fail(f"{label}: minds {n} with no 'blind to:' — a second mind is a claim about what it saw")
        trusted = False
    elif n >= 2 and norm(blind.group(1)) in EMPTY_WORDS | {"nothing", "nothing at all"}:
        fail(f"{label}: minds {n}, blind to {blind.group(1).strip()!r} — a mind that saw everything is a checking reading, one mind")
        trusted = False
    elif n >= 2 and not re.search(r"method\s*:", rest, re.I):
        warn(f"{label}: minds {n} says nothing of method — copies of one mind share a prior")
    if n >= 2 and given and trusted:
        seen = [m.group(1) for m in CHECKING.finditer(given) if not NEGATED.search(given[: m.start()])]
        if seen:
            warn(f"{label}: minds {n}, and given: names the {', '.join(dict.fromkeys(x.lower() for x in seen))} — "
                 f"a checking reading counts one")
            trusted = False
    claim(f"{prefix}{name}: minds {minds}")
    return n, trusted


def check_grade(label, name, grade, derived, by_name):
    g = GRADE.match(grade)
    if not g:
        fail(f"{label}: grade {grade!r} is not on the ladder (hand | derived from | computed over | certified by | kernel | measured)")
        return
    rung, rest = g.group(1).lower(), g.group(2).strip()
    if rung == "measured" and derived:
        fail(f"{label}: grade measured with verdict derived — a measurement is a candidate; only a derivation concludes")
    elif rung in ("certified by", "kernel") and not rest:
        fail(f"{label}: grade {rung} names nothing")
    elif rung == "derived from":
        cited = [c.strip(" `") for c in re.split(r"[,;]|\s+and\s+", rest) if c.strip(" `")]
        if not cited:
            fail(f"{label}: derived from names no entry")
        for c in cited:
            if c not in by_name:
                warn(f"{label}: derived from {c!r}, which is not an entry in these files — its grade cannot be read")
            elif not ladder(by_name[c])[0]:
                fail(f"{label}: derived from {c!r}, which carries nothing yet — the weakest input governs")


def cx_items(value):
    """Counterexample items as (class, object, where it is local), and the unparsed items."""
    items, bad = [], []
    if not value.strip() or re.match(r"^none\b", value.strip(), re.I):
        return items, bad
    for item in CX_SPLIT.split(value.strip()):
        im = CX_ITEM.match(item.strip())
        if im:
            items.append((im.group(1).lower(), im.group(2).strip(), im.group(3).strip()))
        else:
            bad.append(item.strip())
    return items, bad


def check_verifications(docs):
    blocks_v = [b for d in docs for b in d["blocks"] if b["kind"] == "verification"]
    if not blocks_v:
        return
    say("verification lint")
    entries = {b["name"]: b for d in docs for b in d["blocks"] if b["kind"] == "derivation"}
    scored, met, brier = 0, 0, 0.0
    div = dict.fromkeys(DIV_CLASSES, 0)
    cx = dict.fromkeys(CX_CLASSES, 0)
    counts = {}   # entry name -> [(minds, trusted)]
    for b in blocks_v:
        doc = next(d for d in docs if d["path"] == b["path"])
        f, name = b["fields"], b["name"]
        label = f"{os.path.basename(b['path'])}:{b['line']} (verification {name})"
        if not f.get("statement", "").strip():
            fail(f"{label}: no statement — a verifier quotes the statement it derived")
        if name not in entries:
            warn_once(("entry", name), f"verification {name!r} quotes an entry not in these files — its statement was not "
                                       f"compared; pass the entry's file too")
        v = f.get("verdict", "").strip()
        if not VERDICT.match(v):
            fail(f"{label}: verdict {v!r} is not derived | stalls at: <step> | gap: <step> | refuted: <counterexample>")
        kind = re.match(r"^(derived|stalls at|gap|refuted)", v, re.I)
        kind = kind.group(1).lower() if kind else ""
        given = f.get("given", "").strip()
        if norm(given) in EMPTY_WORDS | {"nothing"}:
            fail(f"{label}: no given: — a second mind is a claim about what it was given before it committed, the statement at least")
        else:
            short = given if len(given) <= 90 else given[:90].rsplit(" ", 1)[0] + " …"
            claim(f"verification {name}: given: {short}")
        when = f.get("committed", "").strip()
        if not DATED.search(when):
            fail(f"{label}: committed {when!r} carries no date or commit — when the verdict was committed is the record "
                 f"of what could not yet have been seen")
        else:
            claim(f"verification {name}: committed {when}")
        pred = f.get("predicted", "").strip()
        pm, pp = PREDICTED.match(pred), None
        if pm:
            head = re.split(r";|\b(?:derived|stalls at|gap|refuted)\b", pm.group(2), maxsplit=1)[0]
            for seg in re.split(r"\s+[—–-]\s+|\s*[—–]\s*", head):
                seg = seg.strip().rstrip(".,;:")
                if PROB.fullmatch(seg):
                    t = seg.replace(" ", "")
                    pp = float(t[:-1]) / 100 if t.endswith("%") else float(t)
                    break
        if not pred:
            fail(f"{label}: no predicted: — register the verdict you expect and its probability before deriving")
        elif not pm or pp is None or not 0 <= pp <= 1:
            fail(f"{label}: predicted {pred!r} is not \"<verdict> — <probability>\" with the verdict from the entry vocabulary")
        elif kind:
            hit = pm.group(1).lower() == kind
            scored, met, brier = scored + 1, met + hit, brier + (pp - hit) ** 2
            claim(f"verification {name}: predicted {pm.group(1).lower()} ({pp:g}); verdict {kind} — {'met' if hit else 'missed'}")
        if not f.get("method", "").strip():
            fail(f"{label}: no method: — say how this route differed from the first, or that it could not know")
        att = f.get("attack", "").strip()
        if not att:
            fail(f"{label}: no attack: — a verification that attacks no statement has checked only steps")
        elif resolve(att, doc, label, "attack") is None:
            fail(f"{label}: attack {att!r} is not an address — point to where the statement was attacked")
        dv = f.get("divergences", "").strip()
        if not dv:
            fail(f"{label}: no divergences: — the comparison with the first derivation, or none — <reason>")
        elif re.match(r"^none\b", dv, re.I):
            if not re.match(r"^none\s*[—–:-]\s*\S", dv, re.I):
                fail(f"{label}: divergences none with no reason")
            else:
                warn(f"{label}: divergences {dv!r} — until the comparison finds something, the disagreement has not started")
        else:
            r = resolve(dv, doc, label, "divergences")
            if r is None:
                fail(f"{label}: divergences {dv!r} is not an address or none — <reason>")
            elif r:
                head, rows = table(section(dv, doc))
                cols = [h.lower() for h in head]
                if "class" not in cols:
                    fail(f"{label}: divergences at {dv!r} holds no table with a class column (truth | route | wording)")
                elif not rows:
                    warn(f"{label}: the divergence table at {dv!r} has no rows — until the comparison finds something, "
                         f"the disagreement has not started")
                else:
                    ci, ri = cols.index("class"), (cols.index("resolution") if "resolution" in cols else None)
                    for row in rows:
                        c = row[ci].lower() if ci < len(row) else ""
                        item = next((x for x in row if x and not x.isdigit()), row[0])
                        if c not in DIV_CLASSES:
                            fail(f"{label}: divergence {item!r} is classed {c!r}, not truth | route | wording")
                            continue
                        div[c] += 1
                        res = row[ri] if ri is not None and ri < len(row) else ""
                        if c == "truth" and (norm(res) in EMPTY_WORDS or DENIED.match(res.strip())):
                            fail(f"{label}: divergence {item!r} is of truth and its resolution is {res!r} — one of the two is "
                                 f"wrong: say which, or send it to a third independent mind and say so")
                        elif c == "truth" and re.search(r"\bthird\b", res, re.I):
                            warn(f"{label}: divergence {item!r} is of truth and waits on a third mind — the entry stands "
                                 f"below its claim until it returns")
        cxv = f.get("counterexamples", "").strip()
        items, bad = cx_items(cxv)
        if not cxv:
            fail(f"{label}: no counterexamples: — name what was found, or none — <what was searched>")
        elif re.match(r"^none\b", cxv, re.I):
            if not re.match(r"^none\s*[—–:-]\s*\S", cxv, re.I):
                fail(f"{label}: counterexamples none with no search named")
            elif kind == "refuted":
                fail(f"{label}: verdict refuted with counterexamples none")
            else:
                claim(f"verification {name}: counterexamples {cxv}")
        else:
            for item in bad:
                fail(f"{label}: counterexample {item[:60]!r} is not \"<refutation | monster | thin truth>: <object> — "
                     f"<where it is local>\" — a counterexample with no place in the argument cannot be answered")
            for cls, obj, where in items:
                cx[cls] += 1
                claim(f"verification {name}: {cls}: {obj} — {where}")
            classes = {c for c, _, _ in items}
            if bad:
                pass
            elif kind == "refuted" and not {"refutation", "monster"} & classes:
                fail(f"{label}: verdict refuted with no refutation or monster located")
            elif "refutation" in classes and kind and kind != "refuted":
                fail(f"{label}: a refutation of the statement as meant, beside the verdict {kind!r}")
        minds = f.get("minds", "").strip()
        if not minds:
            fail(f"{label}: no minds: — say how many minds the statement now has, and on what terms")
        else:
            n, trusted = check_minds(label, name, minds, given, prefix="verification ")
            if n is not None:
                counts.setdefault(name, []).append((n, trusted))
        g = f.get("grade", "").strip()
        if not g:
            fail(f"{label}: no grade: — the rung this mind's derivation stands on")
        else:
            check_grade(label, name, g, kind == "derived", entries)
    for name in sorted(set(counts) & set(entries)):
        e = entries[name]["fields"]
        ek = (re.match(r"^(derived|stalls at|gap|refuted)", e.get("verdict", "").strip(), re.I) or [None, ""])[1].lower()
        vk = {(re.match(r"^(derived|stalls at|gap|refuted)", b["fields"].get("verdict", "").strip(), re.I) or [None, ""])[1].lower()
              for b in blocks_v if b["name"] == name} - {""}
        if ek == "derived" and name in REFUTED_BY_V:
            fail(f"{name}: the entry says derived and a verification refutes it ({REFUTED_BY_V[name]}) — demote the entry to "
                 f"refuted, and everything derived from it with it")
        elif ek and vk - {ek}:
            warn(f"{name}: the entry says {ek} and a verification says {', '.join(sorted(vk - {ek}))} — a divergence of truth: "
                 f"demote the entry, or let a third independent mind decide")
        em = MINDS.match(e.get("minds", "").strip())
        if not em:
            continue
        ne = int(em.group(1))
        top = max(n for n, _ in counts[name])
        top_trusted = max((n for n, t in counts[name] if t), default=1)
        if ne > top:
            fail(f"{name}: the entry says {ne} minds and the verifications of it here count at most {top} — the conveyed "
                 f"exceeds the carried; lower the entry, or pass the verification that counts {ne}")
        elif top_trusted > ne:
            warn(f"{name}: a verification counts {top_trusted} minds and the entry says {ne} — carry the count to the entry's minds: line")
    line = f"  verifications: {len(blocks_v)}"
    if scored:
        line += f"  predictions met: {met} of {scored} (Brier {brier / scored:.3f})"
    line += "  divergences: " + ", ".join(f"{k} {div[k]}" for k in DIV_CLASSES)
    line += "  counterexamples: " + ", ".join(f"{k} {cx[k]}" for k in CX_CLASSES)
    say(line)


def check_quotes(docs):
    say("quotes")
    stated = {}
    for d in docs:
        for b in d["blocks"]:
            if b["kind"] in ("derivation", "verification") and b["fields"].get("statement", "").strip():
                stated.setdefault(b["name"], []).append((b, b["fields"]["statement"]))
    compared = 0
    for name, items in stated.items():
        if len(items) < 2:
            continue
        compared += 1
        first = items[0]
        for other in items[1:]:
            a, bb = ws(first[1]), ws(other[1])
            if a != bb:
                where = lambda x: f"{os.path.basename(x['path'])}:{x['line']}"
                k = next((i for i in range(min(len(a), len(bb))) if a[i] != bb[i]), min(len(a), len(bb)))
                fail(f"{name}: statement at {where(other[0])} differs from {where(first[0])} at character {k}: "
                     f"{a[max(0, k - 20):k + 30]!r} against {bb[max(0, k - 20):k + 30]!r}")
    names = {x["name"] for d in docs for x in d["blocks"] if x["kind"] == "derivation"}
    for b in (b for d in docs for b in d["blocks"] if b["kind"] == "verification"):
        if b["name"] not in names:
            warn_once(("entry", b["name"]), f"verification {b['name']!r} quotes an entry not in these files — its statement "
                                            f"was not compared; pass the entry's file too")
    say(f"  statements named in more than one place: {compared}")


def run(cmd, cwd):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, timeout=120)
        dec = lambda b: b.decode("utf-8", errors="replace").strip()
        return p.returncode, dec(p.stdout), dec(p.stderr)
    except subprocess.TimeoutExpired:
        return None, "", "timed out after 120 s"


def planted(run_cmd, fault_cmd):
    """The span where the fault differs from the run, and their similarity."""
    tok = lambda c: re.findall(r"\d+(?:\.\d+)?|\w+|\s+|\S", c)
    a, b = tok(run_cmd), tok(fault_cmd)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    spans = [("".join(a[i1:i2]).strip(), "".join(b[j1:j2]).strip())
             for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    shown = "; ".join(f"{a!r} → {b!r}" for a, b in spans[:3]) + (" …" if len(spans) > 3 else "")
    return shown or "(identical commands)", sm.ratio()


def check_controls(docs):
    say("controls")
    entries = {b["name"]: b for d in docs for b in d["blocks"] if b["kind"] == "derivation"}
    controls = [b for d in docs for b in d["blocks"] if b["kind"] == "control"]
    of_by_entry = {}
    fired = 0
    for c in controls:
        f, label = c["fields"], f"{os.path.basename(c['path'])}:{c['line']} ({c['name']})"
        of = f.get("of", "").strip()
        target = re.split(r"\s*[—–]\s*|\s+", of, maxsplit=1)[0] if of else ""
        if not of:
            fail(f"{label}: no of: — a control names the entry and the direction it checks")
        elif target not in entries:
            warn(f"{label}: of {target!r}, which is not an entry in these files")
        of_by_entry.setdefault(target, []).append(of)
        missing = [k for k in ("run", "expect", "fault") if not f.get(k, "").strip()]
        if missing:
            fail(f"{label}: no {', '.join(missing)} — a control that cannot be re-run, or cannot fire, is a self-test")
            continue
        cwd = os.path.dirname(os.path.abspath(c["path"]))
        expect = ws(f["expect"])
        code, out, err = run(f["run"], cwd)
        if code != 0 or ws(out) != expect:
            last = err.strip().splitlines()[-1] if err.strip() else ""
            detail = f"exit {code}" + (f", stderr {last[-120:]!r}" if last else "")
            fail(f"{label}: run printed {ws(out)[:80]!r} ({detail}) where the entry says {expect!r}")
            continue
        fcode, fout, ferr = run(f["fault"], cwd)
        shown, ratio = planted(f["run"], f["fault"])
        if fcode != 0:
            why = "timed out" if fcode is None else f"exited {fcode}"
            last = ferr.strip().splitlines()[-1] if ferr.strip() else ""
            fail(f"{label}: the fault run {why}" + (f" ({last[-100:]!r})" if last else "") +
                 " — a fault that does not run has not tested the control")
            continue
        if ws(fout) == expect:
            fail(f"{label}: the fault run also printed {expect!r} — the control cannot fire, so its pass says nothing")
            continue
        fired += 1
        FIRED[c["name"]] = True
        say(f"  ok    {c['name']}: printed {ws(out)!r}; with the fault planted ({shown}) it printed {ws(fout)[:40]!r} — it fires")
        if ratio < 0.5:
            warn(f"{label}: the fault shares {ratio:.0%} of the run's text — is it the same check with one fault planted?")
    for name, b in entries.items():
        st = b["fields"].get("statement", "")
        ofs = of_by_entry.get(name, [])
        if ofs and STRICT.search(st) and not any(re.search(r"converse|backward|reverse|⇐|second direction", o, re.I) for o in ofs):
            warn(f"{name}: two-way statement with controls on one direction only — a control that reads one direction passes a fault on the other")
    say(f"  controls: {len(controls)}  fired on their faults: {fired}")


def check_inventions(docs, ran_controls):
    blocks_i = [b for d in docs for b in d["blocks"] if b["kind"] == "invention"]
    if not blocks_i:
        return
    say("invention lint")
    entries = {b["name"]: b for d in docs for b in d["blocks"] if b["kind"] == "derivation"}
    controls = {b["name"]: b for d in docs for b in d["blocks"] if b["kind"] == "control"}
    secured = conjectures = 0
    none_ok = lambda v: re.match(r"^none\s*[—–:-]\s*\S", v, re.I)
    for b in blocks_i:
        doc = next(d for d in docs if d["path"] == b["path"])
        f, name = b["fields"], b["name"]
        label = f"{os.path.basename(b['path'])}:{b['line']} (invention {name})"
        failed_before = FAIL
        for key in FIELDS["invention"]:
            if not f.get(key, "").strip():
                fail(f"{label}: no {key}: — a made description names every receipt, or says none — <reason>")
        rev = f.get("revises", "").strip()
        ok = {}
        for key in ("licence", "premises"):
            v = f.get(key, "").strip()
            ok[key] = resolve(v, doc, label, key) if v else False
            if v and ok[key] is None:
                fail(f"{label}: {key} {v!r} is not an address — point to where it is written")
        prem = f.get("premises", "").strip()
        if rev and prem and ok["premises"]:
            listed = norm(" ".join(section(prem, doc)))
            if norm(rev) not in listed:
                fail(f"{label}: revises {rev!r}, which the premises at {prem!r} do not list — revise a premise that was sorted")
        missing, unread = [], []
        for key in ("model", "recovery", "consequence", "dissolved"):
            v = f.get(key, "").strip()
            if not v:
                unread.append(key)
            elif none_ok(v):
                missing.append(key)
            elif re.match(r"^none\b", v, re.I):
                fail(f"{label}: {key} none with no reason")
                unread.append(key)
            elif key in ("model", "dissolved") and SECTION.search(v):
                if not resolve(v, doc, label, key):
                    unread.append(key)
            else:
                names = [x.strip(" `") for x in re.split(r"[,;]|\s+and\s+", v) if x.strip(" `")]
                bad = [x for x in names if x not in entries or not ladder(entries[x])[0]]
                if bad:
                    fail(f"{label}: {key} names {', '.join(repr(x) for x in bad)}, not a derived entry in these files — a "
                         f"receipt is an entry that carries it")
                    unread.append(key)
        planted = f.get("old premise planted", "").strip()
        if planted and not none_ok(planted):
            c = controls.get(planted.strip(" `"))
            if not c:
                fail(f"{label}: old premise planted names {planted!r}, which is not a control in these files")
            elif ran_controls and not FIRED.get(c["name"]):
                fail(f"{label}: old premise planted names {c['name']!r}, which did not fire on its fault — the old premise "
                     f"planted back changed nothing it printed")
        elif planted:
            claim(f"invention {name}: old premise planted: {planted}")
        if unread or FAIL > failed_before:
            claim(f"invention {name}: not graded — the record fails" + (f"; {', '.join(unread)} unread" if unread else ""))
        elif missing:
            conjectures += 1
            warn(f"invention {name}: revises {rev!r} — a conjecture: no {', '.join(missing)}. Grade it as one, and say so in the headline")
        else:
            secured += 1
            claim(f"invention {name}: revises {rev!r} — secured (model, recovery, consequence, dissolved)")
    say(f"  inventions: {len(blocks_i)}  secured: {secured}  conjectures: {conjectures}  not graded: "
        f"{len(blocks_i) - secured - conjectures}")


def main(argv):
    if len(argv) < 3 or argv[1] not in ("entries", "quotes", "controls", "all"):
        print(__doc__.split("\n\n")[0])
        print("usage: derive_gate.py entries|quotes|controls|all FILE.md [FILE.md …]")
        return 2
    cmd, paths = argv[1], argv[2:]
    for p in paths:
        if not os.path.exists(p):
            print(f"no such file: {p}")
            return 2
    docs = load(paths)
    if cmd in ("entries", "all"):
        check_entries(docs)
    else:
        check_fenced_headers(docs)
    if cmd in ("quotes", "all"):
        check_quotes(docs)
    if cmd in ("controls", "all"):
        check_controls(docs)
    if cmd in ("entries", "all"):
        check_inventions(docs, ran_controls=(cmd == "all"))
    verdict = "PASS" if FAIL == 0 else "FAIL"
    print(f"GATE: {verdict} ({FAIL} failure{'s' if FAIL != 1 else ''}, {WARN} warning{'s' if WARN != 1 else ''})")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
