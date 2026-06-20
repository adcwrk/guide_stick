#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_ROOT="$USB_DIR/backups"
LOG_DIR="$USB_DIR/logs"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$BACKUP_ROOT/portable-$STAMP"
ARCHIVE="$BACKUP_ROOT/portable-$STAMP.tar.gz"
LOG_FILE="$LOG_DIR/backup-portable-$STAMP.log"

mkdir -p "$BACKUP_DIR" "$BACKUP_ROOT" "$LOG_DIR"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

copy_if_present() {
  name="$1"
  src="$USB_DIR/$name"
  if [ -e "$src" ]; then
    log "Backing up $name"
    mkdir -p "$BACKUP_DIR/$(dirname "$name")"
    cp -Rp "$src" "$BACKUP_DIR/$name" 2>>"$LOG_FILE" || log "WARN: failed to copy $name"
  else
    log "Skipping missing path: $name"
  fi
}

log "Portable backup started"
copy_if_present "config"
copy_if_present "documents"
copy_if_present "logs"
copy_if_present "data/chroma"
copy_if_present "data/anythingllm"
copy_if_present "data/openwebui"
copy_if_present "models/installed-models.txt"
copy_if_present "models/Modelfile"
copy_if_present "anythingllm_data/storage"
copy_if_present "anythingllm_data/document_staging"
copy_if_present "ollama/data/manifests"

if tar -czf "$ARCHIVE" -C "$BACKUP_DIR" . 2>>"$LOG_FILE"; then
  log "Backup archive created: $ARCHIVE"
else
  log "ERROR: Could not create backup archive"
  exit 1
fi

log "Portable backup complete"
echo "$ARCHIVE"
