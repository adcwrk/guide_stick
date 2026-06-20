#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="${1:-$USB_DIR/documents}"
STAGING_DIR="$USB_DIR/anythingllm_data/document_staging"
BACKUP_DIR="$USB_DIR/backups/document_staging"
LOG_DIR="$USB_DIR/logs"
LOG_FILE="$LOG_DIR/ingest-documents-$(date -u +%Y%m%dT%H%M%SZ).log"

mkdir -p "$SOURCE_DIR" "$STAGING_DIR" "$BACKUP_DIR" "$LOG_DIR"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

backup_existing() {
  dest="$1"
  [ -f "$dest" ] || return 0
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  rel="${dest#$STAGING_DIR/}"
  mkdir -p "$BACKUP_DIR/$stamp/$(dirname "$rel")"
  cp -p "$dest" "$BACKUP_DIR/$stamp/$rel"
}

log "Document ingestion started"
log "Source: $SOURCE_DIR"
log "Staging: $STAGING_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
  log "ERROR: Source directory missing: $SOURCE_DIR"
  exit 1
fi

count=0
failed=0
while IFS= read -r -d '' src; do
  rel="${src#$SOURCE_DIR/}"
  dest="$STAGING_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && cmp -s "$src" "$dest"; then
    log "UNCHANGED: $rel"
    continue
  fi
  backup_existing "$dest"
  if cp -p "$src" "$dest"; then
    log "STAGED: $rel"
    count=$((count + 1))
  else
    log "ERROR: failed to stage $rel"
    failed=$((failed + 1))
  fi
done < <(find "$SOURCE_DIR" -type f -print0)

log "Document ingestion complete: staged=$count failed=$failed"
log "Original source files were preserved."

[ "$failed" -eq 0 ]
