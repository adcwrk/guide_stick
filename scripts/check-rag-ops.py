#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class Recorder:
    def __init__(self):
        self.pass_count = 0
        self.warn_count = 0
        self.fail_count = 0
        self.checks = []

    def add(self, status, name, detail):
        status = status.upper()
        if status == "PASS":
            self.pass_count += 1
        elif status == "WARN":
            self.warn_count += 1
        elif status == "FAIL":
            self.fail_count += 1
        else:
            raise ValueError(f"unknown status: {status}")
        self.checks.append({"status": status, "check": name, "detail": detail})

    def overall_status(self):
        if self.fail_count:
            return "failed"
        if self.warn_count:
            return "complete_with_warnings"
        return "complete"


def inspect_manifest(manifest_path, corpus_root, recorder):
    rows = 0
    ok_rows = 0
    missing_files = []
    source_types = Counter()
    bytes_total = 0
    if not manifest_path.exists():
        recorder.add("FAIL", "Corpus JSONL manifest", f"missing: {manifest_path}")
        return {
            "path": str(manifest_path),
            "rows": 0,
            "ok_rows": 0,
            "missing_corpus_files": 0,
            "source_type_counts": {},
            "bytes": 0,
        }

    with manifest_path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                recorder.add("FAIL", "Corpus JSONL parse", f"line {line_no}: {exc}")
                continue
            source_types[row.get("source_type") or "unknown"] += 1
            if row.get("status") == "ok":
                ok_rows += 1
                path = Path(row.get("corpus_path") or "")
                if not path.is_absolute():
                    path = corpus_root / path
                if not path.exists():
                    missing_files.append(str(path))
                else:
                    bytes_total += path.stat().st_size

    if rows:
        recorder.add("PASS", "Corpus JSONL manifest", f"{rows} rows, {ok_rows} ok rows")
    else:
        recorder.add("FAIL", "Corpus JSONL manifest", "manifest is empty")

    if missing_files:
        detail = f"{len(missing_files)} referenced corpus files missing"
        if len(missing_files) <= 5:
            detail += f": {', '.join(missing_files)}"
        recorder.add("FAIL", "Corpus file references", detail)
    else:
        recorder.add("PASS", "Corpus file references", "all ok rows point to readable text files")

    return {
        "path": str(manifest_path),
        "rows": rows,
        "ok_rows": ok_rows,
        "missing_corpus_files": len(missing_files),
        "source_type_counts": dict(sorted(source_types.items())),
        "bytes": bytes_total,
    }


def inspect_zims(corpus_summary, recorder):
    zim = corpus_summary.get("zim_extraction") or {}
    records = zim.get("records") or []
    partials = zim.get("partials") or []
    status_counts = Counter(record.get("status") or "unknown" for record in records)
    missing = []
    size_mismatch = []
    for record in records:
        path = Path(record.get("path") or "")
        if not path.exists():
            missing.append(str(path))
            continue
        expected = record.get("size")
        if expected is not None and path.stat().st_size != expected:
            size_mismatch.append(str(path))

    if missing:
        recorder.add("FAIL", "ZIM source inventory", f"{len(missing)} ZIM source files missing")
    else:
        recorder.add("PASS", "ZIM source inventory", f"{len(records)} recorded ZIM source files present")

    if size_mismatch:
        recorder.add("WARN", "ZIM source sizes", f"{len(size_mismatch)} recorded ZIM sizes changed")
    elif records:
        recorder.add("PASS", "ZIM source sizes", "recorded ZIM sizes match current files")

    deferred = status_counts.get("deferred", 0)
    if deferred:
        recorder.add("WARN", "Native ZIM article extraction", f"{deferred} ZIM files deferred")
    else:
        recorder.add("PASS", "Native ZIM article extraction", "no deferred ZIM files recorded")

    if partials:
        recorder.add("WARN", "Partial ZIM imports", f"{len(partials)} partial ZIM import file(s) recorded")
    else:
        recorder.add("PASS", "Partial ZIM imports", "none recorded")

    return {
        "records": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "partials": len(partials),
        "missing_files": len(missing),
        "size_mismatches": len(size_mismatch),
        "tool": zim.get("tool"),
    }


def inspect_chroma(chroma_path, collection_name, recorder):
    try:
        import chromadb
    except Exception as exc:
        recorder.add("WARN", "ChromaDB live collection", f"chromadb is not importable: {exc}")
        return {"available": False, "collection": collection_name, "error": str(exc)}

    try:
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_collection(collection_name)
        count = collection.count()
        recorder.add("PASS", "ChromaDB live collection", f"{collection_name} has {count} chunks")
        return {"available": True, "collection": collection_name, "count": count}
    except Exception as exc:
        recorder.add("FAIL", "ChromaDB live collection", str(exc))
        return {"available": False, "collection": collection_name, "error": str(exc)}


def find_zimdump(root):
    candidates = [
        root / "tools" / "zim-tools" / "zimdump",
        root / "tools" / "zimdump",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    return None


def write_report(path, data):
    rows = "\n".join(
        f"| {item['status']} | {item['check']} | {item['detail']} |"
        for item in data["checks"]
    )
    source_counts = ", ".join(
        f"{name}: {count}" for name, count in data["corpus"]["source_type_counts"].items()
    ) or "none"
    zim_counts = ", ".join(
        f"{name}: {count}" for name, count in data["sources"]["zim"]["status_counts"].items()
    ) or "none"
    text = f"""# RAG Operations Report

Generated: {data['generated_at']}

Status: `{data['status']}`

## Summary

- Passed: {data['summary']['passed']}
- Warnings: {data['summary']['warnings']}
- Failed: {data['summary']['failed']}
- Corpus documents: {data['corpus']['ok_rows']}
- Indexed chunks: {data['index']['indexed_ids_count']}
- Live Chroma count: {data['index']['chroma'].get('count', 'unavailable')}

## Coverage

- Corpus source types: {source_counts}
- ZIM source statuses: {zim_counts}
- Current zimdump: {data['sources']['zim'].get('current_tool') or 'not found'}
- Deferred ZIM files: {data['sources']['zim']['status_counts'].get('deferred', 0)}
- Partial ZIM imports: {data['sources']['zim']['partials']}

## Checks

| Status | Check | Detail |
|---|---|---|
{rows}

## Artifacts

- Consolidated manifest: `{data['paths']['output_manifest']}`
- Corpus summary: `{data['paths']['corpus_summary']}`
- Corpus JSONL: `{data['paths']['corpus_manifest']}`
- Index manifest: `{data['paths']['index_manifest']}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate GUIDE RAG corpus, source inventory, and Chroma index health.")
    parser.add_argument("--corpus-root", default=str(root / "data" / "rag" / "corpus"))
    parser.add_argument("--chroma-path", default=str(root / "data" / "chroma" / "library"))
    parser.add_argument("--collection", default="guide_library")
    parser.add_argument("--output", default=str(root / "data" / "rag" / "library_manifest.json"))
    parser.add_argument("--report", default=str(root / "reports" / "rag_operations_report.md"))
    args = parser.parse_args()

    corpus_root = Path(args.corpus_root)
    chroma_path = Path(args.chroma_path)
    corpus_summary_path = corpus_root / "library_manifest.json"
    corpus_manifest_path = corpus_root / "manifest.jsonl"
    index_manifest_path = chroma_path / "guide_index_manifest.json"
    indexed_ids_path = chroma_path / "indexed_ids.txt"
    output_path = Path(args.output)
    report_path = Path(args.report)
    recorder = Recorder()

    if corpus_summary_path.exists():
        corpus_summary = read_json(corpus_summary_path)
        recorder.add("PASS", "Corpus summary manifest", str(corpus_summary_path))
    else:
        corpus_summary = {}
        recorder.add("FAIL", "Corpus summary manifest", f"missing: {corpus_summary_path}")

    corpus = inspect_manifest(corpus_manifest_path, corpus_root, recorder)
    expected_docs = (corpus_summary.get("file_extraction") or {}).get("written")
    if expected_docs is not None and expected_docs == corpus["ok_rows"]:
        recorder.add("PASS", "Corpus document count", f"{corpus['ok_rows']} ok rows match extraction summary")
    elif expected_docs is not None:
        recorder.add("FAIL", "Corpus document count", f"summary written={expected_docs}, manifest ok rows={corpus['ok_rows']}")

    zim = inspect_zims(corpus_summary, recorder)
    zim["current_tool"] = find_zimdump(root)
    if zim["current_tool"]:
        recorder.add("PASS", "zimdump current availability", zim["current_tool"])
    else:
        recorder.add("WARN", "zimdump current availability", "not found under tools/zim-tools")

    if index_manifest_path.exists():
        index_manifest = read_json(index_manifest_path)
        recorder.add("PASS", "Index manifest", str(index_manifest_path))
    else:
        index_manifest = {}
        recorder.add("FAIL", "Index manifest", f"missing: {index_manifest_path}")

    index_status = index_manifest.get("status")
    if index_status == "complete":
        recorder.add("PASS", "Index status", "complete")
    else:
        recorder.add("FAIL", "Index status", str(index_status or "missing"))

    indexed_ids_count = 0
    if indexed_ids_path.exists():
        with indexed_ids_path.open("r", encoding="utf-8") as fh:
            indexed_ids_count = sum(1 for line in fh if line.strip())
        recorder.add("PASS", "Indexed IDs ledger", f"{indexed_ids_count} chunk IDs")
    else:
        recorder.add("FAIL", "Indexed IDs ledger", f"missing: {indexed_ids_path}")

    chunks_seen = index_manifest.get("chunks_seen")
    if chunks_seen is not None and chunks_seen == indexed_ids_count:
        recorder.add("PASS", "Indexed chunk ledger count", f"{indexed_ids_count} matches chunks_seen")
    elif chunks_seen is not None:
        recorder.add("FAIL", "Indexed chunk ledger count", f"indexed_ids={indexed_ids_count}, chunks_seen={chunks_seen}")

    documents_seen = index_manifest.get("documents_seen")
    if documents_seen is not None and documents_seen == corpus["ok_rows"]:
        recorder.add("PASS", "Indexed document count", f"{documents_seen} matches corpus ok rows")
    elif documents_seen is not None:
        recorder.add("WARN", "Indexed document count", f"documents_seen={documents_seen}, corpus ok rows={corpus['ok_rows']}")

    chroma = inspect_chroma(chroma_path, index_manifest.get("collection") or args.collection, recorder)
    live_count = chroma.get("count")
    manifest_count = index_manifest.get("collection_count")
    if live_count is not None and manifest_count is not None and live_count == manifest_count == indexed_ids_count:
        recorder.add("PASS", "Chroma/index count agreement", f"{live_count} chunks")
    elif live_count is not None:
        recorder.add("FAIL", "Chroma/index count agreement", f"live={live_count}, manifest={manifest_count}, indexed_ids={indexed_ids_count}")

    corpus_generated = parse_utc(corpus_summary.get("generated_at"))
    index_completed = parse_utc(index_manifest.get("completed_at"))
    if corpus_generated and index_completed:
        if index_completed >= corpus_generated:
            recorder.add("PASS", "Index freshness", f"index completed at {index_manifest.get('completed_at')} after corpus generated at {corpus_summary.get('generated_at')}")
        else:
            recorder.add("FAIL", "Index freshness", f"index completed at {index_manifest.get('completed_at')} before corpus generated at {corpus_summary.get('generated_at')}")
    else:
        recorder.add("WARN", "Index freshness", "timestamps unavailable")

    data = {
        "generated_at": utc_now(),
        "status": recorder.overall_status(),
        "summary": {
            "passed": recorder.pass_count,
            "warnings": recorder.warn_count,
            "failed": recorder.fail_count,
        },
        "paths": {
            "output_manifest": str(output_path),
            "corpus_summary": str(corpus_summary_path),
            "corpus_manifest": str(corpus_manifest_path),
            "index_manifest": str(index_manifest_path),
            "indexed_ids": str(indexed_ids_path),
            "chroma_path": str(chroma_path),
        },
        "corpus": corpus,
        "sources": {"zim": zim},
        "index": {
            "manifest": index_manifest,
            "indexed_ids_count": indexed_ids_count,
            "chroma": chroma,
        },
        "checks": recorder.checks,
    }
    write_json(output_path, data)
    write_report(report_path, data)
    print(json.dumps(data, indent=2, sort_keys=True))
    return 1 if recorder.fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
