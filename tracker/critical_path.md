# GUIDE Critical Path

Updated: 2026-08-12

This file tracks the current critical path for the packaged GUIDE USB repository. The repo has been pruned so it tracks the current GUIDE USB state.

| Order | Task | Status | Evidence |
|---:|---|---|---|
| 1 | Maintain current model inventory | Complete | `config/models.json` |
| 2 | Document current packaged USB launch behavior | Complete | `README.md`, `config/services.json` |
| 3 | Provide tester launch and use instructions | Complete | `GUIDE_README.html` |
| 4 | Provide full beta test plan | Complete | `BETA_TEST_PLAN.md` |
| 5 | Package Mac Review Picture fix | Complete | `updates/guide-mac-vision-fix-1.3.1/` |
| 6 | Upload current GUIDE configuration to GitHub | Complete | Commit `73b2008` |
| 7 | Update tracker files for completed GUIDE work | Complete | Commit `41711d6` |
| 8 | Remove stale repository files not matching current GUIDE USB | Complete | Current cleanup commit |

## Current Gates

| Gate | Requirement | Status |
|---|---|---|
| Launch Gate | Windows, macOS, and Linux launch paths documented from the mounted USB | Complete |
| Model Gate | Current model list and roles recorded | Complete |
| Vision Gate | Mac launcher patch ensures USB Ollama exposes vision models | Complete |
| Tester Gate | README and beta test plan available at repo root and in update package | Complete |
| Repository Hygiene Gate | Old installer/runtime scaffold removed | Complete |

## Next Candidates

- Add a release manifest with file list, version, zip name, and checksums.
- Add small automated checks for zip structure and required tester documents.
- Add a concise changelog for each tester update package.
