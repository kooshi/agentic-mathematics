# A verification, as a second mind files it

A worked record in the form `ephodos-verification` gives, on the entry `fermat-little` in `example-clean.md`. Run the gate on
both files together. The record was written by the entry's own author to show the form, so it declares what it was given and
counts itself honestly: a checking reading by a different route is one mind, not two.

verification: fermat-little
  statement: for every prime p and every integer a, a^p ≡ a (mod p)
  given: the statement, and — because this record was written by the entry's author to show the form — the entry's
    argument and verdict
  committed: 2026-09-28
  predicted: derived — 0.97 — likeliest break: the case where p divides a, which a group argument leaves out
  verdict: derived
  method: induction on a with the binomial theorem; the entry argued by Lagrange's theorem on the group of nonzero residues
  attack: § Attack on fermat-little
  divergences: § Divergences on fermat-little
  counterexamples: none — every prime below 300 and every residue, by this route's lemma; the converse fails at 561 and six
    other composite n below 10^4, as the entry's not claimed line already says
  minds: 1 — a checking reading: given the argument and the verdict before deriving
  grade: hand

control: fermat-binomial
  of: fermat-little — the lemma this route consumes: p divides C(p, k) for 0 < k < p, on every prime below 300
  run: python3 -c "import math;print(sum(math.comb(p,k)%p!=0 for p in range(2,300) if all(p%d for d in range(2,p)) for k in range(1,p)))"
  expect: 0
  fault: python3 -c "import math;print(sum(math.comb(p,k)%p!=0 for p in range(2,300) for k in range(1,p)))"

control: fermat-not-claimed
  of: fermat-little — the converse its not claimed line names: composite n below 10^4 at which a^n ≡ a (mod n) for every a
  run: python3 -c "print(sum(1 for n in range(4,10**4) if any(n%d==0 for d in range(2,int(n**.5)+1)) and all(pow(a,n,n)==a for a in range(n))))"
  expect: 7
  fault: python3 -c "print(sum(1 for n in range(4,10**4) if all(pow(a,n,n)==a for a in range(n))))"

## Derivation by another route

For a ≥ 0, by induction on a. The case a = 0 is 0 ≡ 0. If a^p ≡ a, the binomial theorem gives (a + 1)^p = Σ C(p, k) a^k,
and for 0 < k < p the prime p divides C(p, k) = p! / (k! (p − k)!), since it divides the numerator and no factor of the
denominator; so (a + 1)^p ≡ a^p + 1 ≡ a + 1. For a < 0, choose m with a + mp ≥ 0: both sides of the congruence depend only on
a mod p. The route uses primality once, in the divisibility of C(p, k), and never divides by a — so the case p | a needs no
separate treatment.

## Attack on fermat-little

The smallest cases first: p = 2, where a² − a = a(a − 1) is even; p = 3, where a³ − a = (a − 1)a(a + 1) is a product of three
consecutive integers. Each hypothesis removed in turn: without "prime", n = 4 and a = 2 give 2^4 = 16 ≡ 0, not 2, so the
hypothesis is needed. The attack on the converse, over every composite n below 10^4, succeeds at seven moduli, the least 561
(`fermat-not-claimed`). Each satisfies the conclusion while failing the hypothesis — but the entry's *not claimed* line already
names 561, so they confirm that line and are not counterexamples to the statement.

## Divergences on fermat-little

| # | item | this route | the entry | class | resolution |
|---|---|---|---|---|---|
| 1 | the argument | induction on a with the binomial theorem | Lagrange's theorem on the group of nonzero residues | route | kept both — a second method, though not a second mind |
| 2 | the case p divides a | inside the induction | a separate case, both sides 0 | route | kept both |
| 3 | the entry's *not claimed* line, "561 … is the least such n" | can be read as the least modulus n ≥ 2 satisfying the congruence, which is 2 | the least composite such n | wording | both readings reported to the author, who fixes the words; "such" was meant to refer to an n that is not prime, in the clause before |
