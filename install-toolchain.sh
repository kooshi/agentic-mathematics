#!/usr/bin/env bash
# install-toolchain.sh — set up the Lean 4 toolchain and Mathlib for this workspace.
#
# 1. elan, the Lean version manager, if it is missing — from its official installer (https://github.com/leanprover/elan). elan
#    gives per-project pinning: `./lean-toolchain` names the exact toolchain, and Mathlib's prebuilt files exist only for the
#    toolchain they were built with.
# 2. The pinned toolchain.
# 3. Mathlib's prebuilt .olean files for the pinned release (`lake exe cache get`), so Mathlib is never built from source here
#    (that takes hours). This downloads several gigabytes once.
#
# Run it yourself, from the repository root:   ./install-toolchain.sh
# It changes no shell profile: it prints the one PATH line to add if `lean` is not found afterwards.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"
log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$*" >&2; }

if command -v elan >/dev/null 2>&1; then
  log "elan already installed: $(elan --version)"
else
  log "Installing elan from its official installer (no default toolchain; ./lean-toolchain picks it)…"
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
  export PATH="$HOME/.elan/bin:$PATH"
  warn "If 'lean' is not found in a new shell, add this line to your shell profile:  export PATH=\"\$HOME/.elan/bin:\$PATH\""
fi

PIN="$(tr -d '[:space:]' < lean-toolchain)"
log "Installing the pinned Lean toolchain: $PIN"
elan toolchain install "$PIN"

# shellcheck source=/dev/null
. "$REPO_DIR/scripts/dev-env.sh"

log "Fetching Mathlib and its prebuilt files for the pinned release (lake exe cache get)…"
lake exe cache get

log "Versions in this workspace:"
lean --version
lake --version
log "Done. Build with:  python3 scripts/slot.py --mem 8 --cpus 2 -- env MEMMAX=8G ./scripts/build.sh   (never a bare lake build)"
