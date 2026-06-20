#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$USB_DIR/reports"
LOG_DIR="$USB_DIR/logs"
REPORT_FILE="$REPORT_DIR/healthcheck_report.md"
LOG_FILE="$LOG_DIR/healthcheck-linux-$(date -u +%Y%m%dT%H%M%SZ).log"
CONFIG_DIR="$USB_DIR/config"

mkdir -p "$REPORT_DIR" "$LOG_DIR"

if [ -f "$CONFIG_DIR/portable.env.example" ]; then
  # shellcheck disable=SC1090
  . "$CONFIG_DIR/portable.env.example"
fi
if [ -f "$CONFIG_DIR/portable.env" ]; then
  # shellcheck disable=SC1090
  . "$CONFIG_DIR/portable.env"
fi

ANYTHINGLLM_PORT="${ANYTHINGLLM_PORT:-3001}"
OPENWEBUI_PORT="${OPENWEBUI_PORT:-8080}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
ENABLE_OPENWEBUI="${ENABLE_OPENWEBUI:-true}"

PASS=0
WARN=0
FAIL=0
ROWS=""

record() {
  status="$1"
  check="$2"
  detail="$3"
  case "$status" in
    PASS) PASS=$((PASS + 1)) ;;
    WARN) WARN=$((WARN + 1)) ;;
    FAIL) FAIL=$((FAIL + 1)) ;;
  esac
  ROWS="${ROWS}| ${status} | ${check} | ${detail} |
"
  printf '%s %s %s - %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$status" "$check" "$detail" >>"$LOG_FILE"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

ollama_bin() {
  if [ -n "${OLLAMA_BIN:-}" ] && [ -x "$OLLAMA_BIN" ]; then
    printf '%s\n' "$OLLAMA_BIN"
  elif [ -x "$USB_DIR/ollama/ollama" ]; then
    printf '%s\n' "$USB_DIR/ollama/ollama"
  elif have ollama; then
    command -v ollama
  else
    return 1
  fi
}

if "$USB_DIR/scripts/detect-usb.sh" "$USB_DIR" >>"$LOG_FILE" 2>&1; then
  record PASS "USB identity" "THKAILAR validation passed where detectable"
else
  record FAIL "USB identity" "see $LOG_FILE"
fi

for dir in config documents logs backups reports data/chroma data/anythingllm data/openwebui scripts ollama; do
  [ -d "$USB_DIR/$dir" ] && record PASS "Required folder: $dir" "present" || record FAIL "Required folder: $dir" "missing"
done

for script in start-linux.sh setup-linux.sh scripts/detect-usb.sh scripts/get-lan-url.sh scripts/backup-portable.sh scripts/ingest-documents.sh; do
  [ -x "$USB_DIR/$script" ] && record PASS "Executable: $script" "yes" || record WARN "Executable: $script" "not executable; run with bash if exFAT clears mode bits"
done

touch "$USB_DIR/logs/.healthcheck_write" 2>/dev/null && rm -f "$USB_DIR/logs/.healthcheck_write" && record PASS "Logs writable" "$USB_DIR/logs" || record FAIL "Logs writable" "$USB_DIR/logs"
touch "$USB_DIR/documents/.healthcheck_write" 2>/dev/null && rm -f "$USB_DIR/documents/.healthcheck_write" && record PASS "Documents writable" "$USB_DIR/documents" || record FAIL "Documents writable" "$USB_DIR/documents"
touch "$USB_DIR/data/chroma/.healthcheck_write" 2>/dev/null && rm -f "$USB_DIR/data/chroma/.healthcheck_write" && record PASS "ChromaDB path writable" "$USB_DIR/data/chroma" || record FAIL "ChromaDB path writable" "$USB_DIR/data/chroma"

if curl -fsS "http://127.0.0.1:$OLLAMA_PORT/api/tags" >/dev/null 2>&1; then
  record PASS "Ollama reachable" "http://127.0.0.1:$OLLAMA_PORT/api/tags"
else
  record WARN "Ollama reachable" "not reachable on port $OLLAMA_PORT"
fi

if bin="$(ollama_bin)"; then
  record PASS "Ollama installed" "$bin"
  for model in qwen2.5:7b llama3.2:3b nomic-embed-text; do
    "$bin" list 2>/dev/null | awk '{print $1}' | grep -qx "$model" && record PASS "Model: $model" "available" || record WARN "Model: $model" "missing"
  done
else
  record WARN "Ollama installed" "not detected"
fi

curl -fsS "http://127.0.0.1:$ANYTHINGLLM_PORT" >/dev/null 2>&1 && record PASS "AnythingLLM reachable" "port $ANYTHINGLLM_PORT" || record WARN "AnythingLLM reachable" "not reachable on port $ANYTHINGLLM_PORT"

if [ "$ENABLE_OPENWEBUI" = "true" ]; then
  curl -fsS "http://127.0.0.1:$OPENWEBUI_PORT" >/dev/null 2>&1 && record PASS "Open WebUI reachable" "port $OPENWEBUI_PORT" || record WARN "Open WebUI reachable" "not reachable on port $OPENWEBUI_PORT"
else
  record WARN "Open WebUI reachable" "disabled by config"
fi

lan_url="$("$USB_DIR/scripts/get-lan-url.sh" "$OPENWEBUI_PORT" 2>/dev/null | tr '\n' ' ')"
[ -n "$lan_url" ] && record PASS "LAN URL displayed" "$lan_url" || record WARN "LAN URL displayed" "not available"

cat > "$REPORT_FILE" <<EOF
# Healthcheck Report

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

Runtime: Linux/NUC

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
