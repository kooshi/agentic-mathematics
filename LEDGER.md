# LEDGER.md — the novel-results ledger

*One row per result this project has produced, kernel-checked unless graded otherwise (grades: `CLAUDE.md` § Notation), with its
address and its milestone. **This file is read by address, never loaded**: a result is looked up by its row when a brief names a
consumer, a re-grokking walks a row's mechanism, or a close files a row; what is reasoned from lives in the grokkings, each pointing
here. *Why separate:* numbers, certificates, names and addresses grow with every milestone, and a mind needs only the rows its job
touches. Current state only, like `CLAUDE.md`: a corrected row is rewritten in place and the story goes to git. Keryx is this
file's only writer, filing the lanes' drafts verbatim; `tools/claude_md_fact_audit.py` audits `CLAUDE.md` and this file as one
corpus.*

## The claim list — what is ours

*Every result this project calls its own, each with its attribution verbatim: what is prior art (with its `BIBLIOGRAPHY.md` key),
what is ours, and what the kernel check adds. Read it before calling anything ours, because "not found in print" is a claim about
where we looked.*

- ‹none yet›

## A. The novel-results ledger

*Row numbers are stable identifiers cited across `plans/`: never renumber, never reuse, because every citation of a row would then
point at another result. Lean modules are under `Proofs/`. Paths under `build/` are local, untracked, regenerable measurement
artifacts — provenance, never a certificate; the certificate is the Lean module. A row filed at Derived reads "[hand], one mind,
kernel pending"; the close regrades it to [kernel] with its declaration and every assumption it rests on by name.*

| row | result | grade | address | milestone |
|---|---|---|---|---|
| 1 | **EXAMPLE (delete with the first real row):** the sum of the first `n` odd numbers is `n²`, for every natural `n` | [kernel], on no axiom beyond the standard three | `Proofs.Example.oddSum_eq_sq` (`Proofs/Example.lean`) | the template's example |
