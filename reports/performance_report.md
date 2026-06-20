# Performance Report

Generated: 2026-06-20T05:55:00Z

Target USB:

- Device: `/dev/sdb1`
- Label: `THKAILAR`
- UUID: `6676-08D4`
- Filesystem: `exfat`
- Mountpoint: `/mnt/usb`

## Validation Environment

- Host used for this validation: Linux
- Available memory observed: approximately 30 GiB total
- Target runtime A: Apple MacBook Pro M4 Max with macOS and Metal-backed Ollama
- Target runtime B: Intel NUC with Linux and USB mounted at `/mnt/usb`

The current host does not have Ollama, AnythingLLM, or Open WebUI installed, so service runtime performance is reported as blocked with clear warnings rather than guessed.

## USB Disk Utilization

- USB total capacity: approximately 938 GB
- GUIDE size after implementation and generated validation artifacts: approximately tens of MB, excluding future model downloads
- Required persistent data folders:
  - `data/chroma`
  - `data/anythingllm`
  - `data/openwebui`
  - `ollama/data`

## USB I/O

Previous validation on this mount measured:

| Metric | Result | Notes |
|---|---:|---|
| Sequential write | 25.3 MB/s | `dd` with fsync to USB |
| Sequential read | Cache-influenced | Cold read could not be reliably measured without root cache control |

Expected impact:

- Model downloads and backups are write-speed limited.
- Running large models from USB may increase initial model load time.
- ChromaDB/vector writes should be acceptable for moderate document ingestion but slower than internal SSD.

## Startup Time

Not measured end-to-end because required services are not installed on this host.

Measurement commands on NUC:

```bash
time bash start-linux.sh
```

Measurement commands on macOS:

```bash
time ./start-mac.command
```

## Model Load Time

Not measured because Ollama is not installed and models are not pulled in this validation environment.

Models to measure on target hardware:

- `qwen2.5:7b`
- `llama3.2:3b`
- `nomic-embed-text`
- Optional M4 Max: `qwen2.5:14b`, `llama3.1:8b`, `deepseek-r1:14b`

## Memory Consumption

Not measured at runtime because Ollama and GUI services were not running.

Recommended target checks:

```bash
ps aux | grep -E 'ollama|AnythingLLM|open-webui'
```

macOS:

```bash
vm_stat
```

Linux:

```bash
free -h
```

## Response Latency

Not measured because no model runtime is available on this host.

Target test:

```bash
time ollama run qwen2.5:7b "Respond with one short paragraph about local AI."
```

## LAN GUI Latency

Not measured because GUI services were not running. The Linux healthcheck successfully generated a LAN URL:

```text
http://10.20.20.167:8080
```

LAN latency should be measured from another device on the same network after Open WebUI or AnythingLLM is running.

## Conclusions

- USB validation and folder/write checks passed.
- Generated backup and healthcheck workflows are lightweight.
- Runtime performance must be measured on the actual M4 Max and NUC after installing or configuring Ollama, AnythingLLM, and Open WebUI.
- Larger M4 Max models should be pulled only after the default and fallback models are validated.
