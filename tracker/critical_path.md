# GUIDE Critical Path

Generated: 2026-06-21

This file identifies the execution order that turns the current GUIDE USB build into a usable offline emergency knowledge and RAG platform.

## Current Critical Path

| Order | Task | Status | Why It Is Critical |
|---:|---|---|---|
| 1 | T008 Ollama backend | Complete | Required model runtime for chat and embeddings. |
| 2 | T016 Library UI | Complete with Warnings | Establishes local library access and source URLs; full search remains future enhancement. |
| 3 | T017 ZIM import | Complete with Warnings | Provides the trusted offline source corpus. |
| 4 | T028 Pull `nomic-embed-text` | Complete | Required to generate embeddings offline. |
| 5 | T018 Extract ZIM and HTML text | Complete with Warnings | Generated the HTML/text corpus under `data/rag/corpus`; USB-local `zimdump` is installed, and native ZIM article extraction is deferred as a targeted size-guarded job. |
| 6 | T019 Build ChromaDB library index | In Progress | ChromaDB runtime is installed and `guide_library` contains an initial 256 indexed chunks; full corpus indexing is resumable. |
| 7 | T029 Add RAG orchestration endpoint | Backlog | Connects retrieval, prompt construction, and Ollama answer generation. |
| 8 | T020 Add Ask Library UI | Backlog | Exposes source-grounded RAG to users. |
| 9 | T021 Add RAG operations checks | Backlog | Makes the index supportable and auditable. |

## Phase Gates

| Gate | Required Tasks | Exit Criteria |
|---|---|---|
| Model Gate | T008, T028 | Ollama is reachable and `nomic-embed-text` is available in the USB-local model store. |
| Corpus Gate | T016, T017, T018 | Library content is copied, browsable, and extracted to `data/rag/corpus`. |
| Index Gate | T009, T019 | ChromaDB index exists under `data/chroma/library` and can be rebuilt/resumed. |
| Application Gate | T029, T020 | `/api/ask-library` answers questions with citations and the WebUI can call it. |
| Operations Gate | T021 | Health checks report model, corpus, index, and source manifest status. |

## Immediate Next Task

T019: Build ChromaDB library index.

Reason: T019 has the ChromaDB runtime and an initial resumable index, but the full 56,136-document corpus still needs to be indexed under `data/chroma/library`.

## Parallel Work That Does Not Block RAG

- T011: Add authentication to the lightweight GUIDE WebUI or document compensating controls.
- T023: Define household preparedness profile schema.
- T024: Define preparedness inventory schema and calculations.
- T025: Define incident records and operational timeline.
- T026: Define communications center schema and templates.
- T027: Decide map import/viewer strategy.

## Deferred or Warning Items

- T017 is complete with warnings because the selected ZIM payload copied successfully, but rsync returned code 23 due to protected Matomo/Nextcloud/service runtime files outside the selected ZIM payload.
- T018 is complete with warnings because 56,136 HTML/text corpus documents were generated with zero extraction failures, but full native ZIM article extraction remains a deliberate targeted job. USB-local `zimdump` is installed; large dumps are guarded by `ZIM_MAX_BYTES`.
- T019 is in progress because the indexer and ChromaDB runtime are installed and validated, but the complete corpus index is a long-running USB/Ollama job.
- Offline map databases remain a separate import strategy under T027 because the large `.mbtiles` transfer previously stalled.
