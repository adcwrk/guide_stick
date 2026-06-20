#!/usr/bin/env bash

set -u

ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EXPECTED_MOUNT="${EXPECTED_USB_MOUNT:-/mnt/usb}"
EXPECTED_LABEL="${EXPECTED_USB_LABEL:-THKAILAR}"
EXPECTED_UUID="${EXPECTED_USB_UUID:-6676-08D4}"
EXPECTED_FS="${EXPECTED_USB_FS:-exfat}"
STRICT="${STRICT_USB_VALIDATION:-false}"

failures=0

say() {
  printf '%s\n' "$*"
}

pass() {
  say "PASS: $*"
}

warn() {
  say "WARN: $*"
}

fail() {
  say "FAIL: $*"
  failures=$((failures + 1))
}

have() {
  command -v "$1" >/dev/null 2>&1
}

[ -d "$ROOT" ] && pass "portable root exists: $ROOT" || fail "portable root missing: $ROOT"
[ -w "$ROOT" ] && pass "portable root writable: $ROOT" || fail "portable root not writable: $ROOT"

if have findmnt; then
  mount_target="$ROOT"
  while [ "$mount_target" != "/" ] && ! findmnt -n --target "$mount_target" >/dev/null 2>&1; do
    mount_target="$(dirname "$mount_target")"
  done

  source="$(findmnt -no SOURCE --target "$ROOT" 2>/dev/null | head -1 || true)"
  target="$(findmnt -no TARGET --target "$ROOT" 2>/dev/null | head -1 || true)"
  fs="$(findmnt -no FSTYPE --target "$ROOT" 2>/dev/null | head -1 || true)"

  [ -n "$source" ] && pass "mount source: $source" || fail "mount source not detected"
  [ -n "$target" ] && pass "mount target: $target" || fail "mount target not detected"

  if [ "$target" = "$EXPECTED_MOUNT" ] || [ "$ROOT" = "$EXPECTED_MOUNT/Portable-AI-USB" ]; then
    pass "expected mount path observed: $EXPECTED_MOUNT"
  elif [ "$STRICT" = "true" ]; then
    fail "expected mount path $EXPECTED_MOUNT, observed ${target:-unknown}"
  else
    warn "mount path is ${target:-unknown}; expected $EXPECTED_MOUNT for THKAILAR validation"
  fi

  [ "$fs" = "$EXPECTED_FS" ] && pass "filesystem: $fs" || fail "expected filesystem $EXPECTED_FS, observed ${fs:-unknown}"

  if have lsblk && [ -n "$source" ]; then
    label="$(lsblk -no LABEL "$source" 2>/dev/null | head -1 | xargs 2>/dev/null || true)"
    uuid="$(lsblk -no UUID "$source" 2>/dev/null | head -1 | xargs 2>/dev/null || true)"
    [ "$label" = "$EXPECTED_LABEL" ] && pass "label: $label" || fail "expected label $EXPECTED_LABEL, observed ${label:-unknown}"
    [ "$uuid" = "$EXPECTED_UUID" ] && pass "uuid: $uuid" || fail "expected uuid $EXPECTED_UUID, observed ${uuid:-unknown}"
  else
    warn "lsblk not available; label and UUID not checked"
  fi
elif have diskutil; then
  info="$(diskutil info "$ROOT" 2>/dev/null || true)"
  label="$(printf '%s\n' "$info" | awk -F: '/Volume Name/{gsub(/^ +| +$/,"",$2); print $2; exit}')"
  fs="$(printf '%s\n' "$info" | awk -F: '/File System Personality/{gsub(/^ +| +$/,"",$2); print tolower($2); exit}')"
  [ -z "$label" ] || [ "$label" = "$EXPECTED_LABEL" ] && pass "label: ${label:-unknown}" || fail "expected label $EXPECTED_LABEL, observed $label"
  case "$fs" in
    *exfat*|"") pass "filesystem: ${fs:-unknown}" ;;
    *) fail "expected exFAT filesystem, observed $fs" ;;
  esac
else
  warn "no supported mount metadata tool found; path and writability checked only"
fi

exit "$failures"
