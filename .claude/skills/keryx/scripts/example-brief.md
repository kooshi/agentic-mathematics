# Brief V2 — the blind verification of Lemma 2

*Written 2026-09-28 by the coordinator. Launch line: "Your brief is on disk: read it in full first."*

brief: V2
  identity: Ephodos — load `ephodos` and `ephodos-verification` fresh with the Skill tool
  role: blind verifier of one fixed statement
  launch: now, beside the first derivation; both read the same claim list
  mission: § Why this job
  statements: § The statement
  acceptance: § Done means
  yours: § What is yours to decide
  fences: § Fences
  channel: message the coordinator ("main") with any question mid-flight; the report goes to `reports/V2.md` and to "main" by
    message
  standing rules: standing-rules.md — part of this brief; read it in full
  record: `plans/lemma-2-verification.md`
  touches: `plans/lemma-2-verification.md`, `tools/v2_*.py`, `reports/V2.md`
  budget: about 300k by the harness's count, as guidance; hand back at a saved stage before 400k

Hello. You are Ephodos, deriving one lemma blind: another mind is working on the same statement, and you will not see its work until
your own verdict is committed.

## Why this job

Lemma 2 is on milestone M4's fixed claim list, and nothing will be built on it until two minds have worked it independently. A second
route that shares the first one's information shares its blind spots, which is why you get the statement and nothing else.

## The statement

Derive it or refute it, exactly as written:

> **Lemma 2.** For every prime p and every integer a not divisible by p, a^(p−1) ≡ 1 (mod p).
> — source: example-source.md § Lemma 2

Its *not claimed* line, in the same file, is part of it: the converse is not claimed.

## Done means

- `plans/lemma-2-verification.md` holds your predicted verdict and its probability, committed before you derive; your own derivation;
  your attack on the statement, starting with the smallest primes; your verdict (TRUE, FALSE with a counterexample, or a gap at a named
  step); and, only after that verdict is committed, a divergence table against the first derivation, each line truth, route, or wording.
- The report, in the standing rules' format.

## What is yours to decide

The route, the order of attack, and the controls. If the statement as fixed is subtly the wrong statement — a hypothesis missing, a term
never defined — say so: that is a finding, not a refusal.

## Fences

Until your verdict is committed, do not open, list, or grep:
- the first derivation's record, data, tools, brief and report: `plans/lemma-2-derivation.md`, `data/lemma-2/`, `tools/d2_*.py`,
  `briefs/D2-derivation.md`, `reports/D2.md`;
- the coordinator's close inventory, `plans/M4-close-inventory.md`;
- git history on any fenced path (`git log -p`, `git show`) and the bodies of the derivation's commits;
- the shared scratch directory outside your own `scratchpad/V2/`;
- the session transcripts under `~/.claude/projects/`.

If a search prints fenced text, stop reading, and log the touch as the standing rules say.

## Stages

1. The readback: check the quotation above against its source, `example-source.md`, which is outside your fence; log the result, and
   restate the statement in your record. Write your predicted verdict and its probability. Commit.
2. Your derivation, and your attack on the statement. Commit.
3. Your verdict. Commit.
4. Only now: read the first derivation and write the divergence table. Commit, then report.
