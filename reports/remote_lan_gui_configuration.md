# Remote LAN GUI Configuration

GUIDE now supports a future-ready LAN GUI configuration while preserving the upstream desktop workflows.

## Defaults

Configured in `config/portable.env.example`:

```text
ENABLE_REMOTE_ACCESS=true
ENABLE_REMOTE_OLLAMA=false
ENABLE_AUTH=true
ANYTHINGLLM_PORT=3001
OPENWEBUI_PORT=8080
OLLAMA_PORT=11434
BIND_ADDRESS=0.0.0.0
LAN_ONLY=true
```

## Service Exposure

| Service | Local URL | LAN behavior | Authentication |
|---|---|---|---|
| AnythingLLM | `http://localhost:3001` | GUI URL printed when reachable | Managed by AnythingLLM where supported |
| Open WebUI | `http://localhost:8080` | Binds to `0.0.0.0` when started by launcher | First-run admin account expected |
| Ollama | `http://localhost:11434` | Remote disabled by default | No built-in auth in this launcher |

## Safety Rules

- Do not expose Ollama remotely unless `ENABLE_REMOTE_OLLAMA=true` is explicitly set.
- Do not hard-code passwords in scripts or committed config.
- Use GUI first-run admin setup where available.
- If a port is occupied, launchers report it and do not kill existing host services.
- LAN-only exposure is preferred. Internet exposure requires a separate authenticated reverse proxy and TLS, which is outside this phase.

## Open WebUI Startup

Launchers look for Open WebUI in this order:

1. `OPENWEBUI_BIN` from `config/portable.env`
2. `open-webui` on `PATH`
3. `python3 -m open_webui`

Open WebUI persistent data is pointed at:

```text
data/openwebui/
```

## ChromaDB Storage

ChromaDB persistent storage is reserved at:

```text
data/chroma/
```

Scripts must not delete this path. Backups should be taken before migrations.

## Future GUIDE Path

GUIDE is intentionally not built in this phase. The prepared path is:

- Add GUIDE as another GUI service in `config/services.json`.
- Store GUIDE data under `data/guide/`.
- Reuse `scripts/detect-usb.sh` and `scripts/get-lan-url.sh`.
- Add GUIDE health checks without replacing AnythingLLM or Open WebUI.
