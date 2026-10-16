# Architecture — the library in Lean 4

*This file describes the code as it stands: the statement (§ 1), the shape of the argument (§ 2), the module map read off the import
graph (§ 3), where the roadmap lives (§ 4), trust (§ 5), the defences against proving the wrong theorem (§ 6), and the standing
limits (§ 7). What the results mean and what to work on next is `CLAUDE.md` § Frontier. de Bruijn writes this file in the jobs that
touch the code; it is rewritten in place and its history is in git.*

## 1. The statement

‹The headline theorem's Lean statement, once there is one, read against the informal claim.›

## 2. The shape of the argument

‹The reduction and the certified computations it rests on (`LEAN.md` § The shape of the proof).›

## 3. Module map — the import graph

*One row per module under `Proofs/`, named relative to it without `.lean`; its imports from the library (or `—`); what it holds.
`tools/check_architecture.py` fails when a module has no row, a row names no module, or a row's imports differ from the module's own
— so the map can never drift behind the code.*

| module | imports | holds |
|---|---|---|
| `Example` | — | the template's example: `oddSum` and `oddSum_eq_sq`, the sum of the first `n` odd numbers is `n²`, with its spec examples |

## 4. The roadmap

`plans/FRONTIER-STUBS.md`, ranked by Poros; a milestone's module plan is `plans/Mnn-kernel-plan.md`.

## 5. Trust

*Every declared purchase, by name in backticks: each outside theorem imported as an `axiom` (with its bibliography key and where its
read-back is), and each `native_decide` use. `scripts/axioms.sh` fails on a declared import this section does not name.*

- ‹none›

## 6. The defences against proving the wrong theorem

The vacuity scan and its tracked carriers (`LEAN.md` § The gate); a named inhabitant for every structure of hypotheses; the final
statement read aloud against the informal claim.

## 7. Standing limits

‹What the library deliberately does not cover, and why.›
