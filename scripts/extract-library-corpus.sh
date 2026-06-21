#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"
LOG_FILE="$LOG_DIR/rag-corpus-extraction-$(date -u +%Y%m%dT%H%M%SZ).log"

mkdir -p "$LOG_DIR" "$ROOT/data/rag/corpus"

{
  echo "GUIDE RAG corpus extraction"
  echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Root: $ROOT"
  echo "INCLUDE_ZIMS=${INCLUDE_ZIMS:-false}"
  echo
  python3 "$ROOT/scripts/extract-library-corpus.py" "$@"
  echo
  echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} 2>&1 | tee "$LOG_FILE"
