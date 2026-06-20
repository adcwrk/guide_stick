#!/usr/bin/env bash

set -u

USB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$USB_DIR/logs"
CONFIG_DIR="$USB_DIR/config"
MODELS_DIR="$USB_DIR/models"
DATA_DIR="$USB_DIR/data"
OLLAMA_MODELS_DIR="$USB_DIR/ollama/data"
LOG_FILE="$LOG_DIR/setup-linux-$(date -u +%Y%m%dT%H%M%SZ).log"
PORTABLE_ENV="$CONFIG_DIR/portable.env"
ENV_EXAMPLE="$CONFIG_DIR/portable.env.example"

mkdir -p "$LOG_DIR" "$CONFIG_DIR" "$MODELS_DIR" "$DATA_DIR/chroma" "$DATA_DIR/anythingllm" "$DATA_DIR/openwebui" "$OLLAMA_MODELS_DIR" "$USB_DIR/documents" "$USB_DIR/backups" "$USB_DIR/reports"

if [ -f "$ENV_EXAMPLE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_EXAMPLE"
fi
if [ -f "$PORTABLE_ENV" ]; then
  # shellcheck disable=SC1090
  . "$PORTABLE_ENV"
fi

PULL_DEFAULT_MODELS="${PULL_DEFAULT_MODELS:-true}"
PULL_OPTIONAL_MODELS="${PULL_OPTIONAL_MODELS:-false}"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

fail() {
  log "ERROR: $*"
  exit 1
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

wait_for_ollama() {
  for _ in $(seq 1 45); do
    curl -fsS "http://127.0.0.1:${OLLAMA_PORT:-11434}/api/tags" >/dev/null 2>&1 && return 0
    sleep 1
  done
  return 1
}

pull_model_if_missing() {
  model="$1"
  bin="$(ollama_bin)" || fail "Ollama not found while checking model $model"
  if "$bin" list 2>/dev/null | awk '{print $1}' | grep -qx "$model"; then
    log "Model already installed: $model"
  else
    log "Pulling missing model: $model"
    "$bin" pull "$model" >>"$LOG_FILE" 2>&1 || fail "Model pull failed: $model"
  fi
}

log "Linux/NUC setup started"
"$USB_DIR/scripts/detect-usb.sh" "$USB_DIR" >>"$LOG_FILE" 2>&1 || fail "USB validation failed"
log "Linux architecture: $(uname -m)"

if bin="$(ollama_bin)"; then
  log "Using Ollama: $bin"
else
  fail "Ollama not detected. Install Ollama on the NUC or place portable binary at ollama/ollama."
fi

export OLLAMA_MODELS="$OLLAMA_MODELS_DIR"
if ! curl -fsS "http://127.0.0.1:${OLLAMA_PORT:-11434}/api/tags" >/dev/null 2>&1; then
  log "Starting temporary Ollama for setup"
  OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT:-11434}" "$bin" serve >>"$LOG_FILE" 2>&1 &
  OLLAMA_SETUP_PID=$!
  wait_for_ollama || fail "Ollama did not become reachable"
else
  OLLAMA_SETUP_PID=""
  log "Existing Ollama service is reachable; it will not be stopped"
fi

if [ "$PULL_DEFAULT_MODELS" = "true" ]; then
  pull_model_if_missing "qwen2.5:7b"
  pull_model_if_missing "llama3.2:3b"
  pull_model_if_missing "nomic-embed-text"
else
  log "Default model pulls disabled"
fi

if [ "$PULL_OPTIONAL_MODELS" = "true" ]; then
  pull_model_if_missing "qwen2.5:14b"
  pull_model_if_missing "llama3.1:8b"
  pull_model_if_missing "deepseek-r1:14b"
fi

if command -v open-webui >/dev/null 2>&1; then
  log "Open WebUI detected on PATH"
else
  log "Open WebUI not detected. Install it on the NUC or set OPENWEBUI_BIN in config/portable.env."
fi

if [ -n "${OLLAMA_SETUP_PID:-}" ]; then
  kill "$OLLAMA_SETUP_PID" >>"$LOG_FILE" 2>&1 || true
fi

log "Linux/NUC setup complete"
echo "Setup log: $LOG_FILE"
