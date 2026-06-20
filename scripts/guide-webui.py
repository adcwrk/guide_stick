#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "data" / "guide_webui"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")


def ollama_json(path, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{OLLAMA_URL}{path}", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    server_version = "GUIDEWebUI/0.1"

    def log_message(self, fmt, *args):
        log_path = ROOT / "logs" / "guide-webui-access.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write("%s - %s\n" % (self.address_string(), fmt % args))

    def send_json(self, status, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/tags":
            try:
                self.send_json(200, ollama_json("/api/tags"))
            except Exception as exc:
                self.send_json(502, {"error": str(exc), "models": []})
            return

        target = STATIC_DIR / "index.html" if self.path in ("/", "/index.html") else STATIC_DIR / self.path.lstrip("/")
        if not target.exists() or not target.is_file():
            self.send_error(404)
            return
        content = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
            model = incoming.get("model") or "llama3.2:3b"
            message = incoming.get("message", "").strip()
            if not message:
                self.send_json(400, {"error": "message is required"})
                return
            payload = {
                "model": model,
                "stream": False,
                "messages": [{"role": "user", "content": message}],
            }
            self.send_json(200, ollama_json("/api/chat", payload))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            self.send_json(exc.code, {"error": detail})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})


def main():
    host = os.environ.get("GUIDE_WEBUI_HOST", "0.0.0.0")
    port = int(os.environ.get("GUIDE_WEBUI_PORT", "8080"))
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"GUIDE WebUI listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
