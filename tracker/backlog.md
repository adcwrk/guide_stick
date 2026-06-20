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

## Epic E15: Offline Library UI and RAG

- ID: E15-B01
- Title: IIAB library browser in GUIDE WebUI
- Description: Expose copied Internet-in-a-Box library content from `/mnt/usb/GUIDE/library/iiab` through the GUIDE WebUI with searchable sections and stable local links.
- Priority: P0
- Phase: Future
- Status: In Progress
- Dependencies: E08-B01, E14-B01
- Acceptance criteria: WebUI shows Library section; `/api/library` reports copied content; files are browsable under `/library/`; deferred maps/ZIM status is visible.

- ID: E15-B02
- Title: ZIM and HTML extraction pipeline
- Description: Add scripts to extract text and metadata from ZIM files, static HTML, MediaWiki, WordPress, KA Lite, and `documents/` into a normalized USB-local corpus.
- Priority: P0
- Phase: Future
- Status: Backlog
- Dependencies: E15-B01, E11-B01
- Acceptance criteria: `scripts/extract-zim-content.sh` and/or equivalent extractor produces chunkable text under `data/rag/corpus`; originals are never modified or deleted.

- ID: E15-B03
- Title: Library embedding and ChromaDB index
- Description: Install and use `nomic-embed-text` to build a persistent ChromaDB index for the imported library under `/mnt/usb/GUIDE/data/chroma/library`.
- Priority: P0
- Phase: Future
- Status: Backlog
- Dependencies: E07-B01, E15-B02, E06-B01
- Acceptance criteria: `scripts/build-rag-index.sh` creates a resumable vector index; index metadata is written to `data/rag/library_manifest.json`; backups include index metadata.

- ID: E15-B04
- Title: Ask Library RAG mode
- Description: Add an Ask Library mode to GUIDE WebUI that retrieves library chunks from ChromaDB, sends grounded context to Ollama, and returns answers with citations/links back to local library files.
- Priority: P0
- Phase: Future
- Status: Backlog
- Dependencies: E15-B03, E06-B01, E09-B01
- Acceptance criteria: WebUI can answer questions from imported library content; responses include source titles and `/library/...` links; chat still works when RAG index is unavailable.

- ID: E15-B05
- Title: Long-running library import completion
- Description: Finish copying large ZIM payloads and optional map databases from the SD/eMMC source into USB storage using resumable import jobs.
- Priority: P1
- Phase: Future
- Status: In Progress
- Dependencies: E15-B01
- Acceptance criteria: ZIM copy completes or report identifies deferred files; `reports/iiab_library_import_report.md` is updated; WebUI library status reflects complete and partial ZIM files.

## Epic E16: GUIDE Preparedness and Operations Platform

- ID: E16-B01
- Title: Product vision and operating doctrine
- Description: Preserve GUIDE as Generative Unified Intelligence for Disaster and Emergency Management, an offline-first preparedness and operational decision-support platform.
- Priority: P0
- Phase: Future
- Status: In Progress
- Dependencies: E14-B01
- Acceptance criteria: Product vision exists in `reports/guide_product_vision.md`; roadmap and implementation tasks align to preparedness, response, trusted knowledge, and operational decision support.

- ID: E16-B02
- Title: Household intake and preparedness profile
- Description: Capture household or organization profile data including people, ages, medical conditions, medications, pets, power dependencies, mobility limitations, and preparedness goals.
- Priority: P0
- Phase: Future
- Status: Backlog
- Dependencies: E16-B01, E09-B01
- Acceptance criteria: Profile schema exists; data is stored on USB; WebUI can collect and edit intake data; recommendations can use profile context.

- ID: E16-B03
- Title: Preparedness inventory and gap analysis
- Description: Track water, food, medical supplies, medications, fuel, power systems, communications equipment, and shelter supplies, then calculate requirements and gaps.
- Priority: P0
- Phase: Future
- Status: Backlog
- Dependencies: E16-B02
- Acceptance criteria: Inventory schema exists; duration and shortfall calculations work; WebUI displays critical gaps and recommended actions.

- ID: E16-B04
- Title: Incident management workspace
- Description: Add incident records for medical emergencies, power outages, severe weather, wildfires, flooding, search and rescue, and communications failures.
- Priority: P1
- Phase: Future
- Status: Backlog
- Dependencies: E16-B02, E15-B04
- Acceptance criteria: Incidents include status, timeline, documentation, resources, and AI-assisted recommendations with sources.

- ID: E16-B05
- Title: Communications planning center
- Description: Prepare for Meshtastic, radio planning, message drafting, message compression, communications logging, and network visualization.
- Priority: P1
- Phase: Future
- Status: Backlog
- Dependencies: E16-B04
- Acceptance criteria: Communications plan schema exists; message templates exist; future Meshtastic integration path is documented.

- ID: E16-B06
- Title: Maps and situational awareness
- Description: Integrate hazards, incidents, resources, shelters, hospitals, communications infrastructure, and evacuation routes into an offline map workflow.
- Priority: P1
- Phase: Future
- Status: Backlog
- Dependencies: E15-B05, E16-B04
- Acceptance criteria: Offline map source strategy is documented; WebUI can reference local map resources; incident/resource locations can be represented.
