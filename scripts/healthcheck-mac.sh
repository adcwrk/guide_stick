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

for dir in config documents logs backups reports anythingllm_data ollama; do
  [ -d "$USB_DIR/$dir" ] && record PASS "Required directory: $dir" "present" || record FAIL "Required directory: $dir" "missing"
done

touch "$LOG_DIR/.healthcheck_write_test" 2>/dev/null && rm -f "$LOG_DIR/.healthcheck_write_test" 2>/dev/null && record PASS "Logs writable" "$LOG_DIR" || record FAIL "Logs writable" "$LOG_DIR"
touch "$USB_DIR/documents/.healthcheck_write_test" 2>/dev/null && rm -f "$USB_DIR/documents/.healthcheck_write_test" 2>/dev/null && record PASS "Document path writable" "$USB_DIR/documents" || record FAIL "Document path writable" "$USB_DIR/documents"
touch "$USB_DIR/anythingllm_data/.healthcheck_write_test" 2>/dev/null && rm -f "$USB_DIR/anythingllm_data/.healthcheck_write_test" 2>/dev/null && record PASS "Data path writable" "$USB_DIR/anythingllm_data" || record FAIL "Data path writable" "$USB_DIR/anythingllm_data"

if curl -fsS "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
  record PASS "Ollama running" "$OLLAMA_URL/api/tags reachable"
else
  record FAIL "Ollama running" "$OLLAMA_URL/api/tags not reachable"
fi

if bin="$(ollama_bin)"; then
  record PASS "Ollama installed" "$bin"
  for model in qwen2.5:7b llama3.2:3b nomic-embed-text; do
    if "$bin" list 2>/dev/null | awk '{print $1}' | grep -qx "$model"; then
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
