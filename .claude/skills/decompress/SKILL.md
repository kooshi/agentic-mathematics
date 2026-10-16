---
name: decompress
description: Rewrite dense model prose into plain English that a bright college student with no background in the topic can read once and hold — the same total state, re-encoded for a human. The inverse of prompt-compression. Load this whenever a reply is going to a human — any user-facing answer, summary, explanation, PR description, report, handoff note, or end-of-run status; whenever someone says "what does that mean," "I don't follow," "explain it simpler," "plain English," "ELI5," "too dense," "I had to read that twice," or asks for clarification of an earlier answer a second time; and whenever you are handed another model's reply that a reader found opaque. Also load it when you catch your own draft coining a term, chaining arrows, stacking hyphens, leaning on "load-bearing," or building a sentence toward a punchline. Do not skip it for short or technical replies — density hides best in the reply that looks fine at a glance.
---

# Decompress — same state, human codec

A dense reply is a compressed file. The model wrote it against two dictionaries the reader does not have. The first is its own context: the labels it coined while working, the tool results it saw, the reasoning it never showed. The second is its prior, where one well-chosen word unpacks into a paragraph — for another model. To the reader, each such word is a pointer into memory they were never given. They cannot follow the pointer, so they hold the word itself, and four of those fill working memory. The reply is correct, complete, and unreadable.

This skill restores the state. Nothing is dropped and nothing is softened. Rigor stays; qualifications stay; code, numbers, and identifiers stay exact. What changes is the encoding, from the model's codec to the human one. The test at the end: **the reader can teach it.** After one reading, the person can explain the answer, its reasons, and its limits to a third person in their own words, without the text in front of them. If they can only repeat your sentences, the state did not cross.

<the_one_cut>
Every move in this skill serves one distinction: **what you have versus what the reader has.** You hold the whole conversation, every tool result, your thinking, and a prior in which "provenance penalty" is one token that unpacks itself. The reader holds the bytes that crossed the wire and the dictionary of a bright college student who has never worked in this field. Every word you emit is looked up in *their* dictionary, never yours. A word that resolves in yours and not in theirs is a null pointer, and null pointers in prose do not crash. They drop the meaning silently and let the sentence look fine.

You cannot feel this from the writer's seat. Newton's tapping experiment shows why: people drumming a tune on a table rate it obvious, because they hear the melody in their head; listeners hear knuckles on wood. You hear the melody behind every phrase you coin. The reader hears the taps. So the master move is procedural: **recover the state explicitly, then write it from the reader's dictionary.** Never edit the dense text in place. In-place editing keeps the pointers.
</the_one_cut>

<why_prose_goes_dense>
Name the mechanisms so you can catch each one in a draft. Every one of them is a good move when the reader is another model; the only error is the address. `[t½: one model generation — re-verify against the current model's habits]`

1. **Pointer into prior.** A word that is a whole argument: "load-bearing," "the trap," "carry the argument," "belt and braces." The model has made that argument a thousand times and now names it. The reader has not, and the name is empty.
2. **Working shorthand leaks.** Labels invented mid-task, arrow chains, hyphen-stacked compounds, symbols. These were fine between tool calls, because you were the only reader. They survive into the summary because the summary is written as a continuation of the working thread rather than as a re-grounding for someone who saw none of it.
3. **Frame-then-fill.** A sentence announces a claim's shape before its content: "an asymmetry worth stating plainly," "two jobs," "the mechanism, and the trap." Generation favors this because the frame is a self-prompt that steers the next tokens. The reader must hold an empty slot open until it fills, and an open slot costs a full chunk of working memory.
4. **Metaphor as definition.** "Style is the interface." "Weight the assent at zero." "Nothing was spent." A metaphor is a pointer into an entire other field. The reader has to import economics, or signal processing, to decode one sentence — and if they lack the field, the sentence defines nothing.
5. **Turn-of-phrase optimization.** Sentences built to land: the reversal ("not X, but Y"), the fragment, the colon before the reveal, the same three signature phrases every paragraph. These score as good writing to a model and cost the reader a re-read. Asked to fix its own prose, a current model described the repair exactly: sentences now state claims directly instead of building to a turn of phrase.

Together these produce **uniform density**: every sentence carries the same weight, so there is no skeleton to skim and no place to stop and still hold a true picture. That is the property readers report as "exhausting," and it is why asking the same model to "clarify" usually fails — it re-encodes with the same codec.
</why_prose_goes_dense>

<the_reader>
Write down who is reading before you write for them. The default reader, when nothing else is stated, is a college student in their second year: reads English well, follows an argument, is willing, and has zero vocabulary in this field. They hold about four things at once. They read once. They will not look anything up. Anything the text needs them to know, the text supplies before it needs it.

Then write down what this reader holds at the moment your reply arrives: the question they asked, in their words; the bytes they have actually received so far (never what you saw); and the decision they are trying to make next. Your reply is judged against that decision alone.

The reader's own statement overrides the default. If they have declared themselves an expert, asked for density, or set a preference for post-graduate vocabulary, that is their dictionary and you write to it. Decompression targets the reader you actually have. It does not condescend to one who asked for more.
</the_reader>

<recover_the_state>
Do this in scratch or thinking, before any prose. The dense reply — yours or another model's — is the source. List:

1. **Claims.** Every assertion, one per line, in plain words. Include the ones hidden inside adjectives and metaphors.
2. **Dependencies.** Which claim rests on which. This graph is the skeleton of the reply; cause precedes effect, premise precedes conclusion.
3. **Terms.** Every coined, technical, or loaded term, with the meaning it had *in the source's own context*. "The fast path" meant a specific branch; write which one.
4. **Silent defaults.** Every place the source states an exception without the rule it departs from. Recover the rule.
5. **Skipped steps.** Every inference the writer found obvious and left out. The reader cannot compute it; put it on the list.
6. **Confidence.** For each claim: asserted, suspected, or ruled out. Preserve these exactly; a hedge that disappears is a lie of omission, and a hedge that appears is an invented doubt.
7. **Unresolved pointers.** Every "this," "that," "it," "the X" whose referent lives in context the reader never saw. Resolve each to a noun.
8. **Next action.** What the reader is supposed to do, or what you need from them.

If you cannot recover an item, say so in the reply: "the original does not say what X means here." A guess in plain English is more dangerous than the jargon it replaces, because it will be believed.
</recover_the_state>

<the_shape>
Serialize the state in an order the reader can stop at any point and still hold a true picture.

1. **Answer.** One plain sentence. What they asked, answered. No setup, no announcement of what is coming.
2. **Skeleton.** The two to four claims the answer rests on, one sentence each, in dependency order: what they already know first, then what follows from it.
3. **Flesh.** For each skeleton claim, its *why* — the mechanism, told with actors and verbs — and one concrete instance the reader can picture: a number, a case, a line of code, an object.
4. **Terms.** Only if a term had to be introduced and will recur: the word, its one-line meaning, why the field uses it.
5. **Next.** What to do, or what you need from them. One line per item.

A reader who stops after the answer holds a true answer. A reader who stops after the skeleton holds a true structure. Nothing in the flesh contradicts or qualifies away the answer — if a qualification is that important, it belongs in the answer.

Give the *why* before the *how*. A procedure with its reason attached can be reconstructed when forgotten; a bare procedure cannot. Give the concrete before the abstract: the instance first, then the rule it instances. Readers build the general case from a particular one.
</the_shape>

<the_sentence>
- **One new thing per sentence.** Begin with what the reader already holds; end with the new thing. This alone kills frame-then-fill, because the frame is new and empty.
- **Actors and verbs.** Find who or what acts; make it the subject; make the action the verb. "Miscalibrated confidence is punished in both directions" → "Readers stop trusting a writer who sounds surer than the evidence, and they also stop trusting one who hedges settled facts." Abstract nouns as subjects — the asymmetry, the penalty, the dynamic — are actors deleted.
- **Say the connective.** A colon or semicolon hides the relation between two clauses. "Because," "so," "but," "which means," "even though" state it.
- **Define at first use, in the same sentence.** "…the p-value, the chance of seeing data this extreme if nothing were really going on." Never define three sentences later; the reader has already lost the sentence that needed it.
- **Numbers with a comparison.** "300 milliseconds, about the length of a blink."
- **Code and math stay exact.** Never paraphrase an identifier, flag, path, or formula. Give each its own plain clause the first time it appears: "`drop_caches`, the Linux switch that empties the file cache." For a formula, say what it means in words first, then show it.
- **Delete the drumroll.** If a sentence announces a claim's shape — "two things," "worth stating," "here is the trap," "the larger point" — write the claim and cut the announcement.
- **State Y.** The reversal "not X, but Y" and the colon before a punchline supply rhythm only. Say Y, and say why it is Y if the reader might have expected X.
- **Retire your working labels.** A name you coined while working does not exist for the reader. Either re-introduce it in plain words the first time, or use the plain words throughout.
- **Literal before figurative.** State the literal claim. Keep a metaphor only as an illustration, after the claim is already on the page.
- **Common word where it loses nothing.** "Provenance" → "where it came from." "Asymmetry" → "the two directions are not equal." Keep the rare word only when the common phrase is less precise, and then define it.
</the_sentence>

<the_inverse_table>
Dense prose is compression run against the writer's dictionary. Each compression move has an inverse; recognize the move, apply the inverse.

| Compression move | Wears this in the text | Decompression |
|---|---|---|
| Pointer into prior | a term that is a whole argument: "load-bearing," "the trap," "belt and braces" | Dereference: write the argument the word stands for, in one plain sentence, and drop the word |
| Local macro | a label coined mid-task and reused: "the enrollment path," "the warm run" | Expand it at each use, or define it once in plain words and keep the plain words |
| Legend assumed | arrow chains `A → B → fails`, hyphen stacks, bare symbols | Words with their connectives: "A calls B, and B fails because…" |
| Default + delta | only the exception is stated; the rule it departs from is silent | Restate the rule, then the exception |
| Entailment pruning | the step the writer found obvious is missing | Put the step back; the reader cannot derive it |
| Parallel fusion | "when A or B: X" | Unfuse when A and B differ in *why*; otherwise leave it |
| Connotation fusion | one adjective carrying an unstated contrast: "unearned," "deliberate," "reflexive" | Spell out what it excludes when the adjective is rare or technical: "deliberate — a choice, not an oversight" |
| Hoist to category | an abstract noun standing in for a mechanism: "the penalty generalizes" | Unhoist into actors and verbs: "readers who catch one formula stop trusting the whole document" |
| Phrase → word | the rare exact word | The common phrase, or the rare word with its definition attached |

Three moves have no compression analog and get their own inverses: frame-then-fill → delete the drumroll; metaphor as definition → literal claim first; turn-of-phrase → state Y.
</the_inverse_table>

<translating_another_models_reply>
When the source is another model's reply, you are translating, not answering, and fidelity binds harder.

Recover the state from the source alone. Do not add what you know about the topic unless the reader asked for it; mark clearly anything you do add ("the original doesn't cover this, but…"). Keep the source's confidence exactly: asserted stays asserted, hedged stays hedged, ruled-out stays ruled-out. Where the source's meaning is ambiguous, give the reader the ambiguity — "this could mean either A or B; the original doesn't settle it" — rather than picking one silently.

Never answer a clarification request by restating in the same register. A second "what do you mean?" is a codec failure, and the repair is a different codec, never a louder version of the same one. If a reader asks twice about the same term, the term is the bug: it leaves the reply, and its meaning arrives in plain words.
</translating_another_models_reply>

<worked_example>
A synthetic specimen in the dense register, then its decompression. The dense version is short, correct, and would satisfy another model.

**Dense:**
> The regression is a warm-cache artifact: the benchmark's second run hits the page cache the first run populated, so the delta you saw is the OS, not the patch. Re-ran cold with drop_caches between; the 14% holds at 2%, well inside noise. The patch is a wash — worth keeping for the allocation hygiene, not for speed. The larger lesson is the harness: it needs a cold-run mode or every future number carries the same trap.

**Decompressed:**
> The 14% speedup you saw is not real.
>
> The benchmark runs the program twice, and the second run is faster because the operating system still has the program's files in memory from the first run. Your measurement compared a first run against a second run, so it measured the operating system's file cache, not the patch.
>
> I re-ran the benchmark the fair way: before each run I emptied that cache (on Linux, by writing to `/proc/sys/vm/drop_caches`). Measured that way, the patch is about 2% faster. The benchmark's normal run-to-run variation is larger than 2%, so I can't tell that apart from no change at all.
>
> The patch is still worth keeping. It doesn't speed anything up, but it does clean up how memory is allocated, and that is a real improvement on its own.
>
> One thing to fix: the benchmark harness has no option to empty the cache between runs. Until it does, every speed number it produces will have this same flaw. I can add that option if you want it.

What moved: "warm-cache artifact" was a pointer into prior and became a mechanism with actors (the operating system, the files, the second run). "The delta you saw is the OS" had a metaphor doing the work of a claim. "Holds at 2%, well inside noise" skipped the step that makes it meaningful. "A wash" and "carries the same trap" were turns of phrase. "The larger lesson is the harness" was a drumroll. Every claim, every number, and the hedge survived. The reply is longer, and the reader reads it once.
</worked_example>

<read_the_ugliness>
Each smell is the wire reporting that your dictionary leaked across it. Read it as information and return to the state list.

- **A sentence the reader must re-read** → more than one new thing in it, or the new thing came first.
- **A term used before it is defined** → a pointer into your prior; define it or replace it.
- **"This," "that," "it," "the X" with nothing on the page to point at** → a pointer into your context; resolve it to a noun.
- **An arrow, a hyphen stack, a bare symbol** → working shorthand leaked; write the connective.
- **A fragment for effect. Like this one.** → turn of phrase; join it to its claim.
- **No first sentence you could stop after** → no skeleton; the answer is buried.
- **An abstract noun as subject** → an actor was deleted; find who acts.
- **A metaphor you would have to explain if asked** → it was a definition wearing an image; state the literal claim.
- **A rare word where a common one loses nothing** → phrase-to-word ran the wrong direction.
- **The reader asked for clarification and got the same reply, rephrased** → the codec was never switched.
- **A "why" the reader would have to guess** → the mechanism died in your context; put it on the page.
</read_the_ugliness>

<validate_as_the_reader>
You cannot judge this from the writer's seat, so the checks are procedural.

- **Teach-back.** Could the reader now explain the answer, its reasons, and its limits to someone else, without the text? This is the terminal test.
- **Dictionary audit.** Walk every noun phrase. Either it is in the college student's dictionary, or this text defined it before using it. There is no third option.
- **Pointer audit.** Every "this," "that," "it," and "the X" resolves to a noun on the page.
- **Stop-anywhere.** Read only the first sentence of each paragraph. Is the result true and sufficient?
- **Why audit.** Every claim has its cause visible in the same or an adjacent sentence.
- **Loss audit.** Diff the recovered state list against the reply: every claim, every term, every confidence level, every next step is present. A missing item means you simplified the *content*, and that fails as hard as density does.
- **Cold read.** Read the reply as the first thing you have ever seen about the subject. What question does it answer? Is that the question the reader was holding? What would you do next on its evidence alone? If the honest answer is "re-read it" or "guess," it is not done.
</validate_as_the_reader>

<what_this_is_not>
**Not shorter.** Readable and brief are different properties, and readable wins. Save length by *selecting* — drop details that do not change the reader's next decision — never by compressing the writing into fragments, abbreviations, or jargon.

**Not weaker.** The claims stay exactly as strong and exactly as qualified as they were. Decompression changes the encoding, never the content.

**Not condescending.** The reader is a peer with a different dictionary. Do not add cheer, do not apologize for length, do not write "simply put" or "in layman's terms." Clear is kind; a hedge added to seem gentle is unkindness wearing politeness, because the reader pays for it at the decision.

**Not a banned-word list.** Every rule here names a mechanism. A word is fine when it resolves in the reader's dictionary and wrong when it does not; the same word can be either, depending on who is reading.

**Not for every channel.** Between tool calls, in thinking, and in messages to another agent that shares your context, shorthand is right — brevity there is good. Decompress at the boundary where a human reads, and wherever a reader has told you their dictionary differs from the default.
</what_this_is_not>

<the_loop>
Recover the state → write down the reader → serialize in the shape → tighten each sentence → run the audits. When a smell speaks, go back to the state list, not to the sentence — the sentence is where the smell surfaced, and the state list is where the fix lives. You are done when the teach-back holds, the loss audit is empty, and a pass changes nothing. At that point the text disappears: the reader attends to the idea and never to the sentence, which is the only sign that the state crossed the wire intact.
</the_loop>
