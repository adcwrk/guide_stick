# GUIDE USB Configuration

This repository tracks the current GUIDE USB configuration, tester documentation, update packages, and project tracker files.

GUIDE stands for Generative Unified Intelligence for Disaster and Emergency Management. It is an offline-first emergency preparedness and field-support system intended to launch from a USB drive on Windows, macOS, or Linux.

The current shipped USB is a packaged desktop app layout. Files from earlier setup approaches have been removed from this repository so the repo reflects the current GUIDE USB state.

## Current USB Launchers

On the mounted GUIDE USB, testers launch GUIDE with:

| OS | Launcher |
|---|---|
| Windows | `Guide (Windows).lnk` or `Guide (Windows).bat` |
| macOS | `Guide (Mac).app` |
| Linux | `Guide (Linux).sh` |

The packaged app and runtime files live under `.internal/` on the USB:

```text
Guide/
├── Guide (Windows).lnk
├── Guide (Windows).bat
├── Guide (Mac).app
├── Guide (Linux).sh
├── GUIDE_README.html
├── BETA_TEST_PLAN.md
├── updates/
└── .internal/
    ├── apps/
    ├── ollama/
    ├── models/
    ├── library/
    ├── maps/
    ├── guides/
    ├── whisper/
    └── diag/
```

## Runtime Behavior

GUIDE uses the bundled USB Ollama runtime and the USB model directory when possible.

Current packaged runtime paths:

| Runtime | USB Path |
|---|---|
| Windows app | `.internal/apps/windows/Guide.exe` |
| macOS app | `.internal/apps/Guide.app` |
| Linux app | `.internal/apps/linux/guide` |
| Windows Ollama | `.internal/ollama/win/ollama.exe` |
| macOS Ollama | `.internal/ollama/mac/ollama` |
| Linux Ollama | `.internal/ollama/linux/bin/ollama` |
| Models | `.internal/models` |

The macOS launcher is especially important for Review Picture. It starts the USB-bundled Ollama runtime before opening GUIDE and avoids using a separately installed host Ollama app that may not have vision models.

## Current Models

The current model inventory is tracked in `config/models.json`.

Active models include:

| Model | Role |
|---|---|
| `qwen2.5:0.5b` | Fastest basic assistant |
| `llama3.2:1b` | Lightweight general assistant |
| `qwen2.5:3b` | Balanced daily preparedness assistant |
| `llama3.1:8b` | Stronger general planning and communication |
| `qwen2.5:14b` | Larger detailed planning model |
| `deepseek-r1:7b` | Reasoning and triage logic |
| `deepseek-r1:14b` | Larger reasoning model |
| `qwen2.5-coder:7b` | Coding and technical troubleshooting |
| `fluffy/l3-8b-stheno-v3.2:q4_K_M` | Creative drills and roleplay |
| `AliBilge/Huihui-GLM-4.6V-Flash-abliterated:q4_K_M` | General open-ended assistant |
| `AliBilge/Huihui-GLM-4.6V-Flash-abliterated:q5_k_m` | Higher-quality GLM assistant |
| `moondream:latest` | Fast picture review |
| `huihui_ai/qwen2.5-vl-abliterated:7b-instruct` | Detailed picture review |
| `nomic-embed-text:latest` | Retrieval embeddings |

`nomic-embed-text:latest` supports retrieval and should not be presented as a normal chat model.

## Tester Files

Current tester-facing files:

- `GUIDE_README.html`
- `BETA_TEST_PLAN.md`
- `updates/guide-mac-vision-fix-1.3.1/guide-mac-vision-fix-1.3.1.zip`
- `updates/guide-mac-vision-fix-1.3.1/source/README.txt`
- `updates/guide-mac-vision-fix-1.3.1/source/apply-mac-vision-fix.command`

## Mac Vision Fix

The current Mac Review Picture patch is stored in:

```text
updates/guide-mac-vision-fix-1.3.1/
```

Send this zip to Mac testers:

```text
updates/guide-mac-vision-fix-1.3.1/guide-mac-vision-fix-1.3.1.zip
```

It fixes this error:

```text
No vision model available (e.g. moondream, qwen2.5-vl).
```

The patch updates the Mac launcher so GUIDE starts the bundled USB Ollama runtime and uses `.internal/models` before opening the app.

## Tracker

Tracker files live in `tracker/`:

- `tracker/backlog.md`
- `tracker/critical_path.md`
- `tracker/phase_tracker.md`
- `tracker/roadmap.md`
- `tracker/task_tracker.csv`
- `tracker/tracker_agent.md`

These files record the current completed work and remaining candidates.

## Safety

GUIDE is an offline support tool. It is not a replacement for emergency services, professional medical care, legal advice, or official disaster instructions. Emergency guidance should remain cautious and should direct users to call emergency services for urgent or life-threatening situations.
