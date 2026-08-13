# GUIDE Critical Path

Updated: 2026-08-12

This file identifies the execution order that turns the GUIDE USB build into a usable offline emergency knowledge, RAG, model, documentation, and tester-delivery platform.

## Current Critical Path

| Order | Task | Status | Why It Is Critical |
|---:|---|---|---|
| 1 | T008 Ollama backend | Complete | Required model runtime for chat, vision, and embeddings. |
| 2 | T028 Pull `nomic-embed-text` | Complete | Required to generate embeddings offline. |
| 3 | T016 Library UI | Complete with Warnings | Establishes local library access and source URLs; deeper search remains a continuing refinement. |
| 4 | T017 ZIM import | Complete with Warnings | Provides the trusted offline source corpus. |
| 5 | T018 Extract ZIM and HTML text | Complete with Warnings | Generated the HTML/text corpus under `data/rag/corpus`; native ZIM extraction remains guarded by size limits. |
| 6 | T019 Build ChromaDB library index | Complete | ChromaDB `guide_library` contains 213,850 indexed chunks for 56,136 corpus documents. |
| 7 | T029 Add RAG orchestration endpoint | Complete with Warnings | `/api/ask-library` retrieves Chroma chunks, builds source context, asks Ollama, and returns cited answers. |
| 8 | T020 Add Ask Library UI | Complete with Warnings | Ask Library status, citation rendering, risk notes, fallback behavior, and auth-policy status are implemented. |
| 9 | T021 Add RAG operations checks | Complete with Warnings | RAG ops checks validate corpus manifest rows, source inventory, index freshness, indexed chunk counts, and live Chroma collection count. |
| 10 | T023 Define household preparedness profile schema | Complete with Warnings | Establishes household context used by preparedness and operations workflows. |
| 11 | T024 Define preparedness inventory schema | Complete with Warnings | Adds local supplies data and gap calculations used during incidents. |
| 12 | T025 Define incident records and operational timeline | Complete with Warnings | Adds incident status, resources, documents, recommendations, and timeline events under authenticated WebUI/API control. |
| 13 | T026 Define communications center schema and templates | Complete with Warnings | Adds contacts, channels, message templates, and message logs for offline operations. |
| 14 | T027 Decide map import/viewer strategy | Complete with Warnings | Adds a JSON-first offline map/resource context path and reserves `data/guide/maps` for future map packages. |
| 15 | T030 Current GUIDE model inventory config | Complete | `config/models.json` now reflects the current GUIDE USB model set, including text, reasoning, coding, creative, vision, and embedding models. |
| 16 | T031 Mac Review Picture vision patch | Complete | The Mac launcher patch ensures GUIDE uses the USB Ollama service so `moondream` and `qwen2.5-vl` are visible for Review Picture. |
| 17 | T032 Tester beta plan | Complete | `BETA_TEST_PLAN.md` covers launch, offline use, Review Picture, Journal, buttons, all LLMs, emergency medical prompts, and README review. |
| 18 | T033 GUIDE README expansion | Complete | `GUIDE_README.html` now explains models, first-10-minute workflow, test prompts, picture review, Journal, offline verification, privacy, safety, troubleshooting, and defect reporting. |
| 19 | T034 Mac patch delivery package | Complete | `updates/guide-mac-vision-fix-1.3.1.zip` packages the Mac launcher fix, README, beta plan, and source files for testers. |
| 20 | T035 GitHub upload | Complete | The updated model config, README, beta plan, GUIDE README, and Mac patch package were pushed to `adcwrk/guide_stick`. |

## Phase Gates

| Gate | Required Tasks | Exit Criteria |
|---|---|---|
| Model Gate | T008, T028, T030 | Ollama is reachable; chat, vision, and embedding models are represented in config and available on the GUIDE USB. |
| Corpus Gate | T016, T017, T018 | Library content is copied, browsable, and extracted to `data/rag/corpus`. |
| Index Gate | T009, T019 | ChromaDB index exists under `data/chroma/library` and can be rebuilt/resumed. |
| Application Gate | T029, T020 | `/api/ask-library` answers questions with citations and the WebUI can call it. |
| Operations Gate | T021, T023, T024, T025, T026, T027 | Health checks, schemas, examples, and operational JSON paths exist for preparedness workflows. |
| Tester Gate | T031, T032, T033, T034 | Mac testers can apply the vision patch and execute documented beta coverage. |
| Repository Gate | T035 | GitHub contains the current model configuration and tester delivery package. |

## Immediate Next Task

None.

Reason: all tracked critical-path tasks are complete or complete with warnings.

## Remaining Warning Items

- Native ZIM article extraction remains a deliberate targeted job guarded by `ZIM_MAX_BYTES`.
- Some GUIDE WebUI areas use JSON editors; richer form-based dashboards remain future UX refinement.
- Large `.mbtiles` or `.pmtiles` map viewer work remains deferred until a smaller region/export strategy is selected.
- AnythingLLM and Open WebUI authentication still depend on their own first-run auth flows; TLS requires a separate reverse proxy.
- Mac Review Picture fix is packaged and uploaded, but each tester should still verify it on their own Mac and USB.

## Completed Delivery Evidence

- `config/models.json`
- `README.md`
- `updates/guide-mac-vision-fix-1.3.1/guide-mac-vision-fix-1.3.1.zip`
- `updates/guide-mac-vision-fix-1.3.1/BETA_TEST_PLAN.md`
- `updates/guide-mac-vision-fix-1.3.1/GUIDE_README.html`
- `updates/guide-mac-vision-fix-1.3.1/source/`
- GitHub commit `73b2008`
