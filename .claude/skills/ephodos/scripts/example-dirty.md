# A derivation record that fails the gate by design

Each block below is valid except for one planted defect, named in its heading line — or, for a verification, which must
carry its entry's name, and for an invention, in the line above it — so the gate's output reads as a list of the ways a sentence escapes its
argument. The self-test: `derive_gate.py all example-dirty.md` exits non-zero and prints one FAIL per defective block, and one
warning for each of nine: a control hidden in a code fence; "the only" with no converse declared; a verification whose
comparison has not been made; a verification whose verdict disagrees with its entry's; a second mind not carried to the entry;
a divergence table with no rows; a truth divergence sent to a third mind; a second mind whose given names the sketch; and an
invention with no model, which is graded a conjecture. The
stalled and refuted entries are not defects; the entry that derives from the stall is.

derivation: base
  statement: the sum of two even integers is even
  uses only: that each is 2k for an integer k, and that the integers are closed under addition
  not claimed: that an even sum has even summands — 1 + 3 = 4
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 2 + 4 = 6
  prior art: known — elementary
  handoff: none — an exercise

verification: base
  statement: the sum of two even numbers is even
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.99
  verdict: derived
  method: the last binary digit, where the entry wrote 2k + 2m
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every pair of even integers below 100
  minds: 1 — the author's own check, filed as an example
  grade: hand

derivation: verdict-not-in-vocabulary
  statement: the product of two odd integers is odd
  uses only: that each is 2k + 1 for an integer k
  not claimed: that the product of an odd and an even integer is odd
  argument: § Arguments
  verdict: done
  grade: hand
  minds: 1
  model: 3 · 5 = 15
  prior art: known — elementary
  handoff: none — an exercise

derivation: bare-argument
  statement: the square of an odd integer is odd
  uses only: that an odd integer is 2k + 1
  not claimed: that every odd integer is a square
  argument: clearly
  verdict: derived
  grade: hand
  minds: 1
  model: 3² = 9
  prior art: known — elementary
  handoff: none — an exercise

derivation: argument-nowhere
  statement: the sum of an even and an odd integer is odd
  uses only: that the integers split into 2k and 2k + 1
  not claimed: that the sum of two odd integers is odd
  argument: § The missing section
  verdict: derived
  grade: hand
  minds: 1
  model: 2 + 3 = 5
  prior art: known — elementary
  handoff: none — an exercise

derivation: rider
  statement: the sum of two odd integers is even; more generally, the sum of any even number of odd integers is even
  uses only: that each is 2k + 1
  not claimed: that an even sum has odd summands
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 1 + 3 = 4
  prior art: known — elementary
  handoff: none — an exercise

derivation: converse-owed
  statement: an integer n is even if and only if n² is even
  uses only: that (2k)² = 2(2k²)
  not claimed: anything about rationals
  converse: owed
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: n = 6, n² = 36
  prior art: known — elementary
  handoff: none — an exercise

derivation: uses-only-repeats
  statement: the difference of two even integers is even
  uses only: the difference of two even integers is even
  not claimed: that an even difference has even terms — 5 − 3 = 2
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 6 − 2 = 4
  prior art: known — elementary
  handoff: none — an exercise

derivation: not-claimed-missing
  statement: three consecutive integers contain a multiple of 3
  uses only: that the residues mod 3 of n, n + 1, n + 2 are all distinct
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 4, 5, 6
  prior art: known — elementary
  handoff: none — an exercise

derivation: vacuous-model
  statement: every group of order 1 is abelian
  uses only: that a group of order 1 has one element
  not claimed: that every abelian group has order 1
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: none
  prior art: known — elementary
  handoff: none — an exercise

derivation: off-ladder
  statement: a prime greater than 3 is 1 or 5 mod 6
  uses only: that residues 0, 2, 3, 4 mod 6 are divisible by 2 or 3
  not claimed: that every n ≡ 1 or 5 (mod 6) is prime — 25
  argument: § Arguments
  verdict: derived
  grade: proved
  minds: 1
  model: 7 ≡ 1 (mod 6)
  prior art: known — elementary
  handoff: none — an exercise

derivation: measured-called-derived
  statement: n² + n + 41 is prime for every n from 0 to 39
  uses only: a table of forty values
  not claimed: that it is prime for n = 40 — 40² + 40 + 41 = 41²
  argument: § Arguments
  verdict: derived
  grade: measured
  minds: 1
  model: n = 0, 41
  prior art: known — Euler's polynomial
  handoff: none — an exercise

derivation: unfenced-second-mind
  statement: the sum of the first n odd numbers is n²
  uses only: induction on n and (n + 1)² − n² = 2n + 1
  not claimed: any statement about even numbers
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 2
  model: n = 3, 1 + 3 + 5 = 9
  prior art: known — elementary
  handoff: none — an exercise

derivation: new-without-search
  statement: 7 divides 2^(3k) − 1 for every natural number k
  uses only: that 2³ = 8 ≡ 1 (mod 7)
  not claimed: the converse, that 7 divides 2^m − 1 only when 3 divides m — true, and not proved here
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: k = 1, 8 − 1 = 7
  prior art: new
  handoff: none — an exercise

derivation: known-without-source
  statement: 9 divides 10^k − 1 for every natural number k
  uses only: that 10 ≡ 1 (mod 9)
  not claimed: that 99 divides 10^k − 1 for every k — k = 1 gives 9
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: k = 2, 99
  prior art: known
  handoff: none — an exercise

derivation: handoff-without-reason
  statement: 3 divides n³ − n for every integer n
  uses only: that n³ − n = (n − 1)n(n + 1) and one of three consecutive integers is a multiple of 3
  not claimed: that 9 divides n³ − n — n = 2 gives 6
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: n = 2, 6
  prior art: known — elementary
  handoff: none

derivation: base
  statement: the sum of two even integers is even
  uses only: that each is 2k for an integer k
  not claimed: that an even sum has even summands — 1 + 3 = 4
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 2 + 4 = 6
  prior art: known — elementary
  handoff: none — a second entry under a name already used

control: output-mismatch
  of: base — forward, on pairs below 50
  run: python3 -c "print(sum((a+b)%2 for a in range(0,50,2) for b in range(0,50,2))+1)"
  expect: 0
  fault: python3 -c "print(sum((a+b)%2 for a in range(0,50,2) for b in range(1,50,2)))"

control: cannot-fire
  of: base — forward, on pairs below 50
  run: python3 -c "print(0)"
  expect: 0
  fault: python3 -c "print(0)"

control: no-fault
  of: base — forward, on pairs below 50
  run: python3 -c "print(sum((a+b)%2 for a in range(0,50,2) for b in range(0,50,2)))"
  expect: 0

derivation: comma-iff-no-converse
  statement: an integer n is odd if, and only if, n² is odd
  uses only: that (2k + 1)² = 2(2k² + 2k) + 1
  not claimed: anything about rationals
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: n = 3, n² = 9
  prior art: known — elementary
  handoff: none — an exercise

derivation: exactly-the-no-converse
  statement: the integers n with n² ≡ 1 (mod 8) are exactly the odd integers
  uses only: that (2k + 1)² = 4k(k + 1) + 1 and k(k + 1) is even
  not claimed: the same statement mod 16 — 3² = 9
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: n = 5, 25 = 3 · 8 + 1
  prior art: known — elementary
  handoff: none — an exercise

derivation: stalled-lemma
  statement: every even integer greater than 2 is a sum of two primes
  argument: § Arguments
  verdict: stalls at: no argument covers every even integer

derivation: derived-from-a-stall
  statement: every even integer from 4 to 100 is a sum of two primes
  uses only: the stalled lemma, restricted to 4 ≤ n ≤ 100
  not claimed: anything above 100
  argument: § Arguments
  verdict: derived
  grade: derived from: stalled-lemma
  minds: 1
  model: 4 = 2 + 2
  prior art: known — Goldbach's conjecture, checked far beyond 100
  handoff: none — an exercise

derivation: possible-two-way
  statement: 2 is the only even prime
  uses only: that every even integer greater than 2 has 2 as a proper divisor
  not claimed: that 2 is the only prime of any other parity class
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 2
  prior art: known — elementary
  handoff: none — an exercise

verification: off-ladder
  statement: a prime greater than 3 is 1 or 5 mod 6
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: agrees
  method: the residues mod 6 listed, as the entry did
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every prime below 1000
  minds: 1 — the same route as the entry
  grade: hand

derivation: odd-square
  statement: the square of an odd integer is 1 mod 8
  uses only: that (2k + 1)² = 4k(k + 1) + 1 and that k(k + 1) is even
  not claimed: that the square of an even integer is 0 mod 8 — 2² = 4
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: 3² = 9 = 8 + 1
  prior art: known — elementary
  handoff: none — an exercise

derivation: refuted-claim
  statement: every odd integer greater than 1 is prime
  argument: § Arguments
  verdict: refuted: 9 = 3 · 3

*Planted: no given.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: no prediction registered.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: a prediction with no probability.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: no attack on the statement.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: a divergence classed off the list.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § A divergence table with a class off the list
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: a divergence of truth left unresolved.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § A divergence table with a truth unresolved
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: a refutation beside a derived verdict.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: thin truth: 2 — the conclusion is silent on even squares, refutation: 3 — the lemma that k(k + 1) is even
  minds: 1 — an example
  grade: hand

*Planted: a counterexample with no place in the argument.*

verification: refuted-claim
  statement: every odd integer greater than 1 is prime
  committed: 2026-09-28
  given: the statement only
  predicted: refuted — 0.99
  verdict: refuted: 9 = 3 · 3
  method: trial division
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: refutation: 9
  minds: 1 — an example
  grade: hand

*Planted: refuted, and nothing located.*

verification: refuted-claim
  statement: every odd integer greater than 1 is prime
  committed: 2026-09-28
  given: the statement only
  predicted: refuted — 0.99
  verdict: refuted: 9 = 3 · 3
  method: trial division
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: thin truth: 3 — prime, as claimed, and the claim says nothing of why
  minds: 1 — an example
  grade: hand

*Planted, a warning: the comparison not made.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: none — the first derivation not yet read
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted, a warning: a verification whose verdict disagrees with its entry's.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: gap: the case k odd
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted, a warning: a second mind not carried to its entry.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared, where the entry wrote 4k(k + 1) + 1
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 2 — blind to: the entry's argument; method: residues mod 8, the same model
  grade: hand

derivation: overclaimed
  statement: the product of two consecutive integers is even
  uses only: that one of two consecutive integers is even
  not claimed: that the product of three consecutive integers is divisible by 4 — 1 · 2 · 3 = 6
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 2 — blind to: the argument; method: residues mod 2, a different model family
  model: 3 · 4 = 12
  prior art: known — elementary
  handoff: none — an exercise

derivation: refuted-by-a-verification
  statement: every integer of the form n² + n + 41 is prime
  uses only: the values for n from 0 to 39, each checked prime
  not claimed: anything about n² + n + 40
  argument: § Arguments
  verdict: derived
  grade: hand
  minds: 1
  model: n = 1 — 43
  prior art: known — Euler's prime-generating polynomial
  handoff: none — an exercise

*Planted: no committed date.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: an entry that claims more minds than its verification counts.*

verification: overclaimed
  statement: the product of two consecutive integers is even
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.99
  verdict: derived
  method: the same parity split as the entry
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every pair below 1000
  minds: 1 — the same route as the entry
  grade: hand

*Planted: a second mind blind to nothing.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement, the entry's argument, and its verdict
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 2 — blind to: nothing; method: residues mod 8
  grade: hand

*Planted, a warning: a second mind whose given names the sketch.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement and the entry's sketch
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 2 — blind to: the entry's proof; method: residues mod 8, the same model
  grade: hand

*Planted: an entry refuted by a verification and still marked derived.*

verification: refuted-by-a-verification
  statement: every integer of the form n² + n + 41 is prime
  committed: 2026-09-28
  given: the statement only
  predicted: refuted — 0.9 — likeliest break: n = 40
  verdict: refuted: n = 40 gives 1681 = 41²
  method: evaluation at the first n the entry did not check
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: refutation: n = 40 — the lemma the argument hid, that forty checked values carry every value
  minds: 1 — an example
  grade: hand

*Planted: a block the gate cannot read.*

**verification:** odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only

*Planted, a warning: a divergence table with no rows.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § A divergence table with no rows
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: a divergence table with no class column.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § A divergence table with no class column
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted, a warning: a truth divergence sent to a third mind.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § A divergence table awaiting a third mind
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: refuted, with counterexamples none.*

verification: refuted-claim
  statement: every odd integer greater than 1 is prime
  committed: 2026-09-28
  given: the statement only
  predicted: refuted — 0.99
  verdict: refuted: 9 = 3 · 3
  method: trial division
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — trial division below 100
  minds: 1 — an example
  grade: hand

*Planted: a verification graded off the ladder.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: verified

*Planted: no method.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: no divergences line.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  counterexamples: none — every odd integer below 1000
  minds: 1 — an example
  grade: hand

*Planted: counterexamples none, with no search named.*

verification: odd-square
  statement: the square of an odd integer is 1 mod 8
  committed: 2026-09-28
  given: the statement only
  predicted: derived — 0.95
  verdict: derived
  method: the four odd residues mod 8 squared
  attack: § Attacks
  divergences: § Divergences on base
  counterexamples: none
  minds: 1 — an example
  grade: hand

*Planted: an invention whose licence is not an address.*

invention: licence-unaddressed
  revises: the sum of two odd integers is odd
  licence: clearly
  premises: § Premises of the invention examples
  model: odd-square
  recovery: odd-square
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: none — an example

*Planted: an invention that revises a premise its premises section never lists.*

invention: revises-unlisted
  revises: the whole is greater than the part
  licence: § Arguments
  premises: § Premises of the invention examples
  model: odd-square
  recovery: odd-square
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: none — an example

*Planted: an invention whose recovery is a stalled entry.*

invention: recovery-stalled
  revises: the sum of two odd integers is odd
  licence: § Arguments
  premises: § Premises of the invention examples
  model: odd-square
  recovery: stalled-lemma
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: none — an example

*Planted: an invention whose old premise is planted in a control that cannot fire.*

invention: planted-cannot-fire
  revises: the sum of two odd integers is odd
  licence: § Arguments
  premises: § Premises of the invention examples
  model: odd-square
  recovery: odd-square
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: cannot-fire

*Planted: an invention with no model line.*

invention: model-missing
  revises: the sum of two odd integers is odd
  licence: § Arguments
  premises: § Premises of the invention examples
  recovery: odd-square
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: none — an example

*Planted, a warning: an invention with no model, said so — a conjecture.*

invention: honest-conjecture
  revises: the sum of two odd integers is odd
  licence: § Arguments
  premises: § Premises of the invention examples
  model: none — no object satisfying the revised premises has been built
  recovery: odd-square
  consequence: possible-two-way
  dissolved: § Arguments
  old premise planted: none — an example

control: fault-crashes
  of: base — forward, on pairs below 50
  run: python3 -c "print(sum((a+b)%2 for a in range(0,50,2) for b in range(0,50,2)))"
  expect: 0
  fault: python3 -c "print(sum((a+b)%2 for a in range(0,50,2) for b in range(1,50,2))+undefined_name)"

```text
control: fenced-and-unchecked
  of: base — forward, on pairs below 50
  run: python3 -c "print(1)"
  expect: 0
  fault: python3 -c "print(1)"
```

## Arguments

Each entry's argument is one line of parity or residue arithmetic, written out in the entry's own *uses only*; they are
here so the addresses resolve, and the defects above are in the entries, not in these lines.

## Attacks

Each verification's attack: the smallest cases, and every case below the bound its counterexamples line names.

## Divergences on base

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|
| 1 | the argument | the last binary digit | 2k + 2m | route | kept both |

## A divergence table with a class off the list

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|
| 1 | the argument | residues mod 8 | 4k(k + 1) + 1 | agree | none needed |

## A divergence table with a truth unresolved

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|
| 1 | the case k odd | 1 mod 8 | not reached | truth | unresolved |

## A divergence table with no rows

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|

## A divergence table with no class column

| # | item | this route | the entry | resolution |
|---|---|---|---|---|
| 1 | the argument | residues mod 8 | 4k(k + 1) + 1 | kept both |

## A divergence table awaiting a third mind

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|
| 1 | the case k odd | 1 mod 8 | 5 mod 8 | truth | sent to a third independent mind; neither found the other's error |

## Premises of the invention examples

| premise | sort | receipt |
|---|---|---|
| the sum of two odd integers is odd | inherited | none — planted for the examples above; the sum of two odd integers is even |
