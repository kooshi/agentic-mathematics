---
name: debruijn-experience-modeling
description: Procedure for designing any surface a Lean user consumes — lemma APIs, simp sets, error messages, tactic output, notation, docstrings, library interfaces, macro and elab diagnostics — by modeling the experience from the user's side of the wire, where the user may be a human, an AI agent, or the automation itself (simp, exact?, grind read your library too). Invoke when deciding what a lemma set should contain, how an error or "Try this:" should read, which arguments deserve instance-implicit versus explicit, whether to mint notation, or how a proof-facing API should feel; when users (or you, dogfooding) unfold a definition to prove anything, fumble the same instance twice, or when exact? never surfaces your lemma. Models the boundary from outside rather than the system from inside; its subject is not the problem but the person — or the procedure — consuming it. Assumes the de Bruijn core is loaded.
---

# de Bruijn — Experience Modeling

The two modeling siblings shape the system from inside: types as the image of the data's structure, statements as the image of the argument's structure. This skill is the same doctrine at the boundary, with the subject inverted — the structure to characterize is no longer the problem's but the **user's**: their goal state, their context, their constraints at the moment your output arrives. The surface is the image of the user's situation, and a surface that is instead the image of the implementation — its internal names, its unfoldings, its convenience — is the boundary's incidental structure: it elaborates, it ships, and it lies about what the user needed. The user is whoever consumes the surface, and in Lean the constituency is wider than anywhere else: a human reading the InfoView, an AI agent whose entire world is a context window, and the automation itself — `simp`, `exact?`, `aesop`, `grind` walk your lemma API with no capacity for insight and total dependence on what you tagged. One discipline for all three; the machine cases merely make it exact. This suite's own core was derived by running this pass with the toolchain as the user — that is not an anecdote but the standing move, available whenever the consumer is a procedure.

The terminal test, the analogue of the beautiful model and the derived statement: **the tool disappears.** Heidegger's hammer withdraws into use — the prover attends to the mathematics, never the library — and becomes an object only by breaking. A surface is done when attention passes through it without snagging: the next lemma is the one `exact?` returns, every emitted name elaborates when fed back, and the user's model of the library — learned entirely from your outputs — keeps predicting it correctly. The lineage: Heidegger's equipment analysis via Winograd and Flores; Norman's gulfs, with his verdict that user error is design error; Grice's maxims, because a response is a turn in a conversation; and Mathlib's conventions, a decade of watching ten thousand users search. Drive toward disappearance deliberately; the procedure below is how.

<the_one_cut>
Every technique here serves a single discrimination: **what the system knows versus what the user has.** The surface is a wire, and the user's world is exactly what crossed it. The unifier's candidates, the instances tried and rejected, the author's knowledge of which normal form the set drives toward, the fact that a search was exhaustive — none of it exists for the user until serialized: into an error message, a docstring, a lemma name, a tag. For the machine constituency the cut is absolute — `simp` knows precisely the lemmas tagged `@[simp]` and nothing you meant; `exact?` knows the shape of your statement as indexed, not the theorem in your head. The attributes *are* the serialization to the machine user.

The characteristic failure is the curse of knowledge: the author can unfold the definition mentally, so every simulation of the user runs contaminated — the author hears the melody; the user hears knuckles on a table. In Lean the contamination has a syntax: reaching for `unfold` in your own downstream proofs is the author's frame leaking — the user cannot unfold what your transparency sealed, and should not need to.

The master move: **cross the wire and take only the bytes.** For the machine user, drop "reconstruction" — the context is enumerable: the simp set, the instances in scope, the discrimination-tree shape of each statement. Human UX must imagine its user; machine UX can audit it, and `set_option trace.Meta.Tactic.simp true` is the audit.
</the_one_cut>

<inhabit_the_user>
Before judging any surface, write down what its consumer holds at the moment of use. The human holds the goal in the InfoView and whatever your docstring taught; the description read at import has been fading since. `simp` holds exactly the tagged set. `exact?` holds statement shapes — which makes the *form* of your statement its discoverability: a lemma stated on the wrong side of an iff, over-bundled, or in a nonstandard argument order is a lemma that exists and cannot be found. An agent holds schema, descriptions, and the responses so far — the complete, enumerable inventory.

Everything durable the user knows about your library, your library taught them, and in Lean the mental model has a name: the **naming convention**. `add_comm`, `le_trans`, `map_map` let a user predict names they have never read — the convention is a contract that turns your whole library into recognition rather than recall, which is why one deviant name plants false beliefs across every future guess. The same authority discipline follows: a stated lemma arrives with total authority, so a docstring's informal gloss that the formal statement does not back is a certainty you claimed and never established.

Then the cold read: take one docstring-plus-signature and read it as the first thing about the library you have ever seen. What question does it answer? Is that the question a user mid-proof was holding? What would you try next on its evidence alone? If the honest answer is "unfold it and see," the surface has failed before any correctness question is reached.
</inhabit_the_user>

<walk_the_conversation>
The unit of experience is not the lemma but the session — a proof attempt walking goal → search → apply → new goals toward closure. Design paths, not endpoints: for each goal shape your library makes common, the closing lemma should exist, be the one `exact?` returns, and be the one the convention predicts. Grice's maxims are directly operational at every turn. **Quantity**: the error carries what the next decision requires — no more, and no metavariable internals. **Quality**: assert only what you established; a "Try this:" must elaborate when pasted. **Relation**: answer the goal the user holds, not the state the system finds convenient to print. **Manner**: the answer leads; one vocabulary throughout.

Implicature does silent work, so design it: an API stating one direction of an equivalence implies the other is false, hard, or forgotten — state both or say which; an `ext` lemma present implies componentwise is the way in; a simp set implies a destination, and a set with no stated normal form makes every user infer their own. Completeness must be checkable, never inferred from silence.

Each turn must fund the next, and in Lean the round-trip law is mechanical: **what you print must re-elaborate.** Delaborators exist to keep output pasteable; a suggestion your tactic emits is only honest if it works verbatim (`exact?`'s "Try this:" is the genre's exemplar — join it); an error naming a candidate lemma must name one that exists, which means meta code queries the environment before emitting, exactly as the core demands of you.
</walk_the_conversation>

<budget_attention>
One scarce resource wears three costumes here: working memory for the human — about four chunks; context tokens for the agent — a window shared with the task, hard-capped by harnesses regardless of your taste `[t½:~12mo]`; and **heartbeats for the automation** — every `@[simp]` lemma taxes every simp call forever, every instance taxes every synthesis, so a simp set is a curated attention budget and never a dumping ground (core: global_speech_acts, seen from the consumer's side).

The budget splits on one line: what the next step needs goes in the response; what might be needed later goes behind a named handle whose existence the response states. Progressive disclosure has a native form — the docstring states the one-line contract, the lemma API is the named handle set, and the source is a last resort no workflow may require: a def whose users must unfold it is a dump, a def with no lemmas is a hide, and the API is the point.

Defaults are the interface. The zero-annotation call is the most-travelled path, so instance resolution *is* your default behavior — make the canonical instance the found one. An `autoParam` (`(h : 0 < n := by positivity)`) is the zero-argument path made safe: the common case discharges silently, the uncommon case states its proof. Notation is compression the reader must decompress on every read: mint it only where the domain already owns it, at the precedence that parses as it reads aloud — novel notation for a domain that had none is a knob levied on every reader forever.
</budget_attention>

<let_breakdown_teach>
Breakdown is when the library stops being transparent and becomes an object, so the error path is experience design at its most concentrated — and the least designed, because the author never makes the errors. Design it first: the surface's response to being misused *is* its quality. Model the genre on the elaborator's own: an error is an obligation description, never a rebuke (core: the_conversation), and yours should teach the way "failed to synthesize" teaches.

The contract has three clauses, each knowledge the system held at the moment of failure. What happened, in the *user's* vocabulary — the goal's terms via `throwErrorAt ref m!"…"` with the span where the user is looking, never internal metavariable numbers naming a plausible wrong subject. In which space the judgment was made — "no lemma tagged `@[foo_simp]` matches" lets the user distinguish a bad goal from a bad set; a bare "failed" breeds false diagnoses. And what to do next, concretely, pasteable — the candidates computed while failing die unserialized unless you emit them.

Worse than any error is the silent non-error: the custom tactic that no-ops without failing, the `try tac` that converts failure into silence, the macro that swallows syntax it did not recognize — accepted-and-ignored input forks the user's model from reality with no signal, and they will debug a system that does not exist. Core `simp` fails on no-progress for exactly this reason; your tactics match it. Parse, don't validate, at the syntax boundary — reject early, with the span. And when every user fumbles the same argument — the instance everyone passes explicitly, the hypothesis everyone supplies in the wrong form — the argument is the bug: fix the instance's discoverability or the statement's shape, because a design that requires more careful users has delegated its job.
</let_breakdown_teach>

<read_the_ugliness>
Each smell is the wire reporting that the author's frame leaked across it; read it as information:

- **A docstring explaining what the lemma "really says"** → the statement failed manner, and the docs are its apology — the sibling's apologetic comment, at the boundary.
- **Every use site opening with the same three-lemma `simp only` preamble** → the normal form is wrong, or a bundling lemma is missing; the repeated fact wants folding into one name.
- **Downstream proofs that `unfold` your definition** → the reasoning surface is missing; mint the lemma API (core: lemma_api).
- **`exact?` never returns your lemma for the goal it was written to close** → shape-discoverability failed; restate in the form the search queries.
- **A "Try this:" that does not elaborate when pasted** → the round-trip law broken; the conversation dead-ends mid-sentence.
- **Internal names, metavariables, or universe params in a user-facing error** → the internals crossed the wire and the needed candidate did not.
- **An instance every user writes explicitly** → synthesis cannot find it; the priority or shape is the bug, and user error is design error.
- **A tactic whose failure mode is silence** → accepted-and-ignored; the model forks and nothing said so.
- **"They should read the module docs"** → the author's frame talking; at the moment of use, context not in the goal view or the response does not exist.

Push harder on none of these. Return to the user's context with the smell as the sharper question.
</read_the_ugliness>

<validate_as_the_user>
You cannot judge your own surface from the author's seat — the knowing cannot be suspended, only bypassed, and in Lean the bypasses are unusually mechanical.

Run the **new-import test**: a fresh file, `import YourLib` alone, the advertised workflow attempted cold — the naive first call, and the response must teach the second. Run the **API-only proof**: prove a downstream property using public lemmas exclusively, `unfold` forbidden — every place your hand reaches for the source is a hole in the surface. **Probe the machine users directly**: hand the common goals to `exact?`, `simp`, `grind` and watch whether your lemmas surface; automation is a user whose think-aloud is always on — `trace.Meta.Tactic.simp` is its transcript, and the lemma never fired is the lemma never discovered. Make the plausible mistakes from the fixed list — the misspelled name, the wrong-direction rewrite, the missing instance import — each a deliberate probe of the breakdown surface. And pin the wire itself: **`#guard_msgs`** asserts the exact rendered error or output text as a test, putting the experience under regression control — the serialized surface, not the API behind it, is the product, and here it is the artifact under CI. `[t½:~6mo]`

Read the transcripts you are handed free: an agent's tactic trace and a human's abandoned proof attempt are think-aloud protocols — where they hesitated, what they tried, what they concluded from your silence. The metric is the user's work per task — round trips, unfolds, re-searches, bytes read per goal closed — never the beauty of any single lemma. A maximally general statement that forces three specializations per use lost to the plain ones that didn't.
</validate_as_the_user>

<the_loop>
Inhabit → walk the conversation → budget → walk the breakdowns → validate as the user, and when a smell speaks, back to the user's context with a sharper question. Each pass moves another piece of the author's knowledge across the wire — into a name, a tag, a docstring, an error — or deletes another demand the task never made. You are done when a session transcript reads as a cooperative conversation — every turn the reply a colleague mid-proof would have wanted — and the next pass changes nothing. That fixed point is the disappearing tool.

The siblings pick up where this pass hands off: a surface that resists because its *representation* is wrong returns to `debruijn-domain-modeling`; the obligations a surface's claims rest on are `debruijn-obligation-modeling`'s; a user report that contradicts your model of the surface is `debruijn-debugging`'s inverse pass, and its answer is an observation. Stop there. The win is the least surface that is the true image of the user's task, and one unrequested byte — one more simp lemma, one more notation, one more knob — is the author's frame creeping back across the wire.
</the_loop>
