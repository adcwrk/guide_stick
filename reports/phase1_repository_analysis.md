# Phase 1 Repository Analysis

Repository: `https://github.com/techjarves/Portable-AI-USB`

Branch analyzed: `portable-ai-usb-thkailar-m4`

USB target used for analysis:

- Device: `/dev/sdb1`
- Label: `THKAILAR`
- UUID: `6676-08D4`
- Filesystem: `exfat`
- Mountpoint: `/mnt/usb`

## Executive Summary

Portable-AI-USB is a script-first portable deployment for Ollama plus AnythingLLM. The project intentionally avoids a compiled application or framework layer. The USB drive is the unit of deployment, and platform-specific launchers resolve paths relative to the script location.

The current repository is small and operationally direct:

- Windows has the most complete setup path through `install.bat` and `install-core.ps1`.
- Linux has a strong preflight and installer path under `linux/`.
- macOS currently has a launcher, `start-mac.command`, that downloads Ollama and AnythingLLM on first launch but does not have a dedicated setup script, health check, backup workflow, model verification, or Apple Silicon performance tuning.

The correct extension strategy is to preserve the existing scripts and folder conventions while adding guarded macOS automation, reports, logging, backups, and model metadata.

## Project Architecture

```text
USB Drive
|
+-- Platform launchers
|   +-- start-windows.bat
|   +-- start-mac.command
|   +-- linux/start-linux.sh
|
+-- Platform setup
|   +-- install.bat
|   +-- install-core.ps1
|   +-- linux/install.sh
|   +-- linux/install-core.sh
|   +-- linux/preflight-check.sh
|
+-- Runtime assets created during setup
|   +-- ollama/
|   +-- ollama_mac/
|   +-- models/
|   +-- anythingllm/
|   +-- anythingllm_mac/
|   +-- anythingllm_data/
|   +-- installer_data/
|
+-- Proposed extension points
    +-- config/
    +-- scripts/
    +-- logs/
    +-- backups/
    +-- documents/
    +-- reports/
```

The design is a portable script orchestration layer. It uses Ollama as the model runtime and AnythingLLM Desktop as the user interface and knowledge workspace. Scripts set environment variables so model data and AnythingLLM data live on the USB.

## Folder Structure

Current tracked files:

```text
.
+-- README.md
+-- LICENSE
+-- install.bat
+-- install-core.ps1
+-- optimiced.bat
+-- start-mac.command
+-- start-windows.bat
+-- linux/
    +-- install.sh
    +-- install-core.sh
    +-- preflight-check.sh
    +-- start-linux.sh
```

Runtime folders documented or created by scripts:

```text
models/                 GGUF files, Modelfiles, installed-models.txt
ollama/                 Windows/Linux Ollama binary and OLLAMA_MODELS data
ollama_mac/             macOS Ollama app or binary
anythingllm/            Windows/Linux AnythingLLM app
anythingllm_mac/        macOS AnythingLLM.app
anythingllm_data/       AnythingLLM profile, storage, chats, vector DB
installer_data/         Temporary downloaded installers
```

## Startup Flow

### Windows

```text
User double-clicks start-windows.bat
  -> Resolve USB root from %~dp0
  -> Set OLLAMA_MODELS to USB ollama\data
  -> Set STORAGE_DIR and Electron profile vars to USB
  -> Create anythingllm_data folders
  -> Ensure AnythingLLM .env uses external Ollama
  -> Print installed models
  -> Start ollama.exe serve
  -> Wait 3 seconds
  -> Delete Electron cache folders
  -> Start AnythingLLM.exe with --user-data-dir on USB
  -> Wait for user keypress
  -> taskkill Ollama and AnythingLLM
```

### macOS

```text
User double-clicks start-mac.command
  -> cd to script directory
  -> Resolve USB root from pwd
  -> Download Ollama Darwin zip if missing
  -> Download AnythingLLM Apple Silicon DMG if missing
  -> Extract AnythingLLM.app to USB and clear quarantine
  -> Set OLLAMA_MODELS to USB ollama/data
  -> Set STORAGE_DIR to USB anythingllm_data
  -> Ensure AnythingLLM .env uses external Ollama
  -> Print installed models
  -> Start Ollama serve in background
  -> Wait 3 seconds
  -> Delete Electron cache folders
  -> open AnythingLLM.app with --user-data-dir on USB
  -> Wait for ENTER
  -> kill Ollama PID and killall AnythingLLM
```

### Linux

```text
User runs linux/start-linux.sh
  -> Resolve USB root from script directory
  -> Set OLLAMA_MODELS to USB ollama/data
  -> Set STORAGE_DIR and XDG paths to USB
  -> Create storage folders
  -> Ensure AnythingLLM .env uses external Ollama
  -> Print installed models
  -> Validate Ollama binary and AnythingLLM AppImage
  -> Delete Electron cache folders
  -> Start Ollama serve
  -> Start AnythingLLM AppImage with --user-data-dir on USB
  -> Wait for ENTER
  -> kill launched processes and matching background processes
```

## Setup Flow

### Windows

`install.bat` is a wrapper around `install-core.ps1`. The PowerShell script:

1. Defines a curated GGUF model catalog.
2. Prompts for one or more models or a custom HuggingFace GGUF URL.
3. Creates runtime folders on the USB.
4. Downloads selected GGUF files into `models/`.
5. Creates Ollama Modelfiles and `models/installed-models.txt`.
6. Downloads Ollama Windows zip into `ollama/`.
7. Downloads the AnythingLLM Windows installer and asks the user to install it to the USB `anythingllm/` folder.
8. Starts Ollama temporarily.
9. Imports models into Ollama through `ollama create`.
10. Writes AnythingLLM `.env` for external Ollama.

### Linux

`linux/install.sh` runs `linux/preflight-check.sh`. The preflight script detects a USB target, validates required tools, checks filesystem and capacity, benchmarks read/write speed, then launches `install-core.sh`.

`linux/install-core.sh` follows the Windows setup flow with Linux-specific binaries:

- Ollama Linux tarball.
- AnythingLLM AppImage.
- Temporary Ollama server for model import.

### macOS

There is no dedicated `setup-mac.sh`. The macOS launcher performs first-run downloads and runtime setup:

- Downloads Ollama Darwin zip into `ollama_mac/`.
- Downloads AnythingLLM Apple Silicon DMG into `anythingllm_mac/`, mounts it, copies `AnythingLLM.app`, and removes quarantine metadata.
- Creates the AnythingLLM storage `.env`.

The macOS path does not currently pull Ollama registry models, import GGUF models, check Homebrew, validate Apple Silicon, or generate setup logs.

## Ollama Integration

Ollama is treated as a portable engine whose model store is forced onto the USB:

- Windows: `OLLAMA_MODELS=%~dp0ollama\data`
- macOS: `OLLAMA_MODELS="$USB_DIR/ollama/data"`
- Linux: `OLLAMA_MODELS="$USB_DIR/ollama/data"`

Windows and Linux import local GGUF files through generated Modelfiles:

```text
FROM ./model-file.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM ...
```

The macOS launcher starts Ollama but does not import models or validate that configured models exist.

## AnythingLLM Integration

AnythingLLM is configured to use external Ollama:

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_PATH=http://127.0.0.1:11434
OLLAMA_MODEL_PREF=<first installed model>
OLLAMA_MODEL_TOKEN_LIMIT=4096
EMBEDDING_ENGINE=native
VECTOR_DB=lancedb
```

The storage file is written to:

```text
anythingllm_data/storage/.env
```

The launchers pass a USB-local Electron profile using `--user-data-dir`.

## Model Management Workflow

The original model workflow is GGUF-centric:

1. User selects preset or custom GGUF.
2. Installer downloads model into `models/`.
3. Installer writes model-specific Modelfile.
4. Installer starts Ollama.
5. Installer runs `ollama create <local-name> -f Modelfile-<local-name>`.
6. Installed display data is written to `models/installed-models.txt`.
7. Launchers read the first line from `installed-models.txt` to choose the default model.

Current preset model local names:

- `nemomix-local`
- `dolphin-local`
- `mistral-local`
- `qwen-local`
- `llama3-local`
- `phi3-local`

## Document Ingestion Workflow

The repository does not include a script-level document ingestion workflow. AnythingLLM handles document upload, workspace assignment, embedding, and vector storage inside its desktop application.

Expected storage is under `anythingllm_data/`, but the exact document and vector DB layout is managed by AnythingLLM itself.

## Knowledge Storage Workflow

Knowledge storage is delegated to AnythingLLM. The scripts set:

```text
STORAGE_DIR=<USB>/anythingllm_data
VECTOR_DB=lancedb
```

This implies workspace data, chats, settings, and LanceDB vector data should be USB-local when AnythingLLM honors `STORAGE_DIR` and `--user-data-dir`.

## Logging Workflow

The original repository has no durable logging framework.

Current logging behavior:

- Scripts print progress to terminal.
- Ollama is often redirected to `/dev/null` or backgrounded silently.
- Setup errors are printed but not persisted.
- No rotating logs or structured logs exist.

## Backup Workflow

The original repository has no backup script. There is no automated backup before config changes, document ingestion changes, or cache cleanup.

Cache deletion exists for Electron path portability:

- `config.json`
- `Cache`
- `Code Cache`
- `GPUCache`

These are runtime cache folders, not user document backups.

## Portability Mechanisms

Primary mechanisms:

- Resolve USB root from script location.
- Set model and storage environment variables to paths below the USB.
- Use portable binaries where practical.
- Delete Electron path caches when moving between machines.
- Use AnythingLLM `--user-data-dir` to keep profile data on USB.
- Avoid registry or host application profile reliance where possible.

The Windows setup still requires a manual AnythingLLM installer location selection.

## Environment Variable Usage

| Variable | Platform | Purpose |
|---|---|---|
| `OLLAMA_MODELS` | Windows, macOS, Linux | Force Ollama model store to USB |
| `STORAGE_DIR` | Windows, macOS, Linux | Force AnythingLLM storage to USB |
| `ANYTHINGLLM_PROFILE` | Windows | USB-local Electron profile hint |
| `APPDATA` | Windows | Electron safety net |
| `LOCALAPPDATA` | Windows | Electron safety net |
| `XDG_CONFIG_HOME` | Linux | USB-local config |
| `XDG_DATA_HOME` | Linux | USB-local app data |
| `XDG_CACHE_HOME` | Linux | USB-local cache |
| `OLLAMA_HOST` | Linux | Bind Ollama to localhost |

## macOS Support

Current support:

- Has `start-mac.command`.
- Downloads Apple Silicon AnythingLLM DMG.
- Downloads Ollama Darwin zip.
- Extracts both to USB.
- Removes quarantine from AnythingLLM app.
- Starts Ollama and AnythingLLM with USB-local paths.

Gaps:

- No `setup-mac.sh`.
- No Apple Silicon detection.
- No Homebrew detection.
- No model pull/import automation for recommended macOS models.
- No health checks.
- No persistent logs.
- No backup workflow.
- No robust Ollama API readiness loop.
- No explicit Metal acceleration check.
- No validation of THKAILAR USB identity.

## Windows Support

Windows support is the most established user path:

- Interactive installer.
- Curated GGUF catalog.
- Custom GGUF support.
- Ollama import.
- AnythingLLM manual install guidance.
- Portable launcher with Electron cache cleanup.

Compatibility concerns:

- PowerShell downloads directly to final destination instead of `.part` temporary files.
- AnythingLLM install is manual and can accidentally be installed to the host.
- `optimiced.bat` is aggressive and may terminate unrelated Ollama or AnythingLLM processes.
- Some path cache cleanup is destructive to cache folders, although not to user documents.

## Linux Support

Linux support includes:

- USB detection and selection.
- Dependency checks.
- Filesystem checks.
- Capacity checks.
- Read/write benchmarking.
- Installer workflow similar to Windows.
- AppImage launch fallback using `APPIMAGE_EXTRACT_AND_RUN`.

Compatibility concerns:

- AppImage support depends on FUSE or extract-and-run compatibility.
- Ollama tarball URL targets amd64, not ARM Linux.
- Preflight uses Linux-specific commands and Unicode terminal output.

## USB Path Detection Logic

| Platform | Detection mechanism |
|---|---|
| Windows | `%~dp0`, the folder containing the batch file |
| macOS | `cd "$(dirname "$0")"` then `pwd` |
| Linux launcher | `dirname "${BASH_SOURCE[0]}"` |
| Linux preflight | Enumerates mounted removable devices with `findmnt`, `lsblk`, `/sys`, and optional `udevadm` |

There is no current cross-platform validation for a specific label, UUID, or filesystem outside the Linux preflight.

## Browser Launch Workflow

The project launches AnythingLLM Desktop, not a browser-based web UI.

- Windows starts `AnythingLLM.exe`.
- macOS uses `open -a AnythingLLM.app`.
- Linux starts `AnythingLLM.AppImage`.

No script currently opens `http://127.0.0.1:<port>` in a browser. The requested Apple Silicon extension should preserve the desktop workflow and may optionally open the local web interface when reachable.

## Dependency Installation Workflow

The project generally downloads portable binaries instead of installing host dependencies.

Windows:

- Requires PowerShell and `curl.exe`.
- Downloads Ollama zip.
- Downloads AnythingLLM installer.

macOS:

- Requires `curl`, `unzip`, `hdiutil`, `xattr`, and `open`.
- Downloads Ollama and AnythingLLM directly to USB.

Linux:

- Requires `curl`, `tar`, `zstd`, `dd`, `df`, `lsblk`, `awk`, and `findmnt`.
- Does not install dependencies automatically.

## Original Author Assumptions

- The USB root is the directory containing the launcher or installer.
- exFAT is the preferred cross-platform filesystem.
- The default user experience should be double-clickable and terminal-guided.
- GGUF local model import is the primary setup model on Windows and Linux.
- AnythingLLM Desktop is the primary UI.
- External Ollama should be used instead of AnythingLLM's bundled Ollama.
- Moving between hosts requires Electron path cache cleanup.
- After setup, the system should work offline.
- A user can safely keep all chat and settings data on the USB if the launchers set the expected environment variables.

## Data Flow Diagram

```text
User
 |
 | starts launcher
 v
Platform script
 |
 | sets OLLAMA_MODELS and STORAGE_DIR to USB paths
 v
Ollama serve  <-------------------------------+
 |                                             |
 | localhost API http://127.0.0.1:11434       |
 v                                             |
AnythingLLM Desktop --------------------------+
 |
 | stores chats, settings, workspace data, vector DB
 v
USB anythingllm_data/
```

## Setup Data Flow

```text
Installer
 |
 +--> model catalog prompt
 |
 +--> models/*.gguf
 |
 +--> models/Modelfile-*
 |
 +--> ollama binary
 |
 +--> temporary Ollama server
 |       |
 |       +--> ollama create local model
 |
 +--> AnythingLLM app
 |
 +--> anythingllm_data/storage/.env
```

## Startup Sequence

```text
1. Resolve USB root from launcher location.
2. Create required USB data folders.
3. Set environment variables for USB-local model and app data.
4. Repair or create AnythingLLM `.env`.
5. Display installed models.
6. Start Ollama.
7. Start AnythingLLM Desktop.
8. Keep terminal open.
9. On user input, stop processes.
```

## Component Inventory

| Component | Current location | Role |
|---|---|---|
| README | `README.md` | User documentation |
| Windows installer wrapper | `install.bat` | Calls PowerShell setup |
| Windows core installer | `install-core.ps1` | Model download, Ollama/AnythingLLM setup |
| Windows launcher | `start-windows.bat` | Starts portable runtime |
| Alternate Windows launcher | `optimiced.bat` | Aggressive Spanish optimized launcher |
| macOS launcher | `start-mac.command` | First-run downloads and runtime startup |
| Linux installer wrapper | `linux/install.sh` | Runs preflight and installer |
| Linux installer core | `linux/install-core.sh` | Model download, Ollama/AnythingLLM setup |
| Linux preflight | `linux/preflight-check.sh` | USB validation and speed benchmark |
| Linux launcher | `linux/start-linux.sh` | Starts portable runtime |

## Improvement Opportunities

1. Add guarded `setup-mac.sh` for Apple Silicon setup.
2. Add `config/models.json` for model recommendations and metadata.
3. Add macOS health checks with report output.
4. Add durable logs under `logs/`.
5. Add non-destructive backups under `backups/`.
6. Add document ingestion helper that preserves originals.
7. Add THKAILAR USB identity validation.
8. Add robust Ollama API readiness loops.
9. Add model availability checks before launching AnythingLLM.
10. Preserve desktop app workflow while optionally opening reachable local UI.
11. Avoid hard-coded `/mnt/usb` in runtime scripts by resolving script paths dynamically.
12. Improve macOS failure reporting and setup verification.

## Risks

- exFAT does not preserve Unix executable mode bits reliably across systems. Users may need `chmod +x` after copying or remounting on Unix-like hosts.
- Running from USB can be much slower than internal storage, especially for large models and vector DB writes.
- AnythingLLM's internal data layout may change between versions.
- Ollama model registry names and download packaging may change.
- Desktop apps can write host-specific OS metadata despite redirected profiles.
- macOS Gatekeeper/quarantine behavior may vary by version.
- Killing processes by name can stop unrelated host Ollama or AnythingLLM sessions.
- GGUF import models and registry-pulled Ollama models are different model management paths and should not be conflated without clear metadata.

## Compatibility Concerns

### Apple Silicon M4 Max

The current macOS path downloads Apple Silicon AnythingLLM and Darwin Ollama but does not explicitly validate architecture, Metal acceleration, installed model suitability, or memory headroom. Recommended additions should prefer Ollama registry models that use native Apple Silicon acceleration when available.

### exFAT

exFAT is the right cross-platform filesystem for large model files but has weaker Unix permission semantics. Scripts should be callable with `bash script.sh` even if executable bits are absent.

### Offline Operation

The system can operate offline only after all required app binaries, models, embeddings, and AnythingLLM configuration are already present on the USB. First-run macOS startup currently requires internet if apps are missing.

### Host Persistence

The launchers redirect the major model and app data locations to USB. Host persistence can still happen through OS-level app metadata, crash reports, security prompts, DNS cache, or desktop app framework behavior outside the scripts' direct control.

## Phase 1 Conclusion

The repository should be extended rather than replaced. The strongest path is to add an Apple Silicon support layer that:

- Keeps existing launchers and install flows recognizable.
- Adds macOS setup and validation scripts.
- Uses USB-local logs, reports, documents, backups, config, and runtime data.
- Adds recommended Ollama registry model metadata for M4 Max.
- Preserves the existing GGUF workflow and AnythingLLM integration.
