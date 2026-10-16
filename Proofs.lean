-- The library's flat import surface: every module under `Proofs/` is imported here, because the gate's audits import only this
-- root, and a module outside it would be checked by nothing (`scripts/nosorry.py` fails on one).
import Proofs.Example
