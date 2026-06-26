# RAG Orchestration Report

Generated: 2026-06-26

## Summary

T029 is complete with warnings. The lightweight GUIDE WebUI now exposes a RAG orchestration endpoint that retrieves chunks from the USB-local ChromaDB index, builds a cited context prompt, asks Ollama, and returns an answer with citation metadata.

## Implemented Endpoints

- `GET /api/library-index`
  - Reports the Chroma index path, collection name, manifest fields, and live collection count when available.
- `POST /api/ask-library`
  - Accepts `question` or `message`, optional `model`, and optional `top_k`.
  - Embeds the question with `nomic-embed-text`.
  - Queries ChromaDB collection `guide_library` under `data/chroma/library`.
  - Builds a source-bounded prompt with bracketed citation labels.
  - Calls Ollama `/api/chat`.
  - Returns `answer`, `citations`, `retrieved_chunks`, `risk_notes`, `model`, `embedding_model`, and `index_status`.

Normal `/api/chat` behavior remains available.

## Runtime Validation

Validation host: GUIDE USB mounted at `/mnt/usb/GUIDE`.

- `python3 -m py_compile scripts/guide-webui.py`: passed.
- `GET /api/library-index`: returned `status=complete` and `collection_count=213850`.
- `POST /api/ask-library` test:
  - Question: `How do I use KA Lite learner features?`
  - Model: `llama3.2:3b`
  - `top_k`: `3`
  - Result: HTTP 200 with answer, 3 citations, `embedding_model=nomic-embed-text`, and `index_status.status=complete`.

## Warning

The endpoint is functional, but retrieval quality depends on the current corpus. The indexed corpus is the HTML/text extraction output from T018. Native ZIM article extraction is still deferred, so some emergency-domain questions may retrieve weak or off-topic context until that corpus coverage is improved and the index is rebuilt.

## Next Task

T020 is next. Basic Ask Library UI wiring exists, but the production-ready user flow still needs status/fallback behavior and must account for the open T011 authentication/security work.
