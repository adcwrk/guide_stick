#!/usr/bin/env python3
import base64
import hmac
import json
import mimetypes
import os
import secrets
import subprocess
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "data" / "guide_webui"
LIBRARY_DIR = ROOT / "library" / "iiab"
CHROMA_DIR = ROOT / "data" / "chroma" / "library"
PYTHON_PACKAGES = ROOT / "data" / "rag" / "python-packages"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
RAG_COLLECTION = os.environ.get("GUIDE_RAG_COLLECTION", "guide_library")
EMBED_MODEL = os.environ.get("GUIDE_EMBED_MODEL", "nomic-embed-text")
ASK_MODEL = os.environ.get("GUIDE_ASK_MODEL", "qwen2.5:7b")
DEFAULT_TOP_K = int(os.environ.get("GUIDE_RAG_TOP_K", "6"))
MAX_TOP_K = int(os.environ.get("GUIDE_RAG_MAX_TOP_K", "12"))
MAX_CONTEXT_CHARS = int(os.environ.get("GUIDE_RAG_MAX_CONTEXT_CHARS", "14000"))
AUTH_REQUIRED = os.environ.get("ENABLE_AUTH", "true").lower() not in ("0", "false", "no", "off")
AUTH_USER = os.environ.get("GUIDE_WEBUI_USER", "guide")
AUTH_PASSWORD_FILE = Path(os.environ.get("GUIDE_WEBUI_PASSWORD_FILE") or ROOT / "config" / "guide-webui.password")


def find_rag_python():
    configured = os.environ.get("GUIDE_RAG_PYTHON")
    if configured and Path(configured).exists():
        return configured
    uv = ROOT / "tools" / "uv" / "bin" / "uv"
    if uv.exists():
        try:
            found = subprocess.check_output([str(uv), "python", "find", "3.12"], text=True).strip()
            if found:
                return found
        except Exception:
            pass
    fallback = Path("/home/guide/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python3.12")
    if fallback.exists():
        return str(fallback)
    return None


if PYTHON_PACKAGES.exists() and sys.version_info[:2] != (3, 12) and os.environ.get("GUIDE_WEBUI_REEXEC") != "1":
    rag_python = find_rag_python()
    if rag_python:
        env = os.environ.copy()
        env["GUIDE_WEBUI_REEXEC"] = "1"
        os.execvpe(rag_python, [rag_python, str(Path(__file__).resolve())], env)

if PYTHON_PACKAGES.exists():
    sys.path.insert(0, str(PYTHON_PACKAGES))


def load_webui_password():
    configured = os.environ.get("GUIDE_WEBUI_PASSWORD")
    if configured:
        return configured, "GUIDE_WEBUI_PASSWORD"
    if AUTH_PASSWORD_FILE.exists():
        password = AUTH_PASSWORD_FILE.read_text(encoding="utf-8").strip()
        if not password:
            raise RuntimeError(f"GUIDE WebUI password file is empty: {AUTH_PASSWORD_FILE}")
        return password, str(AUTH_PASSWORD_FILE)
    AUTH_PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    password = secrets.token_urlsafe(24)
    AUTH_PASSWORD_FILE.write_text(password + "\n", encoding="utf-8")
    try:
        AUTH_PASSWORD_FILE.chmod(0o600)
    except OSError:
        pass
    return password, str(AUTH_PASSWORD_FILE)


AUTH_PASSWORD = ""
AUTH_PASSWORD_SOURCE = ""
if AUTH_REQUIRED:
    AUTH_PASSWORD, AUTH_PASSWORD_SOURCE = load_webui_password()
AUTH_ENFORCED = AUTH_REQUIRED and bool(AUTH_PASSWORD)


def ollama_json(path, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{OLLAMA_URL}{path}", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ollama_embed(text):
    body = ollama_json("/api/embed", {"model": EMBED_MODEL, "input": [text]})
    embeddings = body.get("embeddings") or []
    if not embeddings:
        raise RuntimeError("Ollama did not return an embedding")
    return embeddings[0]


def chroma_collection():
    try:
        import chromadb
    except Exception as exc:
        raise RuntimeError(f"chromadb is not available: {exc}") from exc
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(RAG_COLLECTION)


def index_status():
    manifest_path = CHROMA_DIR / "guide_index_manifest.json"
    status = {
        "available": CHROMA_DIR.exists(),
        "collection": RAG_COLLECTION,
        "path": str(CHROMA_DIR),
        "index_manifest": str(manifest_path),
    }
    if manifest_path.exists():
        try:
            status.update(json.loads(manifest_path.read_text(encoding="utf-8")))
        except Exception as exc:
            status["manifest_error"] = str(exc)
    return status


def runtime_status():
    return {
        "ollama_url": OLLAMA_URL,
        "rag": {
            "collection": RAG_COLLECTION,
            "embedding_model": EMBED_MODEL,
            "default_model": ASK_MODEL,
            "default_top_k": DEFAULT_TOP_K,
            "max_top_k": MAX_TOP_K,
        },
        "auth": {
            "required_by_policy": AUTH_REQUIRED,
            "enforced_by_webui": AUTH_ENFORCED,
            "username": AUTH_USER if AUTH_ENFORCED else "",
            "password_source": AUTH_PASSWORD_SOURCE if AUTH_ENFORCED else "",
            "warning": (
                "GUIDE WebUI authentication is enforced with HTTP Basic auth. "
                "Use it only on localhost or a trusted LAN unless TLS is provided by a separate reverse proxy."
                if AUTH_ENFORCED else
                "ENABLE_AUTH is true, but no GUIDE WebUI password is configured."
                if AUTH_REQUIRED else
                "GUIDE WebUI authentication is disabled by configuration."
            ),
        },
    }


def clamp_top_k(value):
    try:
        top_k = int(value)
    except (TypeError, ValueError):
        top_k = DEFAULT_TOP_K
    return max(1, min(top_k, MAX_TOP_K))


def retrieve_library_chunks(question, top_k):
    collection = chroma_collection()
    embedding = ollama_embed(question)
    result = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    chunks = []
    for idx, chunk_id in enumerate(ids):
        meta = metas[idx] if idx < len(metas) and metas[idx] else {}
        doc = docs[idx] if idx < len(docs) else ""
        distance = distances[idx] if idx < len(distances) else None
        chunks.append({
            "id": chunk_id,
            "rank": idx + 1,
            "text": doc,
            "distance": distance,
            "title": meta.get("title") or meta.get("library_path") or chunk_id,
            "library_path": meta.get("library_path") or "",
            "library_url": meta.get("library_url") or "",
            "source_type": meta.get("source_type") or "",
            "chunk_index": meta.get("chunk_index"),
        })
    return chunks


def build_rag_prompt(question, chunks):
    context_parts = []
    total = 0
    for chunk in chunks:
        label = f"[{chunk['rank']}] {chunk['title']}"
        if chunk["library_url"]:
            label += f" ({chunk['library_url']})"
        text = chunk["text"].strip()
        remaining = MAX_CONTEXT_CHARS - total
        if remaining <= 0:
            break
        if len(text) > remaining:
            text = text[:remaining].rsplit(" ", 1)[0]
        block = f"{label}\n{text}"
        context_parts.append(block)
        total += len(block)
    context = "\n\n".join(context_parts)
    return (
        "You are GUIDE, an offline emergency knowledge assistant. "
        "Answer using only the provided library context. "
        "If the context is insufficient, say what is missing. "
        "Cite sources inline using bracket numbers like [1] or [2].\n\n"
        f"Question:\n{question}\n\nLibrary context:\n{context}"
    )


def ask_library(question, model, top_k):
    chunks = retrieve_library_chunks(question, top_k)
    if not chunks:
        return {
            "answer": "No matching library chunks were found.",
            "citations": [],
            "retrieved_chunks": [],
            "model": model,
            "embedding_model": EMBED_MODEL,
            "index_status": index_status(),
        }
    prompt = build_rag_prompt(question, chunks)
    response = ollama_json("/api/chat", {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": "You answer from retrieved offline library context and cite bracketed source numbers."},
            {"role": "user", "content": prompt},
        ],
    })
    citations = []
    for chunk in chunks:
        citations.append({
            "rank": chunk["rank"],
            "title": chunk["title"],
            "library_url": chunk["library_url"],
            "library_path": chunk["library_path"],
            "chunk_index": chunk["chunk_index"],
            "distance": chunk["distance"],
        })
    return {
        "answer": response.get("message", {}).get("content", ""),
        "citations": citations,
        "retrieved_chunks": chunks,
        "risk_notes": [
            "Answer is generated from retrieved local library chunks only.",
            "If retrieved citations are off-topic, improve or rebuild the corpus/index before relying on the answer.",
        ],
        "model": model,
        "embedding_model": EMBED_MODEL,
        "index_status": index_status(),
    }


def safe_child(base, requested):
    base_resolved = base.resolve()
    target = (base / requested).resolve()
    if target != base_resolved and base_resolved not in target.parents:
        return None
    return target


def directory_listing(path, url_path):
    entries = []
    for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        entries.append({
            "name": child.name,
            "type": "directory" if child.is_dir() else "file",
            "url": f"{url_path.rstrip('/')}/{child.name}",
            "size": child.stat().st_size if child.is_file() else None,
        })
    return entries


def library_summary():
    if not LIBRARY_DIR.exists():
        return {"available": False, "root": str(LIBRARY_DIR), "entries": [], "zims": []}
    entries = directory_listing(LIBRARY_DIR, "/library")
    zim_dir = LIBRARY_DIR / "zims" / "content"
    zims = []
    if zim_dir.exists():
        for zim in sorted(zim_dir.glob("*.zim")):
            zims.append({"name": zim.name, "size": zim.stat().st_size, "url": f"/library/zims/content/{zim.name}"})
    partials = []
    for partial in zim_dir.glob(".*") if zim_dir.exists() else []:
        if partial.is_file():
            partials.append({"name": partial.name, "size": partial.stat().st_size})
    return {
        "available": True,
        "root": str(LIBRARY_DIR),
        "entries": entries,
        "zims": zims,
        "partials": sorted(partials, key=lambda item: item["name"]),
        "common_links": [
            {"label": "IIAB web root", "url": "/library/www/html/"},
            {"label": "KA Lite content", "url": "/library/ka-lite/content/"},
            {"label": "MediaWiki files", "url": "/library/mediawiki-1.42.3/"},
            {"label": "WordPress files", "url": "/library/wordpress/"},
            {"label": "ZIM content", "url": "/library/zims/content/"},
        ],
    }


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

    def send_auth_required(self):
        body = json.dumps({"error": "authentication required"}).encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="GUIDE WebUI", charset="UTF-8"')
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def is_authenticated(self):
        if not AUTH_REQUIRED:
            return True
        header = self.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "basic" or not token:
            return False
        try:
            decoded = base64.b64decode(token, validate=True).decode("utf-8")
        except Exception:
            return False
        user, sep, password = decoded.partition(":")
        if not sep:
            return False
        return hmac.compare_digest(user, AUTH_USER) and hmac.compare_digest(password, AUTH_PASSWORD)

    def require_auth(self):
        if self.is_authenticated():
            return True
        self.send_auth_required()
        return False

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        if not self.require_auth():
            return

        if self.path == "/api/tags":
            try:
                self.send_json(200, ollama_json("/api/tags"))
            except Exception as exc:
                self.send_json(502, {"error": str(exc), "models": []})
            return

        if self.path == "/api/library":
            self.send_json(200, library_summary())
            return

        if self.path == "/api/status":
            self.send_json(200, runtime_status())
            return

        if self.path == "/api/library-index":
            try:
                status = index_status()
                try:
                    status["collection_count"] = chroma_collection().count()
                except Exception as exc:
                    status["collection_error"] = str(exc)
                self.send_json(200, status)
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})
            return

        if self.path == "/library" or self.path.startswith("/library/"):
            requested = self.path.removeprefix("/library").lstrip("/")
            target = safe_child(LIBRARY_DIR, requested)
            if target is None or not target.exists():
                self.send_error(404)
                return
            if target.is_dir():
                self.send_json(200, {"path": f"/library/{requested}", "entries": directory_listing(target, f"/library/{requested}")})
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()
            with target.open("rb") as fh:
                while True:
                    chunk = fh.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
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
        if not self.require_auth():
            return

        if self.path not in ("/api/chat", "/api/ask-library"):
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/api/ask-library":
                question = (incoming.get("question") or incoming.get("message") or "").strip()
                if not question:
                    self.send_json(400, {"error": "question is required"})
                    return
                model = incoming.get("model") or ASK_MODEL
                top_k = clamp_top_k(incoming.get("top_k"))
                self.send_json(200, ask_library(question, model, top_k))
            else:
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
    if AUTH_ENFORCED:
        print(f"GUIDE WebUI auth enabled for user '{AUTH_USER}'. Password source: {AUTH_PASSWORD_SOURCE}")
    else:
        print("GUIDE WebUI auth disabled.")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
