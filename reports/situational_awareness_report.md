# Situational Awareness Schema Report

Generated: 2026-06-27

## Summary

T027 is complete with warnings. GUIDE now has a USB-local situational awareness schema, example template, authenticated API endpoints, WebUI JSON editor, and a map/resource context summary.

## Artifacts

- Schema: `data/guide/situational_awareness/situational_awareness.schema.json`
- Example template: `data/guide/situational_awareness/situational_awareness.example.json`
- Local situational awareness data path: `data/guide/situational_awareness/situational_awareness.json`
- Reserved large map path: `data/guide/maps`
- WebUI API:
  - `GET /api/situational-awareness`
  - `POST /api/situational-awareness`
- WebUI editor and summary: `data/guide_webui/index.html`

## Schema Coverage

Situational awareness context supports:

- Map strategy and offline map import status
- Operating areas
- Hazards such as wildfire, flood, severe weather, road closures, and outages
- Resources such as shelters, hospitals, clinics, pharmacies, water, food, fuel, charging, rally points, and supply caches
- Routes for evacuation, supply, medical, check-in, alternate, and other uses
- Communications infrastructure such as repeaters and mesh nodes

## Map Import Strategy

The immediate strategy is `geojson_table`: keep operational map context in portable JSON records that can be edited and summarized offline without requiring a large map database. Future `.mbtiles` or `.pmtiles` files should be staged under `data/guide/maps` after selecting a smaller region/export strategy. Large map files are ignored by git.

## Runtime Behavior

- Situational awareness reads and writes are authenticated by the lightweight GUIDE WebUI auth layer.
- If no saved context exists, `GET /api/situational-awareness` returns the example template.
- `POST /api/situational-awareness` validates required structure before writing.
- Saves update `updated_at` and write atomically to the USB-local data path.
- Healthchecks verify `data/guide/situational_awareness`, `data/guide/maps`, and the situational awareness schema file.

## Validation

- JSON schema parsed successfully.
- Example situational awareness template parsed successfully.
- Temporary authenticated WebUI:
  - Unauthenticated `GET /api/situational-awareness`: HTTP 401.
  - Authenticated `GET /api/situational-awareness`: HTTP 200.
  - Authenticated `POST /api/situational-awareness`: HTTP 200.
  - Summary response included areas, hazards, resources, routes, communications infrastructure, and map strategy.
- Python compile passed.
- Shell syntax checks passed.
- Inline WebUI JavaScript syntax check passed.

## Warning

This completes the data path and first UI pass, not a full visual map renderer. The large `.mbtiles` transfer remains deferred until a smaller region/export strategy is selected.
