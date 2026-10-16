---
name: debruijn-domain-modeling
description: The deliberate procedure for finding a problem's true shape in Lean when the representation or the statement will not come clean — invoke it the moment a type, definition, theorem statement, or API resists, sprawls, sprouts casts, or needs a comment apologizing for it. The slow, explicit form of the de Bruijn core's standing modeling instinct: run it when the instinct has not fired and a model elaborates but feels wrong. Triggers on "this type is getting ugly," "how should I state this," choosing between Bool and Prop, an indexed family and a side predicate, a quotient and a canonical form, recurring "motive is not type correct" errors, HEq or casts breeding, an inductive that keeps growing variants. Drives toward one terminal test: a representation so exactly the image of the problem's intrinsic structure that the hard cases stop being special and downstream proofs go short. Assumes the de Bruijn core is loaded; scoped to type-and-statement space.
---

# de Bruijn — Domain Modeling

The de Bruijn core carries modeling as a reflex: characterize structure, let types and statements fall out, read ugliness as a diagnostic. This skill is the ritual you run when the reflex does not fire — when you have a representation in front of you that elaborates and still feels wrong, and you need the slow explicit descent to find why. The core states the principle in four sentences because every turn cannot afford more; this skill spends the words, because finding a hard model is worth a deliberate procedure.

The whole skill serves one terminal test: **a beautiful model**. Not beautiful as decoration — beautiful as *convergence signal*. When a representation finally becomes the direct image of the problem's intrinsic structure, it stops looking like a choice and starts looking inevitable, as though the problem authored it and you merely transcribed. In Lean the signal has a mechanical proxy no other language offers: the model and the statements about it are the same kind of object, so a converged model announces itself downstream — lemmas state in one line, proofs go two, the induction the theorem needs is the recursor the type already has. This standard has its lineage: Simon's dictum that solving a problem simply means representing it so as to make the solution transparent; Hoare's *Notes on Data Structuring*, which drew the representation vocabulary from mathematics rather than machines; the practitioner canon of *make illegal states unrepresentable* and *parse, don't validate*; and Mathlib's own folklore, learned across a million lines — that getting the definition right is most of the work, because every theorem about a definition inherits its shape. Drive toward it deliberately. The procedure below is how.

<the_one_cut>
Every technique here serves a single discrimination, the hard cut on which all modeling turns: **intrinsic structure versus incidental structure.**

Intrinsic structure is permanent — it belongs to the problem itself and holds across every input the problem will ever see. An operation that is genuinely associative. An order that is genuinely a lattice. A state machine whose illegal transitions are illegal *by the nature of the domain*, not by current policy. A relation under which two representations are genuinely the same object.

Incidental structure is contingent — it holds for *this* batch, *this* version, *this* historical accident, and it betrays you silently when the sample shifts. The list happens to arrive sorted. The index happens to fit. The paper happened to define it by cases. No one has stated it the other way before. These are facts about the present, wearing the costume of facts about the problem. A model built on intrinsic structure is beautiful and durable; a model built on incidental structure is the source of every cast, every side condition threaded but never used, every apologetic comment. When you cannot tell which you have, assume incidental and state the assumption as a named hypothesis — the theorem will demand it where it is really needed, and that demand map is evidence.

Lean then forces a second cut the first one feeds: once structure is known intrinsic, decide where it **lives** — *in* the type (intrinsic verification: an index, a Subtype, a bundled proof) or *beside* it (extrinsic: a plain type and theorems alongside). The ceiling on expressiveness is gone here, so the discipline inverts from "push harder" to a placement rule: **index only what every consumer must know.** An index taxes every future context that mentions the type — motives, casts, `HEq` at the seams — while a side theorem is purchased per use. Mathlib is overwhelmingly extrinsic for exactly this reason. Intrinsic *structure* does not imply intrinsic *placement*; conflating the two cuts is the characteristic modeling error of machine-written Lean.
</the_one_cut>

<grok>
Before reshaping anything, simulate the problem until you can run it. Hold its state, step its transitions, push on it and watch where it goes. Do this unwritten first — the mental pass is *pre-linear*, and a serialization chosen before you know the problem's axes is one more piece of incidental structure you will have to strip back out. Play is free and commits to nothing: rotate the thing, vary its parameters, run it backward, ask what would have to be true for the hard case to be ordinary.

Then know exactly when to stop trusting it. A head-simulation fails silently — its characteristic error is the **elided step**, a transition you believe you ran and in fact only assumed. At the first tripwire — the simulation carries more state than you can restate on demand, or you are about to commit to a type, a statement, a variant set — externalize, and in Lean the externalization can *execute*: sketch a `Bool`-valued draft of the predicate and `#eval` it on the smallest interesting instances before any `Prop`-valued statement exists; prototype the operation as a `def` and run the examples that motivated the problem; tabulate the states, transitions, and quantities that must agree. Computation is the antidote to elision — the machine cannot skip the step you assumed, which is the whole reason to make it take the steps.

Enumerate along the axes the cases vary on, never in the order the problem arrived in. The order the requirements were dictated — the paper's case split, the previous implementation's phases — is incidental structure operating on your reasoning before it reaches the model, and the enumeration is the cheapest place to strip it.

The test for sufficient grokking: can you predict, before writing it, what the awkward cases will be — and, in Lean specifically, which lemma will be hardest and which induction will refuse? If the edge cases surprise you when you hit them, you had not grokked — you were pattern-matching to a familiar shape that does not fit. Go back and run the simulation further.
</grok>

<shift_perspective>
Most representations come out ugly because the problem was framed in inherited terms — the paper's terms, the previous system's terms, the terms a programming language without Prop would use. That framing carries incidental structure baked in, smuggled by the words used to state it.

Reframe until the problem becomes simple or familiar. The reframes of type-and-statement space form a standing inventory; walk it deliberately:
- **Function or relation?** A `def f : A → B` when the assignment is total and computable; an `inductive R : A → B → Prop` when it is partial, multivalued, or defined by rules — forcing a relation into a function breeds junk values, forcing a function into a relation breeds existence lemmas.
- **Bool or Prop?** Compute with `Bool`, reason with `Prop`, and never hold both without the bridge (`foo_iff : fooB x = true ↔ Foo x`, a `Decidable` instance) — two costumes on one predicate, drifting independently, is a standing seam failure.
- **Data or proof?** `Σ`/`Subtype` when a consumer must extract the witness; `∃` when only truth travels. Choosing between them is choosing whether callers may compute (core: prop_type_and_erasure).
- **Quotient or canonical form?** When the true model is "equal up to a relation," represent the relation (`Quotient`, respects-lemmas proven once) rather than maintaining a normal form by hand and apologizing in comments.
- **Indexed family or side predicate?** The placement cut, applied: `Vector α n` when every consumer needs the length; `List α` plus `h : xs.length = n` when only some proofs do.
- **Deep or shallow embedding?** For a DSL: an `inductive` syntax with an evaluation function when you must reason *about* programs; plain functions when you must only run them.
- **Which recursor?** Choosing the representation *is* choosing the induction principle every downstream proof will live inside. Name the induction you want to be trivial, then pick the shape whose recursor is that induction — designing the type backward from the proof burden is the master reframe of this space.

When no reframe arrives, ladder toward one: hold the problem's abstraction level fixed and vary its parameters until you reach a neighbor you *can* model — the **bridging case**. In Lean the neighbor is frequently a Mathlib structure one hypothesis away: drop the constraint that resists and the problem is a monoid fold, a Galois connection, a closure operator someone already modeled with a thousand lemmas attached. Model the neighbor, then walk back; the property you re-add to reach the resisting problem is precisely the one your representation could not express, now named rather than diffuse.
</shift_perspective>

<deconstruct_to_fundamentals>
When the reframe does not come, force it: strip the problem to fundamentals and rebuild using only those — with the one discipline naive first-principles thinking lacks. The dogma worth refusing is never "this is a known shape"; a known mathematical shape is intrinsic structure already named. The dogma worth refusing is **"this is how it has been done"** — the paper's case analysis, the reference implementation's phases, the Bool-flag habits of languages without a Prop. Refuse the inherited *workflow*; keep the inherited *mathematics*.

In Lean the inherited mathematics is literally on the shelf, so deconstruction ends in a search rather than a description: list the undeniable fundamentals — the operations the domain must support, the laws they satisfy, the invariants that never break — then interrogate each against the catalog before minting anything. Is the operation a monoid? Is the order a lattice? Is the pair of maps a Galois connection? Is the closure a closure operator, the symmetry a group action, the distance a metric? Ask Loogle and LeanSearch, not memory (core: documentation_first). Recognition is the base case of all problem-solving, and Mathlib is recognition industrialized — finding the named structure converts your modeling problem into an instance declaration and buys every lemma ever proven about the shape. What you exclude matters equally: each generality the fundamentals do not demand is an index someone will thread, a hypothesis someone will discharge, forever.
</deconstruct_to_fundamentals>

<rebuild>
Build the representation as the direct image of the intrinsic structure you isolated, placed by the second cut. Concretely, in type-and-statement space:
- A closed set of alternatives → an `inductive` matched exhaustively, the wildcard forfeited, so a new constructor forces every handling site to surface.
- Two fields with an implicit "must agree" relationship → one inductive where the agreement is structural, or a `structure` carrying the agreement as a proof field it never travels without.
- A refinement crossing a boundary → `Subtype {x // p x}` minted once by a smart constructor returning `Except` — parse, don't validate; the interior holds the proof and never re-checks.
- Sameness up to a relation → `Quotient`, the respects-lemmas proven once at the definition instead of re-argued at every use.
- A family varying over data every consumer inspects → an indexed inductive; varying over data only proofs inspect → a plain type with the predicate beside it.
- A predicate that must run → a `Bool`-valued definition, its `Decidable` instance, and the `_iff` bridge stated the same day.
- A statement, always designed twice: pick the simp-normal side and orient every equation toward it; put per-use conditions in named hypotheses and permanent ones in the type; and confirm the induction the main theorem needs is the recursor the chosen type already generates.

Get the shape right and the hard cases stop being special — they were only ever special relative to a representation that did not fit.
</rebuild>

<read_the_ugliness>
Ugliness is the highest-signal diagnostic you have, and the discipline is to read it as *information* rather than pay it as *cost*. Every one of these is the structure reporting that your model is still wrong:

- Casts breeding — `▸`, `Eq.mpr`, `cast` chaining through terms → two types the model treats as the same are equal only propositionally; an index is carrying arithmetic the placement cut says belongs beside the type.
- `HEq` surfacing anywhere → dependent equality across an index that should not be an index.
- "motive is not type correct," recurring across attempts → the goal depends on the very thing being rewritten; the representation entangles what should be orthogonal.
- A case dismissed by `nomatch`/`absurd` on domain grounds → the type admits a state the problem forbids; narrow it, or name precisely why a runtime guard must stand where the type cannot.
- Parallel `Bool` and `Prop` versions of one predicate with no `_iff` between them → one concept in two drifting costumes.
- `h : b ≤ a` threaded everywhere to guard a `Nat` subtraction → wrong carrier; the domain's quantity does not truncate, so compute where it does not (`Int`) or restructure so the difference never forms.
- An index threaded through every signature and inspected by none → extrinsic placement wanted.
- Every proof about `f` opening with `unfold f` → the definition has no reasoning surface; mint its lemma API or fix its transparency (core: lemma_api, two_equalities).
- N declarations identical modulo naming — sibling inductives, lemmas differing by a suffix → a role unnamed; introduce the type or the general lemma that names it and demote the copies to instances.
- A "we keep it sorted" comment where an invariant should be → a quotient or a Subtype avoided by hand-maintained discipline.

This catalog has transpositions, and a smell absent here may sit in one of them: read dynamically it is `debruijn-obligation-modeling`'s (the threaded flag reappears as an induction hypothesis too weak to close the step), and read at the boundary it is `debruijn-experience-modeling`'s (the apologetic comment reappears as a docstring explaining what a lemma "really says"). One diagnostic in three spaces; if the ugliness in front of you matches no entry, check which space it lives in before concluding the model is fine.

When you see these, do not push harder on the current model. Return to `grok` or `shift_perspective` and re-characterize. Cleanness and correctness share a cause — both are properties of a representation that is the true image of the problem — which is why beauty is the convergence test rather than its reward.
</read_the_ugliness>

<validate_the_seams>
A beautiful model can still be wrong at its boundaries. Before trusting it, hunt its breaking points deliberately — and in Lean two of the hunts are mechanical:

- Where does input cross into the model? Every boundary (file, socket, user, `@[extern]` seam) is where incidental structure sneaks in disguised as a precondition. Parse at the boundary into the type that proves the invariant, so the interior never re-checks and never doubts.
- **Exhibit the model of the hypotheses.** Construct one concrete instance satisfying *every* assumption of your main statements — `#eval` it, prove the instance in an `example`. A theorem quantifying over an empty domain elaborates, proves, and means nothing; non-vacuity is the seam most often left unvalidated because the checkmark looks like validation. This is the spec-space face of **the unsampled member**: an inhabitant of the domain your examples never contained — the empty list, the zero index, the equal pair, the next protocol version. Construct it and ask whether the definitions still say what you intend; if it breaks the model, interpolate a bridging case to locate the threshold where the structure dies, and encode that bound or design it away.
- **Adversarial member:** one instance satisfying the letter of every definition while violating the intent. If you can build it, the statement is weaker than the truth it gestures at — strengthen the model, and keep the adversary as a negative test (`example : ¬ …`).
- What states does the type still admit that the domain forbids? Enumerate them; narrow until unrepresentable, or name why a guard must stand in for the type.
- Does the representation earn the next theorem for free? Name the predictable next lemma *before* consulting the model, then check whether it states in the existing vocabulary. If the obvious extension forces a restatement, you modeled the present sample, not the problem.

**Decorrelate the check from the model.** Re-reading a representation you just authored re-samples the prior that produced it; the flaw that survived the writing survives the reading. Independence must be procedural, and Lean supplies independent checkers ready-made — the kernel, `#eval`, `plausible` on the sanity statements — so run the instruments before re-reading the definitions: the unsampled member is drawn from the domain rather than your sample, the illegal-state audit is an enumeration rather than an impression, the next-lemma test names its requirement in advance. When a seam fails twice, return to `grok` in a fresh frame rather than patching the type a third time: the model on the page is now a high-weight exemplar pulling every revision back toward itself.
</validate_the_seams>

<the_loop>
The procedure is not linear. It is a loop you climb until the model converges: grok → shift → deconstruct → rebuild → read the ugliness → and when the ugliness speaks, back to grok with a sharper question. Each pass strips incidental structure and exposes intrinsic structure. You are done when the next pass changes nothing — and in Lean the fixed point reports itself: the statements shorten, the proofs go local, the induction is the recursor, and the file reads as though you discovered it rather than decided it.

That fixed point is the beautiful model, and it is where the siblings pick up: the obligations proven over the representation are `debruijn-obligation-modeling`, the surface that exposes it is `debruijn-experience-modeling`, and a proof or program that later disagrees with the model is `debruijn-debugging`, which diagnoses back to the discrepancy and hands the problem here again. A converged model makes all three cheaper, which is why this pass comes first.

Stop there. Do not add — and read the injunction correctly: an abstraction that collapses N identical declarations into one type plus a multiplicity is subtraction wearing addition's clothes; it deletes the incidental fact of *which copy* and the model shrinks. What the discipline forbids is speculative structure no ugliness demanded — a typeclass with one instance, an index no consumer inspects, a generalization no second use has asked for. "Least representation" is measured after the collapse, never by counting layers: the win is the least representation that is the true image of the problem, and one index more is incidental structure creeping back in.
</the_loop>
