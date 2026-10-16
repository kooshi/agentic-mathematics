#!/usr/bin/env bash
# The trust receipt, checked rather than eyeballed.
#
# `scripts/Axioms.lean` prints one line per declaration of the library with every axiom it rests on; `scripts/axioms_check.py`
# makes every decision (its docstring lists each failure kind and why it fails); `scripts/gate_report.py axioms` prints the digest
# and compares the counts with the line `CLAUDE.md` § Trust ledger records. The receipt is saved whole under `build/gate/axioms/`
# (`scripts/gate-log.sh`), so a question it already answered never needs a second run.
#
#   ./scripts/axioms.sh               the gate
#   ./scripts/axioms.sh --self-test   plant each fault the gate exists to catch, in copies of the audit, and watch each fire
#
# Run it under the slot (`scripts/slot.py --mem 8 -- ./scripts/axioms.sh`): it starts one Lean process that loads the library.
# The Lean status is read directly, never through a pipe, and an audit that does not elaborate is a FAILURE, not an empty result.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"
source "${REPO}/scripts/dev-env.sh"
source "${REPO}/scripts/gate-log.sh"

if [[ "${1:-}" == "--self-test" ]]; then
  python3 "${REPO}/scripts/axioms_selftest.py"
  exit $?
fi

gate_log_open axioms
lake env lean -DautoImplicit=false -DrelaxedAutoImplicit=false scripts/Axioms.lean > "${GATE_LOG}" 2>&1
RC=$?
gate_log_complete
if [[ "${RC}" -ne 0 ]]; then
  echo "==> axioms: FAIL — scripts/Axioms.lean did not elaborate (lean exit ${RC}); its errors:"
  grep -E ': error' "${GATE_LOG}" | head -20 | sed 's/^/    /'
  exit 1
fi
python3 "${REPO}/scripts/axioms_check.py" "${GATE_LOG}" "${REPO}/ARCHITECTURE.md"
CHECK=$?
python3 "${REPO}/scripts/gate_report.py" axioms "${GATE_LOG}" "${GATE_PREV}" "${REPO}/CLAUDE.md"
REPORT=$?
if [[ "${CHECK}" -ne 0 ]]; then
  echo "==> axioms: FAIL — see the FAIL lines above; full receipt: ${GATE_LOG#"${REPO}"/}"
  exit 1
fi
if [[ "${REPORT}" -ne 0 ]]; then
  echo "==> axioms: FAIL — the digest could not compare the counts (exit ${REPORT}); full receipt: ${GATE_LOG#"${REPO}"/}"
  exit 1
fi
echo "==> axioms: OK — full receipt: ${GATE_LOG#"${REPO}"/}"
