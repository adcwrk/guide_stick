#!/bin/bash
# ================================================================
# PORTABLE UNCENSORED AI - MAC LAUNCHER
# ================================================================
# Double-click this file on macOS to start the portable AI stack.
# Runtime paths are resolved from this script so the USB can be
# remounted under a different /Volumes path without editing config.
# ================================================================

set -u

SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
USB_DIR="$SCRIPT_DIR"
MAC_OLLAMA_DIR="$USB_DIR/ollama_mac"
DATA_DIR="$USB_DIR/ollama/data"
STORAGE_DIR="$USB_DIR/anythingllm_data"
LOG_DIR="$USB_DIR/logs"
REPORT_DIR="$USB_DIR/reports"
INSTALLER_DIR="$USB_DIR/installer_data"
DOCUMENTS_DIR="$USB_DIR/documents"
RUNTIME_BACKUP_DIR="$USB_DIR/backups/runtime-cache"
ENV_FILE="$STORAGE_DIR/storage/.env"
OLLAMA_HOST_URL="http://127.0.0.1:11434"
ANYTHINGLLM_URL="${ANYTHINGLLM_URL:-http://127.0.0.1:3001}"

mkdir -p "$LOG_DIR" "$REPORT_DIR" "$INSTALLER_DIR" "$DOCUMENTS_DIR" "$RUNTIME_BACKUP_DIR" "$STORAGE_DIR/storage" "$DATA_DIR"
LOG_FILE="$LOG_DIR/start-mac-$(date -u +%Y%m%dT%H%M%SZ).log"

log() {
    printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

fail() {
    log "ERROR: $*"
    echo ""
    echo "Startup failed. See log: $LOG_FILE"
    exit 1
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

wait_for_url() {
    url="$1"
    max_wait="${2:-30}"
    count=0
    while [ "$count" -lt "$max_wait" ]; do
        if curl -fsS "$url" >/dev/null 2>&1; then
            return 0
        fi
        count=$((count + 1))
        sleep 1
    done
    return 1
}

archive_path_if_present() {
    target="$1"
    [ -e "$target" ] || return 0
    base="$(basename "$target")"
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "$RUNTIME_BACKUP_DIR/$stamp"
    mv "$target" "$RUNTIME_BACKUP_DIR/$stamp/$base" 2>>"$LOG_FILE" || log "WARN: Could not archive cache path: $target"
}

detect_ollama_bin() {
    if [ -f "$MAC_OLLAMA_DIR/Ollama.app/Contents/MacOS/Ollama" ]; then
        printf '%s\n' "$MAC_OLLAMA_DIR/Ollama.app/Contents/MacOS/Ollama"
    elif [ -f "$MAC_OLLAMA_DIR/ollama" ]; then
        printf '%s\n' "$MAC_OLLAMA_DIR/ollama"
    elif command_exists ollama; then
        command -v ollama
    else
        return 1
    fi
}

validate_usb_root() {
    [ -d "$USB_DIR" ] || fail "USB root does not exist: $USB_DIR"
    [ -w "$USB_DIR" ] || fail "USB root is not writable: $USB_DIR"

    if command_exists diskutil; then
        info="$(diskutil info "$USB_DIR" 2>/dev/null || true)"
        if [ -n "$info" ]; then
            label="$(printf '%s\n' "$info" | awk -F: '/Volume Name/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
            fs_name="$(printf '%s\n' "$info" | awk -F: '/File System Personality/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
            uuid="$(printf '%s\n' "$info" | awk -F: '/Volume UUID/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
            log "USB volume label: ${label:-unknown}"
            log "USB filesystem: ${fs_name:-unknown}"
            log "USB volume UUID: ${uuid:-unknown}"
        fi
    fi
}

echo "==================================================="
echo "    Launching Portable AI Engine for Mac..."
echo "==================================================="
log "Startup begin"
log "USB root: $USB_DIR"
validate_usb_root

if [ "$(uname -s)" = "Darwin" ]; then
    arch="$(uname -m)"
    log "macOS architecture: $arch"
    if [ "$arch" != "arm64" ]; then
        log "WARN: This launcher is optimized for Apple Silicon arm64; detected $arch"
    fi
else
    log "WARN: Non-macOS host detected; this launcher is intended for macOS"
fi

# -----------------------------------------------------------------
# STEP 1: Download Mac Ollama Engine (first time only)
# -----------------------------------------------------------------
if [ ! -d "$MAC_OLLAMA_DIR/Ollama.app" ] && [ ! -f "$MAC_OLLAMA_DIR/ollama" ]; then
    command_exists curl || fail "curl is required to download Ollama"
    command_exists unzip || fail "unzip is required to extract Ollama"
    log "First time on Mac: downloading Ollama engine to USB"
    mkdir -p "$MAC_OLLAMA_DIR"
    curl -L --progress-bar "https://github.com/ollama/ollama/releases/latest/download/ollama-darwin.zip" -o "$MAC_OLLAMA_DIR/ollama-darwin.zip" || fail "Ollama download failed"
    log "Extracting Ollama"
    unzip -o -q "$MAC_OLLAMA_DIR/ollama-darwin.zip" -d "$MAC_OLLAMA_DIR/" || fail "Ollama extraction failed"
    mv "$MAC_OLLAMA_DIR/ollama-darwin.zip" "$INSTALLER_DIR/ollama-darwin.$(date -u +%Y%m%dT%H%M%SZ).zip" 2>>"$LOG_FILE" || true

    if [ -f "$MAC_OLLAMA_DIR/Ollama.app/Contents/MacOS/Ollama" ]; then
        chmod +x "$MAC_OLLAMA_DIR/Ollama.app/Contents/MacOS/Ollama" 2>>"$LOG_FILE" || true
    elif [ -f "$MAC_OLLAMA_DIR/ollama" ]; then
        chmod +x "$MAC_OLLAMA_DIR/ollama" 2>>"$LOG_FILE" || true
    fi
    log "Mac Ollama engine setup complete"
fi

# -----------------------------------------------------------------
# STEP 2: Download AnythingLLM (first time only, fully portable)
# -----------------------------------------------------------------
if [ ! -d "$USB_DIR/anythingllm_mac/AnythingLLM.app" ]; then
    command_exists curl || fail "curl is required to download AnythingLLM"
    command_exists hdiutil || fail "hdiutil is required to extract the AnythingLLM DMG"
    log "First time setup: downloading AnythingLLM Apple Silicon app to USB"
    mkdir -p "$USB_DIR/anythingllm_mac"
    dmg_path="$USB_DIR/anythingllm_mac/AnythingLLM_Installer.dmg"
    curl -L --progress-bar "https://cdn.anythingllm.com/latest/AnythingLLMDesktop-Silicon.dmg" -o "$dmg_path" || fail "AnythingLLM download failed"

    log "Mounting AnythingLLM DMG"
    MOUNT_DIR="$(hdiutil attach -nobrowse "$dmg_path" | awk '/\/Volumes\//{for (i=1;i<=NF;i++) if ($i ~ /^\/Volumes\//) print $i}' | tail -1)"
    [ -n "$MOUNT_DIR" ] || fail "Could not mount AnythingLLM DMG"

    cp -R "$MOUNT_DIR/AnythingLLM.app" "$USB_DIR/anythingllm_mac/" || fail "Could not copy AnythingLLM.app to USB"
    hdiutil detach "$MOUNT_DIR" >>"$LOG_FILE" 2>&1 || log "WARN: Could not detach AnythingLLM DMG mount"
    mv "$dmg_path" "$INSTALLER_DIR/AnythingLLM_Installer.$(date -u +%Y%m%dT%H%M%SZ).dmg" 2>>"$LOG_FILE" || true

    if command_exists xattr; then
        xattr -rc "$USB_DIR/anythingllm_mac/AnythingLLM.app" >>"$LOG_FILE" 2>&1 || log "WARN: Could not clear quarantine attributes"
    fi
    log "AnythingLLM extracted and ready"
fi

# -----------------------------------------------------------------
# STEP 3: Configure USB-local runtime paths
# -----------------------------------------------------------------
export OLLAMA_MODELS="$DATA_DIR"
export STORAGE_DIR="$STORAGE_DIR"
mkdir -p "$STORAGE_DIR/storage" "$DATA_DIR"

DEFAULT_MODEL="qwen2.5:7b"
if [ -f "$USB_DIR/models/installed-models.txt" ]; then
    DEFAULT_MODEL="$(head -n 1 "$USB_DIR/models/installed-models.txt" | cut -d '|' -f 1)"
fi

NEEDS_FIX=0
if [ ! -f "$ENV_FILE" ]; then
    NEEDS_FIX=1
elif ! grep -q "LLM_PROVIDER=ollama" "$ENV_FILE" || grep -q "LLM_PROVIDER=anythingllm_ollama" "$ENV_FILE"; then
    NEEDS_FIX=1
fi

if [ "$NEEDS_FIX" = "1" ]; then
    if [ -f "$ENV_FILE" ]; then
        cp -p "$ENV_FILE" "$USB_DIR/backups/source/anythingllm.env.$(date -u +%Y%m%dT%H%M%SZ).bak" 2>>"$LOG_FILE" || true
    fi
    log "Configuring AnythingLLM to use external Ollama engine"
    cat > "$ENV_FILE" << EOF
LLM_PROVIDER=ollama
OLLAMA_BASE_PATH=$OLLAMA_HOST_URL
OLLAMA_MODEL_PREF=$DEFAULT_MODEL
OLLAMA_MODEL_TOKEN_LIMIT=4096
EMBEDDING_ENGINE=ollama
EMBEDDING_BASE_PATH=$OLLAMA_HOST_URL
EMBEDDING_MODEL_PREF=nomic-embed-text
VECTOR_DB=lancedb
EOF
fi

if [ -f "$USB_DIR/models/installed-models.txt" ]; then
    echo ""
    echo "Installed models:"
    while IFS="|" read -r local_name nice_name tag; do
        [ -n "$nice_name" ] && echo "  - $nice_name [$tag]"
    done < "$USB_DIR/models/installed-models.txt"
    echo ""
fi

OLLAMA_BIN="$(detect_ollama_bin)" || fail "Could not find Ollama on USB or PATH. Run setup-mac.sh first."
chmod +x "$OLLAMA_BIN" 2>>"$LOG_FILE" || true

# -----------------------------------------------------------------
# STEP 4: Start Ollama and verify API
# -----------------------------------------------------------------
if curl -fsS "$OLLAMA_HOST_URL/api/tags" >/dev/null 2>&1; then
    OLLAMA_PID=""
    log "Ollama API already running"
else
    log "Starting Ollama engine from: $OLLAMA_BIN"
    OLLAMA_HOST="127.0.0.1:11434" "$OLLAMA_BIN" serve >>"$LOG_FILE" 2>&1 &
    OLLAMA_PID=$!
fi

wait_for_url "$OLLAMA_HOST_URL/api/tags" 45 || fail "Ollama API did not become ready at $OLLAMA_HOST_URL"
log "Ollama API ready"

if command_exists "$OLLAMA_BIN"; then
    :
fi

for model in qwen2.5:7b llama3.2:3b nomic-embed-text; do
    if "$OLLAMA_BIN" list 2>/dev/null | awk '{print $1}' | grep -qx "$model"; then
        log "Model available: $model"
    else
        log "WARN: Recommended model missing: $model"
    fi
done

# -----------------------------------------------------------------
# STEP 5: Archive Electron path caches for portability
# -----------------------------------------------------------------
archive_path_if_present "$STORAGE_DIR/config.json"
archive_path_if_present "$STORAGE_DIR/Cache"
archive_path_if_present "$STORAGE_DIR/Code Cache"
archive_path_if_present "$STORAGE_DIR/GPUCache"

# -----------------------------------------------------------------
# STEP 6: Launch AnythingLLM
# -----------------------------------------------------------------
APP_PATH="$USB_DIR/anythingllm_mac/AnythingLLM.app"
[ -d "$APP_PATH" ] || fail "AnythingLLM.app not found at: $APP_PATH"

log "Opening AnythingLLM from USB"
open -a "$APP_PATH" --args --user-data-dir="$STORAGE_DIR" >>"$LOG_FILE" 2>&1 || fail "Could not launch AnythingLLM"

if wait_for_url "$ANYTHINGLLM_URL" 20; then
    log "AnythingLLM web interface reachable: $ANYTHINGLLM_URL"
    open "$ANYTHINGLLM_URL" >>"$LOG_FILE" 2>&1 || log "WARN: Browser launch failed for $ANYTHINGLLM_URL"
else
    log "WARN: AnythingLLM local web interface was not reachable at $ANYTHINGLLM_URL; desktop app may still be running"
fi

echo ""
echo "==================================================="
echo "  SYSTEM ONLINE: Your AI is running from the USB!"
echo "==================================================="
echo ""
echo "Log file: $LOG_FILE"
echo "Keep this terminal open while you chat."
echo "Press [ENTER] to shut down the AI safely."
echo ""

read -r -p "Hit [ENTER] to turn off the Engine..."

log "Shutdown requested"
killall AnythingLLM >>"$LOG_FILE" 2>&1 || true
if [ -n "${OLLAMA_PID:-}" ]; then
    kill "$OLLAMA_PID" >>"$LOG_FILE" 2>&1 || true
fi
log "AI shut down. You may safely eject the USB."
echo "AI shut down. You may safely eject the USB."
