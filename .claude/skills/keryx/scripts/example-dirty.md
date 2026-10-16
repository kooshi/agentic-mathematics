# Brief V2 — a fast brief (fails by design; each planted defect is named in italics beside the line that carries it)

brief: V2
  identity: Ephodos — load `ephodos` and `ephodos-verification` fresh with the Skill tool
  role: blind verifier of one fixed statement
  launch: now
  mission: § Why this job
  statements: § The statements
  acceptance: § Done means
  yours: § What is yours
  fences: § Fences
  standing rules: example-source.md
  record: `plans/lemma-2-verification.md`
  touches: `plans/lemma-2-verification.md.draft`, `tools/v2_*.py`
  budget: about 300k by the harness's count, as guidance

*Planted in the header: no channel: field — the recipient has no way to reach the coordinator. yours: names a heading that does not
exist. The standing rules file carries no rule against spawning agents. The record is not among the touches — a longer name that
contains it does not count. The acceptance section below is empty.*

## Why this job

*Planted: the principal's words, quoted from memory with no source.*

> Check the lemma before we build on it.

*Planted: an input that does not exist.*
The first half of the argument is in `plans/lemma-1-derivation.md`.

*Planted: the mission quotes the other job's brief, which the fence closes — the recipient cannot read it back.*

> Launch line: "Your brief is on disk: read it in full first."
> — source: example-brief.md

## The statements

*Planted: the paraphrase that drops the qualifier — a = p is a counterexample to it.*

> **Lemma 2.** For every prime p and every integer a, a^(p−1) ≡ 1 (mod p).
> — source: example-source.md § Lemma 2

*Planted: the same qualifier dropped behind an elision mark.*

> **Lemma 2.** For every prime p and every integer a […] a^(p−1) ≡ 1 (mod p).
> — source: example-source.md § Lemma 2

*Planted: a statement quoted verbatim at the wrong address — it is Lemma 3, not Lemma 2.*

> **Lemma 3.** For every prime p, (p − 1)! ≡ −1 (mod p).
> — source: example-source.md § Lemma 2

*Planted (two warnings): the verdict handed over, as an order and as news of the other route.*
Prove Lemma 2.
The first derivation decided it.

## Done means

## Fences

Until your verdict is committed, do not open the first derivation's record `plans/lemma-2-derivation.md`, its brief
`example-brief.md`, git history on those paths (`git log -p`), the shared scratch outside `scratchpad/V2/`, or the session transcripts.

## Stages

1. Derive it.
