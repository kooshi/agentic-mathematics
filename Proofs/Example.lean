import Mathlib.Tactic.Ring

/-!
# Example — the shape of a module in this library

One definition, one theorem, and the spec examples that pin the definition down. Replace it with the first milestone's module, and
keep its shape: a docstring on every public declaration (the `missingDocs` linter), an `example` or `#guard` per definition that would
fail if the definition drifted, and the theorem's informal claim in its docstring, so that the statement can be read against it.
-/

namespace Proofs.Example

/-- `oddSum n` is the sum of the first `n` odd numbers, `1 + 3 + ⋯ + (2n − 1)`. -/
def oddSum : ℕ → ℕ
  | 0 => 0
  | n + 1 => oddSum n + (2 * n + 1)

/-- **The example theorem.** The sum of the first `n` odd numbers is `n²`, for every natural number `n`.

Informal claim: `1 + 3 + ⋯ + (2n − 1) = n²`. The induction step adds one L-shaped layer of `2n + 1` unit squares to an `n × n`
square. -/
theorem oddSum_eq_sq (n : ℕ) : oddSum n = n ^ 2 := by
  induction n with
  | zero => rfl
  | succ n ih => rw [oddSum, ih]; ring

-- Spec examples: each fails if `oddSum` drifts.
example : oddSum 0 = 0 := rfl
example : oddSum 4 = 16 := by decide
#guard oddSum 10 == 100

end Proofs.Example
