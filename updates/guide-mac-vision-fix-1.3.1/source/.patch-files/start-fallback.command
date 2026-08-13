#!/bin/bash
# Guide Launcher for macOS (fallback — used when the .app launcher fails)
# Starts bundled Ollama, launches the app, then closes this terminal window.

# This script lives in .internal/ — go up one level to Guide/ root
DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP="$DIR/.internal/apps/Guide.app"
OLLAMA_BIN="$DIR/.internal/ollama/mac/ollama"
OLLAMA_MODELS_DIR="$DIR/.internal/models"
OLLAMA_PORT=11434

# Hide non-Mac launchers in Finder (cross-platform USB)
chflags hidden "$DIR/Start Guide (Windows).bat" 2>/dev/null
chflags hidden "$DIR/Start Guide (Linux).sh" 2>/dev/null
chflags nohidden "$DIR/Start Guide.app" 2>/dev/null

# Clear macOS quarantine attribute (USB drives trigger Gatekeeper)
xattr -cr "$APP" 2>/dev/null
xattr -cr "$OLLAMA_BIN" 2>/dev/null

# --- Start Ollama from USB ---
_start_ollama() {
  if [ ! -f "$OLLAMA_BIN" ]; then
    return 1
  fi

  # Check if port already in use
  if lsof -i :$OLLAMA_PORT > /dev/null 2>&1; then
    RUNNING_PID=$(lsof -ti :$OLLAMA_PORT 2>/dev/null | head -1)
    if [ -n "$RUNNING_PID" ]; then
      RUNNING_CMD=$(ps -p "$RUNNING_PID" -o command= 2>/dev/null || true)
      if echo "$RUNNING_CMD" | grep -q "$OLLAMA_BIN" 2>/dev/null; then
        return 0
      fi
      kill "$RUNNING_PID" 2>/dev/null
      pkill -f "/Applications/Ollama.app" 2>/dev/null
      pkill -f "ollama serve" 2>/dev/null
      sleep 1
    fi
  fi

  export OLLAMA_MODELS="$OLLAMA_MODELS_DIR"
  chmod +x "$OLLAMA_BIN"
  "$OLLAMA_BIN" serve > "$DIR/.internal/diag/ollama-usb.log" 2>&1 &
  OLLAMA_PID=$!

  # Wait for Ollama (up to 15s)
  for i in $(seq 1 40); do
    if curl -sf "http://127.0.0.1:$OLLAMA_PORT/api/tags" | grep -q "moondream\\|qwen2.5-vl"; then
      return 0
    fi
    sleep 0.5
  done
  return 0
}

_start_ollama

# --- Launch App & cleanup ---
if [ -d "$APP" ]; then
  open "$APP"

  # Background: wait for app exit, then kill Ollama
  (
    sleep 2
    while pgrep -x "Guide" > /dev/null 2>&1; do
      sleep 5
    done
    if [ -n "$OLLAMA_PID" ] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
      kill "$OLLAMA_PID" 2>/dev/null
    fi
  ) &

  # Close this Terminal window after a short delay
  sleep 1
  osascript -e 'tell application "Terminal" to close front window' > /dev/null 2>&1 &
else
  echo ""
  echo "ERROR: Guide.app not found."
  echo "Make sure the USB drive is properly mounted."
  read -p "Press Enter to exit..."
fi
