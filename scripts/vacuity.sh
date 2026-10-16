#!/usr/bin/env bash
# The vacuity gate — a theorem can pass every other check and still say nothing.
#
# `scripts/Vacuity.lean` scans the library and prints one line per (declaration, carrier) site with one of six verdicts (its header
# says what each means and why); `scripts/vacuity_check.py` decides pass or fail against `scripts/vacuity-baseline.txt`;
# `scripts/gate_report.py vacuity` prints the digest and compares the counts with the line `CLAUDE.md` § The gate records — a silent
# change in those counts is this gate's own failure mode, because a scan that stopped seeing part of the library still prints a
# plausible report.
#
#   ./scripts/vacuity.sh               the gate
#   ./scripts/vacuity.sh --self-test   plant each verdict in copies of the scan and watch each come out as it should
#   ./scripts/vacuity.sh --baseline    rewrite the baseline from this run's UNKNOWN sites (deliberately; read the difference)
#
# Run it under the slot: it starts one Lean process that loads the library. The Lean status is read directly, never through a
# pipe; a run that does not elaborate is a FAILURE, not an empty result; a missing baseline is a failure, not a free pass.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"
source "${REPO}/scripts/dev-env.sh"
source "${REPO}/scripts/gate-log.sh"
BASELINE="${REPO}/scripts/vacuity-baseline.txt"

if [[ "${1:-}" == "--self-test" ]]; then
  python3 "${REPO}/scripts/vacuity_selftest.py"
  exit $?
fi

gate_log_open vacuity
lake env lean -DautoImplicit=false -DrelaxedAutoImplicit=false scripts/Vacuity.lean > "${GATE_LOG}" 2>&1
RC=$?
gate_log_complete
if [[ "${RC}" -ne 0 ]]; then
  echo "==> vacuity: FAIL — scripts/Vacuity.lean did not elaborate (lean exit ${RC}); its errors:"
  grep -E ': error' "${GATE_LOG}" | head -20 | sed 's/^/    /'
  exit 1
fi
if [[ "${1:-}" == "--baseline" ]]; then
  { grep -E '^#' "${BASELINE}" 2>/dev/null; grep -E '^UNKNOWN ' "${GATE_LOG}"; } > "${BASELINE}.new"
  mv "${BASELINE}.new" "${BASELINE}"
  echo "==> vacuity: baseline rewritten with $(grep -c '^UNKNOWN ' "${BASELINE}") entr(ies); give each a reason line, and read the diff"
  exit 0
fi
python3 "${REPO}/scripts/vacuity_check.py" "${GATE_LOG}" "${BASELINE}"
CHECK=$?
python3 "${REPO}/scripts/gate_report.py" vacuity "${GATE_LOG}" "${GATE_PREV}" "${REPO}/CLAUDE.md"
REPORT=$?
if [[ "${CHECK}" -ne 0 ]]; then
  echo "==> vacuity: FAIL — see the FAIL lines above; full output: ${GATE_LOG#"${REPO}"/}"
  exit 1
fi
if [[ "${REPORT}" -ne 0 ]]; then
  echo "==> vacuity: FAIL — the digest could not compare the counts (exit ${REPORT}); full output: ${GATE_LOG#"${REPO}"/}"
  exit 1
fi
echo "==> vacuity: OK — full output: ${GATE_LOG#"${REPO}"/}"
