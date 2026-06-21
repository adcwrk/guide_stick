# Roadmap

## Phase 1: Analysis

- Analyze upstream Portable-AI-USB.
- Document preserved workflows and extension risks.
- Identify remote GUI and authentication gaps.

## Phase 2: Portable Enhancements

- Add Apple Silicon setup and launch support.
- Add Linux/NUC setup and launch support.
- Add remote LAN GUI configuration.
- Add Open WebUI as an optional GUI.
- Add ChromaDB data path.
- Add env-based authentication policy.

## Phase 3: Validation

- Validate GUIDE USB identity and writability.
- Run health checks.
- Run backup automation.
- Record performance measurements.
- Document runtime gaps requiring the target M4 Max or NUC.

## Future Phase: GUIDE

GUIDE is now defined as Generative Unified Intelligence for Disaster and Emergency Management. It is an offline-first preparedness, response, and operational decision-support platform.

Future GUIDE work should:

### Milestone M1: Library RAG

- Add GUIDE to `config/services.json`.
- Store GUIDE state under `data/guide`.
- Reuse LAN URL and USB detection helpers.
- Preserve AnythingLLM and Open WebUI as supported GUI options.
- Add authentication and service health checks before LAN exposure.
- Expand the current GUIDE WebUI Library panel into a full offline library browser.
- Add a RAG pipeline over copied IIAB/ZIM/HTML/document content.
- Store extracted corpus data under `data/rag/corpus`.
- Store library vector indexes under `data/chroma/library`.
- Add Ask Library mode with citations to local `/library/...` URLs.
- Keep future GUIDE integration compatible with later GUIDE service/runtime additions.

### Milestone M2: Preparedness Core

- Add household intake and preparedness profiles.
- Add inventory management and preparedness gap analysis.

### Milestone M3: Operations

- Add incident management with timelines, resources, and recommendations.
- Add communications planning with a future Meshtastic integration path.
- Add maps and situational awareness for hazards, resources, shelters, hospitals, communications infrastructure, and evacuation routes.
