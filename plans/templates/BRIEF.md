# Brief ‹job id› — ‹what the job does, in a line›

*Written ‹date› by Keryx. Launch line: "Your brief is on disk: read it in full first." Copy to
`data/mNN/briefs/<job id>-<slug>.md`, fill every `‹…›`, run `python3 .claude/skills/keryx/scripts/brief_gate.py all <brief>` from the
repository root, and launch only on a pass. Each header field is a part a fast brief drops: the `keryx` identity's `<the_brief>` says
what each one is for.*

brief: ‹job id›
  identity: ‹the lane — its agent file is its identity and its workflow; the skills it loads fresh›
  role: ‹one line›
  launch: ‹now, or after which hand-back or commit›
  mission: § Why this job
  statements: § The statements
  acceptance: § Done means
  yours: § What is yours to decide
  fences: ‹§ Fences, or "none — nothing here is blind", with the reason›
  channel: message the coordinator ("main") mid-flight for a question you cannot work around or a finding that cannot wait; the report goes to `data/mNN/reports/‹job id›.md` and to "main" as your hand-back
  standing rules: plans/STANDING-RULES.md — part of this brief; read it in full
  record: `‹path›`
  touches: `‹path›`, `‹path›`
  budget: about ‹N›k by the harness's count, as guidance; hand back at a saved stage before about ‹M›k

## Why this job

‹The why, with the principal's words quoted from a file where they are the reason.›

## The statements

‹Each quoted whole, by script (`scripts/brief_quote.py`), with its source line:›

## Done means

‹What done looks like, before the work; the first stage is always the readback.›

## What is yours to decide

‹The decisions that belong to the recipient, and the invitation to attack the framing: a wrong statement reported is a finding.›

You start no agents of your own (standing rule 1: delegation is one level deep, because the coordinator can only review work it knows
exists).
