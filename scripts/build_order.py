#!/usr/bin/env python3
"""Print the library's modules in dependency order, grouped into batches of a given size.

One batch per line, module names separated by spaces. `scripts/build.sh` feeds each line to
`lake build` as an explicit target list.

Why the order matters and not just the size: naming a target whose dependencies are not built makes
Lake build those too, in the same unrestricted job pool. A batch is only a bound on concurrency if
everything it needs already exists -- so batches are cut from a topological order, and no batch ever
contains a module that imports another module in the same batch.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMPORT = re.compile(r"^import\s+(Proofs[\w.]*)", re.M)


def modules() -> dict[str, set[str]]:
    """Every module of the `Proofs` library, mapped to the library imports it declares."""
    out: dict[str, set[str]] = {}
    files = list((REPO / "Proofs").rglob("*.lean")) + [REPO / "Proofs.lean"]
    names = set()
    for f in files:
        rel = f.relative_to(REPO).with_suffix("")
        names.add(".".join(rel.parts))
    for f in files:
        rel = f.relative_to(REPO).with_suffix("")
        name = ".".join(rel.parts)
        src = f.read_text(encoding="utf-8", errors="replace")
        # Only the header's imports; a module docstring may quote `import` in a code block.
        head = src.split("\n/-", 1)[0]
        out[name] = {m for m in IMPORT.findall(head) if m in names and m != name}
    return out


def layers(deps: dict[str, set[str]]) -> list[list[str]]:
    """Kahn's algorithm, keeping each level together: a level depends only on earlier ones."""
    remaining = {k: set(v) for k, v in deps.items()}
    done: set[str] = set()
    out = []
    while remaining:
        ready = sorted(k for k, v in remaining.items() if not (v - done))
        if not ready:
            print("import cycle among: " + ", ".join(sorted(remaining)), file=sys.stderr)
            sys.exit(1)
        out.append(ready)
        done |= set(ready)
        for k in ready:
            del remaining[k]
    return out


def main() -> None:
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for level in layers(modules()):
        for i in range(0, len(level), size):
            print(" ".join(level[i:i + size]))


if __name__ == "__main__":
    main()
