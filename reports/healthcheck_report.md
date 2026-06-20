# Healthcheck Report

Generated: 2026-06-20T05:43:17Z

USB root: `/mnt/usb/Portable-AI-USB`

Summary:

- Passed: 12
- Warnings: 2
- Failed: 2

| Status | Check | Detail |
|---|---|---|
| PASS | USB mounted | /mnt/usb/Portable-AI-USB exists |
| PASS | USB writable | /mnt/usb/Portable-AI-USB is writable |
| PASS | Required directory: config | present |
| PASS | Required directory: documents | present |
| PASS | Required directory: logs | present |
| PASS | Required directory: backups | present |
| PASS | Required directory: reports | present |
| PASS | Required directory: anythingllm_data | present |
| PASS | Required directory: ollama | present |
| PASS | Logs writable | /mnt/usb/Portable-AI-USB/logs |
| PASS | Document path writable | /mnt/usb/Portable-AI-USB/documents |
| PASS | Data path writable | /mnt/usb/Portable-AI-USB/anythingllm_data |
| FAIL | Ollama running | http://127.0.0.1:11434/api/tags not reachable |
| FAIL | Ollama installed | no portable or PATH ollama found |
| WARN | AnythingLLM running | process not detected |
| WARN | Web interface reachable | http://127.0.0.1:3001 not reachable |


Log file: `/mnt/usb/Portable-AI-USB/logs/healthcheck-mac-20260620T054316Z.log`
