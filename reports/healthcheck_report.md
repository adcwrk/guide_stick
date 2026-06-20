# Healthcheck Report

Generated: 2026-06-20T05:53:01Z

Runtime: Linux/NUC

USB root: `/mnt/usb/GUIDE`

Summary:

- Passed: 21
- Warnings: 4
- Failed: 0

| Status | Check | Detail |
|---|---|---|
| PASS | USB identity | THKAILAR validation passed where detectable |
| PASS | Required folder: config | present |
| PASS | Required folder: documents | present |
| PASS | Required folder: logs | present |
| PASS | Required folder: backups | present |
| PASS | Required folder: reports | present |
| PASS | Required folder: data/chroma | present |
| PASS | Required folder: data/anythingllm | present |
| PASS | Required folder: data/openwebui | present |
| PASS | Required folder: scripts | present |
| PASS | Required folder: ollama | present |
| PASS | Executable: start-linux.sh | yes |
| PASS | Executable: setup-linux.sh | yes |
| PASS | Executable: scripts/detect-usb.sh | yes |
| PASS | Executable: scripts/get-lan-url.sh | yes |
| PASS | Executable: scripts/backup-portable.sh | yes |
| PASS | Executable: scripts/ingest-documents.sh | yes |
| PASS | Logs writable | /mnt/usb/GUIDE/logs |
| PASS | Documents writable | /mnt/usb/GUIDE/documents |
| PASS | ChromaDB path writable | /mnt/usb/GUIDE/data/chroma |
| WARN | Ollama reachable | not reachable on port 11434 |
| WARN | Ollama installed | not detected |
| WARN | AnythingLLM reachable | not reachable on port 3001 |
| WARN | Open WebUI reachable | not reachable on port 8080 |
| PASS | LAN URL displayed | Local:    http://localhost:8080 Remote:   http://10.20.20.167:8080 Hostname: http://guide.local:8080  |


Log file: `/mnt/usb/GUIDE/logs/healthcheck-linux-20260620T055300Z.log`
