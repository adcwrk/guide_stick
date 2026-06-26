# Healthcheck Report

Generated: 2026-06-26T06:10:23Z

Runtime: Linux/NUC

USB root: `/mnt/usb/GUIDE`

Summary:

- Passed: 36
- Warnings: 2
- Failed: 0

| Status | Check | Detail |
|---|---|---|
| PASS | USB identity | GUIDE validation passed where detectable |
| PASS | Required folder: config | present |
| PASS | Required folder: documents | present |
| PASS | Required folder: logs | present |
| PASS | Required folder: backups | present |
| PASS | Required folder: reports | present |
| PASS | Required folder: data/chroma | present |
| PASS | Required folder: data/rag/corpus | present |
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
| PASS | Executable: scripts/install-anythingllm-linux.sh | yes |
| PASS | Executable: scripts/extract-library-corpus.sh | yes |
| PASS | Executable: scripts/build-rag-index.sh | yes |
| PASS | Executable: scripts/check-rag-ops.sh | yes |
| PASS | Logs writable | /mnt/usb/GUIDE/logs |
| PASS | Documents writable | /mnt/usb/GUIDE/documents |
| PASS | ChromaDB path writable | /mnt/usb/GUIDE/data/chroma |
| PASS | RAG corpus manifest | 56136 rows |
| PASS | RAG Chroma index | 213850 indexed chunks |
| PASS | zimdump installed | zim-tools 3.7.0 |
| PASS | RAG operations checks | complete_with_warnings: 15 pass, 2 warn, 0 fail |
| PASS | Ollama reachable | http://127.0.0.1:11434/api/tags |
| PASS | Ollama installed | /mnt/usb/GUIDE/ollama/ollama |
| PASS | Model: qwen2.5:7b | available |
| PASS | Model: llama3.2:3b | available |
| PASS | Model: nomic-embed-text | available |
| WARN | AnythingLLM reachable | not reachable on port 3001 |
| PASS | AnythingLLM AppImage runtime | installed on USB |
| WARN | Open WebUI reachable | not reachable on port 8080 |
| PASS | LAN URL displayed | Local:    http://localhost:8080 Remote:   http://10.20.20.167:8080 Hostname: http://guide.local:8080  |


Log file: `/mnt/usb/GUIDE/logs/healthcheck-linux-20260626T061020Z.log`
