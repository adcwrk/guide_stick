#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$USB_DIR/reports"
LOG_DIR="$USB_DIR/logs"
REPORT_FILE="$REPORT_DIR/healthcheck_report.md"
LOG_FILE="$LOG_DIR/healthcheck-mac-$(date -u +%Y%m%dT%H%M%SZ).log"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
ANYTHINGLLM_URL="${ANYTHINGLLM_URL:-http://127.0.0.1:3001}"
OPENWEBUI_URL="${OPENWEBUI_URL:-http://127.0.0.1:8080}"
GUIDE_WEBUI_PORT="${GUIDE_WEBUI_PORT:-8080}"
OLLAMA_MODELS="${OLLAMA_MODELS:-$USB_DIR/ollama/data}"
export OLLAMA_MODELS

mkdir -p "$REPORT_DIR" "$LOG_DIR"

PASS=0
FAIL=0
WARN=0
ROWS=""

record() {
  status="$1"
  check="$2"
  detail="$3"
  case "$status" in
    PASS) PASS=$((PASS + 1)) ;;
    FAIL) FAIL=$((FAIL + 1)) ;;
    WARN) WARN=$((WARN + 1)) ;;
  esac
  ROWS="${ROWS}| ${status} | ${check} | ${detail} |
"
  printf '%s %s %s - %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$status" "$check" "$detail" >>"$LOG_FILE"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

ollama_bin() {
  if [ -x "$USB_DIR/ollama_mac/Ollama.app/Contents/MacOS/Ollama" ]; then
    printf '%s\n' "$USB_DIR/ollama_mac/Ollama.app/Contents/MacOS/Ollama"
  elif [ -x "$USB_DIR/ollama_mac/ollama" ]; then
    printf '%s\n' "$USB_DIR/ollama_mac/ollama"
  elif have ollama; then
    command -v ollama
  else
    return 1
  fi
}

[ -d "$USB_DIR" ] && record PASS "USB mounted" "$USB_DIR exists" || record FAIL "USB mounted" "$USB_DIR missing"
[ -w "$USB_DIR" ] && record PASS "USB writable" "$USB_DIR is writable" || record FAIL "USB writable" "$USB_DIR is not writable"

for dir in config documents logs backups reports anythingllm_data ollama data/chroma data/rag/corpus data/anythingllm data/openwebui; do
  [ -d "$USB_DIR/$dir" ] && record PASS "Required directory: $dir" "present" || record FAIL "Required directory: $dir" "missing"
done

touch "$LOG_DIR/.healthcheck_write_test" 2>/dev/null && rm -f "$LOG_DIR/.healthcheck_write_test" 2>/dev/null && record PASS "Logs writable" "$LOG_DIR" || record FAIL "Logs writable" "$LOG_DIR"
touch "$USB_DIR/documents/.healthcheck_write_test" 2>/dev/null && rm -f "$USB_DIR/documents/.healthcheck_write_test" 2>/dev/null && record PASS "Document path writable" "$USB_DIR/documents" || record FAIL "Document path writable" "$USB_DIR/documents"
touch "$USB_DIR/anythingllm_data/.healthcheck_write_test" 2>/dev/null && rm -f "$USB_DIR/anythingllm_data/.healthcheck_write_test" 2>/dev/null && record PASS "Data path writable" "$USB_DIR/anythingllm_data" || record FAIL "Data path writable" "$USB_DIR/anythingllm_data"
touch "$USB_DIR/data/chroma/.healthcheck_write_test" 2>/dev/null && rm -f "$USB_DIR/data/chroma/.healthcheck_write_test" 2>/dev/null && record PASS "ChromaDB path writable" "$USB_DIR/data/chroma" || record FAIL "ChromaDB path writable" "$USB_DIR/data/chroma"

[ -s "$USB_DIR/data/rag/corpus/manifest.jsonl" ] && record PASS "RAG corpus manifest" "$(wc -l < "$USB_DIR/data/rag/corpus/manifest.jsonl") rows" || record WARN "RAG corpus manifest" "missing or empty"
[ -s "$USB_DIR/data/chroma/library/indexed_ids.txt" ] && record PASS "RAG Chroma index" "$(wc -l < "$USB_DIR/data/chroma/library/indexed_ids.txt") indexed chunks" || record WARN "RAG Chroma index" "not started"
[ -x "$USB_DIR/scripts/check-rag-ops.sh" ] && record PASS "Executable: scripts/check-rag-ops.sh" "yes" || record WARN "Executable: scripts/check-rag-ops.sh" "not executable; run with bash if exFAT clears mode bits"

if "$USB_DIR/scripts/check-rag-ops.sh" >>"$LOG_FILE" 2>&1; then
  rag_ops_detail="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("%s: %s pass, %s warn, %s fail" % (d.get("status"), d.get("summary", {}).get("passed"), d.get("summary", {}).get("warnings"), d.get("summary", {}).get("failed")))' "$USB_DIR/data/rag/library_manifest.json" 2>/dev/null || true)"
  [ -n "$rag_ops_detail" ] || rag_ops_detail="see data/rag/library_manifest.json"
  record PASS "RAG operations checks" "$rag_ops_detail"
else
  record FAIL "RAG operations checks" "see reports/rag_operations_report.md and data/rag/library_manifest.json"
fi

if curl -fsS "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
  record PASS "Ollama running" "$OLLAMA_URL/api/tags reachable"
else
  record FAIL "Ollama running" "$OLLAMA_URL/api/tags not reachable"
fi

guide_status_body="$(mktemp)"
guide_status_code="$(curl -sS -o "$guide_status_body" -w '%{http_code}' "http://127.0.0.1:$GUIDE_WEBUI_PORT/api/status" 2>/dev/null || true)"
if [ "$guide_status_code" = "401" ]; then
  record PASS "GUIDE WebUI auth" "unauthenticated /api/status returned 401 on port $GUIDE_WEBUI_PORT"
elif [ "$guide_status_code" = "200" ]; then
  guide_auth_marker="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("auth", {}).get("enforced_by_webui"))' "$guide_status_body" 2>/dev/null || true)"
  if [ "${ENABLE_AUTH:-true}" = "true" ] && [ "$guide_auth_marker" = "False" ]; then
    record FAIL "GUIDE WebUI auth" "ENABLE_AUTH=true but unauthenticated /api/status returned 200 on port $GUIDE_WEBUI_PORT"
  else
    record WARN "GUIDE WebUI auth" "unauthenticated /api/status returned 200 on port $GUIDE_WEBUI_PORT; verify service identity or ENABLE_AUTH setting"
  fi
else
  record WARN "GUIDE WebUI auth" "lightweight WebUI not reachable on port $GUIDE_WEBUI_PORT"
fi
rm -f "$guide_status_body"

if bin="$(ollama_bin)"; then
  record PASS "Ollama installed" "$bin"
  model_list="$("$bin" list 2>/dev/null | awk 'NR > 1 {print $1}')"
  for model in qwen2.5:7b llama3.2:3b nomic-embed-text; do
    if printf '%s\n' "$model_list" | grep -Eqx "$model|$model:latest"; then
      record PASS "Model installed: $model" "available"
    else
      record WARN "Model installed: $model" "not found in ollama list"
    fi
  done
else
  record FAIL "Ollama installed" "no portable or PATH ollama found"
fi

if pgrep -f "AnythingLLM" >/dev/null 2>&1; then
  record PASS "AnythingLLM running" "process detected"
else
  record WARN "AnythingLLM running" "process not detected"
fi

if curl -fsS "$ANYTHINGLLM_URL" >/dev/null 2>&1; then
  record PASS "Web interface reachable" "$ANYTHINGLLM_URL"
else
  record WARN "Web interface reachable" "$ANYTHINGLLM_URL not reachable"
fi

if curl -fsS "$OPENWEBUI_URL" >/dev/null 2>&1; then
  record PASS "Open WebUI reachable" "$OPENWEBUI_URL"
else
  record WARN "Open WebUI reachable" "$OPENWEBUI_URL not reachable"
fi

lan_urls="$("$USB_DIR/scripts/get-lan-url.sh" 8080 2>/dev/null | tr '\n' ' ')"
[ -n "$lan_urls" ] && record PASS "LAN URL displayed" "$lan_urls" || record WARN "LAN URL displayed" "not available"

cat > "$REPORT_FILE" <<EOF
# Healthcheck Report

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

USB root: \`$USB_DIR\`

Summary:

- Passed: $PASS
- Warnings: $WARN
- Failed: $FAIL

| Status | Check | Detail |
|---|---|---|
$ROWS

Log file: \`$LOG_FILE\`
EOF

cat "$REPORT_FILE"
[ "$FAIL" -eq 0 ]
