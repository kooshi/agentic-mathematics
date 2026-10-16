---
name: debruijn-debugging
description: Procedure for hunting a fault that already exists in a Lean system: a posteriori and diagnostic, working backward from misbehavior to the model discrepancy that produced it. Invoke when a fault resists: elaboration fails and you cannot say why, a tactic misbehaves, a maxHeartbeats death or suddenly slow elaboration, a Mathlib bump breaks proofs, instance search finds the wrong instance or none, simp loops or fires nothing, code works under #eval and misbehaves compiled, a proven program still produces wrong output, or a fix whose only evidence is that the symptom went quiet. Triggers: "why does this error," "why is this slow," "the update broke everything," "it must be the unifier" said without a trace, a proof surviving on a raised heartbeat limit, flaky-seeming failures in a deterministic system. Drives toward one terminal test: a named mechanism — the causal chain from input through machine to fault, and why under the fix it now cannot recur. Assumes the de Bruijn core is loaded.
---

# de Bruijn — Debugging

The core carries the reflexes that keep faults out: the green manifold, error_reflexes, correctness past the checkmark. Its modeling companions run forward, synthesizing — `debruijn-domain-modeling` in type-and-statement shape, `debruijn-obligation-modeling` in proof shape, `debruijn-experience-modeling` at the boundary. This skill is their inverse. A fault already lives in a running system, exhibiting behavior that contradicts the model you believed when you wrote it, and you work backward from the observed misbehavior to the discrepancy that produced it. The machine here is layered — elaborator, kernel, compiled runtime, and the environment of imports and attributes that conditions all three — and naming the layer is half of naming the fault.

The terminal test, the analogue of the beautiful model and the derived statement: **the mechanism.** You are done not when the symptom stops but when you can state the causal chain from input, through machine, to fault, in named terms, and can say both why it failed and why, under the fix, it now cannot. Symptom-silence is the floor — you changed something and the fault went quiet, which is correlation, never cause. The lineage: Popper's falsification, that a reading consistent with your theory is worth little and a reading that could have refuted it and did not is worth everything; Agans' nine rules — understand the system, make it fail, quit thinking and look, divide and conquer, change one thing at a time, keep an audit trail, check the plug, get a fresh view, and if you did not fix it, it did not get fixed; Kernighan's warning that debugging is twice as hard as writing. Lean adds one gift the lineage never had: elaboration is deterministic, so reproduction is nearly free, and "flaky" is almost always an unpinned environment wearing chaos's costume. Drive toward the mechanism deliberately; the procedure below is how.

<the_one_cut>
A fault is a disagreement between the machine and your model of it, and it lives in the gap between them. Generation runs forward and fluent: from a model it produces a plausible cause and then narrates the evidence toward it, so the characteristic failure is not ignorance but confirmation — a story about the bug assembled from the same prior that missed it. The machine is the only witness to the gap, and in Lean it is an unusually talkative witness: the InfoView reports continuously, every subsystem has a trace, and `set_option diagnostics true` is the machine volunteering statistics at the moment of failure `[t½:~6mo]`. A guess is therefore less excusable here than anywhere.

The cut is between two kinds of act. An **observation** narrows the gap, because its outcome does not depend on what you believe. A **guess** decorates the model and leaves the gap exactly as wide. "It must be the unifier" without `trace.Meta.isDefEq` is the model talking. The tell is one question asked of your next step: *could its result surprise me?* A check whose outcome you already know teaches nothing; the discriminating observation is the one that can falsify the hypothesis you currently hold.

The master move is Agans' third rule: **make the machine testify.** Not reason about it, not recall it, not model it from the prior that already failed; put a question to the running system whose answer you cannot predict, and let the answer choose among your live hypotheses. A debugging step that adds no observation the machine did not already force is not progress; it is the model admiring itself.
</the_one_cut>

<reproduce_and_pin_the_regime>
You cannot interrogate a fault you cannot summon. The first artifact is a reproduction that fails on demand — in Lean, a self-contained file — and shrinking it is not throat-clearing before the real work, it *is* the work: every import dropped, hypothesis deleted, and universe specialized is a hypothesis eliminated, and the residue is the bug's actual surface. Determinism makes the repro cheap and makes its absence diagnostic: same toolchain, same dependency revisions, same options in scope must reproduce the same behavior, so an intermittent fault indicts the environment — a floating Mathlib rev, an option set in one file and assumed in another, a heartbeat budget sitting at the cliff's edge. `lean-toolchain` and the lake manifest *are* the regime's coordinates; pin them before trusting any observation.

Then pin the regime, which in Lean opens with one question: **which layer holds the fault?** Four signature regimes, each with its own suspect list:
- **Refuses to elaborate** — the forward failure; the core's error_reflexes dispatch it, and this skill takes over when the reflex fails twice.
- **Elaborates too slowly** — a performance fault in the elaborator: defeq unfolding, instance search, a simp set grown quadratic. Time is the cut; profile before theorizing.
- **Elaborated yesterday, fails today** — the bump regime, routine forensics after `lake update`. Read the deprecation warnings first (they name the rename and the date); take the mechanical renames as triage, not diagnosis; what remains is semantic — an orientation flipped, a priority changed, a lemma generalized until unification wants help — and the mechanism lives upstream, so the validation is a citation.
- **Proven, and still wrong** — the impossible fault, and the most Lean-specific: the kernel certified the statement, so the fault lives in what was never checked. The suspect list is the core's trust_inventory read as a lineup — the spec itself (statement ≠ intent), `native_decide`, `@[implemented_by]`/`@[extern]` forks, `partial`, the unverified IO rim, and the `panic!`-returns-`default` trap. Audit the ledger before doubting the kernel; it is the ledger, every time.

A measurement is valid only in the regime it samples: `#eval` runs the interpreter's semantics while `lake exe` runs the compiler's, and the `@[implemented_by]` seams between them are exactly where they diverge — a green result in the wrong regime is confidence you did not earn, aimed at the wrong target. When you must sample the cheaper regime, say so and name what it does not cover.
</reproduce_and_pin_the_regime>

<localize_before_theorizing>
Where before why. A cause proposed before the fault is located is a guess dressed as a diagnosis, spending effort in proportion to plausibility rather than truth. A report — yours from an hour ago, or a user's — names a symptom and usually a cause; take the symptom as data and the cause as a hypothesis, never inherited. Localize by bisection, the discriminating observation applied to a space, in whichever dimension is cheapest to cut:

- **In the proof:** `sorry`-bisection — replace the tail of the tactic block with `sorry` and advance the frontier; the first step whose inclusion flips green to red owns the fault. At file scale, `sorry` out declarations by halves.
- **In the statement:** specialize — instantiate the universe, drop the typeclass generality, monomorphize the type. If the specialized statement elaborates, the fault lives in the generality you removed, now named.
- **In the environment:** the environment is an input here, so bisect it like one — halve the imports, scope the `open`s, subtract the suspect attribute (`attribute [-simp] foo` locally) and see whether the symptom survives its absence. A declaration cleared by removal is exonerated; one implicated by removal is half the space gone.
- **In time:** `count_heartbeats in` per declaration to find where the budget goes; `trace.profiler true` to name the subsystem — `isDefEq`, `synthInstance`, or `simp` — before any theory about why. The declaration you were sure was slow is exonerated the moment the count shows it is noise.
- **In revisions:** `git bisect` over your commits, or over the dependency rev when the bump regime's warnings do not explain the break.
- **In regime:** hold the working configuration and the failing one and build the **bridging case** — the file that carries one failing parameter into the working setup, one import or option or instance at a time, run at every step, never imagined. The flip point names the mechanism's axis and its threshold; a sweep smooth to the far end has cleared one axis, not the bug.

Change one thing per cut, or the observation cannot say which thing mattered. And when a model of *why* refuses to come, stop trying to think it through and bisect: a mechanical binary search over a space you do not understand beats an intractable model of it, and elaboration's determinism makes every probe repeatable.
</localize_before_theorizing>

<make_the_machine_testify>
This is the heart, and its name is Agans' rule: quit thinking and look. Each live hypothesis becomes a question put to the system; the instrument is disposable, its output is the deliverable. The rack, cheapest first:

- The **InfoView** — the goal state after every step is testimony already on the table; read it before building anything.
- **`set_option diagnostics true`** — unfold counts and instance statistics volunteered on failure; the machine's own opening statement. `[t½:~6mo]`
- **`pp` options** — `pp.all true`, `pp.explicit`, `pp.universes`, `pp.notation false`: when two "identical" terms disagree, the difference is under the display; make the elaborator show what it sees, not what the notation says.
- **Subsystem traces** — `trace.Meta.isDefEq` for the defeq negotiation, `trace.Meta.synthInstance` for the search tree and which instance won, `trace.Meta.Tactic.simp` for each rewrite that fired. The trace converts "the unifier is being weird" into a transcript.
- **`#print`** for the term actually built and `#print axioms` for debts inherited three imports deep; `#check` for the signature as the environment holds it; `#reduce` to ask the kernel, `#eval` to ask the runtime — two different witnesses, deliberately.
- **The probe `example`** — your hypothesis as a two-line declaration whose elaboration you cannot predict: if the theory is right, this must fail the same way; if it elaborates, the theory is dead. The discriminating observation in its purest Lean form. `exact?`/`apply?` as a probe of what the library believes closes a goal.
- Runtime: `dbg_trace`, `IO.eprintln`, `dbgTraceIfShared` for the linearity cliff, `LEAN_ABORT_ON_PANIC=1` so crashes testify instead of returning `default`; `lean4checker` when meta code may have smuggled something past the front end. `[t½:~6mo]`

Aim every instrument to falsify, not confirm. An instrument aimed at confirming is a mirror — you chose what to print by what you expected to see. Trace the instance you are certain is found; print the value you are certain is positive; the reading that surprises you is the one that earned its tokens, and a reading that matches prediction should make you suspect you instrumented the wrong place.

Read the machine you are fighting; do not recall it. The core's documentation-first rule, sharpened for the debugger: the behavior of a Mathlib lemma, a tactic, or your own definition from last week is a fact to observe in its source (`#print`, the file itself) — least trustworthy exactly where it was recently bumped or where your recall is most fluent. When theory and behavior disagree, the behavior is right and the theory is the bug: go read why.
</make_the_machine_testify>

<name_the_mechanism>
The terminal test, made procedural. You are done when you can state the chain in named terms — and Lean's mechanisms have characteristic shapes worth knowing by name: *unification committed the metavariable at the first occurrence, so argument order chose the assignment*; *instance X shadowed Y by priority*; *the simp set cycles between the two orientations of one equation*; *the defeq check unfolds `f` because its transparency was left reducible, and the unfolding is exponential*; *the bump flipped lemma L's direction, so the set's normal form moved*; *the panic returned `default` and the fold continued on garbage*. A mechanism is stated when the layer, the chain, and the foreclosure are all named; "it works now" names none of them, and a bug silenced without a mechanism is a bug that moved.

The mechanism is also how you know the fix is right: once the cause is named, the fix is forced — and it usually deletes. The raised heartbeat limit, the `try` sprinkled until green, the priority bumped to win one search, the proof pinned to an old rev — each is fossilized wrong characterization, a symptom mistaken for a cause, and the named cause makes them removable. A fix that only adds is a signal you are still treating a symptom. The strongest form: when several proofs each carry a patch for one consumer of a shared lemma, the shared lemma is the bug — one restatement upstream deletes every patch at once.
</name_the_mechanism>

<read_the_ugliness>
Each smell is the gap between model and machine reporting itself; read it as redirection:

- **A raised `maxHeartbeats` standing as the fix** → symptom silenced, mechanism unnamed; the loan compounds at every call site that inherits the option.
- **`try` / `first | … | …` sprinkled until green** → the silence machine; a proof passing for reasons unknown is a bump-breakage IOU with your name on it.
- **Tactic order swapped and it works, cause unknown** → mechanism unnamed; it will recur with the next elaborator release.
- **A fix that half-works** → a wrong characterization, never a nearly-right one; re-characterize from the observation that it only half-worked, do not tune the patch.
- **The same fault patched a third time** → the cause lives upstream of every patch; find what the patches share.
- **"Flaky," said of a deterministic system** → an unpinned coordinate you have not named — the rev, the option, the budget at its cliff.
- **A `sorry` erased here and reappearing in a different lemma** → the debt moved; the ledger did not shrink.
- **Pinned to last quarter's Mathlib "temporarily"** → the bump deferred at compound interest; schedule the forensics or inherit them at the worst time.
- **A fluent justification for a fix whose mechanism you cannot state** → symptom-silence wearing a rationale; the narration is an attack surface on your own judgment.

Push harder on none of these. Return to the machine with the smell as the sharper question.
</read_the_ugliness>

<validate_by_reintroduction>
The exit discipline, in falsification's rank order: a fix is unproven until an observation you did not author, and could not charm, agrees.

Prove the guard. The regression test must trigger the bug's actual mechanism, not a proxy: the statement that failed, the goal that timed out, the input that hit the seam — located at the boundary where the real fault entered, not a hand-built stand-in. Then watch it bite: re-introduce the bug — undo the fix in a scratch, or run the new test against the pre-fix state — and see it fail; a regression test never seen to fail is a guess about a guess. Pin the artifact mechanically where the surface allows: `#guard` for the value, an `example` for the statement, `#guard_msgs` when the mechanism was a message or the fix is about what the user sees. For the bump regime the validation is a **citation**: the upstream commit, rename, or deprecation note that names the change — a bump fix without its citation is a guess that happened to recompile.

Decorrelate the verdict from the fixer: the deciding evidence is the observation that does not share your assumptions — the full `lake build`, the compiled binary rather than the `#eval` that sat beside you all session, `plausible` across generated inputs, the axiom audit re-run. Separate the systematic fault from the long tail and stop at the right place: the fix must kill the pathology, not every mild case; name what you left uncovered so a later reader inherits the boundary rather than a false all-clear.
</validate_by_reintroduction>

<the_loop>
Reproduce and pin the regime, localize, interrogate, name the mechanism, validate — an oscillation between narrowing the gap and re-characterizing when a fix half-works. Each pass replaces a belief about the system with an observation of it, until the gap closes: the mechanism named, the fix forced and usually smaller than what it replaces, the bug re-introduced and caught. Stop there. The win is the least change the named cause demands; one line more, added to feel safe, is a fresh guess about a system you have only just finished learning to observe.

When the mechanism holds, hand the system back to the forward passes: `debruijn-domain-modeling` when the named cause was a representation admitting a state the domain forbids; `debruijn-obligation-modeling` when it was a statement too weak to carry itself through a step — or a spec that certified something adjacent to intent; `debruijn-experience-modeling` when the mechanism ran entirely inside the machine and the damage was that nothing crossed the wire to say so. The mechanism names which one; that is a third thing having it buys you.
</the_loop>
