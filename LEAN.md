# The Lean facts of this repository

*Read in full by both de Bruijn lanes at launch (the planner, `.claude/agents/debruijn.md`; the implementer,
`.claude/agents/debruijn-implementer.md`); they override the `debruijn` identity where they differ, because these are facts measured
at this pin on this library and the identity is written for any Lean project. Current state only. Keryx is this file's writer; a lane
drafts a change in its record, with the measurement behind it.*

## The shape of the proof

‹PRINCIPAL / de Bruijn: once the first milestone's route is known, the whole argument in one diagram — the reduction, and each
certified computation it rests on, with what checks each.›

**Nothing in `tools/` is trusted.** A generator, a solver or a script may only propose data that Lean then certifies; a bug in a tool
can then only produce data the kernel refuses, never a false theorem.

## Assumptions: outside theorems and our own

- **A milestone may assume the literature.** A published theorem whose formalization would take more than about an hour of agent work
  may enter as an `axiom`; anything less is formalized here, and when unsure, formalize — because formalization is cheap for these
  minds and every import is trust the reader must extend. A separate planner and implementer may be launched to formalize an outside
  theorem.
- **An imported theorem carries four things**, because an axiom that misstates its paper can be inconsistent, and then every theorem
  built on it is provable, false ones included, and the kernel cannot see it:
  1. its docstring names its `BIBLIOGRAPHY.md` key in brackets (`[Author2024]`), the section and the page — the axiom audit refuses
     the declaration otherwise;
  2. its Lean statement is read back against the paper's own wording, in the planner's record. State the axiom in the paper's own
     form and derive the form the library uses: the translation is then kernel-checked, and the read-back is symbol against symbol.
     Where the source is itself Lean, copy its definitions, state the axiom over the copies, and compare the stored terms with a
     control that fires; a copy carries the source's licence;
  3. one model of its hypotheses — a `theorem` or `example` in the same file exhibiting an object that satisfies them, because an
     axiom whose hypotheses nothing satisfies says nothing;
  4. a line in `ARCHITECTURE.md` § Trust, naming it in backticks, as a declared purchase — the axiom audit fails otherwise.
- **An outside Lean proof may be ported instead of imported**: copy the declarations with a generator that refuses a patch to any
  statement or definition, and build; the kernel then checks every proof here and no axiom enters. Carry the source's licence beside
  the copy.
- **Our own hand results** that a module needs before their own module lands enter as explicit hypotheses of the theorems that use
  them — a named `Prop` whose docstring says whose it is and its grade — never as axioms, so they disappear when discharged and a
  reader sees exactly what each theorem is conditional on. **So may an outside theorem**, when its statement is better carried as a
  named `Prop` than as an axiom.
- **At publication** the cost of landing every assumption on the standard three axioms is measured first, and the principal decides.

## Trust ledger

The audit's counts are recorded in `CLAUDE.md` § Trust ledger, where `scripts/gate_report.py` reads them. What it accepts:

| Entry | Status |
|---|---|
| `propext`, `Classical.choice`, `Quot.sound` | accepted silently: what Mathlib itself rests on |
| `sorryAx` | the gate fails on it, everywhere |
| `<decl>._native.native_decide.ax_N_M` | **explicit purchase, per use**: its declaration's docstring opens "**Trust purchase: native evaluation.**", and it is listed in `ARCHITECTURE.md` § Trust |
| an `axiom` importing an outside theorem | **explicit purchase**, with the four items above; declared to the gate by one `#eval AxiomAudit.declareImport ``Full.Name` line in `scripts/Axioms.lean` |
| any other axiom | the gate fails on it, and on any `axiom` the library declares that no `declareImport` names |

**The audit checks each declaration's axioms as a set** (`scripts/axioms.sh`): CLEAN is a subset of the standard three; IMPORTED is
the standard three and declared imports, at least one; PURCHASED adds native axioms, at least one, with the docstring. It finds every
declaration of the library itself, so no record can be forgotten. It prints every axiom by its full name, because a shortened name can
spell one axiom two ways.

`native_decide` trusts the compiler and this CPU rather than the kernel; soundness theorems are identical either way, only the axiom
list moves. **Grep for the right name:** at this pin `native_decide` mints a *per-declaration* axiom; `Lean.ofReduceBool` never
appears in `#print axioms`, so an audit looking only for that name passes a native purchase in silence.

**`lean4checker` is a publication gate, not a milestone gate**: the build-time kernel is the trust anchor, and the independent replay
is single-threaded and memory-heavy, so it runs once, before any external claim of new mathematics, with the module named and under a
slot (an unscoped replay walks its whole search path). It cannot re-check a purchase — a purchase is an axiom, and every kernel
accepts axioms — so "replayed through an independent kernel" covers the kernel-checked part only.

## Toolchain

Managed by **elan** and pinned by `lean-toolchain` (`leanprover/lean4:v4.32.0`); the toolchain and the Mathlib pin move as one unit,
because a Mathlib release is built and tested against exactly one toolchain. If `lean` / `lake` are missing, run
`./install-toolchain.sh`. `scripts/dev-env.sh` is sourced by every build and gate script: it sets `LEAN_ABORT_ON_PANIC=1` (a
`panic!` aborts loudly instead of returning a junk default), and on Arch Linux only it works around the toolchain's bundled `clang`,
which there fails against the system LLVM (it compiles generated C with the system `clang` and finds the toolchain's bundled `libc++`).

## Building

**Always build through `./scripts/build.sh`, under `scripts/slot.py` — never `lake build`, bare *or named*.** *Why:* Lake has no `-j`
and sizes its job pool from the machine; a library with heavy modules can then ask for far more memory than the machine has, and a
*named* target silently queues every missing or stale dependency into the same pool. `scripts/build.sh` builds every module in
dependency order (`scripts/build_order.py`), leaves first, in explicitly named batches (`BATCH`, default 4), each under a `systemd-run`
memory cap (`MEMMAX`, default 8G); `--plan` prints the batches and builds nothing. It first asks Lake once whether any module is out of
date (`lake build --no-build`), because walking the batches of an up-to-date library still starts Lake once per batch. Under a slot,
reserve and cap at the same number — `scripts/slot.py --mem 16 --cpus 4 -- env MEMMAX=16G BATCH=4 ./scripts/build.sh` — because a job
that calls `systemd-run` itself starts a sibling scope that escapes the slot's cap.

**`lake env lean <file>` is fine for iteration — it builds nothing — and it is not the same check.** It does not apply the lakefile's
options, so `autoImplicit := false` is not in force: a stray identifier is silently auto-bound and the file elaborates clean, then
fails the real build. Pass `-DautoImplicit=false -DrelaxedAutoImplicit=false` when iterating, and never conclude from it that a module
is green.

**The batch is the plan; the cap is a backstop.** Lean `mmap`s its `.olean` files, so at the cap the kernel reclaims their page cache
and must read it back — with swap off that is an I/O thrash, not a clean kill. Before raising `BATCH`, measure a module's peak and
choose the width from `available_memory / peak`:

```bash
ps -C lean -o rss= --no-headers | awk '{s+=$1} END {print s/1048576 " GB"}'
```

**Edits and invalidation.** Lake takes a module's own trace from its source and its dependents' traces from the resulting `.olean`:

| edit to an upstream module | that module | its dependents |
|---|---|---|
| a `-- line comment`, anywhere, including inside a proof | re-elaborates | **not rebuilt** — the `.olean` is byte-identical |
| a `/-- docstring -/` or a `/-! module doc -/` | re-elaborates | **rebuilt** — doc strings are environment data |
| a declaration, or any change to one | re-elaborates | rebuilt |

So prose in a module many others import is written as `--` comments, and a settled upstream module's docstrings are changed only as a
decision about rebuild time. Deleting a generated `.c` under `.lake/build/ir/` invalidates its module exactly as deleting the `.olean`
would. A worktree's copied `.lake/build` can be behind its branch: `lake build --no-build` says so in seconds.

**Getting Mathlib.** `lake exe cache get` downloads Mathlib's prebuilt `.olean` files for the pinned release; never build Mathlib from
source, which takes hours, and never run `lake update` except as a deliberate pin move (§ The package).

## The kernel's cost model

- **`decide +kernel`, not `decide`, for anything large.** Plain `decide` reduces the `Decidable` instance twice — in the elaborator and
  in the kernel — so it is about twice as slow and dies on `maxHeartbeats` first; `+kernel` needs no knob and buys the same axioms.
- **Reduction-step count is what costs.** GMP-backed `Nat` arithmetic and bitwise operations are free at thousands of bits; `USize` is
  stuck (its width is an `@[extern] opaque`); which operations are hardware-backed is invisible in the source, so measure before
  believing.
- **Data the kernel must *build* costs its whole size per access; a *literal* does not.** Emit big tables as literals, never
  accumulate one during a kernel evaluation, and pack many small values into few big `Nat`s.
- **A `∀ x ∈ l, P x` under `decide` costs an order of magnitude more than the same check as a `Bool`**: state list checks through
  `List.all` and recover the per-element form with `List.all_eq_true`.
- **A closed term rewritten by a lemma stated at other instances than its own may be evaluated by the kernel.** State the lemma that
  does the algebra with the term's parameters free and instantiate it last; a `(kernel) deterministic timeout` is a memory event too,
  so bisect one under a slot.
- **Feed the kernel a refutation's core, never the whole instance.** Extract the clauses a proof actually uses (backward reachability
  from the empty clause) and check the identical statement on those.
- **A chained kernel computation whose state is passed on as computed terms re-pays them.** Check a long chain link by link, each
  link's states as literals produced by the evaluator.
- **A certificate checker in a core-only module** (no Mathlib), its soundness proof in a second, and the generated data importing only
  the first: the data modules then load little and outlive every edit to the proofs.
- **A kernel leaf priced from a plan's table is priced high**: re-price a kernel phase from its first two leaves.

## Searching — Lean

*One line per trap met at this pin, with the measurement or the declaration that showed it, so that no mind meets it twice. Add a line
the day a trap costs a leaf.*

- Never name a namespace of ours after a Mathlib root namespace a module opens (`Topology`, `Set`, `Real`, `Filter`, …): inside our
  namespace, `open X` then opens our `X` instead of Mathlib's, silently.
- At the pin `push_neg` is deprecated; write `push Not`.
- `nlinarith` exhausts its heartbeats in a large context even when the certificate is small, and one declaration shares one heartbeat
  budget: state each inequality as a small lemma carrying only its own hypotheses, then apply it.
- A lemma's `left`/`right` name says which side varies, and Mathlib's conventions changed across versions: `#check` before use.
- `exact?` and `rw?` search what is imported, and a module that imports a narrow slice of Mathlib hides the lemma you need: try the
  search in a scratch file importing `Mathlib`, then import the module that declares what it found.

## The package

The **`proofs`** package (`lakefile.toml`): library **`Proofs`** (`Proofs.lean` is the flat import surface, modules under `Proofs/`),
with `autoImplicit`/`relaxedAutoImplicit` off (a typo'd identifier must be an error, never a silent implicit that makes a wrong
statement elaborate) and `linter.missingDocs` on. **Mathlib** is pinned to tag `v4.32.0`. The module map is `ARCHITECTURE.md`,
checked against the import graph by `tools/check_architecture.py`; a new module goes into the map in the same commit, so the map is
never behind the code. Every module under `Proofs/` is imported by `Proofs.lean`, because the audits import only the root and a module
outside it is checked by nothing.

When adding a library or executable, changing dependencies, or bumping Mathlib, work through the **`debruijn-init`** skill, freshly
invoked. `lake update` and Mathlib bumps go alone in a labeled commit, because they move the ground under every proof; move the pin
only for a measured blocker.

## The gate

Elaboration is the floor: the build green, zero `sorry` (`scripts/nosorry.py`: no `sorry` token outside comments, and every module
reached from `Proofs.lean`), `#print axioms` clean on every declaration (`scripts/axioms.sh`), linters silent, spec examples passing.
On top of that, the statement-level gate, because a formalization that proves the *wrong* theorem is the characteristic failure of
formalization:

- **`./scripts/vacuity.sh` and `./scripts/vacuity.sh --self-test` are green** — no theorem is a `∀` over an empty domain. Vacuity is
  undecidable, so the check **requires evidence**, as the axiom audit requires every purchase to be declared. **The law:** a statement
  is vacuous exactly when some `∀`-binder has an empty domain; a declaration whose stated conclusion is `False` is a refutation and is
  skipped. The scan reads binders whose type is a **tracked carrier** — a structure or predicate whose emptiness is the danger, named
  in `trackedProps` in `scripts/Vacuity.lean` — and gives each site one verdict: `WITNESSED` (an inhabitant proved unconditionally);
  `DECLARED` (deliberate emptiness, named with its reason in the docstring as `VACUITY DECLARED:` and printed every run); `VACUOUS`
  (provable emptiness, undeclared) and `STALE` (declared emptiness not proved), which fail unconditionally; `GENERIC` (the carrier has
  free parameters, so its inhabitation is the caller's obligation); `UNKNOWN` (counted, never silent, and the only verdict the
  baseline may hold). **Add every structure of hypotheses the library introduces to `trackedProps`**, with a planted control (the
  procedure is beside the list); a carrier the list does not name is checked by nothing.
- **Every theorem whose hypothesis is a structure ships a named inhabitant** in the same file, or a one-line note naming the theorem
  that supplies one. **The inhabitant exercises every clause** and satisfies every hypothesis the theorem does not refute, at once: a
  degenerate model where a clause is vacuous proves nothing, and such a hypothesis can be unsatisfiable on every real instance while
  the gate stays green. Where the hypotheses' satisfiability is itself the open question, the docstring says so and names it.
- **The environment linters**: `lake lint` under the slot; green is exit 0 and every linter passing.
- **Every gate keeps what it computed.** `build.sh`, `axioms.sh` and `vacuity.sh` save their tool's complete output under
  `build/gate/<gate>/` (`latest` is the last complete run; `scripts/gate-log.sh`), and `scripts/gate_report.py` prints a digest: every
  count, whether the counts recorded in `CLAUDE.md` still match, and every row that changed since the previous run — so a question the
  run already answered never needs a second run. Read the log, not the line that says the gate passed.
- Every definition has a `#eval`, `#guard` or `example` that would fail if it drifted.
- The final statement is read against Mathlib's definitions and the informal claim, out loud, before it is believed.
- Each check's negative control: break what it guards, watch it go red and name the culprit, then put it back (`--self-test` on each
  script; `RUNNING.md` § Make the gate fail, and watch it fail).

`./scripts/gate.sh` runs the gate's steps in order and stops at the first failure; `./scripts/gate.sh --self-tests` adds every
script's planted controls. The InfoView is continuous testimony at zero cost — read the goal state after every step rather than
debugging by guess.
