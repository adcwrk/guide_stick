# Preparedness Inventory Schema Report

Generated: 2026-06-26

## Summary

T024 is complete with warnings. GUIDE now has a USB-local preparedness inventory schema, example template, authenticated API endpoints, deterministic duration and shortfall calculations, and WebUI gap display.

## Artifacts

- Schema: `data/guide/inventory/inventory.schema.json`
- Example template: `data/guide/inventory/inventory.example.json`
- Local inventory data path: `data/guide/inventory/inventory.json`
- WebUI API:
  - `GET /api/inventory`
  - `POST /api/inventory`
- WebUI editor and gap summary: `data/guide_webui/index.html`

## Schema Coverage

Inventory items support:

- Water
- Food
- Medical supplies
- Medications
- Fuel
- Power systems
- Communications equipment
- Shelter supplies
- Sanitation
- Tools
- Other supplies

Items can record quantity, unit, storage location, priority, expiration, calories per unit, gallons per unit, watt-hours per unit, medication days on hand, person linkage, fuel type, and notes.

## Calculations

The inventory API calculates:

- Household planning context from `data/guide/profile`
- Water target: 1 gallon per person per day plus 0.25 gallon per pet per day
- Food target: 2,000 calories per person per day
- Medication shortfalls against the profile planning horizon
- Critical power requirement from household critical loads
- Duration estimates for water, food, and power
- Sorted gap list with severity, required amount, available amount, and shortfall

## Runtime Behavior

- Inventory reads and writes are authenticated by the lightweight GUIDE WebUI auth layer.
- If no saved inventory exists, `GET /api/inventory` returns the example template.
- `POST /api/inventory` validates required structure before writing.
- Saves update `updated_at` and write atomically to the USB-local data path.
- The local inventory JSON file is ignored by git.
- Backups already include `data/guide`.
- Healthchecks now verify `data/guide/inventory` and the inventory schema file.

## Validation

- JSON schema parsed successfully.
- Example inventory parsed successfully.
- Temporary authenticated WebUI:
  - Unauthenticated `GET /api/inventory`: HTTP 401.
  - Authenticated `GET /api/inventory`: HTTP 200.
  - Authenticated `POST /api/inventory`: HTTP 200.
  - Calculation response included water, food, medication, and power gaps for an intentionally understocked test case.
- Python compile passed.
- Shell syntax checks passed.
- Inline WebUI JavaScript syntax check passed.

## Warning

The first UI pass is a JSON editor plus gap summary. A richer inventory form and item-category widgets can build on the same schema and API later.
