#!/usr/bin/env bash
# The whole Lean gate, in order, stopping at the first failure (LEAN.md § The gate has why each step exists).
#
#   ./scripts/gate.sh               the gate: build, zero sorry, axiom audit, vacuity scan, linters, the module map
#   ./scripts/gate.sh --self-tests  the same, then every gate script's planted controls (each must fail where it should)
#
# Run it under the slot, reserving what the build's cap asks for, because every step that loads the library is one Lean process:
#   scripts/slot.py --mem 8 --cpus 2 -- env MEMMAX=8G ./scripts/gate.sh
# Each step's exit status is read directly — never through a pipe, never chained with `;` — and a step that cannot run is a failure.
# Every step keeps its complete output (build/gate/<step>/), so read the logs, not this script's last line.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"
source "${REPO}/scripts/dev-env.sh"

step() {  # step <label> <command…>
  local label="$1"; shift
  echo "==> gate: ${label}"
  "$@"
  local rc=$?
  if [[ "${rc}" -ne 0 ]]; then
    echo "==> gate: FAIL at '${label}' (exit ${rc}); the steps after it did not run"
    exit 1
  fi
}

step "build"                ./scripts/build.sh
step "zero sorry"           python3 scripts/nosorry.py
step "axiom audit"          ./scripts/axioms.sh
step "vacuity scan"         ./scripts/vacuity.sh
step "linters"              lake lint --no-build -- --no-build --trace
step "module map"           python3 tools/check_architecture.py
step "identities"           python3 scripts/identities.py check

if [[ "${1:-}" == "--self-tests" ]]; then
  step "self-test: identities"      python3 scripts/identities.py --self-test
  step "self-test: zero sorry"      python3 scripts/nosorry.py --self-test
  step "self-test: axiom audit"     ./scripts/axioms.sh --self-test
  step "self-test: vacuity scan"    ./scripts/vacuity.sh --self-test
  step "self-test: module map"      python3 tools/check_architecture.py --self-test
  step "self-test: fact audit"      python3 tools/claude_md_fact_audit.py --self-test
  step "self-test: bibliography"    python3 tools/bib_audit.py --self-test
fi
echo "==> gate: OK — every step passed; the logs are under build/gate/"
