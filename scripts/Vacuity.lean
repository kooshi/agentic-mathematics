import Proofs

/-!
# Vacuity audit — a theorem can pass every other check and still say nothing

A theorem `∀ x : C, P x` over an empty `C` is true and says nothing, and the kernel accepts it as gladly as any other. A formal
statement that drops a hypothesis or quantifies over an empty domain is the characteristic way a formalization proves the wrong
theorem, and the axiom audit cannot see it. This scan reads every declaration of the library and reports, for each binder whose type
is a **tracked carrier**, whether the library proves that carrier inhabited.

**The law:** a statement is vacuous exactly when some `∀`-binder has an empty domain. A declaration whose *stated* conclusion is
`False` is a refutation — its binders are meant to be jointly unsatisfiable — and is skipped and counted. `¬ P` and `a ≠ b` are claims,
not refutations: their binders are audited like any other's.

**The verdicts**, one per (declaration, carrier) site:
* `WITNESSED` — the library proves the carrier inhabited, unconditionally (a `Nonempty` theorem, or a constant of the carrier's type);
* `DECLARED`  — provably empty, and the declaration's docstring says so on a line `VACUITY DECLARED: <reason>`, printed every run;
* `VACUOUS`   — provably empty (an `IsEmpty` theorem, or `¬ C` for a tracked `C`), undeclared: always fails;
* `STALE`     — a `VACUITY DECLARED:` docstring on a site whose emptiness is not proved: always fails, which makes the marker a claim
  rather than a suppression;
* `GENERIC`   — undecided, and the carrier has free parameters, so its inhabitation is the caller's obligation;
* `UNKNOWN`   — undecided at a concrete carrier: counted, never silent, and the only verdict `scripts/vacuity-baseline.txt` may hold.

Only **unconditional** evidence counts: a theorem with real hypotheses is a conditional claim.

**What it cannot see**, stated rather than chased: a carrier the list below does not name; a carrier reachable only inside a data
structure (`Set C`, a structure field); hypotheses jointly unsatisfiable while each is satisfiable alone. The last is why every
theorem whose hypothesis is a structure ships a named inhabitant (`LEAN.md` § The gate).

The output is a contract with `scripts/vacuity.sh` and `scripts/gate_report.py`: `=== DECLARED ===` rows `DECLARED <decl> ::
<reason>`; `=== FLAGGED ===` rows `<VACUOUS|STALE|UNKNOWN> <decl>`; `=== EVIDENCE ===` rows; `=== SITES ===` rows `SITE <verdict>
<decl> :: <carrier>`; `=== SCANNED === declarations=… refutations-skipped=…`; `=== TOTALS === sites=… … untelescoped=…`.
-/

namespace VacuityAudit

open Lean Meta Elab Command

inductive Verdict | vacuous | declared | stale | witnessed | generic | unknown
  deriving BEq, Inhabited

/-- The verdict's printed tag. -/
def Verdict.tag : Verdict → String
  | .vacuous => "VACUOUS" | .declared => "DECLARED" | .stale => "STALE"
  | .witnessed => "WITNESSED" | .generic => "GENERIC" | .unknown => "UNKNOWN"

/-- The marker a declaration uses to say its emptiness is deliberate. It lives in the docstring, where a reader meets the
justification at the declaration rather than in a side file. -/
def marker : String := "VACUITY DECLARED:"

/-- The reason a declaration gives, if it gives one: the rest of the marker's line. -/
def reasonIn? (doc : String) : Option String :=
  match doc.splitOn marker with
  | _ :: rest :: _ => some (((rest.splitOn "\n").headD "").trimAscii.copy)
  | _ => none

/-- Ours: declared in a module under `Proofs`, or in the file being elaborated now — which is what makes a planted control a
one-file operation (`scripts/vacuity.sh --self-test` plants its controls in a copy of this file). This file's own instruments are
not ours to scan. -/
def isOurs (env : Environment) (n : Name) : Bool :=
  !(`VacuityAudit).isPrefixOf n &&
  match env.getModuleIdxFor? n with
  | some idx =>
    match env.header.moduleNames[idx.toNat]? with
    | some m => (`Proofs).isPrefixOf m
    | none => false
  | none => true

/-- **The tracked carriers**: the full names of every structure or predicate of the library whose emptiness would make a statement
vacuous — a structure of hypotheses, a certificate, a class of objects. A carrier this list does not name is checked by nothing.

To add one: (1) add its full name here; (2) run `./scripts/vacuity.sh`, and explain every new site; (3) if its sites read
`UNKNOWN`, prove an inhabitant or add the site to the baseline with the reason. A mistyped name is tracked by nothing and raises no
error, which is why the self-test's control carrier, `VacuityControls.Carrier` (declared only in the self-test's copies), sits in this
list: a scan that stopped reading the list would fail its controls. -/
def trackedProps : List Name :=
  [`VacuityControls.Carrier]

/-- A carrier or a statement as one line of text, for the report, printed where its binders are still in scope. Never throws. -/
def showCarrier (τ : Expr) : MetaM String := do
  try
    return ((← ppExpr τ).pretty 1000000).replace "\n" " "
  catch _ =>
    return "<did not pretty-print>"

/-- The evidence the library holds, each piece with the declaration that supplied it and its statement as text. -/
structure Evidence where
  empties   : Array (Name × Expr × String) := #[]
  witnesses : Array (Name × Expr × String) := #[]

/-- Collect every unconditional declaration whose type is `IsEmpty τ`, `¬ P` for a tracked `P` (emptiness), `Nonempty τ`, or a
tracked carrier itself (a constant of the carrier's type is its inhabitant). Only instance-implicit binders may remain: anything else
is a real hypothesis, and a conditional claim is not evidence. A refutation `¬ P` is read without reducing, because `Not P` is
`P → False` and a reducing telescope would eat the arrow and lose the evidence. -/
def gather (env : Environment) : MetaM Evidence := do
  let mut ev : Evidence := {}
  for (n, ci) in env.constants.toList do
    if n.isInternal || !isOurs env n then continue
    let refuted : Option (Expr × String) ← (try forallTelescope ci.type fun xs concl => do
        for x in xs do
          if !(← x.fvarId!.getDecl).binderInfo.isInstImplicit then return none
        let some p := (if concl.getAppFn.constName? == some ``Not then concl.getAppArgs[0]? else none)
          | return none
        return some (p, ← showCarrier p)
      catch _ => pure none)
    if let some (p, shown) := refuted then
      if !p.hasLooseBVars then
        if let some h := p.getAppFn.constName? then
          if trackedProps.contains h then
            ev := { ev with empties := ev.empties.push (n, p, shown) }
            continue
    let found : Option (Expr × String) ← (try forallTelescopeReducing ci.type fun xs concl => do
        for x in xs do
          if !(← x.fvarId!.getDecl).binderInfo.isInstImplicit then return none
        let evidential := match concl.getAppFn.constName? with
          | some h => h == ``IsEmpty || h == ``Nonempty || trackedProps.contains h
          | none => false
        let shown ← if evidential then showCarrier concl else pure ""
        return some (concl, shown)
      catch _ => pure none)
    let some (τ, shown) := found | continue
    if τ.hasLooseBVars then continue
    match τ.getAppFn.constName? with
    | some ``IsEmpty =>
      if let some c := τ.getAppArgs[0]? then
        if !c.hasLooseBVars then ev := { ev with empties := ev.empties.push (n, c, shown) }
    | some ``Nonempty =>
      if let some c := τ.getAppArgs[0]? then
        if !c.hasLooseBVars then ev := { ev with witnesses := ev.witnesses.push (n, c, shown) }
    | some h =>
      if trackedProps.contains h then ev := { ev with witnesses := ev.witnesses.push (n, τ, shown) }
    | none => pure ()
  return ev

/-- The first collected piece of evidence `τ` matches, compared under `withNewMCtxDepth` inside `withoutModifyingState`, so a probe
can never leak an assignment into the next one. -/
def firstMatch? (τ : Expr) (cands : Array (Name × Expr × String)) : MetaM (Option Name) := do
  for (n, c, _) in cands do
    let hit ← withoutModifyingState <| withNewMCtxDepth <| (try isDefEq τ c catch _ => pure false)
    if hit then return some n
  return none

/-- Is `τ` provably empty, provably inhabited, or neither — and what decided it. The third answer is the point: a carrier the scan
cannot decide is reported and counted, never passed over in silence. -/
def probe (ev : Evidence) (τ : Expr) : MetaM (Verdict × String) := do
  if let some n ← firstMatch? τ ev.empties then return (.vacuous, toString n)
  if let some n ← firstMatch? τ ev.witnesses then return (.witnessed, toString n)
  let synth (head : Name) : MetaM Bool := do
    try
      match ← synthInstance? (← mkAppM head #[τ]) with
      | some _ => pure true | none => pure false
    catch _ => pure false
  if ← synth ``IsEmpty then return (.vacuous, "instance search")
  if ← synth ``Nonempty then return (.witnessed, "instance search")
  return (.unknown, "")

/-- The carrier a binder commits to, taken as it stands and never unfolded: a binder whose type's head is tracked. -/
def carrierOf? (e : Expr) : MetaM (Option Expr) :=
  return match e.getAppFn.constName? with
    | some n => if trackedProps.contains n then some e else none
    | none => none

/-- `¬ P` and `a ≠ b`, read as written: the two heads whose definitions are `… → False`. -/
def isNegationConcl (concl : Expr) : Bool :=
  concl.isAppOf ``Not || concl.isAppOf ``Ne

/-- A refutation: the stated conclusion, after the binders, is `False` itself — the reducing telescope ends in `False` and the
statement as written does not end in a negation. -/
def isRefutation (type : Expr) : MetaM Bool :=
  forallTelescopeReducing type fun _ concl =>
    if !concl.isConstOf ``False then pure false
    else forallTelescope type fun _ stated => pure !isNegationConcl stated

/-- Every carrier a declaration's statement commits to: each binder's type, plus the conclusion. A refutation is skipped; a stated
negation's own `P` (the arrow a reducing telescope finds in `Not`) is not a hypothesis anyone wrote, and is dropped. -/
def carriersOf (type : Expr) : MetaM (Array (Expr × String)) :=
  forallTelescopeReducing type fun xs concl => do
    if ← isRefutation type then return #[]
    let xs ← if concl.isConstOf ``False && xs.size > 0 then
        (do let stated ← forallTelescope type fun _ c => pure c
            pure (if isNegationConcl stated then xs.pop else xs))
      else pure xs
    let mut out : Array Expr := #[]
    for x in xs do
      if let some τ ← carrierOf? (← inferType x) then out := out.push τ
    if let some τ ← carrierOf? concl then out := out.push τ
    (out.filter (!·.hasLooseBVars)).mapM fun τ => do return (τ, ← showCarrier τ)

/-- Machine-written API of a type (constructors, recursors, `casesOn`, `noConfusion`, projections): counted in `declarations=`,
never made a site, because each binds the tracked structure at a variable index and nobody chose its statement. -/
def isGeneratedDecl (env : Environment) (n : Name) (ci : ConstantInfo) : Bool :=
  (match ci with | .ctorInfo _ | .recInfo _ => true | _ => false) ||
  isAuxRecursor env n || isNoConfusion env n || (env.getProjectionFnInfo? n).isSome ||
  (match n with | .str _ s => s == "ctorIdx" || s == "noConfusionType" | _ => false)

/-- One audited site. -/
structure Row where
  decl    : Name
  verdict : Verdict
  reason  : String
  carrier : String
  source  : String

/-- Run the audit and print its report (the contract is in this file's header). -/
def audit : CommandElabM Unit := liftTermElabM do
  let env ← getEnv
  let ev ← gather env
  logInfo (s!"evidence: {ev.empties.size} emptiness proof(s), {ev.witnesses.size} witness(es)")
  let mut rows : Array Row := #[]
  let mut scanned : Nat := 0
  let mut refutations : Nat := 0
  let mut untelescoped : Nat := 0
  for (n, ci) in env.constants.toList do
    if n.isInternal || !isOurs env n then continue
    scanned := scanned + 1
    if ← (try isRefutation ci.type catch _ => pure false) then
      refutations := refutations + 1
    if isGeneratedDecl env n ci then continue
    -- A declaration whose type cannot be telescoped is counted and named, never skipped in silence: a check that cannot run fails.
    let carriers ← try carriersOf ci.type catch e => do
      logWarning m!"UNTELESCOPED {n}: carriersOf failed ({e.toMessageData}); declaration not classified"
      untelescoped := untelescoped + 1
      pure #[]
    for (τ, shown) in carriers do
      -- Probe first, always: a carrier that is demonstrably empty is reported as such even when it is generic.
      let (probed, source) ← probe ev τ
      let raw := if probed == .unknown && (← instantiateMVars τ).hasFVar then .generic else probed
      let reason := (← findDocString? env n).bind reasonIn?
      let (v, r) := match raw, reason with
        | .vacuous, some r => (Verdict.declared, r)
        | .vacuous, none   => (Verdict.vacuous, "")
        | _,        some r => (Verdict.stale, r)
        | v,        none   => (v, "")
      rows := rows.push { decl := n, verdict := v, reason := r, carrier := shown, source := source }
  let count (v : Verdict) := rows.filter (·.verdict == v) |>.size
  logInfo "=== VACUITY AUDIT ==="
  logInfo "=== DECLARED ==="
  for row in rows do
    if row.verdict == .declared then logInfo (s!"DECLARED {row.decl} :: {row.reason}")
  logInfo "=== FLAGGED ==="
  for row in rows do
    if row.verdict == .vacuous || row.verdict == .stale || row.verdict == .unknown then
      logInfo (s!"{row.verdict.tag} {row.decl}")
  logInfo "=== EVIDENCE ==="
  for (d, _, s) in ev.empties do logInfo (s!"EVIDENCE EMPTY {d} :: {s}")
  for (d, _, s) in ev.witnesses do logInfo (s!"EVIDENCE WITNESS {d} :: {s}")
  logInfo "=== SITES ==="
  for row in rows do
    let decidedBy := if row.source.isEmpty then "" else s!" [by {row.source}]"
    logInfo (s!"SITE {row.verdict.tag} {row.decl} :: {row.carrier}{decidedBy}")
  logInfo (s!"=== SCANNED === declarations={scanned} refutations-skipped={refutations}")
  logInfo (s!"=== TOTALS === sites={rows.size} vacuous={count .vacuous} stale={count .stale} declared={count .declared} witnessed={count .witnessed} generic={count .generic} unknown={count .unknown} untelescoped={untelescoped}")

end VacuityAudit

-- VACUITY CONTROLS END (scripts/vacuity.sh --self-test plants its controls above this line)

#eval VacuityAudit.audit
