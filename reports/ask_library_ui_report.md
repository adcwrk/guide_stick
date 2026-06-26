# Ask Library UI Report

Generated: 2026-06-26

## Summary

T020 is complete with warnings. The lightweight GUIDE WebUI now provides a source-grounded Ask Library path with index readiness status, citation rendering, risk note rendering, and fallback to normal chat when the RAG index is unavailable.

## Implemented UI Behavior

- Shows live library index readiness from `GET /api/library-index`.
- Disables `Ask Library` while the index is unavailable or a request is running.
- Falls back to normal `/api/chat` when Ask Library is unavailable or fails.
- Renders citation links returned by `/api/ask-library`.
- Renders RAG risk notes returned by the backend.
- Shows auth policy status from `GET /api/status`.
- Warns when `ENABLE_AUTH=true` but the lightweight GUIDE WebUI is not enforcing authentication yet.

## Runtime Validation

- `python3 -m py_compile scripts/guide-webui.py`: passed.
- Inline browser script syntax check with `node --check`: passed.
- `GET /api/status`: returned `required_by_policy=true`, `enforced_by_webui=false`, and an explicit trusted-LAN warning.
- `GET /api/library-index`: returned `status=complete`, `collection_count=213850`, and no live collection error.
- `POST /api/ask-library`: returned HTTP 200 with an answer, 3 citations, 2 risk notes, and `index_status.status=complete`.

## Warning

T011 remains open. The UI now clearly warns when auth is required by policy but not enforced by this lightweight WebUI. Until T011 is complete, run the WebUI only on localhost or a trusted LAN.

## Next Task

T021 is next on the critical path: add deeper RAG operations checks for source/index freshness and supportability.
