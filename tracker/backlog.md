# GUIDE Backlog

Updated: 2026-08-12

## Epic E01: Upstream Portable-AI-USB Preservation

- ID: E01-B01
- Title: Preserve upstream launch and setup behavior
- Description: Keep original Windows, macOS, and Linux entry points working while adding optional enhancements.
- Priority: P0
- Phase: 1-3
- Status: Complete with Warnings
- Dependencies: None
- Acceptance criteria: Existing upstream scripts remain present; enhancements are additive; reports document preserved behavior.
- Notes: AnythingLLM/Open WebUI runtime behavior still depends on host GUI/runtime availability.

## Epic E02: Apple Silicon Support

- ID: E02-B01
- Title: M4 Max optimized macOS startup
- Description: Detect Apple Silicon, use USB-local Ollama models, and prepare default/fallback/embedding models.
- Priority: P0
- Phase: 2
- Status: Complete
- Dependencies: E01-B01
- Acceptance criteria: `setup-mac.sh` and `start-mac.command` load config, write logs, and avoid host-specific paths.

## Epic E03: Linux/NUC Support

- ID: E03-B01
- Title: NUC startup with host-service preservation
- Description: Support `/mnt/usb` execution on Linux without killing existing GUIDE, Ollama, or GUI services.
- Priority: P0
- Phase: 2
- Status: Complete
- Dependencies: E01-B01
- Acceptance criteria: `setup-linux.sh`, `start-linux.sh`, and `healthcheck-linux.sh` exist and detect occupied ports.

## Epic E04: GUI Runtime Support

- ID: E04-B01
- Title: Preserve AnythingLLM GUI workflow
- Description: Continue supporting AnythingLLM Desktop while preparing USB-local service data.
- Priority: P0
- Phase: 2
- Status: Complete with Warnings
- Dependencies: E01-B01
- Acceptance criteria: Launchers preserve AnythingLLM flow and store data under USB paths.
- Notes: LAN port `3001` still depends on Docker/server runtime or a graphical desktop session on the target host.

- ID: E04-B02
- Title: Add optional Open WebUI launch path
- Description: Detect host or configured Open WebUI and launch it with USB-local data.
- Priority: P1
- Phase: 2
- Status: Complete
- Dependencies: E04-B01
- Acceptance criteria: Launchers attempt Open WebUI startup only when available and report missing runtime clearly.

## Epic E05: Core Runtime, Access, Security, Backup

- ID: E05-B01
- Title: Preserve localhost Ollama backend
- Description: Keep Ollama local by default and use it as backend for GUIDE, AnythingLLM, and Open WebUI.
- Priority: P0
- Phase: 2
- Status: Complete
- Dependencies: E02-B01, E03-B01
- Acceptance criteria: Remote Ollama API remains disabled unless `ENABLE_REMOTE_OLLAMA=true`.

- ID: E05-B02
- Title: LAN URL discovery and display
- Description: Print local, LAN, and hostname URLs for GUI services.
- Priority: P0
- Phase: 2
- Status: Complete
- Dependencies: E05-B01
- Acceptance criteria: `scripts/get-lan-url.sh` exists and launchers print URLs.

- ID: E05-B03
- Title: GUI authentication policy
- Description: Require GUI auth where supported and document first-run admin setup.
- Priority: P0
- Phase: 2
- Status: Complete with Warnings
- Dependencies: E04-B01, E04-B02
- Acceptance criteria: `ENABLE_AUTH=true` exists; docs warn if selected GUI lacks auth in current launch mode.
- Notes: Lightweight GUIDE WebUI supports HTTP Basic auth; TLS requires a separate reverse proxy.

- ID: E05-B04
- Title: Portable backup archive
- Description: Back up config, documents, logs, GUI data, ChromaDB data, and runtime settings to USB.
- Priority: P0
- Phase: 2
- Status: Complete
- Dependencies: None
- Acceptance criteria: `scripts/backup-portable.sh` creates timestamped archives under `backups/`.

- ID: E05-B05
- Title: macOS and Linux health reports
- Description: Validate USB identity, required folders, ports, models, and writable paths.
- Priority: P0
- Phase: 3
- Status: Complete
- Dependencies: E02-B01, E03-B01
- Acceptance criteria: `reports/healthcheck_report.md` is generated from healthcheck scripts.

## Epic E06: Offline Library UI and RAG

- ID: E06-B01
- Title: IIAB library browser in GUIDE WebUI
- Description: Expose copied Internet-in-a-Box library content through GUIDE WebUI with searchable sections and stable local links.
- Priority: P0
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E05-B02
- Acceptance criteria: WebUI shows Library section; `/api/library` reports copied content; files are browsable under `/library/`.

- ID: E06-B02
- Title: ZIM and HTML extraction pipeline
- Description: Extract text and metadata from ZIM files, static HTML, MediaWiki, WordPress, KA Lite, and `documents/` into a normalized USB-local corpus.
- Priority: P0
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E06-B01
- Acceptance criteria: Corpus files are generated under `data/rag/corpus`; originals are never modified or deleted.
- Notes: Full native ZIM extraction remains a targeted guarded job.

- ID: E06-B03
- Title: Library embedding and ChromaDB index
- Description: Use `nomic-embed-text` to build a persistent ChromaDB index for the imported library.
- Priority: P0
- Phase: 4
- Status: Complete
- Dependencies: E06-B02
- Acceptance criteria: `scripts/build-rag-index.sh` creates a resumable vector index and writes metadata.

- ID: E06-B04
- Title: Ask Library RAG mode
- Description: Retrieve library chunks from ChromaDB, send grounded context to Ollama, and return answers with citations.
- Priority: P0
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E06-B03
- Acceptance criteria: WebUI can answer questions from imported library content; responses include source titles and local links.

- ID: E06-B05
- Title: RAG operations checks
- Description: Add library manifest and index health checks.
- Priority: P1
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E06-B03, E06-B04
- Acceptance criteria: `library_manifest.json` records sources, chunks, and index status.

## Epic E07: GUIDE Preparedness and Operations Platform

- ID: E07-B01
- Title: Product vision and operating doctrine
- Description: Preserve GUIDE as Generative Unified Intelligence for Disaster and Emergency Management.
- Priority: P0
- Phase: 4
- Status: Complete
- Dependencies: E05-B02
- Acceptance criteria: Product vision exists in `reports/guide_product_vision.md`.

- ID: E07-B02
- Title: Household intake and preparedness profile
- Description: Capture household or organization profile data including people, medical needs, pets, power dependencies, and preparedness goals.
- Priority: P0
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E07-B01, E05-B03
- Acceptance criteria: Profile schema exists; data is stored on USB; WebUI can collect and edit intake data.

- ID: E07-B03
- Title: Preparedness inventory and gap analysis
- Description: Track water, food, medical supplies, medications, fuel, power systems, communications equipment, and shelter supplies.
- Priority: P0
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E07-B02
- Acceptance criteria: Inventory schema exists; duration and shortfall calculations work.

- ID: E07-B04
- Title: Incident management workspace
- Description: Add incident records for medical emergencies, power outages, severe weather, wildfires, flooding, search and rescue, and communications failures.
- Priority: P1
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E07-B02, E06-B04
- Acceptance criteria: Incidents include status, timeline, documentation, resources, and AI-assisted recommendations with sources.

- ID: E07-B05
- Title: Communications planning center
- Description: Prepare contacts, channels, message templates, message logs, and future Meshtastic integration.
- Priority: P1
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E07-B04
- Acceptance criteria: Communications schema and templates exist; future Meshtastic integration path is documented.

- ID: E07-B06
- Title: Maps and situational awareness
- Description: Represent hazards, incidents, resources, shelters, hospitals, communications infrastructure, and evacuation routes.
- Priority: P1
- Phase: 4
- Status: Complete with Warnings
- Dependencies: E07-B04
- Acceptance criteria: Offline map/resource context schema exists; local map package path is reserved.

## Epic E08: Current GUIDE USB Tester Delivery

- ID: E08-B01
- Title: Update current model inventory configuration
- Description: Align `config/models.json` and README model guidance to the current GUIDE USB model set.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E05-B01
- Acceptance criteria: Config includes fast text, planning, reasoning, coding, creative, vision, and embedding models.

- ID: E08-B02
- Title: Fix Mac Review Picture vision-model detection
- Description: Patch the Mac launcher so GUIDE starts USB Ollama before opening the app and sees `moondream` and `qwen2.5-vl`.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E08-B01
- Acceptance criteria: Patch source starts USB Ollama, verifies a vision model appears in `/api/tags`, and avoids attaching to a host Ollama service.

- ID: E08-B03
- Title: Create comprehensive beta test plan
- Description: Provide tester coverage for launch, offline use, Review Picture, Journal, buttons, all LLMs, emergency medical prompts, and README review.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E08-B01, E08-B02
- Acceptance criteria: `BETA_TEST_PLAN.md` exists and is included in the patch package.

- ID: E08-B04
- Title: Expand GUIDE README
- Description: Add model picker, first-10-minute workflow, known-good prompts, picture review, Journal, offline verification, privacy, safety, troubleshooting, and defect reporting.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E08-B01
- Acceptance criteria: `GUIDE_README.html` exists and is included in the patch package.

- ID: E08-B05
- Title: Package Mac tester update
- Description: Package the Mac vision patch with hidden payload, README, beta plan, and GUIDE README.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E08-B02, E08-B03, E08-B04
- Acceptance criteria: `guide-mac-vision-fix-1.3.1.zip` passes archive integrity checks and opens with only user-facing files visible in Finder.

- ID: E08-B06
- Title: Upload guide configurations to GitHub
- Description: Push updated configs, documentation, test plan, and Mac patch package to `adcwrk/guide_stick`.
- Priority: P0
- Phase: 5
- Status: Complete
- Dependencies: E08-B05
- Acceptance criteria: Remote `main` contains commit `73b2008` with the update package.

## Future Backlog

- ID: FB-B01
- Title: Guided preparedness forms
- Description: Replace raw JSON editors with structured forms for household profile, inventory, incidents, communications, and situational awareness.
- Priority: P1
- Phase: Future
- Status: Backlog
- Dependencies: E07-B02, E07-B03, E07-B04, E07-B05, E07-B06
- Acceptance criteria: Users can edit core preparedness data without directly editing JSON.

- ID: FB-B02
- Title: Release manifest and checksums
- Description: Add versioned release notes and checksums for each USB patch package.
- Priority: P1
- Phase: Future
- Status: Backlog
- Dependencies: E08-B05
- Acceptance criteria: Each patch release has a manifest with files, hash, purpose, install steps, and rollback notes.

- ID: FB-B03
- Title: Automated launcher smoke tests
- Description: Add host-safe tests for model visibility, Mac launcher paths, and patch script validation.
- Priority: P2
- Phase: Future
- Status: Backlog
- Dependencies: E08-B02
- Acceptance criteria: Smoke tests can run without modifying user data or killing unrelated services unexpectedly.

- ID: FB-B04
- Title: Small-region offline maps
- Description: Select and package a manageable `.pmtiles` or `.mbtiles` region and validate viewer behavior.
- Priority: P2
- Phase: Future
- Status: Backlog
- Dependencies: E07-B06
- Acceptance criteria: A small offline map region can be opened and referenced by GUIDE.
