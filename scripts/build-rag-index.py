#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def chunks(text, size, overlap):
    text = " ".join(text.split())
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end == len(text):
            break
        start = max(end - overlap, start + 1)


def ollama_embed(base_url, model, texts, timeout):
    payload = json.dumps({"model": model, "input": texts}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    embeddings = body.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise RuntimeError(f"unexpected Ollama embedding response for {len(texts)} texts")
    return embeddings


def load_manifest(path, max_docs):
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") != "ok":
                continue
            yield row
            count += 1
            if max_docs and count >= max_docs:
                break


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_indexed_ids(path):
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the GUIDE ChromaDB RAG index from extracted corpus text.")
    parser.add_argument("--manifest", default=str(root / "data" / "rag" / "corpus" / "manifest.jsonl"))
    parser.add_argument("--chroma-path", default=str(root / "data" / "chroma" / "library"))
    parser.add_argument("--collection", default=os.environ.get("GUIDE_RAG_COLLECTION", "guide_library"))
    parser.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--model", default=os.environ.get("GUIDE_EMBED_MODEL", "nomic-embed-text"))
    parser.add_argument("--chunk-chars", type=int, default=int(os.environ.get("GUIDE_CHUNK_CHARS", "1800")))
    parser.add_argument("--chunk-overlap", type=int, default=int(os.environ.get("GUIDE_CHUNK_OVERLAP", "250")))
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("GUIDE_INDEX_BATCH_SIZE", "16")))
    parser.add_argument("--max-docs", type=int, default=int(os.environ.get("GUIDE_INDEX_MAX_DOCS", "0")))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("GUIDE_OLLAMA_TIMEOUT", "180")))
    args = parser.parse_args()

    try:
        import chromadb
    except Exception as exc:
        print(f"ERROR: chromadb is not importable: {exc}", file=sys.stderr)
        return 1

    manifest = Path(args.manifest)
    chroma_path = Path(args.chroma_path)
    if not manifest.exists():
        print(f"ERROR: corpus manifest not found: {manifest}", file=sys.stderr)
        return 1

    chroma_path.mkdir(parents=True, exist_ok=True)
    indexed_ids_path = chroma_path / "indexed_ids.txt"
    indexed_ids = load_indexed_ids(indexed_ids_path)
    client = chromadb.PersistentClient(path=str(chroma_path))
    collection = client.get_or_create_collection(
        name=args.collection,
        metadata={"hnsw:space": "cosine", "guide_model": args.model},
    )

    batch_ids = []
    batch_texts = []
    batch_metadatas = []
    stats = {
        "started_at": utc_now(),
        "completed_at": None,
        "status": "running",
        "collection": args.collection,
        "embedding_model": args.model,
        "manifest": str(manifest),
        "chroma_path": str(chroma_path),
        "documents_seen": 0,
        "chunks_seen": 0,
        "chunks_added": 0,
        "chunks_skipped_existing": 0,
        "batches_added": 0,
        "errors": 0,
    }

    def flush():
        if not batch_ids:
            return
        existing = indexed_ids.intersection(batch_ids)
        if existing:
            keep = [(i, t, m) for i, t, m in zip(batch_ids, batch_texts, batch_metadatas) if i not in existing]
            stats["chunks_skipped_existing"] += len(batch_ids) - len(keep)
        else:
            keep = list(zip(batch_ids, batch_texts, batch_metadatas))
        batch_ids.clear()
        batch_texts.clear()
        batch_metadatas.clear()
        if not keep:
            return
        ids, docs, metas = zip(*keep)
        embeddings = ollama_embed(args.ollama_url, args.model, list(docs), args.timeout)
        collection.add(ids=list(ids), documents=list(docs), metadatas=list(metas), embeddings=embeddings)
        with indexed_ids_path.open("a", encoding="utf-8") as fh:
            for item_id in ids:
                fh.write(item_id + "\n")
                indexed_ids.add(item_id)
        stats["chunks_added"] += len(ids)
        stats["batches_added"] += 1
        if stats["batches_added"] % 10 == 0:
            write_json(chroma_path / "guide_index_manifest.json", stats)
            print(
                f"indexed batches={stats['batches_added']} chunks_added={stats['chunks_added']} "
                f"docs_seen={stats['documents_seen']}",
                flush=True,
            )

    try:
        for row in load_manifest(manifest, args.max_docs):
            stats["documents_seen"] += 1
            corpus_path = Path(row["corpus_path"])
            if not corpus_path.exists():
                stats["errors"] += 1
                continue
            text = corpus_path.read_text(encoding="utf-8", errors="replace")
            for idx, chunk in enumerate(chunks(text, args.chunk_chars, args.chunk_overlap)):
                chunk_id = f"{row['id']}-{idx:05d}"
                stats["chunks_seen"] += 1
                batch_ids.append(chunk_id)
                batch_texts.append(chunk)
                batch_metadatas.append({
                    "source_id": row["id"],
                    "title": row.get("title") or "",
                    "library_path": row.get("library_path") or "",
                    "library_url": row.get("library_url") or "",
                    "source_type": row.get("source_type") or "",
                    "chunk_index": idx,
                    "chars": len(chunk),
                })
                if len(batch_ids) >= args.batch_size:
                    flush()
            if stats["documents_seen"] % 1000 == 0:
                write_json(chroma_path / "guide_index_manifest.json", stats)
        flush()
        stats["status"] = "complete" if not args.max_docs else "partial"
        stats["completed_at"] = utc_now()
        stats["collection_count"] = collection.count()
        write_json(chroma_path / "guide_index_manifest.json", stats)
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    except KeyboardInterrupt:
        stats["status"] = "interrupted"
        stats["completed_at"] = utc_now()
        write_json(chroma_path / "guide_index_manifest.json", stats)
        return 130
    except Exception as exc:
        stats["status"] = "failed"
        stats["completed_at"] = utc_now()
        stats["last_error"] = str(exc)
        stats["errors"] += 1
        write_json(chroma_path / "guide_index_manifest.json", stats)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
