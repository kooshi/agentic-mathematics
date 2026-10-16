#!/usr/bin/env python3
"""Is every work this repository cites logged in `BIBLIOGRAPHY.md`?

    python3 tools/bib_audit.py               # exit 1 if any cited key or arXiv id resolves to no row
    python3 tools/bib_audit.py --self-test   # plant one citation of each kind and require both reported

*Why a script:* `BIBLIOGRAPHY.md`'s rule is that a work is added the day it is first used, and the rule is broken exactly where
nobody looks — a work named in a stub, a plan or a report and never in the bibliography. Every such work is recorded somewhere, which
is why nobody notices: **prose is not an index.**

A key merged into another entry is listed in `BIBLIOGRAPHY.md` § A′ (retired and alternate keys), which this script reads, so a
resolved alias is never reported as a gap — a check that reports false gaps trains its reader to ignore it.

Two populations, counted separately, because they fail differently: an **arXiv id** is unambiguous and a miss is certainly a gap; a
**bracketed key** is ours and a miss may be an alias, a typo, or a genuine omission."""
from __future__ import annotations
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "BIBLIOGRAPHY.md")
ARXIV = re.compile(r"arXiv:(\d{4}\.\d{4,5})|arXiv:(math/\d+)|(?<![\w/])(math/\d{7})")
KEY = re.compile(r"\[([A-Z][A-Za-z]+\d{4}[a-z]?)\]")
# A CamelCase key with no year digits (`[SmithJones]`) is a citation the KEY pattern cannot see, and such a key once pointed at the
# wrong paper for days unnoticed. Such keys are cited keys too, and must resolve or be given their year.
YEARLESS = re.compile(r"\[([A-Z][a-z]+(?:[A-Z][a-z]+)+)\]")
# CamelCase words in brackets that are code identifiers, not citations (reviewed; extend with a reason).
NOT_KEYS = {"Author2024": "the placeholder key in LEAN.md and the axiom audit's messages",
            "AuthorYear": "the key's form, named in BIBLIOGRAPHY.md",
            "Smith2020": "the example key in BIBLIOGRAPHY.md § A and the audits' self-tests",
            "SmithJones2020b": "the example key in BIBLIOGRAPHY.md § A",
            "SmithJones": "the example of a yearless key, in this script",
            "Example2020": "the planted import's key in scripts/axioms_selftest.py"}
DEFN = re.compile(r"\*\*\[([A-Za-z0-9]+)\]\*\*")


def _md_files(extra_text=None):
    for dirpath, dirnames, names in os.walk(ROOT):
        # skipped: build products, and .claude, whose vendored skills cite their own sources and whose worktrees are stale copies
        dirnames[:] = [d for d in dirnames if d not in (".git", ".lake", "build", "node_modules", ".claude")]
        for n in names:
            if n.endswith(".md"):
                yield os.path.join(dirpath, n)
    # the parts of .claude this project writes: the grokkings, the lanes and the coordinator's workflow
    for rel in ("skills/grokkings/SKILL.md", "agents", "output-styles"):
        p = os.path.join(ROOT, ".claude", rel)
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for n in sorted(os.listdir(p)):
                if n.endswith(".md"):
                    yield os.path.join(p, n)


def scan(extra_text=""):
    bib = open(BIB, encoding="utf-8").read()
    defined = set(DEFN.findall(bib))
    aliases = set()
    m = re.search(r"### A′\. Retired and alternate keys(.*?)\n## ", bib, re.S)
    if m:
        aliases = {a for a in KEY.findall(m.group(1))} | set(YEARLESS.findall(m.group(1)))  # a yearless alias resolves too (FS-73)
    bib_arxiv = {g for t in ARXIV.findall(bib) for g in t if g}

    cited_arxiv, cited_keys = {}, {}
    for f in _md_files():
        txt = open(f, encoding="utf-8", errors="replace").read()
        for t in ARXIV.findall(txt):
            for g in t:
                if g:
                    cited_arxiv.setdefault(g, f)
        for k in KEY.findall(txt) + YEARLESS.findall(txt):
            cited_keys.setdefault(k, f)
    for k in KEY.findall(extra_text) + YEARLESS.findall(extra_text):
        cited_keys.setdefault(k, "<planted>")
    for t in ARXIV.findall(extra_text):
        for g in t:
            if g:
                cited_arxiv.setdefault(g, "<planted>")

    miss_a = {k: v for k, v in cited_arxiv.items() if k not in bib_arxiv}
    miss_k = {k: v for k, v in cited_keys.items() if k not in defined and k not in aliases and k not in NOT_KEYS}
    return defined, aliases, cited_arxiv, cited_keys, miss_a, miss_k


def main(argv):
    if "--self-test" in argv:
        return _self_test()
    defined, aliases, ca, ck, ma, mk = scan()
    print(f"bibliography: {len(defined)} keyed rows, {len(aliases)} retired/alternate keys")
    print(f"cited across the repository: {len(ca)} arXiv ids, {len(ck)} bracketed keys")
    print(f"\narXiv ids cited but NOT in the bibliography: {len(ma)}")
    for k, v in sorted(ma.items()):
        print(f"   arXiv:{k}   first seen in {os.path.relpath(v, ROOT)}")
    print(f"\nbracketed keys cited but neither defined nor aliased: {len(mk)}")
    for k, v in sorted(mk.items()):
        print(f"   [{k}]   first seen in {os.path.relpath(v, ROOT)}")
    bad = len(ma) + len(mk)
    print(f"\n{'UNLOGGED PRIOR ART: ' + str(bad) if bad else 'every cited work resolves to a row or a recorded alias'}")
    return 1 if bad else 0


def _self_test():
    """Plant one citation of each kind and require the audit to report both. A check that cannot
    see a planted gap is not a check — and this one shipped with a blind spot on its first run."""
    ok = True
    _, _, _, _, ma0, mk0 = scan()
    planted = "see arXiv:9999.99999 and [NotARealWork2099] for details"
    _, _, _, _, ma1, mk1 = scan(extra_text=planted)
    for name, got in (("planted arXiv id is reported", "9999.99999" in ma1),
                      ("planted bracketed key is reported", "NotARealWork2099" in mk1),
                      ("the planted items are the ONLY new ones",
                       len(ma1) == len(ma0) + 1 and len(mk1) == len(mk0) + 1)):
        print(f"  {'ok ' if got else 'FAILED'} {name}")
        ok &= got
    print(f"  (baseline with nothing planted: {len(ma0)} arXiv, {len(mk0)} keys unlogged)")
    print("\n" + ("3 controls, ALL FIRED" if ok else "CONTROL DID NOT FIRE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
