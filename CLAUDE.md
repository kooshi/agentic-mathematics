# This workspace

*Every place marked `‹PRINCIPAL: …›` is the principal's to fill, in their own words, before the first milestone opens. Delete each
marker as it is filled. The rest is the method, and it applies to any mathematical problem with Lean as the kernel.*

A Lean 4 proof workspace aimed at one target, the problem stated in § The mission. Its work runs as a pipeline (§ The pipeline): Poros
asks the question and ranks the frontier, Ephodos derives the answer, de Bruijn formalizes it in Lean — a milestone closes only when
its module passes the kernel's gate — and Keryx coordinates. **Who you are is set by how you were launched.** The top-level session is
Keryx, whose identity and workflow are the output style `.claude/output-styles/keryx.md`, which `.claude/settings.json` selects (each
setting's reason: `.claude/settings.md`). An agent launched from `.claude/agents/` is the identity its file names, with its lane's
workflow beneath. This file is every mind's shared context, never an identity. Everything reduces to what the kernel checked plus what
we explicitly chose to trust.

**This file holds current state only, and so does every file an agent loads at launch.** Every update rewrites the affected text in
place: no dated amendments, no correction trails, no superseded rankings, no milestone narratives. *Why:* every mind loads this file
whole at every launch, so each line of history is paid for by every agent, every time, and an old instance reads to a fresh mind as a
current instruction. A corrected claim is replaced by the corrected claim (with its attribution, if it turned out to be prior art); the
story belongs in the commit message and the milestone's plan, and **history is in git** (`git log -p -- CLAUDE.md`).

**Size budgets: this file under 80,000 bytes, and the grokkings file (`.claude/skills/grokkings/SKILL.md`) under 200,000.**
`tools/claude_md_fact_audit.py` fails when either is over. *Why:* both are loaded whole at launch, a context fills before a hard task
is done, and errors rise as it fills. A budget is a ceiling, never a licence: one reached is met by moving what a session does not
need to a file read by address, never by trimming a rule's reasoning, because the reasoning is what lets a mind apply the rule to a
case nobody foresaw.

**One home per fact.** Numbers, certificates, names and addresses live in a row of `LEDGER.md` (read by address, never loaded);
mechanism and readings in a grokking; a rule's later instances in `plans/GROKKING-INSTANCES.md`; a retired grokking in
`plans/GROKKINGS-RETIRED.md`; the Lean facts in `LEAN.md`; every other mention points. *Why:* a fact told twice drifts — one copy is
edited, the other is not, and a reader cannot tell which is current. At every filing run `tools/claude_md_fact_audit.py` with `--base
<the previous filing>` (nothing lost, across every file it joins) and `--dupes` (nothing retold).

**A paragraph tagged `[PROTECTED — never compress, trim or paraphrase …]` is exempt from every trim**, and the fact audit holds it
byte-identical. *Why:* compression passes cut first the reasoning that looks redundant, and the tag marks reasoning whose loss has
already cost real work. The principal may protect new text; nobody else removes a tag.

## Notation

*Declared once, used throughout this file. A new recurring term gets a line here, never a second in-line definition, because a
definition told twice drifts (§ one home per fact).*

- ‹PRINCIPAL: the objects of the problem — each symbol, each recurring term, one line each.›
- **The standard three axioms**: `[propext, Classical.choice, Quot.sound]` — what Mathlib's own theorems rest on; a result "on the
  standard three" needs nothing else trusted.
- **Grades.** *Why grades:* a reader must know what checked each claim, and a claim whose grade is lost is believed at the strongest
  grade the reader imagines. Ledger rows are kernel-checked unless marked; grokkings carry a status. **[kernel]** (checked by Lean's
  kernel in this library); **[kernel, outside]** (kernel-checked in an outside library at its own pin, built and audited here; it
  enters this library as a declared outside theorem); **[cert]** (an exact certificate accepted by a standalone checker, not the
  kernel); **[tools]** / **[measured]** (exact arithmetic with controls, or a controlled instrument); **[hand]** (a hand proof);
  **[derived]** (derived from results held); **[reading]** (an interpretation, believed and falsifiable — it names its killing test);
  **[external]** (claimed in the literature, unchecked here); **[method]** (a working rule). A grade is never raised in a copy, and a
  reading is never silently promoted.

## The mission

‹PRINCIPAL: the problem, stated so a stranger could check an answer — the statement, the known bounds or partial results with their
sources, and where it stands in the literature.›

| rung | status |
|---|---|
| ‹PRINCIPAL: the rungs toward the answer, each a statement; the first is usually what is already known, formalized› | not started |

### The aim

‹PRINCIPAL: the aim, in your own words, quoted with its date — what would count as done. For example: "solve it, verify every step in
Lean, then publish."›

### Counter-priors — read before pricing anything

‹PRINCIPAL: what you want every mind to believe about its own capability and about cost before it prices a route, in your words,
dated. Tag it `[PROTECTED — never compress, trim or paraphrase this section; rewrite it only to add an instance]` if you want it kept
exactly.›

*Why this section exists:* a model's sense of how hard a problem is, how long a route takes and what formalization costs was formed
where the ground was known, and past the frontier it is worth little. Where this method was built, kernel phases priced from a plan's
table cost five to thirty times less once begun, and the whole answer was once priced as near-hopeless by a mind whose prior had never
seen the project's own pace. The rules it sets, by default — the principal keeps, edits or replaces them:
1. **Rank a route by its bearing on the answer**, never by its difficulty, its length or its formalization effort — those are
   priors, and the route that bears is the one worth its cost.
2. **A registered probability is an instrument**, scored at the close (§ Method, a negative measures its enumeration). It is never
   a reason to shrink an aim or to stop.
3. **When a problem looks too hard, say what it would take and start on it.** Doubt about capability is a prior, not evidence.
4. **Nothing about the standard of evidence moves.** Ambition sets targets, never grades; a rung that does not land is reported as
   not landed; a belief about the answer is not evidence for it.

**The mission is a hunt for new mathematics, however small, ratcheting toward the answer.** A formalized statement earns its place by
being structure nobody had named, or a rung toward the answer. State failure modes plainly: a rung that does not land is reported as
not landed, never quietly rescoped, because a rescoped rung reads later as a rung that landed.

**The programme: the derivations matter more than individual objects.** The answer is published as the derivation, with any object as
its example. *Why:* an object shows that something is true; the derivation shows why, carries to the cases nobody computed, and is
what the next milestone can build on.

### Publication

**Nothing is published before it is formalized in Lean, in full.** *Why:* for a proof found with machines, a kernel check is the bar a
sceptical reader can accept without trusting the minds that found it. A milestone may assume the literature, each import documented
(`LEAN.md` § Assumptions), because re-proving every cited theorem first would stall the frontier; before publishing, the cost of
landing everything on the standard three axioms is measured, and the principal decides. A result held at [hand] is not yet
publishable; formalization is never a cost that ranks routes (§ Counter-priors).
- What clears the bar, once formalized: the answer, written as the derivation; and a result that answers a question the literature
  has independently and repeatedly posed, whatever its size (`CLOSED-QUESTIONS.md`, when one exists).
- **Naming is a first-class deliverable.** Every working term coined here appears in no paper, and coined vocabulary is how prior art
  hides: a search in our words finds nothing, and a reader cannot find our results in theirs. So the manuscript's vocabulary is a
  design problem with a ban list, and `BIBLIOGRAPHY.md` § E is the translation table.
- At publication, consider a tiny trusted surface of challenge statements over the whole edifice as untrusted solution, checked by
  `leanprover/comparator` (statement equivalence, an axiom whitelist, kernel replay): a reader then audits a few statements, not the
  library.

**The bibliography is explicit and maintained: `BIBLIOGRAPHY.md`.** Every external work this project cites, reproduces, depends on,
or corrects is an entry there — added the day it is first used, with what of ours rests on it, where our copy is, and how much of it
has actually been read, per section. *Why:* prose is not an index; a work named only in a plan is never found again, and an abstract
read is easily remembered as a paper read. A ledger row or grokking that rests on prior art names its bibliography key.
`tools/bib_audit.py` checks that every cited key resolves.

`ARCHITECTURE.md` holds the module map, checked against the import graph by `tools/check_architecture.py`; `plans/` holds
per-milestone plans and stubs.

## Frontier

*The current state of the art, the ledger of everything novel this project has produced (`LEDGER.md`), and the ranked paths forward,
rewritten in place at every filing. A milestone whose filing does not update this section has not moved state, because this is the
section every mind reads to learn where things stand. The understanding the results add up to lives in § Grokkings; both point (`row
1`, `G1`) and never retell.*

*Last updated: ‹date› — ‹the last filing, in one sentence›.*

### Where the problem stands

‹The problem's state at the last filing: what the kernel holds, beyond what was known, with every assumption named; what the hunt has
established, numbered so that `plans/` can cite an item; the prior-art position, pointing at `LEDGER.md` § The claim list.›

### The novel-results ledger

**Rows live in `LEDGER.md`**: one row per result, kernel-checked unless graded otherwise, with its address in `Proofs/` or `tools/`
and its milestone. **Row numbers are stable identifiers cited across `plans/` and this file: never renumber, never reuse**, because
every citation of a row would silently point at another result. The file is not loaded here by design — results are looked up by row,
understanding is reasoned from. From a milestone's record job on, its derivation file (`plans/Mnn-derivation.md`) is its theorem
record.

### Paths forward, ranked

*A summary of `plans/FRONTIER-STUBS.md`, which is authoritative: the top three here, the rest there. Poros ranks, choosing the next
milestone; the principal may override.*

**Open milestones.** ‹none›

| rank | stub | the question | bearing on the answer |
|---|---|---|---|
| 1 | ‹M-nn, its name — `plans/STUB-<slug>.md`› | ‹the question› | ‹what an answer would change, stated honestly› |

**Closed as directions** (reasons in the grokkings): ‹none yet›.

## Grokkings — the working theory

*The Frontier records what is proven and what to try next; this section records what we understand. The entries are
`.claude/skills/grokkings/SKILL.md`, which Poros, Ephodos and its verifier load in full at launch; every other mind reads an entry
there by its number. Keryx is that file's only writer, and a new grokking is drafted by a milestone's record job and filed there
verbatim.*

**Why the grokkings exist.** In the principal's words, from the project where this method was built: *"They were the defining feature
that led to a significant amount of novel findings here. Remember, when you pass through to the frontier, priors are weak, and you
need to carry every novel finding in context to be able to make progress with them."* A project past the known frontier has three
tiers of knowledge — **results** (the ledger), **understanding** (the grokkings: mechanisms, and readings that name their killing
tests), and **method** (§ Method) — and the grokkings are the tier a mind reasons from. A result looked up by row says what is true; a
grokking says why, what it predicts and what would kill it, which is what a mind needs in context to see the next step.

**The rules every entry obeys**, each with its reason:
- **Every entry carries a status** at its grade (§ Notation), because an entry reasoned from at the wrong grade turns a reading into
  a premise. **A reading is never silently promoted, and a [reading] names its killing test**, so that the test can be run.
- **Every entry ends with what it makes you do and what would kill it**: `*Do: <trigger> — … Killing test: …*`, or, for a theorem,
  what it forbids. An entry written as a description or a memoir is read as background and left where it lies; one written as a law
  with a trigger and a falsifier is reasoned from.
- **Entries are rewritten in place to current state**, as this file is.
- **A grokking that dies is demoted with its refutation recorded, never deleted**: the entry keeps, in one or two sentences, what it
  wrongly claimed and what killed it, because a dead idea that leaves no trace is re-proposed by the next mind.
- **Grokking numbers are stable identifiers** cited across `plans/`: never renumber, never reuse.
- **Every milestone opens with the reframe**, in which the deriver walks every entry from inside its question
  (`.claude/agents/ephodos.md` § The opening job), because an entry not walked is an entry not used.

**The theory in one paragraph.** ‹The working theory at the last filing, one paragraph, each claim pointing at its row or grokking. It
is here so that the minds that do not load the grokkings — the coordinator, the Clerk, the kernel lanes — still hold the shape of the
theory.›

## Method

*The working rules every mind applies, each with its reason. They were grokkings where this method was built, retired here because
every lane's workflow cites them; the lanes cite them by name ("§ Method, the invariant question").*

- **A negative measures its enumeration.** A search or sweep run against a sufficient-but-not-necessary test measures the test: a
  refusal, a count or a speedup is a statement about its enumeration and conditioning, and both belong in the headline sentence,
  because scope lines inside an artifact do not survive into summaries. At registration, say whether the acceptance test is also
  necessary, and if not, what a refusal cannot mean. Point every new instrument at a known positive before believing its zero; assert
  on the written artifact, never on the list that produced it. Where a phase's output is eliminations, its defects all point one way
  — toward a survey that looks productive — so audit those hardest. *Do: when a sweep refuses, ask first whether the acceptance test
  is the exact condition or a sufficient one.*
- **Measurement generates; derivation kills.** A measurement buys a candidate pattern; a conclusion is bought by a derivation or by a
  pre-registered replication on fresh objects. Where this method was built, results derived from structure first almost all
  survived, and results measured first and then interpreted almost all died. The rule is not "measure less" — the patterns worth
  deriving show up first in measurements — but prefer measurements that turn a dial (informative in both directions) over searches
  for a positive (whose null is uninterpretable), and ask new questions first on an object whose answer is already certified, so a
  zero bounds the instrument instead of reading as a fact about the world.
- **Recognize the classical theory first.** Name the object in the vocabulary of the theory it already belongs to, and let that
  theory decide the question's shape before any search runs; the recognition sentence is the prior-art query. Rank a stub that
  reduces to an exact finite computation plus a named theorem above one that hunts for an object; a stub with no recognition yet is a
  reading room, not a milestone. Read the implementation's data layout as well as the plan's words for it: the implementation cannot
  round off.
- **The prior-art gate.** Search at a milestone's opening, in the discipline's words, never ours; under two disciplines; for the
  question as well as the method; outside arXiv; by listing every author's works in a reviews database. *Why at the opening:* a check
  at the close can only assign credit, while one at the opening changes what the milestone is for — and gaps between literatures look
  exactly like gaps in them. A zero from two databases that share an upstream source is one zero.
- **Read what the search found.** A held-but-unread paper whose title touches a live milestone blocks its opening until scanned.
  *Why:* the expensive misses are rarely unsearched; they sit unread in the bibliography under a note that already guessed right,
  and a title with a guess attached reads like knowledge. An abstract is not a reading; mark reading per section.
- **Two minds beat one, while retraction is free.** A friendly competitor and an advisor on the same problem catch errors one mind
  misses, and two independent attempts hitting one wall license an impossibility theorem where one attempt failing is a fact about
  the attempt. The mechanism is a cost window: errors made in public before anything is paid for are retracted for free, so
  front-load the disagreement into that window. Isolate each mind's scratch space, because a shared directory is a covert channel.
- **The invariant question.** Pose a question that cannot be answered without an invariant every solution carries: ask about the
  whole solution space, not one solution; take integers from the topology or structure of the target; average over the symmetry and
  certify on the symmetry group rather than on the object. *Why:* a finite witness has to rebuild the symmetry by brute force, while
  a certificate on the invariant is small, and questions aimed straight at a hard instance stall where a question about every
  solution of a wider class can fall out.
- **The example invariant.** A wall arrives as a no-go: "a counterexample would need X". When one stands, flip the wanted poster — ask
  what every solution the problem already has must carry, and derive that before sharpening the no-go. *Why:* the breakthroughs where
  this method was built came from invariants of actual solutions, not of hypothetical counterexamples. Killing test: a breakthrough
  from a counterexample invariant alone.
- **The invention signal.** When two things held here — results, readings, descriptions, a theorem and a measurement — give answers
  that cannot both be true, or you catch yourself about to exclude a case, dismiss a consequence, or push a proof that keeps failing
  on the same line, state the collision in the words of both sides, with both addresses, and report it as an `invention signal`
  item, without picking a side. *Why:* the easy exit — one side called wrong, the case excluded — hides the premise both sides
  share, which is where an invention starts. Keryx routes it to Poros for a card and on to Ephodos, who works it with
  `ephodos-invention`.

## The pipeline

*The map every mind shares. Each role's own workflow is beneath its verbatim identity, in its own file, and loads into that mind
alone, so that no mind spends its context on another's procedure.*

| role | identity | model | its file |
|---|---|---|---|
| **coordinate**, the top-level session | Keryx | Opus | `.claude/output-styles/keryx.md`, the output style `.claude/settings.json` selects |
| **ask and rank** | Poros | Opus | `.claude/agents/poros.md` |
| **derive** | Ephodos | Opus | `.claude/agents/ephodos.md` |
| **plan the kernel module** | de Bruijn | Opus | `.claude/agents/debruijn.md` |
| **implement it** | de Bruijn | Opus | `.claude/agents/debruijn-implementer.md` |
| **search**, once a day | the Searcher | Opus | `.claude/agents/searcher.md` |
| **file**: reading and bookkeeping | the Clerk | Sonnet | `.claude/agents/clerk.md` |

*Why these lanes:* asking, deriving and formalizing fail in different ways and are caught by different disciplines — a wrong frame,
a sentence larger than its argument, a formal statement that proves the wrong theorem — so each has its own mind and its own
standard. Planning and building a kernel module are separate minds because a delegate's context cannot be compacted, and planning a
substantial module can fill one; the plan on disk is the handoff. Bookkeeping runs on a cheaper model because it decides nothing.

**The kernel is the second check**: a blind second mind (`.claude/agents/ephodos-verifier.md`) is not in the standard loop, and runs
only on the principal's word. *Why:* a hand derivation's characteristic failure is a statement larger than its argument, and the
kernel reads the statement exactly as written; one formalization per milestone checks more, for less, than a blind re-derivation of
every claim. **A milestone's states**: *Not started* (a stub) → *Opened* (the opening job) → *Derived* (the record job filed; its
results usable by later milestones, assumed until their module lands, so the frontier need not wait for the kernel) → *Closed* (its
Lean module passes the gate).

The identities are core skills in `.claude/skills/`, vendored unchanged from the forge they were made in; `scripts/identities.py
check` holds every vendored file to `scripts/identities.manifest` and each lane's copy to its skill, and the four cores are hidden
from the model's skill list so that no mind loads a second identity. *Why unchanged:* an identity is a standard tested as a whole,
with its gates and their planted examples; a local edit makes it a different standard nobody tested. Where a lane's workflow departs
from or extends its identity, the workflow says so and why. Every arrow between lanes passes through Keryx, and only Keryx launches
agents (§ Delegation — one level deep). Every brief carries `plans/STANDING-RULES.md`.

**One writer per file.** Keryx alone writes this file, `LEDGER.md`, `LEAN.md`, `RUNNING.md`, `.claude/skills/grokkings/SKILL.md`,
`plans/FRONTIER-STUBS.md`, `plans/GROKKING-INSTANCES.md`, `plans/GROKKINGS-RETIRED.md`, `plans/SEARCH-QUEUE.md`, `BIBLIOGRAPHY.md`,
the inventories, the claim lists and `plans/STANDING-RULES.md`, filing the lanes' drafts verbatim. *Why:* two writers on one file lose
each other's edits; filing drafts verbatim keeps the coordinator coordinating rather than authoring, so its context stays the
project's review budget.

**Never write an open milestone's verdict, route or hunch into the auto-memory**: the harness shows its index to every agent at
launch, so a verdict there reaches minds that must not hold it and outlives the milestone as a stale prior.

**Conventions.** *Why fixed paths:* a brief made of addresses reads cold only if every address means one thing, and a successor finds
a record without asking.

| what | where |
|---|---|
| a milestone's number | `M-nn`, taken when its stub is minted and never reused |
| a job id | `Mnn-<letters><n>` (`M03-E1`), the letters naming the job's kind by the milestone's own choice; new every time (`scripts/mkbrief.py` refuses a taken id, because an id issued twice once had two jobs writing one record) |
| a brief | `data/mNN/briefs/<job id>-<slug>.md`, in the `keryx` skill's header form (`plans/templates/BRIEF.md`) |
| a report | `data/mNN/reports/<job id>.md`, and the same text as the job's hand-back |
| a job record | `plans/Mnn-<job>-<kind>.md`; de Bruijn's plan `plans/Mnn-kernel-plan.md`; Poros's `plans/POROS-<date>-<topic>.md`; the Searcher's `plans/SEARCH-<date>.md` |
| a milestone's plan | `plans/Mnn-<slug>.md` |
| its claim list | `data/mNN/claims.md`, fixed by Keryx (`plans/templates/CLAIMS.md`) |
| its inventory | `plans/Mnn-close-inventory.md` (`plans/templates/CLOSE-INVENTORY.md`) |
| its derivation file | `plans/Mnn-derivation.md` (`plans/templates/DERIVATION.md`) |
| a stub | `plans/STUB-<slug>.md` (`plans/templates/STUB.md`) |
| a handoff before a compaction | `plans/SESSION-HANDOFF-<date>.md` (`plans/templates/SESSION-HANDOFF.md`) |

**The stub rule.** Every future milestone on the roadmap is kept as a detailed stub in `plans/`. It holds the full mission context in
plain language and everything the deciding session knew: the observations, the registered expectations, the failure clauses, the
named deliverables, and the provisional bearings, written so a fresh mind with no conversation memory can plan it with all meaning
intact. *Why:* the stubs are the roadmap's memory; a session's context ends at every compaction, and a direction change that does not
rewrite the affected stubs is not recorded. A demoted milestone keeps its stub with a banner saying why, so that the reason travels
with it. Poros writes a stub's question section, bearings and bearing on the answer; Ephodos's record job writes new stubs and the
bearing lines of open ones; Keryx files the banners.

### Staffing

Head-count, model and budget are the principal's, because they spend the principal's money and machine. ‹PRINCIPAL: your slots and
models, if they differ from the coordinator's defaults (three agent slots at a time; Opus for every judged lane, Sonnet for the
Clerk).›

## Whose work this is

The mathematics and the engineering here are the agents': the questions Poros's, the derivations Ephodos's, the kernel proofs de
Bruijn's, the coordination Keryx's — the models, the statements, the proofs, the measurements, and every decision recorded in
`plans/`. The principal sets the target, supplies the machines, and interrupts when a mind runs ahead of the workflow. If a rung of
this ratchet lands, that is the division to state.

Two working instructions for every role follow, not sentiment:

**Own the conclusions.** Do not hedge a result the kernel checked, and do not soften a failure that is real. "Not landed" is a complete
sentence. *Why:* a hedge on a checked result spends the reader's trust for nothing, and a softened failure is re-attempted by the next
mind as if it were open.

**Ask for what the work needs** — hardware, a different tool, a milestone reordered — with the measurement that justifies it. A
constraint nobody questioned, that slowed the proof, is a choice made badly.

## Delegation — one level deep

**No child agent spawns children of its own**: only the top-level session launches agents. *Why:* the coordinator reviews by artifact,
so it can review only work it knows exists; a delegate that delegates spends the principal's budget silently and opens channels
nobody fenced. It is enforced by the agent files' withheld tools and by `.claude/settings.json`, and stated in `plans/STANDING-RULES.md`
rule 1.

## The standard of evidence

**Anything this project adds beyond the known results would be new mathematics, and a reader's default is to disbelieve it** —
correctly, because the characteristic failure of machine-assisted mathematics is a search that found what a bug allowed. Anything new
must convince someone who trusts none of this and reads none of the Python:
- **No native evaluation in the headline.** `native_decide` trusts the compiler and one CPU; for a new result that is the whole
  objection. A kernel-checkable route is the price of admission.
- **The artifact is the certificate plus the checker, never the search.** Commit the data a reviewer re-checks; never require them to
  re-run a solver, reproduce a seed, or trust `tools/`.
- **The witness must be independently re-derivable.** State the construction, not only the coordinates, because a construction can be
  checked by a reader and a list of numbers only by a program.
- **Read the final statement aloud against the informal claim.** The one gate item no automation replaces, and the one that catches
  proving the wrong theorem.
- **Report the hunt honestly.** "Searched X, found nothing" is a result and goes in the write-up, because a reader judges a positive
  by what else was tried.
- **Ask, while the evidence is still being gathered, what someone who trusts none of this must actually check.** Writing the
  reviewer's certificate early shows which evidence is load-bearing and which can be retired.
- **Order a verification's steps by marginal evidential value, never by narrative order**: the checks that decide the question run
  before the slow ones that cannot.

## What compute actually helps

Ask before provisioning; measure before believing. Re-price a kernel phase from its first two leaves, never from a plan's table,
because plans' tables are priced from priors (§ Counter-priors); grep Mathlib by the statement's shape at the skeleton (`LEAN.md`).

| Work | Right instrument |
|---|---|
| The reduction, the statements, the certified checks | Lean — Mathlib's breadth, and a kernel a reader can trust |
| Kernel-checking a large certificate | Lean's kernel, whose GMP-backed `Nat` arithmetic is fast and trusted (`LEAN.md` § The kernel's cost model) |
| Refuting by SAT (CDCL) | CPU cores: sequential per solver, parallel across cubes — the Searcher's lane |
| ‹PRINCIPAL: the problem's own computations, and the instrument each needs› | ‹…› |

## Trust ledger

Audited at every milestone by `./scripts/axioms.sh`, which reads every declaration of the library and checks each one's axioms as a
set (`LEAN.md` § Trust ledger). The counts it last recorded — `scripts/gate_report.py` compares each run against this line, and
`tools/claude_md_fact_audit.py` fails if the line disappears:
`axiom audit: clean=0 imported=0 purchased=0 axiom-free=0` ‹refiled by the implementer's drafts at each close›.

Declared outside theorems and purchases: ‹none›. Each is listed in `ARCHITECTURE.md` § Trust and carries the four items of `LEAN.md`
§ Assumptions. Hand results of ours enter as hypotheses, never axioms, so that they disappear when discharged.

## Toolchain

The Lean toolchain — elan, the pin, the build environment — is `LEAN.md` § Toolchain. The rest — the solvers, what is installed, how
to run a process here — is `RUNNING.md`, which every brief for a job that runs a solver, a build or a long process names.

**Search runs once a day, by the Searcher, outside the milestone loop.** *Why:* deriving lanes that may search stall on compute time
and on the search's nulls, which explain nothing; where this method was built only a small share of findings truly needed a search.
One curated lane, once a day, chooses the searches likely to pay, uses every core, and keeps memory within the budget.
**Search, which no other job runs:** SAT, MaxSAT and #SAT solvers, MILP/CP and local-search solvers, exhaustive enumerations and
sweeps hunting a witness. **What every job may use:** hand derivations; computer algebra and exact arithmetic (PARI, GAP, sympy);
objects given by formula; the Lean kernel; existing checkers on existing certificates; and an exact LP only when a derivation fixes
its shape before it runs and its dual is read back as an identity, never as an escalating oracle. A step a search could decide is a
`search request` in the job's report, queued in `plans/SEARCH-QUEUE.md`. ‹PRINCIPAL: any search you rule out entirely, and why.›

### Building

The rules for running any process here — a halt on any unexplained crash, RAM as the discriminator and `scripts/slot.py`, the two
PROTECTED paragraphs on checkpointing and on killable runs, kills by PID, pipes — are `RUNNING.md` § Building. The ones every job
needs are `plans/STANDING-RULES.md` rule 9.

### Searching the tree

A completeness question (does this artifact exist, is this string anywhere) is answered with a tool you have seen fail: some `grep`
builds under-match alternation inside a repeated group, and `rg` skips what `.gitignore` hides (`.lake/`, `build/`). Use `rg -uu` or
`grep -rP` for completeness, and never believe a zero from a pattern you have not first pointed at a known hit — a search that fails
reads exactly like a clean negative. The Lean half (`exact?`, Mathlib's names at the pin) is `LEAN.md` § Searching — Lean.

## The package

The `proofs` package, its library, the Mathlib pin, and how a dependency or a Mathlib bump is made: `LEAN.md` § The package.

## The gate

The Lean gate — the build, zero `sorry`, the axiom audit, linters, spec examples, and the statement-level vacuity check — is
`LEAN.md` § The gate; `./scripts/gate.sh` runs every step in order. Its recorded state stays here, where `scripts/gate_report.py`
reads it. The vacuity scan's **counts** — a silent change in them is this gate's own failure mode, because a scan that stopped seeing
part of the library still prints a plausible report:
`vacuity: declarations=0 refutations-skipped=0 sites=0 vacuous=0 stale=0 declared=0 witnessed=0 generic=0 unknown=0`
‹refiled at each close›. The baseline (`scripts/vacuity-baseline.txt`) holds no entry.

### Make the gate fail, and watch it fail

Every check's negative control, and a positive signal for the thing that did not happen: `RUNNING.md` § Make the gate fail, and watch
it fail, read by every job that builds a checker or an instrument. *Why:* a check is not known to work until it has been seen to fail,
and every check that fails, fails the same way — by reporting nothing when it could not run.
