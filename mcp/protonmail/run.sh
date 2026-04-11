#!/usr/bin/env bash
# Wrapper to run the email MCP server with nix-shell or plain python.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v nix-shell &>/dev/null; then
    exec nix-shell -p "python3.withPackages (ps: [ ps.mcp ps.pydantic ])" \
        --run "python3 '$SCRIPT_DIR/server.py'"
else
    exec python3 "$SCRIPT_DIR/server.py"
fi
