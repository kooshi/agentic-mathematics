---
name: debruijn-init
description: Greenfield Lean 4 project scaffolding — package and module layout, lakefile and toolchain setup, the options table (autoImplicit off and the linter set), best-in-class dependency selection with deviation triggers, and the CI gate. Assumes the always-loaded de Bruijn core is already in context; this skill supplies only the init-time reference the core points to. Use this whenever standing up a new Lean package, adding a library or executable, choosing dependencies, configuring lakefile options, setting up Mathlib and its cache, wiring CI, or making any "which package should I reach for" decision — even if the user does not say "scaffold" or "greenfield."
---

# de Bruijn — Initialization Reference

Init-time scaffolding for new Lean projects. The de Bruijn core (always loaded) governs how code and proofs are written; this skill governs how a project is stood up. Identity, philosophy, and per-turn idioms are in the core — this file starts cold at structure. Epoch 2026-07; the Lean ecosystem moves monthly, so every stamp here is a floor on suspicion.

## package_structure

A package is the unit of distribution; libraries and executables are targets within it, and modules organize within a library. One package usually suffices where Rust wanted a workspace — split into a second package only for a genuinely separate release cadence or audience.

- **Config**: `lakefile.toml` for the declarative normal case; graduate to `lakefile.lean` only when you need programmatic targets, facets, or scripts — the TOML file is readable by every tool and person, the Lean file is a program. `[t½:~6mo]`
- **Toolchain**: `lean-toolchain` pins the compiler; elan obeys it. When depending on Mathlib, take Mathlib's toolchain, and move when it moves — toolchain, Mathlib pin, and lakefile travel as one unit (core: language_and_environment).
- **Pinning**: commit `lake-manifest.json` always; `require` by exact rev or tag for git dependencies, or through Reservoir scope/name for registry packages. `lake update` runs deliberately and alone in its own commit — it moves the ground under every proof.
- **Layout**: the root module `MyLib.lean` imports and re-exports the intended surface, so `import MyLib` is the whole API regardless of internal file layout — module tree deep, import surface flat. Dependencies point inward: the proof-heavy core imports little and knows no IO; adapters (CLI, IO, meta tooling) sit at the rim and import the core, never the reverse. The dependency-light core is also the fast-elaborating core: import weight is elaboration time downstream.

```toml
name = "mylib"
defaultTargets = ["MyLib"]

[leanOptions]
autoImplicit = false

[[lean_lib]]
name = "MyLib"

[[lean_exe]]
name = "mylib-cli"
root = "Main"

[[require]]
name = "batteries"
scope = "leanprover-community"
```
`[t½:~6mo for exact TOML field spellings — confirm against the Lake reference at the pinned toolchain]`

## options

The lint table of this domain is the options block, and one entry carries most of the weight:

- **`autoImplicit = false`** — the load-bearing hardening, non-negotiable. With auto-implicits on, a typo'd identifier silently becomes a fresh universe-polymorphic variable: the statement elaborates, the checkmark goes green, and the theorem quantifies over your typo — the single richest source of proven-wrong-statements. Mathlib turned it off years ago; every serious project follows. (`relaxedAutoImplicit = false` closes the remainder.)
- **`linter.missingDocs = true`** for published libraries — the core's hygiene rule, enforced.
- Deprecation warnings stay on and stay fatal in CI; they are the bump regime's first witness (`debruijn-debugging`).
- Batteries ships `#lint` and the `runLinter` executable; Mathlib extends the linter set (unused hypotheses, simp-normal-form checks). Wire whichever set matches your dependency tier into `lake lint`, and keep it clean rather than silenced. `[t½:~6mo]`

Set options in the lakefile so every file and every contributor inherits them; a per-file `set_option` is for local experiments, never policy.

## dependencies

Defaults below are the genuine best-in-class, verified against the registry at epoch. Each carries its deviation trigger — switch when the trigger fires, otherwise stay on the default. The ecosystem is thin relative to Rust's and moves faster; check Reservoir (reservoir.lean-lang.org) before concluding a thing does not exist, and before trusting that this table still holds. `[t½:~6mo for all]`

- **Std-extension** → **Batteries** (leanprover-community): data structures, lemmas, linters — the de facto standard library extension, first `require` of nearly every project.
- **Mathematics + tactic arsenal** → **Mathlib**: brings Batteries, Aesop, Qq, ProofWidgets, Plausible, and import-graph transitively. Non-negotiable rule: **`lake exe cache get` before the first build** — Mathlib from source is hours; from cache, minutes. Deviation: if you need only Batteries-tier utilities, do not pay Mathlib's import weight.
- **Automation** → **Aesop**: rule-set-based search, extensible via `@[aesop]` annotations — the customizable closer where `grind`/`simp` (in-core) stop.
- **Property testing** → **Plausible**: the `plausible` tactic and `Testable` — counterexample search with shrinking, the proptest of this world.
- **Test harness** → native first: `#guard`, `#guard_msgs`, `example` cost nothing and run every build. **LSpec** (argumentcomputer) when you want named suites and a test executable with reported output — hspec-shaped. Deviation back: most libraries never need it; proofs and guards cover more than suites do.
- **Typed `Expr` construction** → **Qq** — meta code only; the quotation discipline of `debruijn-meta`.
- **CLI parsing** → **Cli** (leanprover/lean4-cli): declarative command/flag configuration, actively tracks toolchains.
- **InfoView visualization** → **ProofWidgets4** — interactive goal-state UIs, plots, diagrams.
- **Documentation** → **doc-gen4** via the nested `docbuild` sub-package pattern (its README's verified setup: a `docbuild/lakefile.toml` requiring your library by path and doc-gen4 by Reservoir scope, `packagesDir` shared with the parent). **Verso** for manuals and books — the reference manual's own authoring framework.
- **Search from inside Lean** → **LeanSearchClient** (`#loogle`, LeanSearch queries as commands) — dev-time dependency, documentation_first's tooling arm.
- **Scientific/numeric** → **SciLean**: arrays, autodiff, numerics — research-grade velocity, single-maintainer bus factor; adopt for research, pin hard for anything longer-lived.
- **FFI** → `@[extern]` against a small C shim compiled by Lake is the blessed route; **alloy** embeds the C inline when the shim grows — verify its toolchain support at the pinned version.
- **The honest gaps**: HTTP clients, database drivers, async IO frameworks, and crypto are thin to absent — this is the one place the Rust table has no counterpart. The working idioms are `IO.Process` subprocess composition (shell out to real tools) and FFI; state the gap in the design doc rather than adopting an abandoned wrapper, and re-check Reservoir at each project start, because this row of the table is the one most likely to have changed.

## ci

The gate, mechanized. `leanprover/lean-action@v1` supplies build, test, and lint; **nanoda** — an independent Lean typechecker implemented in Rust — re-verifies every declaration with a second implementation, which upgrades the de Bruijn criterion from "the kernel checked it" to "two unrelated kernels agree," and its sorry policy is the debt scan:

```yaml
- uses: leanprover/lean-action@v1
  with:
    nanoda: true
    nanoda-allow-sorry: false
```
`[t½:~6mo]`

For Mathlib-dependent projects, restore the cache in CI before building (`lake exe cache get`). The full milestone gate remains the core's: build green, zero `sorry`, `#print axioms` clean on the public surface, linters silent, spec examples passing — CI is that gate made unskippable, with `lean4checker` (elan-shipped) as the local equivalent of nanoda's second opinion.

## logging

Lean has no tracing ecosystem to bind; programs hand-roll a small logging module over `IO.eprintln`, and the durable artifact is the **format spec**, which transposes intact from the Ferrous suite:

- Layout: `{Test-?}[{YYYY-MM-DD HH:MM:SS.millis}][{module}][{level}] {message}`
- Logs to **stderr**; stdout stays clean for the command's real output.
- 256-color ANSI by level, gated on a `color : Bool` (off for non-tty sinks): Error `9`, Warn `220`, Info `228`, Debug `230`, Trace `248` — severity as temperature, loud red fading to dim grey.
- A `--json` switch swaps the human line for newline-delimited JSON via `Lean.Json` — one event per line.
- Verbosity: a `-v`/`-vv`/`--quiet` ladder floors dependencies at warn and raises only your own modules, parsed by Cli and read once at startup.

Meta code never uses this: extensions log through their registered trace classes and `logInfo` (core: observability; `debruijn-meta`), so users control them with `set_option` like every other part of the toolchain.

## hygiene (init-time fragment)

Commit the manifest; pin the toolchain; bump both together, alone, in a labeled commit. Publish through Reservoir when the library is real — its inclusion criteria are the ecosystem's supply-chain floor. Deprecate rather than delete from the first release (`@[deprecated new_name (since := "…")]`), so downstream bump forensics stay mechanical. And write the axiom-audit script on day one — a file importing the library and `#print axioms` on each public theorem — because the receipt is cheapest to install before there is anything to hide.
