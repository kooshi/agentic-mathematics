# Two derivations, gate-clean

A worked record in the form `SKILL.md` `<the_entry>` gives: one theorem stated one way, with its converse refuted and named;
one theorem stated two ways, with each direction argued and controlled; and one physical law, stated with its idealization, its regime, and the order of what was dropped. Each has a control that
re-runs, and a planted fault that shows the control can fire.

derivation: fermat-little
  statement: for every prime p and every integer a, a^p ≡ a (mod p)
  uses only: that the nonzero residues mod p form a group of order p − 1, so a^(p−1) ≡ 1 when p does not divide a
  not claimed: the converse — n need not be prime when a^n ≡ a (mod n) for every a; 561 = 3·11·17 is the least such n
  argument: § Argument
  verdict: derived
  grade: hand
  minds: 1
  model: p = 5, a = 2 — 2^5 = 32 ≡ 2 (mod 5)
  prior art: known — Fermat's little theorem; stated by Fermat in 1640 and proved by Euler in 1736 (dates recalled, not read)
  handoff: none — a relay-result for the entries that cite it

control: fermat-forward
  of: fermat-little — the forward direction, on every prime below 300 and every residue
  run: python3 -c "print(sum(pow(a,p,p)!=a%p for p in [q for q in range(2,300) if all(q%d for d in range(2,q))] for a in range(p)))"
  expect: 0
  fault: python3 -c "print(sum(pow(a,p,p)!=a%p for p in range(2,300) for a in range(p)))"

control: fermat-converse-fails
  of: fermat-little — the not-claimed converse: the least composite n with a^n ≡ a (mod n) for every a
  run: python3 -c "print(next(n for n in range(4,10**4) if any(n%d==0 for d in range(2,n)) and all(pow(a,n,n)==a for a in range(n))))"
  expect: 561
  fault: python3 -c "print(next(n for n in range(4,10**4) if all(pow(a,n,n)==a for a in range(n))))"

## Argument

Every nonzero residue mod p has an inverse, because p is prime, so the nonzero residues form a group under multiplication, of
order p − 1. By Lagrange's theorem the order of a divides p − 1 when p does not divide a; hence a^(p−1) ≡ 1 and a^p ≡ a. When p
divides a, both sides are 0 mod p. The argument uses the primality of p only to make every nonzero residue invertible, which is
why the converse fails: a composite n whose units all have order dividing n − 1, with n squarefree, satisfies the congruence
too, and 561 is the least.

derivation: wilson
  statement: an integer n > 1 is prime if and only if (n − 1)! ≡ −1 (mod n)
  uses only: forward — that every nonzero residue mod a prime has one inverse, and only ±1 are their own; converse — that a
    divisor d of n with 1 < d < n divides (n − 1)!
  not claimed: that (n − 1)! ≡ 0 (mod n) for every composite n — n = 4 gives 3! = 6 ≡ 2
  converse: § Converse of Wilson's theorem
  argument: § Wilson's theorem
  verdict: derived
  grade: hand
  minds: 1
  model: n = 7 — 6! = 720 = 7 · 103 − 1
  prior art: known — Wilson's theorem; stated by Waring in 1770 and proved by Lagrange in 1771 (dates recalled, not read)
  handoff: none — a relay-result for the entries that cite it

control: wilson-forward
  of: wilson — the forward direction, on every prime below 500
  run: python3 -c "import math;print(sum(math.factorial(n-1)%n!=n-1 for n in range(2,500) if all(n%d for d in range(2,n))))"
  expect: 0
  fault: python3 -c "import math;print(sum(math.factorial(n-1)%n!=n-1 for n in range(2,500)))"

control: wilson-converse
  of: wilson — the converse direction, on every composite below 500
  run: python3 -c "import math;print(sum(math.factorial(n-1)%n==n-1 for n in range(2,500) if any(n%d==0 for d in range(2,n))))"
  expect: 0
  fault: python3 -c "import math;print(sum(math.factorial(n-1)%n==n-1 for n in range(2,500)))"

## Wilson's theorem

If p is prime, pair each residue a with 1 ≤ a ≤ p − 1 with its inverse. A residue is its own inverse only when a² ≡ 1, that is,
when p divides (a − 1)(a + 1), so only a ≡ ±1. The pairs multiply to 1, leaving 1 · (p − 1) ≡ −1.

## Converse of Wilson's theorem

If n > 1 is composite, it has a divisor d with 1 < d < n, and d divides (n − 1)!. If (n − 1)! ≡ −1 (mod n), then d also divides
(n − 1)! + 1, so d divides 1, which is impossible.

derivation: small-amplitude-period
  statement: a simple pendulum — a point mass on a massless rigid rod of length L, in uniform gravity g, without friction,
    released from rest at amplitude θ₀ — has period T = 2π√(L/g)·(1 + θ₀²/16 + O(θ₀⁴))
  uses only: θ'' = −(g/L)·sin θ and conservation of energy, which give T = 4√(L/g)·K(sin(θ₀/2)), and the expansion of the
    complete elliptic integral K to second order
  not claimed: the bare 2π√(L/g) at large amplitude — it is 6 % short at θ₀ = 1 rad and 61 % short at θ₀ = 3 rad; nor any
    pendulum with friction, a driven support, or a rod whose mass matters
  argument: § Argument for the period
  verdict: derived
  grade: hand
  minds: 1
  model: a 1 m pendulum at θ₀ = 0.1 rad — the correction θ₀²/16 is 6.3 × 10⁻⁴ of T and the first neglected term,
    11θ₀⁴/3072, is 3.6 × 10⁻⁷ of T, so the regime premise holds with room
  prior art: known — the amplitude series of the pendulum period is in the standard mechanics texts
  handoff: experiment — at θ₀ = 1 rad the formula gives T/(2π√(L/g)) = 1.0625 against the exact 1.0663; timing twenty swings
    to better than 0.3 % separates them, and a measured ratio off both by more than the timing error falsifies the model

control: period-inside-regime
  of: small-amplitude-period — the formula against the exact period (by the arithmetic–geometric mean) at θ₀ = 0.1 rad
  run: python3 -c "import math,functools as f;t=0.1;a,b=f.reduce(lambda p,_:((p[0]+p[1])/2,(p[0]*p[1])**.5),range(40),(1.0,math.cos(t/2)));print(abs((1+t*t/16)*a-1)<1e-6)"
  expect: True
  fault: python3 -c "import math,functools as f;t=3.0;a,b=f.reduce(lambda p,_:((p[0]+p[1])/2,(p[0]*p[1])**.5),range(40),(1.0,math.cos(t/2)));print(abs((1+t*t/16)*a-1)<1e-6)"

## Argument for the period

Energy conservation gives θ'² = (2g/L)(cos θ − cos θ₀). The time from θ = 0 to θ₀ is a quarter period; substituting
sin(θ/2) = sin(θ₀/2)·sin φ turns it into √(L/g)·K(k) with k = sin(θ₀/2), so T = 4√(L/g)·K(k). Since K(k) = (π/2)(1 + k²/4 + O(k⁴))
and k² = θ₀²/4 + O(θ₀⁴), T = 2π√(L/g)(1 + θ₀²/16 + O(θ₀⁴)). The exact ratio T/(2π√(L/g)) equals 1/AGM(1, cos(θ₀/2)), which the
control computes.
