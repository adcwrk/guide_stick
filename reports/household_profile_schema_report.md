# Household Preparedness Profile Schema Report

Generated: 2026-06-26

## Summary

T023 is complete with warnings. GUIDE now has a USB-local household preparedness profile schema, example template, authenticated API endpoints, and WebUI editing path.

## Artifacts

- Schema: `data/guide/profile/household_profile.schema.json`
- Example template: `data/guide/profile/household_profile.example.json`
- Local profile data path: `data/guide/profile/household_profile.json`
- WebUI API:
  - `GET /api/profile`
  - `POST /api/profile`
- WebUI editor: `data/guide_webui/index.html`

## Schema Coverage

The schema captures:

- Household or organization metadata
- Household members and age groups
- Pets
- Medical conditions
- Medications
- Medical equipment
- Power dependencies
- Backup power sources
- Critical electrical loads
- Mobility limitations
- Assistive devices
- Emergency contacts
- Communications devices
- Rally points
- Preparedness goals

## Runtime Behavior

- Profile reads and writes are authenticated by the lightweight GUIDE WebUI auth layer from T011.
- If no saved profile exists, `GET /api/profile` returns the example template.
- `POST /api/profile` validates required top-level structure before writing.
- Saves update `updated_at` and write atomically to the USB-local data path.
- The local household profile JSON file is ignored by git.
- Backups now include `data/guide`.
- Healthchecks now verify `data/guide/profile` and the profile schema file.

## Validation

- JSON schema parsed successfully.
- Example profile parsed successfully.
- Example profile passed the built-in profile validator.
- Temporary authenticated WebUI:
  - Unauthenticated `GET /api/profile`: HTTP 401.
  - Authenticated `GET /api/profile`: HTTP 200.
  - Authenticated `POST /api/profile`: HTTP 200.
- Python compile passed.
- Shell syntax checks passed.
- Inline WebUI JavaScript syntax check passed.

## Warning

The WebUI editor is a JSON editor for the first schema pass. A richer form-based intake flow can build on the same schema and API later.
