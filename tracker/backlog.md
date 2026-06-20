# GUIDE Backlog

## Epic E01: Upstream Portable-AI-USB Preservation

- ID: E01-B01
- Title: Preserve upstream launch and setup behavior
- Description: Keep original Windows, macOS, and Linux entry points working while adding optional enhancements.
- Priority: P0
- Phase: 1-3
- Status: In Progress
- Dependencies: None
- Acceptance criteria: Existing upstream scripts remain present; enhancements are additive; reports document preserved behavior.

## Epic E02: Apple Silicon Support

- ID: E02-B01
- Title: M4 Max optimized macOS startup
- Description: Detect Apple Silicon, use USB-local Ollama models, and prepare default/fallback/embedding models.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: E01-B01
- Acceptance criteria: `setup-mac.sh` and `start-mac.command` load config, write logs, and avoid host-specific paths.

## Epic E03: Linux/NUC Support

- ID: E03-B01
- Title: NUC startup with host-service preservation
- Description: Support `/mnt/usb` execution on Linux without killing existing GUIDE, Ollama, or GUI services.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: E01-B01
- Acceptance criteria: `setup-linux.sh`, `start-linux.sh`, and `healthcheck-linux.sh` exist and detect occupied ports.

## Epic E04: AnythingLLM GUI

- ID: E04-B01
- Title: Preserve AnythingLLM GUI workflow
- Description: Continue supporting AnythingLLM Desktop while preparing USB-local service data.
- Priority: P0
- Phase: 2
- Status: In Progress
- Dependencies: E01-B01
- Acceptance criteria: Launchers preserve AnythingLLM flow and store data under USB paths.

## Epic E05: Open WebUI GUI

- ID: E05-B01
- Title: Add optional Open WebUI launch path
- Description: Detect host or configured Open WebUI and launch it with USB-local data.
- Priority: P1
- Phase: 2
- Status: Implemented
- Dependencies: E06-B01
- Acceptance criteria: Launchers attempt Open WebUI startup only when available and report missing runtime clearly.

## Epic E06: Ollama Backend

- ID: E06-B01
- Title: Preserve localhost Ollama backend
- Description: Keep Ollama local by default and use it as backend for AnythingLLM and Open WebUI.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: E01-B01
- Acceptance criteria: Remote Ollama API remains disabled unless `ENABLE_REMOTE_OLLAMA=true`.

## Epic E07: ChromaDB Persistence

- ID: E07-B01
- Title: Reserve USB ChromaDB storage
- Description: Store ChromaDB/vector data under `data/chroma` and back it up before migrations.
- Priority: P1
- Phase: 2
- Status: Implemented
- Dependencies: E12-B01
- Acceptance criteria: `data/chroma` exists, is writable, and is included in backups.

## Epic E08: Remote LAN Access

- ID: E08-B01
- Title: LAN URL discovery and display
- Description: Print local, LAN, and hostname URLs for GUI services.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: E05-B01
- Acceptance criteria: `scripts/get-lan-url.sh` exists and launchers print URLs.

## Epic E09: User Authentication

- ID: E09-B01
- Title: GUI authentication policy
- Description: Require GUI auth where supported and document first-run admin setup.
- Priority: P0
- Phase: 2
- Status: In Progress
- Dependencies: E04-B01, E05-B01
- Acceptance criteria: `ENABLE_AUTH=true` exists; docs warn if selected GUI lacks auth in current launch mode.

## Epic E10: One-Click Launchers

- ID: E10-B01
- Title: macOS and Linux launchers
- Description: Provide root-level launchers for M4 Max and NUC execution.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: E02-B01, E03-B01
- Acceptance criteria: `start-mac.command` and `start-linux.sh` validate USB, log, and print URLs.

## Epic E11: Document Ingestion

- ID: E11-B01
- Title: Non-destructive document staging
- Description: Stage files from `documents/` without deleting originals.
- Priority: P1
- Phase: 2
- Status: Implemented
- Dependencies: E12-B01
- Acceptance criteria: `scripts/ingest-documents.sh` logs operations and backs up overwritten staged files.

## Epic E12: Backup and Recovery

- ID: E12-B01
- Title: Portable backup archive
- Description: Back up config, documents, logs, GUI data, ChromaDB data, and runtime settings to USB.
- Priority: P0
- Phase: 2
- Status: Implemented
- Dependencies: None
- Acceptance criteria: `scripts/backup-portable.sh` creates timestamped archives under `backups/`.

## Epic E13: Health Checks

- ID: E13-B01
- Title: macOS and Linux health reports
- Description: Validate USB identity, required folders, ports, models, and writable paths.
- Priority: P0
- Phase: 3
- Status: Implemented
- Dependencies: E02-B01, E03-B01
- Acceptance criteria: `reports/healthcheck_report.md` is generated from healthcheck scripts.

## Epic E14: Future GUIDE Integration

- ID: E14-B01
- Title: GUIDE architecture path
- Description: Reserve a future integration path without building GUIDE in this phase.
- Priority: P2
- Phase: Future
- Status: Backlog
- Dependencies: E08-B01, E09-B01
- Acceptance criteria: GUIDE can be added later as a service in `config/services.json` with data under `data/guide`.
