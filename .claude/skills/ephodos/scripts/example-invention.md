# An invention, as a derivation record files it

A worked record in the form `ephodos-invention` gives: Galileo's squares, made into Dedekind's definition of the infinite. It is a
record of a known invention, so it shows the form and not the search — the made description has been in print since 1888. Galileo is
quoted from Crew and de Salvio's translation (1914), Dedekind from Beman's (1901); Bolzano's route and Cantor's argument are recalled,
not read, and every entry carries its own argument.

**The question, fixed.** Which is the larger collection: the positive integers, or the positive integers that are squares?

## The collision

Two held descriptions both apply, and they disagree.
- *By pairing:* 1 ↔ 1, 2 ↔ 4, 3 ↔ 9, …; every integer has its square and every square its root, so the collections match one to
  one, and are the same size.
- *By part and whole:* every square is an integer and not every integer is a square, so the squares are a proper part, and "the
  whole is greater than the part" makes them smaller; counting up to any bound agrees — up to 10,000 there are 100 squares.

Galileo stated the datum in 1638 and dismissed it: "the attributes 'equal,' 'greater,' and 'less,' are not applicable to infinite,
but only to finite, quantities."

## The licence

The ordinary moves, each with the line it fails on.
1. **The dismissal** — declare the concepts inapplicable, as Galileo did. Not a home: it answers nothing, and the question is fixed.
2. **Counting inside a common bound.** Dictionary: size ↔ the number below a bound N. It fails on its bound: the question names
   none, and moving it reverses the verdict — the integers below N against the squares below N, or against the squares below N².
   The line it fails on is that a count needs the collection to end.
3. **Part and whole.** Dictionary: size ↔ inclusion. It fails against the pairing, term by term, and the line it fails on is the
   finite count behind "greater".
Both homes fail at the same place: where the collections do not end.

## The premises

| premise | sort | receipt, and how far it reaches |
|---|---|---|
| two collections are the same size when they pair one to one | earned for finite collections; beyond them, unsorted | for finite collections it *is* counting — counting n things is pairing them with 1, …, n. No receipt reaches collections that do not end; extending it there is a stipulation, not a finding |
| the whole is greater than the part | earned for finite collections; inherited beyond them | the finite receipt is `finite-whole-exceeds-part`, whose *uses only* is induction on n — its reach ends exactly where collections stop ending; beyond, its only support is that every finite description held it |
| the positive integers do not end | earned | every n has a successor n + 1 |
| the squares are a proper part of the integers | earned | 2 is not a square |

The collision uses two premises past the reach of their receipts: the pairing description extends the first, the part-and-whole
description the second. They are two candidates, revised one at a time, the least first. The reach decides the order. Pairing is a
relation — two collections pair or they do not — and its finite receipt consumes nothing that needs an end; part-and-whole is a
consequence of counting, and its receipt consumes an induction that stops at the end of the finite. Keeping the relation and dropping
the consequence beyond its reach is the least revision. The other route keeps part-and-whole and denies that pairing makes collections
equal: it is Bolzano's, and a size of that kind has since been built with a model of its own (both recalled, not read). The sort does
not choose between the two routes; what each lets one derive does.

**The search, before deriving.** In the revision's words — "infinite", "similar to a proper part" — the home is found at once:
Dedekind, 1888. A live derivation would stop here and carry it across by recognition's transfer; this record goes on to show the form.

## The revision

Dedekind's: "64. Definition. A system S is said to be infinite when it is similar to a proper part of itself" — similar meaning paired
one to one. Size is compared by pairing, everywhere; the whole is greater than the part only where its receipt reaches, for collections
that end. The paradox is not dismissed; it is the definition. The revision defines a word the question uses, "larger": the answer below
is in that sense, and whether it is the question that was asked is the poser's to say. Dedekind named the cost as the derivation that
follows: others had noticed the property, and "neither of these authors made the attempt to use this property for the definition of
the infinite and upon this foundation to establish with rigorous logic the science of numbers, and just in this consists the content
of my wearisome labor".

## Squares and integers

The map n ↦ n² sends every positive integer to a square. It is one to one, since m² = n² with m, n > 0 gives m = n. It is onto the
squares, since every positive square is k² for some positive k. So it pairs the integers with a proper part of themselves: under the
revision they are the same size, and the integers are infinite in Dedekind's sense. No step above compares sizes by inclusion — the
drift check for a revision whose old premise no finite control can plant, since on every finite collection the old premise holds.

derivation: squares-and-integers
  statement: the map n ↦ n² pairs the positive integers one to one with the positive squares, a proper part of them
  uses only: that squaring is one to one on positive integers, and that every positive square has a positive root
  not claimed: that squares are as common as integers below a bound — up to N there are only ⌊√N⌋ of them
  argument: § Squares and integers
  verdict: derived
  grade: hand
  minds: 1
  model: n = 3 ↦ 9; and 2, which no integer squares to, so the part is proper
  prior art: known — Galileo 1638 stated the pairing; Dedekind 1888 made it the definition of the infinite
  handoff: none — the collision's datum, now a theorem under the revised premise

control: squares-distinct
  of: squares-and-integers — the pairing's engine on a window: the first 10^4 positive integers have 10^4 distinct squares; the
    fault replaces squaring with squaring mod 1000, which is not one to one
  run: python3 -c "N=10**4;print(len({n*n for n in range(1,N+1)})==N)"
  expect: True
  fault: python3 -c "N=10**4;print(len({n*n%1000 for n in range(1,N+1)})==N)"

## The whole exceeds the part, where it was earned

By induction on n. For n = 1 there is no proper part to map into, save the empty one, which receives nothing. Suppose no set of n
elements pairs one to one with a proper part of itself, and let f be a one-to-one map from {1, …, n + 1} into a proper part of
itself. If n + 1 is not in the image, f restricted to {1, …, n} maps {1, …, n} one to one into {1, …, n} minus f(n + 1), a proper
part. If n + 1 = f(k) for some k, exchange the values of f at k and at n + 1; the new map is still one to one into the same proper
part, and fixes n + 1, so its restriction maps {1, …, n} one to one into a proper part of {1, …, n}. Either way the hypothesis is
contradicted.

derivation: finite-whole-exceeds-part
  statement: for every n ≥ 1, no one-to-one map sends {1, …, n} into a proper part of itself
  uses only: induction on n, and the exchange of two values of a one-to-one map
  not claimed: the same for any set that does not end — the positive integers pair with the squares
  argument: § The whole exceeds the part, where it was earned
  verdict: derived
  grade: hand
  minds: 1
  model: n = 2 — the maps from {1, 2} into {1} are not one to one
  prior art: known — the pigeonhole principle
  handoff: none — the earned result recovered where the old premise held

control: pigeonhole-small
  of: finite-whole-exceeds-part — every set of 1 to 6 elements, every map into a proper part, exhaustively; the fault maps into the
    whole instead
  run: python3 -c "import itertools as I;print(sum(1 for n in range(1,7) for f in I.product(range(n-1),repeat=n) if len(set(f))==n))"
  expect: 0
  fault: python3 -c "import itertools as I;print(sum(1 for n in range(1,7) for f in I.product(range(n),repeat=n) if len(set(f))==n))"

## Infinite collections of different sizes

Suppose s₁, s₂, … lists infinite binary sequences, one for each positive integer. Let d be the sequence whose i-th term is
1 minus the i-th term of sᵢ. Then d differs from every sᵢ at place i, so d is not in the list. No list of the positive integers'
length exhausts the binary sequences.

derivation: infinite-sizes-differ
  statement: no map from the positive integers onto the infinite binary sequences exists
  uses only: that a sequence can be built to differ from the i-th listed sequence at place i, for every i at once
  not claimed: anything about the sizes between the integers and the binary sequences
  argument: § Infinite collections of different sizes
  verdict: derived
  grade: hand
  minds: 1
  model: the list 000…, 111…, 0101…, … — its flipped diagonal begins 1, 0, 1, … and differs from each listed sequence at its own place
  prior art: known — Cantor's diagonal argument (recalled, not read)
  handoff: none — the consequence no earlier description could state

control: diagonal-small
  of: infinite-sizes-differ — every list of three binary words of length three: the flipped diagonal is never on the list; the fault
    leaves the diagonal unflipped
  run: python3 -c "import itertools as I;print(sum(any(tuple(1-m[i][i] for i in range(3))==r for r in m) for m in I.product(I.product((0,1),repeat=3),repeat=3)))"
  expect: 0
  fault: python3 -c "import itertools as I;print(sum(any(tuple(m[i][i] for i in range(3))==r for r in m) for m in I.product(I.product((0,1),repeat=3),repeat=3)))"

## Secured

- **A model of the new premises inside held theory.** The positive integers under n ↦ n²: a collection that pairs with a proper part of
  itself, built from arithmetic already held, so the definition speaks of something. For a definition, consistency is this cheap; the
  model's work is to show the definition is not empty.
- **The earned results recovered where the old premise held.** `finite-whole-exceeds-part`: for collections that end, the whole is
  greater than the part, as it always was.
- **A consequence no earlier description could state.** `infinite-sizes-differ`: under Galileo's description infinite collections
  could not be compared at all; under the revision two of them differ in size. For a definition this receipt measures what the
  definition lets one derive, not whether it is true of the world; it could have failed only in the sense that a pairing of the
  integers with the binary sequences would have refuted it.
- **The collision dissolved.** The pairing and the part both stand; they no longer contradict, because "the whole is greater than
  the part" was never earned where the paradox lives. What was a paradox is `squares-and-integers`, a two-line theorem.

invention: squares-to-infinite
  revises: the whole is greater than the part
  licence: § The licence
  premises: § The premises
  model: squares-and-integers
  recovery: finite-whole-exceeds-part
  consequence: infinite-sizes-differ
  dissolved: § Secured
  old premise planted: none — on every finite collection the old premise holds, so no finite check can plant it; the drift check is
    § Squares and integers, read for a comparison by inclusion

## Look back

*Wonder is no wonder:* once size means pairing, the squares' equality with the integers is the first thing the definition says. *New
in the new words?* No: Galileo held the datum in 1638, Bolzano and Cantor the property, and Dedekind the definition in 1888. *What else
does it say?* Cantor's comparison of infinite sizes follows from it, and is the neighbour `infinite-sizes-differ` states.
