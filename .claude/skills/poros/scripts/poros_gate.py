#!/usr/bin/env python3
"""poros_gate.py — text-level quality gate for question cards, hunch ledgers, and evidence
inventories written in markdown.

Conventions checked (see SKILL.md <the_card>, <the_two_ledgers>, <commands>; a gate-clean example is
example-clean.md beside this file, and example-dirty.md fails fifteen ways by design):

  question card   a line "question: <name>" at column 0 (a leading "- " is allowed), followed by indented
                  "key: value" lines; a value may continue on further indented lines:
                    evidence:    what was seen, with an address (a path, a line, an id, a date, a
                                 measurement name, a quoted fragment, a count) — why this question, now
                    expected:    what the frame or the prior said the evidence would show (optional;
                                 absent or empty is warned — without it the surprise cannot be measured)
                    ask:         the one question, at most 45 words, not advice-shaped
                    if <answer>: <next move>      — at least two, and the moves must differ; the answer
                                 label may hold digits, hyphens, symbols; it ends at the first ": "
                    answered by: record | run | derivation | human | experiment — a capitalised name
                                 counts as a human; "running", "reading", "measuring" count as their verbs
                    cost:        what getting the answer costs
                    hunch:       what you think the answer is (optional; if present, falsifier: is required)
                    falsifier:   the reading that would kill the hunch
                    rank:        1..n when a document holds several cards (the rank-1 card is the ask)
  no-question     a line "no question: <reason>" followed by an indented "need: <what to read or run first>"
                  — the honest exit; a document with neither a card nor this line has ended in advice
  hunch ledger    a line "hunch: <name>" at column 0 followed by indented lines
                    claim: … / basis: measured | derived | analogy | prior | read / falsifier: … /
                    registered: YYYY-MM-DD / status: open | confirmed (by: …) | killed (by: …)
                  a measured, analogy, or prior hunch may be confirmed only by a derivation or a
                  replication and "by:" must say which; a read hunch (a fact with an address) is
                  confirmed by the address; a derived hunch by anything named
  inventory       a heading containing "evidence inventory" followed by bullets
                    - <item> — read against: <expectation> — surprised: yes | no | unread
                  (— or | or ; separate the three parts); an unread item is a standing finding; an
                  empty expectation fails; inventory-shaped bullets under another heading are warned

What the gate cannot see, so it does not claim to: whether the question is the right one; whether two
branches that differ as strings are different moves; whether an item was read rather than listed.

Subcommands: cards | hunches | inventory | all
Exit status is non-zero when a check fails, so it composes with CI and with `&&`.
Standard library only.
"""
import re
import sys
from datetime import date

FAIL = 0
WARN = 0


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


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_fences(text):
    """Blank out fenced code so a quoted example is never linted as the artifact."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return out


# ---------------------------------------------------------------- block parsing

# a block head starts at column 0 (an indented `hunch:` is a field inside a card, not a ledger entry)
BLOCK_HEAD = re.compile(r"^(?:[-*]\s+)?(?:\*\*)?(question|hunch|no question)(?:\*\*)?\s*:\s*(.*?)\s*$", re.I)
KV = re.compile(r"^\s+(?:[-*]\s+)?([A-Za-z][A-Za-z !]*?)\s*:\s*(.*?)\s*$")
IF_LINE = re.compile(r"^\s+(?:[-*]\s+)?if\s+(.+?):\s+(.*?)\s*$")   # the label ends at the first ": "
IF_BARE = re.compile(r"^\s+(?:[-*]\s+)?if\s+(.*):\s*$")            # "if <label>:" with no move on the line


def field_line(line):
    """Return (key, value) for an indented field line, or None."""
    m = IF_LINE.match(line)
    if m:
        return "if " + m.group(1).strip(), m.group(2)
    m = IF_BARE.match(line)
    if m:
        return "if " + m.group(1).strip(), ""
    m = KV.match(line)
    if m:
        return m.group(1).strip().lower(), m.group(2)
    return None


def blocks(lines, kind):
    """Yield (line_no, name, fields) for every block headed `kind:`; fields is a list of (key, value)
    in file order so repeated keys (the if-branches) survive. An indented line that is not a field
    continues the previous field's value."""
    i, n = 0, len(lines)
    while i < n:
        m = BLOCK_HEAD.match(lines[i])
        if m and m.group(1).lower() == kind:
            start, name, fields = i + 1, m.group(2), []
            i += 1
            while i < n and lines[i].strip() and (lines[i][0] in " \t"):
                kv = field_line(lines[i])
                if kv:
                    fields.append(kv)
                elif fields:
                    k, v = fields[-1]
                    fields[-1] = (k, (v + " " + lines[i].strip()).strip())
                i += 1
            yield start, name, fields
        else:
            i += 1


def get(fields, key):
    for k, v in fields:
        if k == key:
            return v
    return None


def branches(fields):
    return [(k[3:].strip(), v) for k, v in fields if k.startswith("if ")]


def normalize(move):
    return re.sub(r"[^a-z0-9]+", " ", move.lower()).strip()


# ---------------------------------------------------------------- lints

ADDRESS = re.compile(
    r"[\w.-]+/[\w./-]+"        # a path
    r"|\b[\w-]+\.(?:md|py|rs|lean|txt|json|csv|log|cir|tjp|sh)\b"  # a file
    r"|\bline\s*\d+|:\d+\b"    # a line
    r"|\b(?:M|G|T|P|Q|K|FS)-?\d+\b"  # a milestone / grokking / theorem id
    r"|\b\d{4}-\d{2}-\d{2}\b"  # a date
    r"|`[^`]+`"                # a quoted name
    r"|\"[^\"]{3,}\"|“[^”]{3,}”"  # a quoted fragment
    r"|#\w+"                   # an anchor
    r"|\b\d+(?:[.,]\d+)?\s*(?:of|/)\s*\d+"  # a count
)
ADVICE_SHAPED = [
    r"\bhave you (?:considered|thought about|tried|looked at)\b",
    r"\bit (?:might|may|could|would) be (?:worth|interesting|useful|good)\b",
    r"\byou (?:might|may|could) want to\b",
    r"\bconsider (?:whether|if|using|adding)\b",
    r"^\s*what about\b",
]
SAME_MOVE = {"", "continue", "proceed", "same", "as planned", "continue as planned", "keep going", "nothing"}
ADDRESSEE = re.compile(
    r"\b(record|run|running|derivation|derive|deriving|human|experiment|world|measure|measuring|measurement|"
    r"bench|user|person|read|reading|fresh mind|subagent|second session)\b|\b[A-Z][a-z]+\b"
)
BASES = {"measured", "derived", "analogy", "prior", "read"}
STATUS = re.compile(r"^(open|confirmed|killed)\b(.*)$", re.I)
DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
PROMOTION = re.compile(r"\b(deriv|proof|proved|theorem|replicat|pre-?registered)\w*", re.I)
ASK_MAX_WORDS = 45


def check_cards(text):
    lines = strip_fences(text)
    say("card lint")
    cards = list(blocks(lines, "question"))
    exits = list(blocks(lines, "no question"))
    if not cards and not exits:
        fail("no question card and no `no question:` line — the turn has ended in advice")
        return
    for ln, name, fields in exits:
        if not get(fields, "need"):
            fail(f"line {ln}: `no question: {name}` carries no `need:` — say what must be read or run before a question exists")
    ranks = {}
    for ln, name, fields in cards:
        label = f"line {ln} ({name or 'unnamed'})"
        ev = get(fields, "evidence")
        if not ev:
            fail(f"{label}: no evidence: — a question with nothing that begged it is a genre question")
        elif not ADDRESS.search(ev):
            fail(f"{label}: evidence carries no address (a path, line, id, date, quoted fragment, or count): {ev!r}")
        exp = get(fields, "expected")
        if exp is None:
            warn(f"{label}: no expected: — without a stated expectation the surprise cannot be measured")
        elif not exp.strip():
            warn(f"{label}: expected: is empty — without a stated expectation the surprise cannot be measured")
        ask = get(fields, "ask")
        if not ask:
            fail(f"{label}: no ask:")
        else:
            if len(ask.split()) > ASK_MAX_WORDS:
                fail(f"{label}: ask is {len(ask.split())} words — one question is one line; several questions are several cards")
            for pat in ADVICE_SHAPED:
                if re.search(pat, ask, re.I):
                    fail(f"{label}: advice-shaped ask ({pat}): {ask!r}")
                    break
        br = branches(fields)
        if len(br) < 2:
            fail(f"{label}: {len(br)} branch(es) — a question whose answer cannot go two ways is not a question")
        else:
            moves = {normalize(v) for _, v in br}
            if len(moves) < 2:
                fail(f"{label}: every branch leads to the same move ({br[0][1]!r}) — the answer would change nothing")
            elif all(m in SAME_MOVE for m in moves):
                fail(f"{label}: branches name no move — say what each answer changes")
        ab = get(fields, "answered by")
        if not ab:
            fail(f"{label}: no answered by: — who or what returns the answer?")
        elif not ADDRESSEE.search(ab):
            fail(f"{label}: answered by names no addressee (record, run, derivation, human or a name, experiment): {ab!r}")
        if not get(fields, "cost"):
            fail(f"{label}: no cost: — the cheapest reading cannot be chosen without it")
        if get(fields, "hunch") is not None and not get(fields, "falsifier"):
            fail(f"{label}: a hunch with no falsifier: — a hunch is scored, never defended")
        r = get(fields, "rank")
        if r is not None:
            if not r.isdigit():
                fail(f"{label}: rank is not an integer: {r!r}")
            elif int(r) in ranks:
                fail(f"{label}: rank {r} already used at line {ranks[int(r)]}")
            else:
                ranks[int(r)] = ln
    if len(cards) > 1 and 1 not in ranks:
        fail(f"{len(cards)} cards and none ranked 1 — which one is the ask?")
    if len(cards) > 3:
        warn(f"{len(cards)} cards — three is a menu; more is a spray; one is a turn")
    say(f"  cards: {len(cards)}  no-question exits: {len(exits)}")
    if 1 in ranks or len(cards) == 1:
        ln, name, fields = next((c for c in cards if get(c[2], "rank") == "1"), cards[0])
        say(f"  the ask: {get(fields, 'ask') or '(none)'}  [line {ln}]")


def check_hunches(text):
    lines = strip_fences(text)
    say("hunch ledger")
    hunches = list(blocks(lines, "hunch"))
    open_n = conf_n = kill_n = 0
    for ln, name, fields in hunches:
        label = f"line {ln} ({name or 'unnamed'})"
        if not get(fields, "claim"):
            fail(f"{label}: no claim:")
        basis = (get(fields, "basis") or "").lower()
        if basis not in BASES:
            fail(f"{label}: basis must be one of {sorted(BASES)}: {basis!r}")
        if not get(fields, "falsifier"):
            fail(f"{label}: no falsifier: — an unfalsifiable hunch is a belief")
        reg = get(fields, "registered")
        if not reg or not DATE.search(reg):
            fail(f"{label}: no registered: date (YYYY-MM-DD)")
        else:
            y, m, d = map(int, DATE.search(reg).groups())
            try:
                if date(y, m, d) > date.today():
                    warn(f"{label}: registered in the future: {reg}")
            except ValueError:
                fail(f"{label}: registered date is not a date: {reg!r}")
        st = get(fields, "status") or ""
        sm = STATUS.match(st)
        if not sm:
            fail(f"{label}: status must be open | confirmed (by: …) | killed (by: …): {st!r}")
            continue
        kind, rest = sm.group(1).lower(), sm.group(2)
        if kind == "open":
            open_n += 1
        else:
            if "by:" not in rest and "by " not in rest:
                fail(f"{label}: {kind} with no `by:` — say what settled it")
            elif kind == "confirmed":
                conf_n += 1
                if basis in ("measured", "analogy", "prior") and not PROMOTION.search(rest):
                    fail(f"{label}: a {basis} hunch confirmed by something other than a derivation or a registered replication: {rest.strip()!r}")
                elif basis == "read" and not ADDRESS.search(rest):
                    fail(f"{label}: a read hunch confirmed without the address that was read: {rest.strip()!r}")
            else:
                kill_n += 1
    say(f"  hunches: {len(hunches)}  open: {open_n}  confirmed: {conf_n}  killed: {kill_n}")


INV_HEAD = re.compile(r"^#+\s.*evidence inventory", re.I)
HEAD = re.compile(r"^#+\s")
INV_ITEM = re.compile(r"^\s*[-*]\s+(.*)$")
SURPRISED = re.compile(r"surprised\s*:\s*(yes|no|unread)\b", re.I)
AGAINST = re.compile(r"read against\s*:\s*([^—|;]*)", re.I)


def check_inventory(text):
    lines = strip_fences(text)
    say("evidence inventory")
    start = next((i for i, l in enumerate(lines) if INV_HEAD.match(l)), None)
    if start is None:
        stray = sum(1 for l in lines if INV_ITEM.match(l) and SURPRISED.search(l))
        if stray:
            warn(f"{stray} inventory-shaped line(s) found, but no section is headed 'evidence inventory' — they were not linted")
        else:
            warn("no section headed 'evidence inventory' — what is in front of you is not listed, so nothing can be marked unread")
        return
    items, unread, surprised = 0, [], 0
    for l in lines[start + 1:]:
        if HEAD.match(l):
            break
        m = INV_ITEM.match(l)
        if not m:
            continue
        items += 1
        body = m.group(1)
        s = SURPRISED.search(body)
        a = AGAINST.search(body)
        if not s:
            fail(f"inventory item without `surprised: yes|no|unread`: {body[:70]!r}")
            continue
        if s.group(1).lower() == "unread":
            unread.append(body.split("—")[0].split("|")[0].strip())
        elif not a or not a.group(1).strip():
            fail(f"inventory item read against nothing: {body[:70]!r}")
        elif s.group(1).lower() == "yes":
            surprised += 1
    if items == 0:
        fail("evidence inventory is empty")
    for u in unread:
        warn(f"unread: {u}")
    say(f"  items: {items}  surprised: {surprised}  unread: {len(unread)}")


CHECKS = {"cards": check_cards, "hunches": check_hunches, "inventory": check_inventory}


def main(argv):
    if len(argv) < 2 or argv[0] not in list(CHECKS) + ["all"]:
        say(__doc__)
        return 2
    cmd, path = argv[0], argv[1]
    try:
        text = read(path)
    except (OSError, UnicodeDecodeError) as e:
        say(f"cannot read {path}: {e}")
        return 2
    for name, fn in CHECKS.items():
        if cmd in (name, "all"):
            fn(text)
    say(f"GATE: {'FAIL' if FAIL else 'PASS'} ({FAIL} failure{'s' if FAIL != 1 else ''}, {WARN} warning{'s' if WARN != 1 else ''})")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
