#!/usr/bin/env bash

set -u

USB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$USB_DIR/config"
LOG_DIR="$USB_DIR/logs"
DATA_ROOT="$USB_DIR/data"
LOG_FILE="$LOG_DIR/start-linux-$(date -u +%Y%m%dT%H%M%SZ).log"
PORTABLE_ENV="$CONFIG_DIR/portable.env"
ENV_EXAMPLE="$CONFIG_DIR/portable.env.example"

mkdir -p "$LOG_DIR" "$DATA_ROOT/chroma" "$DATA_ROOT/anythingllm" "$DATA_ROOT/openwebui" "$USB_DIR/documents" "$USB_DIR/backups" "$USB_DIR/reports" "$USB_DIR/ollama/data"

if [ -f "$ENV_EXAMPLE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_EXAMPLE"
fi
if [ -f "$PORTABLE_ENV" ]; then
  # shellcheck disable=SC1090
  . "$PORTABLE_ENV"
fi

ENABLE_REMOTE_ACCESS="${ENABLE_REMOTE_ACCESS:-true}"
ENABLE_REMOTE_OLLAMA="${ENABLE_REMOTE_OLLAMA:-false}"
ENABLE_AUTH="${ENABLE_AUTH:-true}"
ENABLE_ANYTHINGLLM="${ENABLE_ANYTHINGLLM:-true}"
ENABLE_OPENWEBUI="${ENABLE_OPENWEBUI:-true}"
ANYTHINGLLM_PORT="${ANYTHINGLLM_PORT:-3001}"
OPENWEBUI_PORT="${OPENWEBUI_PORT:-8080}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
BIND_ADDRESS="${BIND_ADDRESS:-0.0.0.0}"
LAN_ONLY="${LAN_ONLY:-true}"

OLLAMA_BIND="127.0.0.1"
[ "$ENABLE_REMOTE_OLLAMA" = "true" ] && OLLAMA_BIND="$BIND_ADDRESS"
OLLAMA_URL="http://127.0.0.1:$OLLAMA_PORT"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

fail() {
  log "ERROR: $*"
  echo "Startup failed. See log: $LOG_FILE"
  exit 1
}

have() {
  command -v "$1" >/dev/null 2>&1
}

port_in_use() {
  port="$1"
  if have ss; then
    ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]$port$"
  elif have lsof; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
  else
    curl -fsS "http://127.0.0.1:$port" >/dev/null 2>&1
  fi
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

wait_for_url() {
  url="$1"
  max_wait="${2:-30}"
  for _ in $(seq 1 "$max_wait"); do
    curl -fsS "$url" >/dev/null 2>&1 && return 0
    sleep 1
  done
  return 1
}

print_urls() {
  service="$1"
  port="$2"
  echo "$service:"
  "$USB_DIR/scripts/get-lan-url.sh" "$port" | sed 's/^/  /'
  echo ""
}

start_ollama() {
  export OLLAMA_MODELS="$USB_DIR/ollama/data"
  bin="$(ollama_bin)" || fail "Ollama not found. Install host Ollama or add portable ollama/ollama."
  if wait_for_url "$OLLAMA_URL/api/tags" 2; then
    log "Existing Ollama service reachable; leaving it untouched"
    OLLAMA_PID=""
  else
    if port_in_use "$OLLAMA_PORT"; then
      fail "Port $OLLAMA_PORT is in use but Ollama API is not reachable. Choose another OLLAMA_PORT or stop the conflicting service."
    fi
    log "Starting Ollama on $OLLAMA_BIND:$OLLAMA_PORT"
    OLLAMA_HOST="$OLLAMA_BIND:$OLLAMA_PORT" "$bin" serve >>"$LOG_FILE" 2>&1 &
    OLLAMA_PID=$!
    wait_for_url "$OLLAMA_URL/api/tags" 45 || fail "Ollama did not become reachable"
  fi
}

start_anythingllm() {
  [ "$ENABLE_ANYTHINGLLM" = "true" ] || {
    log "AnythingLLM disabled"
    return 0
  }
  export STORAGE_DIR="$DATA_ROOT/anythingllm"
  export APPDATA="$DATA_ROOT/anythingllm"
  export LOCALAPPDATA="$DATA_ROOT/anythingllm"
  export XDG_CONFIG_HOME="$DATA_ROOT/anythingllm/config"
  export XDG_DATA_HOME="$DATA_ROOT/anythingllm/data"
  export XDG_CACHE_HOME="$DATA_ROOT/anythingllm/cache"
  mkdir -p "$STORAGE_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"

  if port_in_use "$ANYTHINGLLM_PORT"; then
    log "AnythingLLM port $ANYTHINGLLM_PORT already in use; not starting another instance"
    return 0
  fi

  app="${ANYTHINGLLM_BIN:-}"
  [ -z "$app" ] && [ -f "$USB_DIR/anythingllm/AnythingLLM.AppImage" ] && app="$USB_DIR/anythingllm/AnythingLLM.AppImage"

  if [ -n "$app" ] && [ -f "$app" ]; then
    chmod +x "$app" 2>/dev/null || true
    log "Starting AnythingLLM AppImage"
    "$app" --user-data-dir="$STORAGE_DIR/anythingllm-desktop" --no-sandbox >>"$LOG_FILE" 2>&1 &
    ANYTHINGLLM_PID=$!
  else
    log "WARN: AnythingLLM AppImage not found. Existing services are left untouched."
  fi
}

start_openwebui() {
  [ "$ENABLE_OPENWEBUI" = "true" ] || {
    log "Open WebUI disabled"
    return 0
  }
  if port_in_use "$OPENWEBUI_PORT"; then
    log "Open WebUI port $OPENWEBUI_PORT already in use; not starting another instance"
    return 0
  fi

  export DATA_DIR="$DATA_ROOT/openwebui"
  export OLLAMA_BASE_URL="$OLLAMA_URL"
  export HOST="$BIND_ADDRESS"
  export PORT="$OPENWEBUI_PORT"
  [ "$ENABLE_AUTH" = "true" ] && export WEBUI_AUTH="True"

  if [ -n "${OPENWEBUI_BIN:-}" ] && [ -x "$OPENWEBUI_BIN" ]; then
    log "Starting Open WebUI from OPENWEBUI_BIN"
    "$OPENWEBUI_BIN" serve --host "$BIND_ADDRESS" --port "$OPENWEBUI_PORT" >>"$LOG_FILE" 2>&1 &
    OPENWEBUI_PID=$!
  elif have open-webui; then
    log "Starting Open WebUI from PATH"
    open-webui serve --host "$BIND_ADDRESS" --port "$OPENWEBUI_PORT" >>"$LOG_FILE" 2>&1 &
    OPENWEBUI_PID=$!
  elif have python3 && python3 -m open_webui --help >/dev/null 2>&1; then
    log "Starting Open WebUI through python module"
    python3 -m open_webui serve --host "$BIND_ADDRESS" --port "$OPENWEBUI_PORT" >>"$LOG_FILE" 2>&1 &
    OPENWEBUI_PID=$!
  else
    log "WARN: Open WebUI not found. Install on NUC or set OPENWEBUI_BIN."
  fi
}

shutdown_started_services() {
  [ -n "${ANYTHINGLLM_PID:-}" ] && kill "$ANYTHINGLLM_PID" >>"$LOG_FILE" 2>&1 || true
  [ -n "${OPENWEBUI_PID:-}" ] && kill "$OPENWEBUI_PID" >>"$LOG_FILE" 2>&1 || true
  [ -n "${OLLAMA_PID:-}" ] && kill "$OLLAMA_PID" >>"$LOG_FILE" 2>&1 || true
}

log "Linux/NUC startup begin"
"$USB_DIR/scripts/detect-usb.sh" "$USB_DIR" >>"$LOG_FILE" 2>&1 || fail "USB validation failed"
log "Remote GUI access: $ENABLE_REMOTE_ACCESS"
log "Remote Ollama API: $ENABLE_REMOTE_OLLAMA"
log "GUI authentication requested: $ENABLE_AUTH"

start_ollama
start_anythingllm
start_openwebui

echo ""
echo "GUIDE running."
echo ""
print_urls "AnythingLLM" "$ANYTHINGLLM_PORT"
print_urls "Open WebUI" "$OPENWEBUI_PORT"
echo "Ollama:"
echo "  Local:  http://localhost:$OLLAMA_PORT"
if [ "$ENABLE_REMOTE_OLLAMA" = "true" ]; then
  "$USB_DIR/scripts/get-lan-url.sh" "$OLLAMA_PORT" | sed 's/^/  /'
else
  echo "  Remote: disabled unless ENABLE_REMOTE_OLLAMA=true"
fi
echo ""
echo "Active ports: AnythingLLM=$ANYTHINGLLM_PORT OpenWebUI=$OPENWEBUI_PORT Ollama=$OLLAMA_PORT"
echo "Authentication: $ENABLE_AUTH"
echo "LAN only requested: $LAN_ONLY"
echo "Log file: $LOG_FILE"
echo ""
echo "Press Enter to stop services started by this launcher."
read -r

log "Shutdown requested"
shutdown_started_services
log "Linux/NUC startup ended"
