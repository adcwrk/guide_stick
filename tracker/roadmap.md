# GUIDE Roadmap

Updated: 2026-08-12

This roadmap reflects the current packaged GUIDE USB distribution.

## Phase 1: Current USB Baseline

Status: Complete

- Review mounted GUIDE USB structure.
- Identify current launchers for Windows, macOS, and Linux.
- Confirm packaged app/runtime paths under `.internal/`.

## Phase 2: Model and Runtime Configuration

Status: Complete

- Maintain current model inventory in `config/models.json`.
- Record current packaged service/runtime map in `config/services.json`.
- Document model roles for tester use.

## Phase 3: Tester Documentation

Status: Complete

- Provide `GUIDE_README.html`.
- Provide `BETA_TEST_PLAN.md`.
- Include Review Picture, Journal, button testing, model testing, and README review.
- Include emergency test prompts such as shock treatment and CPR.

## Phase 4: Mac Review Picture Fix

Status: Complete

- Package Mac launcher fix under `updates/guide-mac-vision-fix-1.3.1/`.
- Include tester-facing `README.txt`.
- Include `apply-mac-vision-fix.command`.
- Include hidden `.patch-files` payload in the zip.

## Phase 5: Repository Cleanup

Status: Complete

- Remove older installer scripts, backup snapshots, historical reports, and script-first runtime files that do not match the current packaged GUIDE USB.
- Promote current tester docs to the repo root.
- Update README and service map to match the current USB layout.

## Future Work

- Release manifest and checksums.
- Automated package validation.
- Tester changelog.
- Platform-specific launch screenshots or short videos.
- Smaller region-specific offline map packages if needed.
