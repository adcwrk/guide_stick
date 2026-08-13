# Roadmap

Updated: 2026-08-12

## Phase 1: Analysis

- Analyze upstream Portable-AI-USB.
- Document preserved workflows and extension risks.
- Identify remote GUI and authentication gaps.
- Status: Complete.

## Phase 2: Portable Enhancements

- Add Apple Silicon setup and launch support.
- Add Linux/NUC setup and launch support.
- Add remote LAN GUI configuration.
- Add Open WebUI as an optional GUI.
- Add ChromaDB data path.
- Add env-based authentication policy.
- Status: Complete with known GUI/auth caveats.

## Phase 3: Validation

- Validate GUIDE USB identity and writability.
- Run health checks.
- Run backup automation.
- Record performance measurements.
- Document runtime gaps requiring target Mac or NUC validation.
- Status: Complete with runtime warnings.

## Phase 4: GUIDE RAG and Operations Core

GUIDE is defined as Generative Unified Intelligence for Disaster and Emergency Management: an offline-first preparedness, response, and operational decision-support platform.

### Milestone M1: Library RAG

- Add GUIDE to `config/services.json`.
- Store GUIDE state under `data/guide`.
- Reuse LAN URL and USB detection helpers.
- Preserve AnythingLLM and Open WebUI as supported GUI options.
- Add authentication and service health checks before LAN exposure.
- Expand the GUIDE WebUI Library panel into an offline library browser.
- Add a RAG pipeline over copied IIAB/ZIM/HTML/document content.
- Store extracted corpus data under `data/rag/corpus`.
- Store library vector indexes under `data/chroma/library`.
- Add Ask Library mode with citations to local `/library/...` URLs.
- Status: Critical path complete with warnings.

### Milestone M2: Preparedness Core

- Add household intake and preparedness profiles.
- Add inventory management and preparedness gap analysis.
- Add incident records and operational timelines.
- Add communications planning and message templates.
- Add situational-awareness schema for hazards, resources, shelters, hospitals, routes, and communications infrastructure.
- Status: JSON schema/API/WebUI foundations complete with warnings; richer guided forms remain future UI work.

## Phase 5: GUIDE USB Tester Delivery

### Milestone M3: Model Inventory and Documentation

- Update `config/models.json` to match the current GUIDE USB model inventory.
- Document fast chat, planning, reasoning, coding, creative, vision, and embedding models.
- Expand `GUIDE_README.html` with model picker, known-good prompts, picture review, Journal, offline verification, privacy, safety, troubleshooting, and defect reporting.
- Status: Complete.

### Milestone M4: Beta Test Coverage

- Create `BETA_TEST_PLAN.md`.
- Cover USB launch, offline operation, system status, emergency classification, medical safety, water planning, communications, evacuation, retrieval, household/inventory, decision trees, bad input, dangerous requests, updates, shutdown/data integrity, Review Picture, Journal, buttons, all LLMs, emergency medical prompts, and README review.
- Status: Complete.

### Milestone M5: Mac Review Picture Patch

- Diagnose `No vision model available (e.g. moondream, qwen2.5-vl)` as a Mac launcher/Ollama service selection issue.
- Patch the Mac launcher and fallback launcher to start the bundled USB Ollama service before opening GUIDE.
- Verify the USB Ollama service exposes `moondream:latest` and `huihui_ai/qwen2.5-vl-abliterated:7b-instruct`.
- Package a Mac tester update as `updates/guide-mac-vision-fix-1.3.1.zip`.
- Hide patch payload under `.patch-files` so Finder shows only the README and command script.
- Status: Complete.

### Milestone M6: GitHub Distribution

- Upload model config, README updates, beta test plan, GUIDE README, Mac patch zip, and patch source files to `adcwrk/guide_stick`.
- Status: Complete in commit `73b2008`.

## Next Roadmap Candidates

- Convert JSON editors into guided preparedness forms.
- Add richer Journal UX tests once Journal UI details stabilize.
- Add automated smoke tests for launcher/model visibility where host permissions allow.
- Add release notes and versioned checksum manifest for each USB patch package.
- Build a smaller-region offline map package and map viewer path.
