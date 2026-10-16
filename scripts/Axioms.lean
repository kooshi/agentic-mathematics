import Proofs

/-!
# Axiom audit — the trust receipt

Everything shipped must reduce to what the kernel verified plus what we explicitly chose to trust. This file prints one line per
declaration of the library with the axioms it rests on, and `scripts/axioms.sh` checks each line's axioms as a set:

* **CLEAN** — a subset of `propext`, `Classical.choice`, `Quot.sound`, the empty set included;
* **IMPORTED** — the standard three and **declared imports**, at least one: an `axiom` importing an outside theorem, named below by
  one `#eval AxiomAudit.declareImport ``Full.Name` line, each with the four items of `LEAN.md` § Assumptions;
* **PURCHASED** — those and native-evaluation axioms, at least one, on a declaration whose docstring opens
  "**Trust purchase: native evaluation.**";
* anything else fails: `sorryAx`, an undeclared axiom, a native purchase with no docstring saying so.

*Why every declaration, found by the file itself:* an audit that reads a hand-kept list of records passes a declaration nobody added
to the list. *Why printed, not eyeballed:* at this pin `native_decide` mints a per-declaration axiom,
`foo._native.native_decide.ax_1_1`, and `Lean.ofReduceBool` never appears; that difference is one long name in a wall of text.

Run it through the gate script (`./scripts/axioms.sh`), or by hand with `lake env lean scripts/Axioms.lean`.

**Every axiom is printed by its full name** (`pp.fullNames`), because a name shortened against the open namespaces spells one axiom
two ways. The output is a contract with `scripts/axioms.sh` and `scripts/gate_report.py`:
`DECLARED IMPORT <name>`, `RECORD <name> PURCHASE-DOC <0|1> AXIOMS <a,b,…>` (`-` for none), `LIBRARY AXIOM <name>`, and a last line
`SUMMARY records=N library-axioms=M`.
-/

set_option pp.fullNames true

namespace AxiomAudit

open Lean Elab Command

/-- `n` is declared in the library — a module under `Proofs` — or in the file being elaborated now. The second clause is what
makes a planted control a one-file operation: `scripts/axioms.sh --self-test` declares its plants in a copy of this file. -/
def inScope (env : Environment) (n : Name) : Bool :=
  match env.getModuleIdxFor? n with
  | none => true
  | some i => match env.header.moduleNames[i.toNat]? with
    | some m => (`Proofs).isPrefixOf m
    | none => false

/-- A native-evaluation auxiliary: `native_decide` mints `foo._native.native_decide.ax_N_M` per use. -/
def isNativeAux (n : Name) : Bool :=
  n.components.contains `_native

/-- A bibliography key in `BIBLIOGRAPHY.md`'s form — capitalized letters, a four-digit year, at most one lower-case letter:
`Smith2020`, `SmithJones2020b`. -/
def isBibKey (k : String) : Bool :=
  let cs := k.toList
  let letters := cs.takeWhile Char.isAlpha
  let rest := cs.drop letters.length
  let digits := rest.takeWhile Char.isDigit
  let tail := rest.drop digits.length
  (cs.head?.map Char.isUpper).getD false && digits.length == 4 &&
    (tail.isEmpty || (tail.length == 1 && tail.all Char.isLower))

/-- Some bracketed span of `doc` is a bibliography key (`isBibKey`). -/
def hasBibKey (doc : String) : Bool :=
  ((doc.splitOn "[").drop 1).any fun piece =>
    match piece.splitOn "]" with
    | k :: _ :: _ => isBibKey k
    | _ => false

example : isBibKey "Smith2020" ∧ isBibKey "SmithJones2020b" ∧ ¬ isBibKey "Smith" ∧
    ¬ isBibKey "smith2020" ∧ ¬ isBibKey "Smith2020bc" := by decide

#guard hasBibKey "`[Smith2020]` Theorem 2, p. 15"
#guard !hasBibKey "Theorem 2 [i], p. 15"

/-- **Declare an imported outside theorem to the gate.** Refuses — so the audit does not elaborate and the gate fails — unless `n` is
an `axiom` declared in the library whose docstring names a bibliography key (`LEAN.md` § Assumptions item 1). The double backtick in
`#eval AxiomAudit.declareImport ``Full.Name` elaborates only if the constant exists, so a mistyped name cannot read as an empty
declaration. Prints `DECLARED IMPORT <full name>`. -/
def declareImport (n : Name) : CommandElabM Unit := do
  let env ← getEnv
  let some ci := env.find? n | throwError "declareImport: unknown constant {n}"
  unless ci.isAxiom do
    throwError "declareImport: {n} is not an `axiom`; only an axiom is an imported outside theorem"
  unless inScope env n do
    throwError "declareImport: {n} is not declared in the library; an axiom of a dependency is not ours to declare"
  let some doc ← findDocString? env n
    | throwError "declareImport: {n} has no docstring; LEAN.md § Assumptions item 1 asks it to name its bibliography key, \
        section and page"
  unless hasBibKey doc do
    throwError "declareImport: {n}'s docstring names no bibliography key of the form [Author2024]; LEAN.md § Assumptions item 1"
  logInfo (s!"DECLARED IMPORT {n}")

/-- A component of a name the compiler or the equation compiler writes, never an author: `_private`, `_native`, `match_1`,
`proof_2`, `eq_1`, `eq_def`, `splitter`, `congr_simp` and the like. -/
def isGeneratedComponent : Name → Bool
  | .str _ s => s.startsWith "_" || s == "eq_def" || s == "splitter" || s == "congr_simp" ||
      ["match_", "proof_", "eq_", "omega_"].any fun pre =>
        (s.dropPrefix? pre).any (fun rest => !rest.isEmpty && rest.all fun c => c.isDigit || c == '_')
  | .num _ _ => true
  | .anonymous => false

/-- A declaration this audit reads: ours, a theorem, a definition or an opaque constant, written by an author — no component of its
name generated (after a private prefix is stripped, so a `private theorem` is read too), not machine-written API of a type, and not
this file's own instruments. A generated declaration needs no line of its own: whatever axiom it uses reaches the declaration it was
generated for. -/
def isRecord (env : Environment) (n : Name) (ci : ConstantInfo) : Bool :=
  let base := (privateToUserName? n).getD n
  inScope env n && !(base.components.any isGeneratedComponent) && !(`AxiomAudit).isPrefixOf n &&
    (match ci with | .thmInfo _ | .defnInfo _ | .opaqueInfo _ => true | _ => false) &&
    !isAuxRecursor env n && !isNoConfusion env n && (env.getProjectionFnInfo? n).isNone

/-- **The audit.** One `RECORD` line per declaration `isRecord` accepts, sorted by name, with whether its docstring declares a native
purchase and every axiom it rests on; then one `LIBRARY AXIOM` line per `axiom` the library declares (native auxiliaries left out),
so that an axiom no record uses still reaches the gate, which fails on any the `declareImport` lines do not name; then the
`SUMMARY`. It must stay the file's last command: a declaration made after it is not seen. -/
def audit : CommandElabM Unit := do
  let env ← getEnv
  let names := (env.constants.fold (init := (#[] : Array Name)) fun acc n ci =>
    if isRecord env n ci then acc.push n else acc).qsort (fun a b => a.toString < b.toString)
  for n in names do
    let axs ← collectAxioms n
    let axs := axs.qsort (fun a b => a.toString < b.toString)
    let doc := (← findDocString? env n).getD ""
    let purchase := if (doc.trimAscii.copy).startsWith "**Trust purchase: native evaluation.**" then 1 else 0
    let shown := if axs.isEmpty then "-" else ",".intercalate (axs.toList.map toString)
    logInfo (s!"RECORD {n} PURCHASE-DOC {purchase} AXIOMS {shown}")
  let own := (env.constants.fold (init := (#[] : Array Name)) fun acc n ci =>
    if ci.isAxiom && inScope env n && !isNativeAux n then acc.push n else acc).qsort (fun a b => a.toString < b.toString)
  for n in own do
    logInfo (s!"LIBRARY AXIOM {n}")
  logInfo (s!"SUMMARY records={names.size} library-axioms={own.size}")

end AxiomAudit

/-! ## Declared imports

One line per imported outside theorem, each an `axiom` of the library with the four items of `LEAN.md` § Assumptions:

```
#eval AxiomAudit.declareImport ``Proofs.Some.outside_theorem
```

and the axiom named in backticks in `ARCHITECTURE.md` § 5 Trust, which `scripts/axioms.sh` checks. None yet. -/

-- DECLARED IMPORTS END (scripts/axioms.sh --self-test plants its controls above this line)

#eval AxiomAudit.audit
