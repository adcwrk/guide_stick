#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"
LOG_FILE="$LOG_DIR/rag-ops-check-$(date -u +%Y%m%dT%H%M%SZ).log"
PYTHON="${GUIDE_RAG_PYTHON:-}"

if [ -z "$PYTHON" ]; then
  if [ -x "$ROOT/tools/uv/bin/uv" ]; then
    PYTHON="$("$ROOT/tools/uv/bin/uv" python find 3.12 2>/dev/null || true)"
  fi
fi
if [ -z "$PYTHON" ] && command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
fi
if [ -z "$PYTHON" ]; then
  echo "ERROR: no Python runtime found. Install uv under tools/uv/bin first." >&2
  exit 1
fi

export PYTHONPATH="$ROOT/data/rag/python-packages${PYTHONPATH:+:$PYTHONPATH}"
export ANONYMIZED_TELEMETRY=False

mkdir -p "$LOG_DIR"

{
  echo "GUIDE RAG operations check"
  echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Root: $ROOT"
  echo "Python: $PYTHON"
  echo
  "$PYTHON" "$ROOT/scripts/check-rag-ops.py" "$@"
  echo
  echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} 2>&1 | tee "$LOG_FILE"
