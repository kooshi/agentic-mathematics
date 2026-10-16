#!/usr/bin/env python3
"""Fill `{{Q:<file>|<heading>|<bullet id>}}` placeholders in a brief template with the bullet quoted whole.

    python3 scripts/brief_quote.py <template.md> <brief.md>

Each placeholder becomes the bullet that opens `- **<bullet id>**` under the `## <heading>` (or `### <heading>`) of `<file>`, as a
blockquote, followed by `> — source: <file> § <heading>`. *Why by script:* a statement copied by hand is the characteristic slip of a
capable coordinator writing fast — a dropped qualifier turns a true lemma into a false one — and the brief gate
(`.claude/skills/keryx/scripts/brief_gate.py quotes`) can hold only a quotation to its source, never a paraphrase beside it. Fails
loudly (a Python exception, non-zero exit) when the file, the heading or the bullet is missing, so a placeholder is never left
half-filled. Paths are relative to the directory you run it from; run it from the repository root.
"""
import re
import sys


def bullet(path: str, heading: str, bid: str) -> str:
    s = open(path, encoding="utf-8").read()
    i = s.index("\n## " + heading) if ("\n## " + heading) in s else s.index("\n### " + heading)
    j = s.find("\n## ", i + 5)
    sec = s[i:j if j > 0 else len(s)]
    k = sec.index("- **" + bid + "**")
    rest = sec[k:]
    m = re.search(r"\n(?=- \*\*|\n)", rest[2:])
    item = rest[: (m.start() + 2) if m else len(rest)].rstrip("\n")
    out = ["> " + line for line in item.split("\n")]
    out.append("> — source: " + path + " § " + heading)
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    t = open(sys.argv[1], encoding="utf-8").read()
    t = re.sub(r"\{\{Q:([^|]+)\|([^|]+)\|([^}]+)\}\}", lambda m: bullet(m.group(1), m.group(2), m.group(3)), t)
    open(sys.argv[2], "w", encoding="utf-8").write(t)
