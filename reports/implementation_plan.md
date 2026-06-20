# Implementation Plan

## Goal

Extend and rename the deployment to GUIDE for the GUIDE USB and Apple Silicon M4 Max systems without replacing the upstream Portable-AI-USB architecture.

## Preserved Workflows

- Windows setup remains `install.bat` -> `install-core.ps1`.
- Windows startup remains `start-windows.bat`.
- Linux setup remains `linux/install.sh` -> `linux/preflight-check.sh` -> `linux/install-core.sh`.
- Linux startup remains `linux/start-linux.sh`.
- Existing GGUF model download and Ollama import workflow is unchanged.
- Existing AnythingLLM Desktop workflow is unchanged.
- Existing USB-relative path resolution is preserved.

## Added Capabilities

1. Apple Silicon model metadata in `config/models.json`.
2. macOS setup automation in `setup-mac.sh`.
3. Logged macOS startup improvements in `start-mac.command`.
4. USB-local health checks in `scripts/healthcheck-mac.sh`.
5. Non-destructive document staging in `scripts/ingest-documents.sh`.
6. USB-local backup archive creation in `scripts/backup-portable.sh`.
7. Reports and logs stored on the USB.

## Apple Silicon Defaults

- Default chat model: `qwen2.5:7b`
- Fallback chat model: `llama3.2:3b`
- Embeddings model: `nomic-embed-text`

Optional M4 Max models:

- `qwen2.5:14b`
- `llama3.1:8b`
- `deepseek-r1:14b`

## USB Layout

```text
GUIDE/
+-- config/
+-- documents/
+-- logs/
+-- reports/
+-- backups/
+-- scripts/
+-- models/
+-- ollama/
+-- ollama_mac/
+-- anythingllm/
+-- anythingllm_mac/
+-- anythingllm_data/
+-- installer_data/
```

## Validation Strategy

1. Validate GUIDE mount identity and writability before changes.
2. Validate Bash syntax for added scripts.
3. Validate JSON syntax for model metadata.
4. Run health check against the current USB state.
5. Run backup automation and verify archive creation.
6. Measure USB I/O and record platform limitations.

## Known Limits During This Build

The current implementation environment is Linux, not macOS on Apple Silicon. macOS-specific runtime behavior must be verified on the target MacBook Pro M4 Max after the USB is moved to that host.
