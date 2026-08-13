#!/bin/bash
set -u

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
FILES_DIR="$PATCH_DIR/.patch-files"

find_guide_root() {
  local candidates=(
    "$PATCH_DIR/../.."
    "$PATCH_DIR/.."
    "/Volumes/Guide/Guide"
  )

  for candidate in "${candidates[@]}"; do
    if [ -d "$candidate/.internal/apps/Guide.app" ] && [ -d "$candidate/Guide (Mac).app" ]; then
      cd "$candidate" >/dev/null 2>&1 && pwd
      return 0
    fi
  done

  for volume in /Volumes/*; do
    if [ -d "$volume/Guide/.internal/apps/Guide.app" ] && [ -d "$volume/Guide/Guide (Mac).app" ]; then
      cd "$volume/Guide" >/dev/null 2>&1 && pwd
      return 0
    fi
  done

  return 1
}

fail() {
  echo ""
  echo "ERROR: $1"
  echo ""
  read -r -p "Press Return to close this window..."
  exit 1
}

GUIDE_ROOT="$(find_guide_root)" || fail "Could not find a GUIDE USB folder. Put this patch folder inside Guide/updates/ or plug in the GUIDE USB drive."

LAUNCHER_TARGET="$GUIDE_ROOT/Guide (Mac).app/Contents/MacOS/launcher"
FALLBACK_TARGET="$GUIDE_ROOT/.internal/start-fallback.command"
TEST_PLAN_TARGET="$GUIDE_ROOT/BETA_TEST_PLAN.md"
GUIDE_README_TARGET="$GUIDE_ROOT/GUIDE_README.html"

LAUNCHER_SOURCE="$FILES_DIR/launcher"
FALLBACK_SOURCE="$FILES_DIR/start-fallback.command"
TEST_PLAN_SOURCE="$FILES_DIR/BETA_TEST_PLAN.md"
GUIDE_README_SOURCE="$FILES_DIR/GUIDE_README.html"

[ -f "$LAUNCHER_SOURCE" ] || fail "Missing patch file: .patch-files/launcher"
[ -f "$FALLBACK_SOURCE" ] || fail "Missing patch file: .patch-files/start-fallback.command"

echo "GUIDE Mac Vision Fix 1.3.1"
echo "GUIDE USB folder: $GUIDE_ROOT"
echo ""
echo "Quitting GUIDE and conflicting Ollama processes..."

osascript -e 'tell application "Guide" to quit' >/dev/null 2>&1 || true
osascript -e 'tell application "Ollama" to quit' >/dev/null 2>&1 || true
launchctl unload "$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist" >/dev/null 2>&1 || true
pkill -f "/Applications/Ollama.app" >/dev/null 2>&1 || true
pkill -f "ollama serve" >/dev/null 2>&1 || true
sleep 1

echo "Backing up current Mac launch files..."
STAMP="$(date +%Y%m%d-%H%M%S)"
cp "$LAUNCHER_TARGET" "$LAUNCHER_TARGET.backup-$STAMP" || fail "Could not back up Mac launcher."
cp "$FALLBACK_TARGET" "$FALLBACK_TARGET.backup-$STAMP" || fail "Could not back up fallback launcher."

echo "Installing patched Mac launch files..."
cp "$LAUNCHER_SOURCE" "$LAUNCHER_TARGET" || fail "Could not update Mac launcher."
cp "$FALLBACK_SOURCE" "$FALLBACK_TARGET" || fail "Could not update fallback launcher."
chmod +x "$LAUNCHER_TARGET" "$FALLBACK_TARGET"

if [ -f "$TEST_PLAN_SOURCE" ]; then
  cp "$TEST_PLAN_SOURCE" "$TEST_PLAN_TARGET" || echo "Warning: could not update BETA_TEST_PLAN.md"
fi

if [ -f "$GUIDE_README_SOURCE" ]; then
  cp "$GUIDE_README_SOURCE" "$GUIDE_README_TARGET" || echo "Warning: could not update GUIDE_README.html"
fi

echo "Clearing quarantine attributes..."
xattr -cr "$GUIDE_ROOT/Guide (Mac).app" >/dev/null 2>&1 || true
xattr -cr "$GUIDE_ROOT/.internal/apps/Guide.app" >/dev/null 2>&1 || true
xattr -cr "$GUIDE_ROOT/.internal/ollama/mac/ollama" >/dev/null 2>&1 || true
xattr -cr "$GUIDE_ROOT/.internal/start-fallback.command" >/dev/null 2>&1 || true

echo "Re-signing the visible Mac launcher..."
codesign --force --deep --sign - "$GUIDE_ROOT/Guide (Mac).app" >/dev/null 2>&1 || echo "Warning: could not re-sign Guide (Mac).app. macOS may ask for Open confirmation."

echo "Starting USB Ollama for verification..."
export GUIDE_USB_ROOT="$GUIDE_ROOT"
export OLLAMA_MODELS="$GUIDE_ROOT/.internal/models"
export OLLAMA_ORIGINS="*"
"$GUIDE_ROOT/.internal/ollama/mac/ollama" serve > "$GUIDE_ROOT/.internal/diag/ollama-usb.log" 2>&1 &
OLLAMA_PID=$!

FOUND_VISION=0
for i in $(seq 1 40); do
  TAGS="$(curl -sf "http://127.0.0.1:11434/api/tags" 2>/dev/null || true)"
  if echo "$TAGS" | grep -q "moondream\\|qwen2.5-vl"; then
    FOUND_VISION=1
    break
  fi
  sleep 0.5
done

if [ "$FOUND_VISION" = "1" ]; then
  echo ""
  echo "Patch applied successfully."
  echo "USB vision model detected."
  echo ""
  echo "Next step: launch GUIDE from Guide (Mac).app and retest Review Picture."
else
  echo ""
  echo "Patch installed, but no USB vision model was detected on port 11434."
  echo "Check that this USB contains moondream or qwen2.5-vl models."
  echo "Log file: $GUIDE_ROOT/.internal/diag/ollama-usb.log"
fi

if [ -n "${OLLAMA_PID:-}" ] && kill -0 "$OLLAMA_PID" >/dev/null 2>&1; then
  kill "$OLLAMA_PID" >/dev/null 2>&1 || true
fi

echo ""
read -r -p "Press Return to close this window..."
