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

GUIDE is intentionally not built yet.

Future GUIDE work should:

- Add GUIDE to `config/services.json`.
- Store GUIDE state under `data/guide`.
- Reuse LAN URL and USB detection helpers.
- Preserve AnythingLLM and Open WebUI as supported GUI options.
- Add authentication and service health checks before LAN exposure.
