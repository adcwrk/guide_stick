# Communications Center Schema Report

Generated: 2026-06-26

## Summary

T026 is complete with warnings. GUIDE now has a USB-local communications center schema, example template, authenticated API endpoints, WebUI JSON editor, and message/channel summary.

## Artifacts

- Schema: `data/guide/communications/communications.schema.json`
- Example template: `data/guide/communications/communications.example.json`
- Local communications data path: `data/guide/communications/communications.json`
- WebUI API:
  - `GET /api/communications`
  - `POST /api/communications`
- WebUI editor and communications summary: `data/guide_webui/index.html`

## Schema Coverage

The communications center supports:

- Contacts with roles, priority, and contact methods
- Channel plans for phone tree, SMS, email, GMRS, FRS, ham, Meshtastic, runner, in-person, and other paths
- Message templates with scenario, priority, audience, variables, and citation references
- Message log entries with direction, channel, contacts, incident linkage, delivery status, operator, and notes

## Runtime Behavior

- Communications reads and writes are authenticated by the lightweight GUIDE WebUI auth layer.
- If no saved communications file exists, `GET /api/communications` returns the example template.
- `POST /api/communications` validates required structure before writing.
- Saves update `updated_at` and write atomically to the USB-local data path.
- The local communications JSON file is ignored by git.
- Backups already include `data/guide`.
- Healthchecks now verify `data/guide/communications` and the communications schema file.

## Validation

- JSON schema parsed successfully.
- Example communications template parsed successfully.
- Temporary authenticated WebUI:
  - Unauthenticated `GET /api/communications`: HTTP 401.
  - Authenticated `GET /api/communications`: HTTP 200.
  - Authenticated `POST /api/communications`: HTTP 200.
  - Summary response included contacts, channels, templates, message log entries, and recent messages.
- Python compile passed.
- Shell syntax checks passed.
- Inline WebUI JavaScript syntax check passed.

## Warning

The first UI pass is a JSON editor plus summary. A richer communications dashboard with guided contact forms, template rendering, radio settings, and Meshtastic integration can build on the same schema and API later.
