# GUIDE Tracker Agent Notes

Updated: 2026-08-12

Use this tracker for the current packaged GUIDE USB repository.

## Source of Truth

- Current model inventory: `config/models.json`
- Current packaged service map: `config/services.json`
- Tester instructions: `GUIDE_README.html`
- Beta test: `BETA_TEST_PLAN.md`
- Mac update package: `updates/guide-mac-vision-fix-1.3.1/`
- Current repo summary: `README.md`

## Rules

1. Keep tracker references limited to files that exist in the current repository.
2. Treat the packaged USB layout as current: visible launchers plus `.internal/`.
3. Do not reintroduce the older installer/runtime scaffold unless a future task explicitly restores it.
4. Keep model names synchronized with `config/models.json`.
5. Keep tester instructions synchronized with `GUIDE_README.html` and `BETA_TEST_PLAN.md`.
6. Treat Mac Review Picture support as dependent on the patched launcher using USB Ollama and `.internal/models`.

## Current Recommendation

No current critical-path task remains incomplete.

Recommended next work:

- Add release manifest and checksums.
- Add package validation checks.
- Add a short tester changelog.
