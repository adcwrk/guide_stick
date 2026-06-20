#!/usr/bin/env bash
# Apple Silicon setup helper for Portable-AI-USB.
# This script extends the upstream macOS launcher without replacing the
# existing Windows, Linux, GGUF, or AnythingLLM workflows.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$SCRIPT_DIR"
LOG_DIR="$USB_DIR/logs"
REPORT_DIR="$USB_DIR/reports"
CONFIG_DIR="$USB_DIR/config"
DOCUMENTS_DIR="$USB_DIR/documents"
BACKUP_DIR="$USB_DIR/backups"
INSTALLER_DIR="$USB_DIR/installer_data"
OLLAMA_MODELS_DIR="$USB_DIR/ollama/data"
ANYTHINGLLM_DATA_DIR="$USB_DIR/anythingllm_data"
ENV_FILE="$ANYTHINGLLM_DATA_DIR/storage/.env"
PORTABLE_ENV="$USB_DIR/config/portable.env"
ENV_EXAMPLE="$USB_DIR/config/portable.env.example"
LOG_FILE="$LOG_DIR/setup-mac-$(date -u +%Y%m%dT%H%M%SZ).log"

REQUIRED_LABEL="${REQUIRED_USB_LABEL:-GUIDE}"
REQUIRED_UUID="${REQUIRED_USB_UUID:-6676-08D4}"
REQUIRED_MOUNT="${REQUIRED_USB_MOUNT:-/mnt/usb}"
PULL_OPTIONAL="${PULL_OPTIONAL_MODELS:-0}"

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
ENABLE_AUTH="${ENABLE_AUTH:-true}"
ENABLE_REMOTE_OLLAMA="${ENABLE_REMOTE_OLLAMA:-false}"

mkdir -p "$LOG_DIR" "$REPORT_DIR" "$CONFIG_DIR" "$DOCUMENTS_DIR" "$BACKUP_DIR" "$INSTALLER_DIR" "$OLLAMA_MODELS_DIR" "$ANYTHINGLLM_DATA_DIR/storage" "$USB_DIR/data/chroma" "$USB_DIR/data/anythingllm" "$USB_DIR/data/openwebui"

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

validate_usb() {
  log "Validating USB root: $USB_DIR"
  [ -d "$USB_DIR" ] || fail "USB root missing: $USB_DIR"
  [ -w "$USB_DIR" ] || fail "USB root is not writable: $USB_DIR"

  if have findmnt && { [ "$USB_DIR" = "$REQUIRED_MOUNT/GUIDE" ] || [ "$USB_DIR" = "$REQUIRED_MOUNT/Portable-AI-USB" ]; }; then
    source="$(findmnt -no SOURCE "$REQUIRED_MOUNT" 2>/dev/null || true)"
    fs="$(findmnt -no FSTYPE "$REQUIRED_MOUNT" 2>/dev/null || true)"
    label="$(lsblk -no LABEL "$source" 2>/dev/null | head -1 | xargs 2>/dev/null || true)"
    uuid="$(lsblk -no UUID "$source" 2>/dev/null | head -1 | xargs 2>/dev/null || true)"
    [ "$fs" = "exfat" ] || fail "Expected exfat at $REQUIRED_MOUNT, found: ${fs:-unknown}"
    [ "$label" = "$REQUIRED_LABEL" ] || fail "Expected USB label $REQUIRED_LABEL, found: ${label:-unknown}"
    [ "$uuid" = "$REQUIRED_UUID" ] || fail "Expected USB UUID $REQUIRED_UUID, found: ${uuid:-unknown}"
    log "USB validation passed for $REQUIRED_MOUNT ($label / $uuid / $fs)"
  elif have diskutil; then
    info="$(diskutil info "$USB_DIR" 2>/dev/null || true)"
    label="$(printf '%s\n' "$info" | awk -F: '/Volume Name/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
    fs="$(printf '%s\n' "$info" | awk -F: '/File System Personality/{gsub(/^ +| +$/,"",$2); print tolower($2); exit}')"
    uuid="$(printf '%s\n' "$info" | awk -F: '/Volume UUID/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
    [ -z "$label" ] || [ "$label" = "$REQUIRED_LABEL" ] || fail "Expected USB label $REQUIRED_LABEL, found: $label"
    case "$fs" in
      *exfat*|"") ;;
      *) fail "Expected exFAT-compatible volume, found: $fs" ;;
    esac
    log "macOS volume validation observed label=${label:-unknown} uuid=${uuid:-unknown} fs=${fs:-unknown}"
  else
    log "WARN: Could not perform device-label validation on this host; path and writability passed"
  fi
}

ensure_ollama_ready() {
  export OLLAMA_MODELS="$OLLAMA_MODELS_DIR"
  bin="$(ollama_bin)" || fail "Ollama not found. Run start-mac.command once or install Ollama."
  log "Using Ollama binary: $bin"

  if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    log "Starting temporary Ollama server"
    OLLAMA_HOST=127.0.0.1:11434 "$bin" serve >>"$LOG_FILE" 2>&1 &
    OLLAMA_SETUP_PID=$!
    for i in $(seq 1 45); do
      curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
      sleep 1
      [ "$i" -eq 45 ] && fail "Ollama API did not become ready"
    done
  else
    OLLAMA_SETUP_PID=""
    log "Ollama API already running"
  fi
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

write_anythingllm_env() {
  if [ -f "$ENV_FILE" ]; then
    cp -p "$ENV_FILE" "$BACKUP_DIR/anythingllm.env.$(date -u +%Y%m%dT%H%M%SZ).bak" 2>>"$LOG_FILE" || true
  fi
  cat > "$ENV_FILE" <<'EOF'
LLM_PROVIDER=ollama
OLLAMA_BASE_PATH=http://127.0.0.1:11434
OLLAMA_MODEL_PREF=qwen2.5:7b
OLLAMA_MODEL_TOKEN_LIMIT=4096
EMBEDDING_ENGINE=ollama
EMBEDDING_BASE_PATH=http://127.0.0.1:11434
EMBEDDING_MODEL_PREF=nomic-embed-text
VECTOR_DB=lancedb
EOF
  log "AnythingLLM environment configured for external Ollama"
}

log "Portable-AI-USB macOS setup started"
validate_usb
log "GUI authentication requested: $ENABLE_AUTH"
log "Remote Ollama enabled: $ENABLE_REMOTE_OLLAMA"

if [ "$(uname -s)" = "Darwin" ]; then
  arch="$(uname -m)"
  log "Detected macOS architecture: $arch"
  [ "$arch" = "arm64" ] || log "WARN: Apple Silicon arm64 expected for M4 Max optimization"
else
  log "WARN: Not running on macOS; setup file generation and USB validation will continue, macOS runtime checks are limited"
fi

if have brew; then
  log "Homebrew detected: $(brew --prefix 2>/dev/null || true)"
else
  log "Homebrew not detected; portable Ollama/AnythingLLM downloads are still supported"
fi

if have curl; then
  log "curl detected"
else
  fail "curl is required"
fi

ensure_ollama_ready
if [ "$PULL_DEFAULT_MODELS" = "true" ]; then
  pull_model_if_missing "qwen2.5:7b"
  pull_model_if_missing "llama3.2:3b"
  pull_model_if_missing "nomic-embed-text"
else
  log "Default model pulling disabled by PULL_DEFAULT_MODELS"
fi

if [ "$PULL_OPTIONAL" = "1" ] || [ "$PULL_OPTIONAL_MODELS" = "true" ]; then
  pull_model_if_missing "qwen2.5:14b"
  pull_model_if_missing "llama3.1:8b"
  pull_model_if_missing "deepseek-r1:14b"
fi

write_anythingllm_env
log "Open WebUI data path prepared: $USB_DIR/data/openwebui"
log "ChromaDB data path prepared: $USB_DIR/data/chroma"
log "If Open WebUI is installed, complete first-run admin account creation before LAN use."

if [ -x "$USB_DIR/scripts/healthcheck-mac.sh" ]; then
  bash "$USB_DIR/scripts/healthcheck-mac.sh" || log "WARN: healthcheck returned non-zero"
fi

if [ -n "${OLLAMA_SETUP_PID:-}" ]; then
  kill "$OLLAMA_SETUP_PID" >>"$LOG_FILE" 2>&1 || true
fi

log "Portable-AI-USB macOS setup complete"
echo "Setup log: $LOG_FILE"
