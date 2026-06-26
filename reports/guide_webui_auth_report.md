# GUIDE WebUI Authentication Report

Generated: 2026-06-26

## Summary

T011 is complete with warnings. The lightweight GUIDE WebUI now enforces HTTP Basic authentication when `ENABLE_AUTH=true`.

## Implemented Behavior

- `ENABLE_AUTH=true` requires authentication for static WebUI pages, library browsing, and API endpoints.
- Default username: `guide`.
- Password sources, in priority order:
  - `GUIDE_WEBUI_PASSWORD`
  - `GUIDE_WEBUI_PASSWORD_FILE`
  - generated first-run file at `config/guide-webui.password`
- Generated password files are ignored by git.
- `/api/status` reports whether auth is required and enforced.
- Linux and macOS healthchecks detect whether a running lightweight WebUI rejects unauthenticated `/api/status` requests.

## Validation

- `python3 -m py_compile scripts/guide-webui.py scripts/check-rag-ops.py`: passed.
- `bash -n scripts/healthcheck-linux.sh scripts/healthcheck-mac.sh`: passed.
- Inline WebUI JavaScript syntax check with `node --check`: passed.
- Temporary WebUI with `ENABLE_AUTH=true`, `GUIDE_WEBUI_PASSWORD=test-password`, and `GUIDE_WEBUI_PORT=8090`:
  - Unauthenticated `GET /api/status`: HTTP 401.
  - Authenticated `GET /api/status`: HTTP 200.
  - `/api/status` reported `required_by_policy=true` and `enforced_by_webui=true`.
- Temporary WebUI with `GUIDE_WEBUI_PASSWORD_FILE` pointing at a new temp path:
  - Password file was generated.
  - Unauthenticated `GET /api/status`: HTTP 401.
  - Authenticated `GET /api/status`: HTTP 200.
- Linux healthcheck with the authenticated test WebUI running:
  - `GUIDE WebUI auth`: PASS.
  - Overall: 37 pass, 2 warn, 0 fail.

## Warnings

HTTP Basic auth protects against casual unauthenticated LAN access, but it is not encrypted without TLS. Keep GUIDE WebUI on localhost or a trusted LAN unless a separate TLS reverse proxy is provided.

AnythingLLM and Open WebUI still rely on their own first-run/user-account auth flows. This task secures the lightweight GUIDE WebUI and documents the compensating control for other GUIs.
