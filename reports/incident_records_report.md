# Incident Records Schema Report

Generated: 2026-06-26

## Summary

T025 is complete with warnings. GUIDE now has a USB-local incident record schema, example template, authenticated API endpoints, WebUI JSON editor, and operational timeline summary.

## Artifacts

- Schema: `data/guide/incidents/incidents.schema.json`
- Example template: `data/guide/incidents/incidents.example.json`
- Local incident data path: `data/guide/incidents/incidents.json`
- WebUI API:
  - `GET /api/incidents`
  - `POST /api/incidents`
- WebUI editor and timeline summary: `data/guide_webui/index.html`

## Schema Coverage

Incident records support:

- Incident type, status, severity, start/end time, location, and summary
- Operational objectives
- Assigned or tracked resources
- Timeline events for observations, decisions, actions, communications, resource updates, status changes, and notes
- Document references
- Recommendations with citation references and disposition status
- Free-form notes

## Runtime Behavior

- Incident reads and writes are authenticated by the lightweight GUIDE WebUI auth layer.
- If no saved incidents file exists, `GET /api/incidents` returns the example template.
- `POST /api/incidents` validates required structure before writing.
- Saves update `updated_at` and write atomically to the USB-local data path.
- The local incidents JSON file is ignored by git.
- Backups already include `data/guide`.
- Healthchecks now verify `data/guide/incidents` and the incidents schema file.

## Validation

- JSON schema parsed successfully.
- Example incident template parsed successfully.
- Temporary authenticated WebUI:
  - Unauthenticated `GET /api/incidents`: HTTP 401.
  - Authenticated `GET /api/incidents`: HTTP 200.
  - Authenticated `POST /api/incidents`: HTTP 200.
  - Summary response included incident counts, severity counts, and latest timeline events.
- Python compile passed.
- Shell syntax checks passed.
- Inline WebUI JavaScript syntax check passed.

## Warning

The first UI pass is a JSON editor plus timeline summary. A richer incident dashboard with guided forms, filters, and operational views can build on the same schema and API later.
