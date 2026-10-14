#!/usr/bin/env bash
# Portable runner for dream.py — finds a Python interpreter, falling back to
# Nix (NixOS or macOS/Linux with the Nix package manager) to pull one transiently.
# dream.py is stdlib-only, so `nix-shell -p python3` is all that is needed.
#
#   ./dream.sh sessions --last 20
#   ./dream.sh digest <session-id>
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/dream.py"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$PY" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$PY" "$@"
elif command -v nix-shell >/dev/null 2>&1; then
  # Quote each argument for the string that nix-shell --run evaluates.
  cmd="python3 '$PY'"
  for a in "$@"; do cmd="$cmd '$a'"; done
  exec nix-shell -p python3 --run "$cmd"
else
  echo "dream.sh: no Python found." >&2
  echo "Install python3, or install Nix (https://nixos.org/download) so this" >&2
  echo "script can run 'nix-shell -p python3' automatically." >&2
  exit 1
fi
