# scripts/dev-env.sh — sourced by every build and gate script; source it yourself before building by hand.
#
#   source scripts/dev-env.sh
#
# LEAN_ABORT_ON_PANIC=1: a `panic!` aborts loudly instead of printing and returning a junk `default`, which would otherwise let a
# broken tool produce plausible output (the de Bruijn core's totality discipline).
#
# Arch Linux only: the toolchain's bundled `clang` resolves the system `libclang-cpp.so` there and dies with a symbol-lookup error, so
# every native compile (Mathlib's `cache` tool, executables) fails. The fix compiles generated C with the system clang and puts the
# toolchain's bundled static libc++ on the linker path. It is applied only on Arch (or with LEAN_CLANG_WORKAROUND=1), because
# elsewhere the bundled clang works and a system clang may not exist.

export LEAN_ABORT_ON_PANIC=1

if [ -f /etc/arch-release ] || [ "${LEAN_CLANG_WORKAROUND:-0}" = 1 ]; then
  export LEAN_CC="${LEAN_CC:-clang}"
  if command -v elan >/dev/null 2>&1; then
    _lean_lib="$(dirname "$(dirname "$(elan which lean 2>/dev/null)")")/lib"
    if [ -d "$_lean_lib" ]; then
      case ":${LIBRARY_PATH:-}:" in
        *":$_lean_lib:"*) ;;
        *) export LIBRARY_PATH="$_lean_lib${LIBRARY_PATH:+:$LIBRARY_PATH}" ;;
      esac
    fi
    unset _lean_lib
  fi
fi
