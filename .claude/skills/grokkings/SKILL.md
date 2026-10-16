---
name: grokkings
description: This project's grokkings, the working theory of the problem stated in CLAUDE.md § The mission — every entry with its status, its mechanism, its Do and its killing test or what it forbids. Preloaded at launch into the poros, ephodos and ephodos-verifier agents through their skills field; the coordinator, the Clerk and both de Bruijn lanes read an entry here by its number instead of loading the file.
---

# Grokkings — the working theory of this project's problem (the entries)

*The theory this project reasons from, one entry per mechanism, reading or rule it has grokked. Keryx is this file's only writer:
new entries are drafted by a milestone's record job (`.claude/agents/ephodos.md` § The record job) and filed here verbatim. The
section's rules are in `CLAUDE.md` § Grokkings, which every mind loads, with the theory in one paragraph; this file holds the
entries. Its size budget is 200,000 bytes (`tools/claude_md_fact_audit.py` fails over it): a budget reached is met by retiring an
entry into a workflow or a rule, never by trimming an entry's reasoning.*

*The rules every entry obeys:*
- **A number is never reused and never renumbered.** `G1`, `G2`, … are identifiers cited across `plans/`, the ledger and the lanes'
  records.
- **Every entry carries a status at its grade** (`CLAUDE.md` § Notation): `[kernel]`, `[cert]`, `[tools]`, `[measured]`, `[hand]`,
  `[derived]`, `[reading]`, `[external]`, `[method]`. A reading is never silently promoted.
- **The form**: the title as a claim, the status, the mechanism in a few sentences, then one closing line —
  `*Do: <trigger> — <what it makes you do>. Killing test: <what would kill it>.*` The *Do* opens with its **trigger** (*when you meet
  a new object of kind X; before a search over Y; when a sweep reads zero*), never a bare verb. The second half takes one of two
  shapes, by grade: a reading or a measurement names its **falsifier**; a theorem names what it **forbids** (*nothing kills it; it
  kills X*). An entry without both is understood, not grokked, and a mind will read it as background instead of reasoning from it.
- **Current state only.** An entry is rewritten in place when understanding moves. Its later instances go to
  `plans/GROKKING-INSTANCES.md` under its number, verbatim, with their sources.
- **An entry that dies is demoted, never deleted**: it keeps, in one or two sentences, what it wrongly claimed and what killed it.
- **An entry absorbed into a workflow or a rule is retired**: its full text moves to `plans/GROKKINGS-RETIRED.md`, and here it keeps
  a titled pointer naming where it is now carried.

*The two entries below are EXAMPLES of the form, taken from no problem in particular. Delete both when the first real entry is
filed, and start the numbering again at G1.*

* **G1 — EXAMPLE (delete): Parity is the first invariant to compute. [reading]** When a problem moves objects by local steps (a
  piece slides, an edge flips, a colour swaps), the cheapest invariant every reachable state carries is a parity: a count modulo 2
  that each step changes by a fixed amount. It decides reachability questions before any search runs, and when it does not decide
  them, the classes it leaves are where the next invariant lives. *Do: when a question asks whether one configuration reaches
  another by local moves, compute how each move changes a count modulo 2 before enumerating anything, and state the classes that
  count separates. Killing test: three milestones in a row whose reachability questions were decided by something other than a
  parity or a refinement of one, with the parity computed first each time and deciding nothing.*
* **G2 — EXAMPLE (delete): The sum of the first `n` odd numbers is `n²`. [kernel]** `Proofs.Example.oddSum_eq_sq` (`LEDGER.md`
  row 1, the example row). The mechanism is the square's L-shaped layers: going from `n²` to `(n+1)²` adds `2n + 1` unit squares, so
  the induction step is one line of algebra. *Do: when a sum over `1 … n` has a guessed closed form, look for the shape whose layers
  the summands count, and prove the closed form by induction on the layers. Nothing kills it; it kills any claimed closed form for
  `1 + 3 + … + (2n − 1)` other than `n²`, at every `n`.*
