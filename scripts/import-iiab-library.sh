#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${IIAB_SOURCE:-/mnt/sdcard/rootfs/library}"
TARGET="${IIAB_TARGET:-$ROOT/library/iiab}"
LOG_DIR="$ROOT/logs"
LOG_FILE="$LOG_DIR/iiab-library-import-$(date -u +%Y%m%dT%H%M%SZ).log"

INCLUDE_ZIMS="${INCLUDE_ZIMS:-false}"
INCLUDE_MAPS="${INCLUDE_MAPS:-false}"
INCLUDE_BACKUPS="${INCLUDE_BACKUPS:-false}"

mkdir -p "$TARGET" "$LOG_DIR"

if [[ ! -d "$SOURCE" ]]; then
  echo "ERROR: IIAB source not found: $SOURCE" >&2
  exit 1
fi

if [[ ! -w "$TARGET" ]]; then
  echo "ERROR: GUIDE library target is not writable: $TARGET" >&2
  exit 1
fi

excludes=()
if [[ "$INCLUDE_BACKUPS" != "true" ]]; then
  excludes+=(--exclude="www/html/common/html/urgentanswersbak/")
fi
if [[ "$INCLUDE_MAPS" != "true" ]]; then
  excludes+=(--exclude="www/osm-vector-maps/")
fi
if [[ "$INCLUDE_ZIMS" != "true" ]]; then
  excludes+=(--exclude="zims/content/")
fi

{
  echo "GUIDE IIAB library import"
  echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Source: $SOURCE"
  echo "Target: $TARGET"
  echo "INCLUDE_ZIMS=$INCLUDE_ZIMS"
  echo "INCLUDE_MAPS=$INCLUDE_MAPS"
  echo "INCLUDE_BACKUPS=$INCLUDE_BACKUPS"
  echo
  rsync -rtL \
    --no-perms --no-owner --no-group --omit-dir-times \
    --partial --ignore-existing --human-readable \
    --info=progress2,stats2,name1 \
    "${excludes[@]}" \
    "$SOURCE/" "$TARGET/"
  rc=$?
  echo
  echo "Rsync exit code: $rc"
  echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  exit "$rc"
} 2>&1 | tee "$LOG_FILE"
