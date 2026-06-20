# Performance Report

Generated: 2026-06-20T05:45:00Z

Target USB:

- Device: `/dev/sdb1`
- Label: `THKAILAR`
- UUID: `6676-08D4`
- Filesystem: `exfat`
- Mountpoint: `/mnt/usb`

## Environment

Validation host:

- OS observed by scripts: Linux
- Available memory during validation: 30 GiB total, 29 GiB available
- Target macOS hardware: Apple Silicon M4 Max

The current validation host is not the target M4 Max Mac. Apple Silicon Metal performance must be measured again on the Mac after running `setup-mac.sh`.

## Disk Utilization

- USB total capacity: 938 GB
- USB available capacity after deployment: approximately 938 GB
- Portable-AI-USB directory size after implementation and validation artifacts: approximately 42 MB

## USB I/O Behavior

Test command used a temporary 256 MB file inside `/mnt/usb/Portable-AI-USB`.

| Metric | Result | Notes |
|---|---:|---|
| Sequential write | 25.3 MB/s | `dd` with `conv=fsync`; representative of sustained writes to this mount |
| Sequential read | 5004.7 MB/s | Likely page-cache accelerated on the validation host; not a reliable cold-read number |

The direct-I/O read/write attempt was rejected by the exFAT mount with `Invalid input`, so direct cold-read measurement was not available without remounting or root-level cache control.

## Startup Time

Not fully measurable in this environment because portable macOS Ollama and AnythingLLM binaries are not installed and the current host is not macOS.

Expected measurement method on the target M4 Max:

1. Run `bash setup-mac.sh`.
2. Run `./start-mac.command`.
3. Measure elapsed time from launcher start to Ollama API readiness.
4. Measure elapsed time from launcher start to AnythingLLM interface reachable.

## Model Load Time

Not measured in this environment because Ollama is not installed and no models are currently pulled to the USB.

Recommended target measurements:

- `qwen2.5:7b`
- `llama3.2:3b`
- `nomic-embed-text`
- Optional: `qwen2.5:14b`, `llama3.1:8b`, `deepseek-r1:14b`

## Memory Consumption

Runtime memory was not measured because Ollama and AnythingLLM were not running.

The validation host had 30 GiB total memory and 29 GiB available before runtime startup. On an M4 Max system, unified memory pressure should be measured with Activity Monitor or:

```bash
vm_stat
ps aux | grep -E 'Ollama|ollama|AnythingLLM'
```

## Response Latency

Not measured in this environment because no model runtime was available.

Recommended target test:

```bash
time ollama run qwen2.5:7b "Respond with one short paragraph about local AI."
```

Then repeat for `llama3.2:3b` and optional larger models.

## Performance Conclusions

- USB write speed is adequate for logs, configuration, document staging, and moderate AnythingLLM vector updates.
- Large model pulls and backup archives will be limited by the observed write speed.
- The measured read value is cache-influenced and should not be used for model load planning.
- The M4 Max should run the recommended default and fallback models comfortably once the models are available in the USB-local Ollama store.
