#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$USB_DIR/config"
LOG_DIR="$USB_DIR/logs"
INSTALL_DIR="$USB_DIR/anythingllm"
LOG_FILE="$LOG_DIR/install-anythingllm-linux-$(date -u +%Y%m%dT%H%M%SZ).log"

mkdir -p "$LOG_DIR" "$INSTALL_DIR" "$USB_DIR/anythingllm_data/storage" "$USB_DIR/data/anythingllm"

if [ -f "$CONFIG_DIR/portable.env.example" ]; then
  # shellcheck disable=SC1090
  . "$CONFIG_DIR/portable.env.example"
fi
if [ -f "$CONFIG_DIR/portable.env" ]; then
  # shellcheck disable=SC1090
  . "$CONFIG_DIR/portable.env"
fi

ANYTHINGLLM_APPIMAGE_URL="${ANYTHINGLLM_APPIMAGE_URL:-https://cdn.anythingllm.com/latest/AnythingLLMDesktop.AppImage}"
target="$INSTALL_DIR/AnythingLLMDesktop.AppImage"
tmp="$target.partial"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

fail() {
  log "ERROR: $*"
  exit 1
}

"$USB_DIR/scripts/detect-usb.sh" "$USB_DIR" >>"$LOG_FILE" 2>&1 || fail "USB validation failed"

if [ -f "$target" ]; then
  log "AnythingLLM AppImage already installed: $target"
  exit 0
fi

command -v curl >/dev/null 2>&1 || fail "curl is required to download AnythingLLM"

log "Downloading AnythingLLM AppImage from $ANYTHINGLLM_APPIMAGE_URL"
curl --fail --location --progress-bar -o "$tmp" "$ANYTHINGLLM_APPIMAGE_URL" || fail "AnythingLLM download failed"
mv "$tmp" "$target" || fail "Failed to move AppImage into place"
chmod +x "$target" 2>/dev/null || true
log "AnythingLLM AppImage installed: $target"
log "On headless NUCs, use ANYTHINGLLM_RUNTIME=docker with Docker installed for LAN browser access."
