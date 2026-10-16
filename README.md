# agentic-mathematics

A template for attacking a mathematical problem of your own with a team of Claude agents, in Claude Code, with Lean 4 as the
judge. You state the problem; a coordinator runs an asker, a deriver, a Lean planner and a Lean implementer through a fixed cycle of
milestones; nothing counts as held until Lean's kernel has checked it. Clone it, write your problem into `CLAUDE.md`, open it in
Claude Code, and ask the coordinator to open the first milestone.

## Why it is shaped this way

Three facts about machine-assisted mathematics decide the design.

1. **A fluent mind overclaims.** A hand derivation rarely fails on a wrong step; it fails when the sentence claims more than the
   argument carried — the "if and only if" with one direction proved, the class claimed where one case was shown. So every
   statement is fixed in writing before anyone works on it, every result carries a grade saying what checked it, and **a milestone
   closes only when its Lean module passes the gate**: the kernel reads the statement exactly as written, and the gate checks that
   the statement is not empty (§ What the gates check).
2. **Past the known frontier, priors are worth little.** A model's sense of what usually works, what is hard and what formalization
   costs was formed where the ground was known. So the project carries its own theory — the grokkings — and every milestone opens by
   reading that theory from inside its question, then searching the literature in the words of the discipline the object belongs to
   (§ The grokkings).
3. **A context window is a budget, and minds that share one lose independence.** So each role is its own agent with its own
   standard, the coordinator only briefs, routes and files, every hand-off is a file on disk, and delegation is one level deep, so
   that the coordinator can review all the work, because it knows all the work exists.

Every rule in the template carries its reason beside it, in the file the mind that obeys it loads, so that an agent arriving with
no context can apply it and can tell when it no longer applies.

## The minds, and what each hands on

| mind | role | runs on | hands on |
|---|---|---|---|
| **Keryx** (the herald) | coordinates: the top-level session | Opus | briefs on disk, fences, rulings, the inventory, the filing, the report to you |
| **Poros** (the way through) | asks and ranks | Opus | the ranked frontier; the next milestone and its question card, in an existence form and a structural form |
| **Ephodos** (the method of approach) | derives | Opus | the plan and the claim list; derived statements at their grades; the derivation file and the stubs it surfaces |
| **de Bruijn**, planner | plans the Lean module | Opus | the Lean skeleton with `sorry` at every leaf and a plan per leaf, made first from the claim list alone |
| **de Bruijn**, implementer | builds it | Opus | the finished module through the gate, and the lines that close the milestone |
| **the Searcher** | runs searches, once a day | Opus | the day's chosen searches (SAT, MILP, enumerations), their certificates and their nulls |
| **the Clerk** | files | Sonnet | drafts filed verbatim, reports folded, mechanical audits, a `CHECK:` line wherever it would have had to guess |
| *Ephodos, verification form* | a blind second mind | Opus | a verdict per claim before it sees the first derivation — off by default, because the kernel is the second check |

The arrows run backward as well as forward: de Bruijn sends a statement defect back to Ephodos, Ephodos sends "stalls at this
step" back to Poros, and Poros sends a re-posed question forward again — all through Keryx, who changes nothing in a packet and
makes sure it arrives whole at the mind that can act on it. Only the Searcher searches, because a deriving lane that may search
stalls on compute and on nulls that explain nothing.

## A milestone's states

**Not started** (a stub: a file holding the milestone's whole context) → **Opened** (Ephodos's opening job: the re-grokking, the
prior-art gate, the invariant question, the plan, the claim list) → **Derived** (the derivations done and filed; later milestones
may build on the results, assumed until their module lands, so the frontier never waits for the kernel) → **Closed** (the Lean
module passes the gate). A milestone whose claims all stalled closes at its record — a stall at a named step is a result.

## The grokkings

The grokkings are the project's working theory: one entry per mechanism, reading or rule the project has understood, each with a
status at its grade, its mechanism, a *Do* that opens with its trigger, and a killing test (or, for a theorem, what it forbids). They
are the defining feature of the method. In the words of the person who built it, from the project where it was built:

> "They were the defining feature that led to a significant amount of novel findings here. Remember, when you pass through to the
> frontier, priors are weak, and you need to carry every novel finding in context to be able to make progress with them."

A project past the known frontier has three tiers of knowledge: **results** (the ledger, `LEDGER.md`, looked up by row),
**understanding** (the grokkings, reasoned from), and **method** (`CLAUDE.md` § Method, the rules that keep a measurement honest).
The asker, the deriver and its verifier load the grokkings in full at every launch
(`.claude/skills/grokkings/SKILL.md`); every opening job walks every entry from inside its question, and an entry neither used nor
listed as silent is a plan defect; every record job drafts the new entries, and the coordinator files them verbatim. Entries are
rewritten in place to current state; an entry that dies is demoted with its refutation recorded, never deleted, so that a dead idea
is not proposed again; numbers are never reused. The file ships with its rules and two example entries to delete.

## What the gates check

Every gate fails loudly, keeps its complete output under `build/gate/`, and ships with planted controls that are watched failing
(`--self-test`), because a check never seen failing may be checking nothing.

| gate | what it checks | why |
|---|---|---|
| `scripts/build.sh` | the library builds, in batches under a memory cap; Mathlib is never built here | Lake sizes its job pool from the machine, and a machine out of memory stops for every job |
| `scripts/nosorry.py` | no `sorry` in the source, and every module reached from `Proofs.lean` | the audits read only what the root imports |
| `scripts/axioms.sh` | every declaration's axioms, as a set: the standard three, declared imports of outside theorems (each with its source and a read-back), declared native-evaluation purchases — nothing else | everything shipped reduces to what the kernel checked plus what we chose to trust, and says which |
| `scripts/vacuity.sh` | no theorem is a statement over an empty domain, for every carrier the library tracks | the kernel accepts a vacuous theorem as gladly as any other |
| `lake lint` | the environment linters | missing docstrings and unused arguments hide wrong statements |
| `tools/check_architecture.py` | the module map in `ARCHITECTURE.md` matches the import graph | a fresh mind finds results through the map |
| `scripts/identities.py check` | every vendored identity file matches its recorded hash, and every lane's copy of its identity matches its skill | an identity is a standard tested as a whole; an edit makes a standard nobody tested |
| `.claude/skills/keryx/scripts/brief_gate.py` | every brief: its fields, its quotations verbatim at the address they name, its paths | a paraphrased statement is the characteristic slip of a coordinator writing fast |
| `.claude/skills/ephodos/scripts/derive_gate.py`, `.claude/skills/poros/scripts/poros_gate.py` | every derivation entry and every question card, in their identity's grammar | a statement's scope is the part a summary drops |
| `tools/claude_md_fact_audit.py`, `tools/bib_audit.py` | no fact lost or told twice when the front files are rewritten, the size budgets; every cited work in the bibliography | the files every mind loads hold current state only, and must lose nothing in the rewriting |

`./scripts/gate.sh` runs the Lean gate in order; `./scripts/gate.sh --self-tests` adds every planted control.

## How to start

1. **Install** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and, for the Lean side, run `./install-toolchain.sh`:
   it installs `elan` if it is missing, the pinned toolchain (Lean v4.32.0), and Mathlib's prebuilt files (`lake exe cache get`, a
   download of several gigabytes, once). Never build Mathlib from source here. The memory tool (`scripts/slot.py`) and the build's
   cap need Linux with a systemd user session; elsewhere, `MEMCAP=none` builds uncapped, by decision.
2. **Build once** and run the gate's controls:
   `python3 scripts/slot.py --mem 8 --cpus 2 -- env MEMMAX=8G ./scripts/gate.sh --self-tests`. Every self-test should pass.
3. **Open the repository in Claude Code.** The top-level session becomes Keryx, the coordinator (`.claude/settings.json` selects
   its output style; `.claude/settings.md` says why each setting is there).
4. **State your problem.** Ask Keryx to fill `CLAUDE.md`'s `‹PRINCIPAL: …›` markers with you, in your words: the problem and where
   it stands, your aim, the notation, and your counter-priors. Name a few candidate milestones; each becomes a stub in `plans/`.
5. **Ask Keryx to open the first milestone.** It briefs Poros to rank the stubs and pose the first question, then runs the cycle.
   It reports to you at a gate, a decision or a check-in, in plain words, with every decision that is yours (budget, head-count,
   model, anything irreversible) put to you and the rest settled.

To run one lane as your own session (`claude --agent poros`), pass `--settings '{"outputStyle":"default"}'` too, or that session
holds two identities.

## What it costs to run

- **Tokens.** Each job is a fresh agent with a brief that budgets roughly 200k–500k tokens of context, and an agent deep in its
  context is replaced rather than continued. A milestone usually runs an opening, one or more derivations, a record, a kernel plan
  and an implementation — several million tokens in all — and the coordinator's own session besides. Opus does all the judged work;
  the Clerk runs on Sonnet. The coordinator runs three agents at a time by default; head-count and models are yours to set.
- **Machine.** Mathlib's prebuilt files take a few gigabytes of disk; a small library builds in 8 GB of RAM; heavy certificate
  modules need more, and `scripts/slot.py` keeps every job inside the machine's memory budget.
- **Your time.** You state the problem and the aim, rule on what is yours, and check in. The coordinator does not need you between
  decisions.

## Where things are

| file | who loads it | holds |
|---|---|---|
| `CLAUDE.md` | every mind | the problem, the frontier, the theory in one paragraph, the method, the pipeline, the standard of evidence |
| `.claude/output-styles/keryx.md` | the top-level session | the `keryx` identity, then the coordinator's workflow |
| `.claude/agents/*.md` | each lane | its identity, verbatim, then its workflow |
| `.claude/skills/` | lanes, by name | the vendored identities and their companions, the two stance skills, the grokkings |
| `plans/STANDING-RULES.md` | every briefed job | the rules every brief shares, each with its reason |
| `LEAN.md` | both de Bruijn lanes | the Lean facts: assumptions, trust, the build, the cost model, the gate |
| `RUNNING.md` | jobs that run processes or build checkers | how to run a process here, and how a check must fail |
| `LEDGER.md`, `BIBLIOGRAPHY.md`, `ARCHITECTURE.md` | read by address | results by row, every cited work, the module map |
| `plans/` | read by address | the ranked stubs, the search queue, the grokkings' instances and retired entries, templates for every record |

## Credit

The method is Kooshi's (GitHub `kooshi`): the identities Keryx, Poros, Ephodos and de Bruijn with their companions and gates, the
two stance skills (`decompress`, `peer-delegation`), and the workflow beneath each identity, which grew in the project below. The
identities derive from his earlier engineering identity, Ferrous, which is public at <https://github.com/kooshi/rusty-tools-mcp>
(MIT/Apache) and is credited here, not included. The mathematics and engineering in any project run with this template are its
agents' and its principal's.

## A worked example (from the project where the method was built)

> *This section is the only place this repository mentions a particular problem.* The method was built in **lean-dir**
> (`<lean-dir public URL>`), a Lean 4 workspace aimed at the Hadwiger–Nelson problem: how many colours the plane needs so that no
> two points at distance exactly 1 share a colour. There the pipeline ran milestone after milestone from the question's classical
> bounds to a library that kernel-checks the interval 5 ≤ χ(ℝ²) ≤ 7 on Lean's standard three axioms, together with a body of
> derived and kernel-checked results about the problem's algebraic and measurable forms. Its `CLAUDE.md`, ledger, grokkings and
> milestone records show every file of this template filled in for one problem, including the failures and the stalls.

## Licence

Apache-2.0 (`LICENSE`).
