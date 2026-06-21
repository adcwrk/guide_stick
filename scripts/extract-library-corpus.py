#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".htm",
    ".html",
    ".json",
    ".md",
    ".rst",
    ".text",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    "node_modules",
}

SKIP_SUFFIXES = {
    ".map",
    ".min.css",
    ".min.js",
}


class TextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "canvas"}:
            self.skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in {"p", "br", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "canvas"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "div", "section", "article", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self._in_title:
            self.title += data.strip()
        self.parts.append(data)

    def text(self):
        return normalize_text(" ".join(self.parts))


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_text(value):
    value = html.unescape(value)
    value = value.replace("\x00", " ")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def read_text(path, max_bytes):
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"file exceeds max bytes: {size}")
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def extract_text(path, max_bytes):
    source = read_text(path, max_bytes)
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        parser = TextHTMLParser()
        parser.feed(source)
        return parser.text(), normalize_text(parser.title)
    return normalize_text(source), ""


def should_skip(path):
    lowered = path.name.lower()
    return any(lowered.endswith(suffix) for suffix in SKIP_SUFFIXES)


def corpus_id(root, path):
    rel = path.relative_to(root).as_posix()
    return hashlib.sha256(rel.encode("utf-8")).hexdigest()[:24]


def write_doc(output_dir, doc_id, text):
    target = output_dir / "files" / f"{doc_id}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text + "\n", encoding="utf-8")
    return target


def iter_source_files(source):
    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for name in files:
            path = Path(root) / name
            if should_skip(path):
                continue
            if path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def extract_files(source, output, manifest_path, max_bytes, min_chars):
    stats = {
        "scanned": 0,
        "written": 0,
        "skipped_short": 0,
        "skipped_large": 0,
        "failed": 0,
        "bytes_written": 0,
    }
    output.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as manifest:
        for path in iter_source_files(source):
            stats["scanned"] += 1
            doc_id = corpus_id(source, path)
            rel = path.relative_to(source).as_posix()
            try:
                text, title = extract_text(path, max_bytes)
            except ValueError:
                stats["skipped_large"] += 1
                continue
            except Exception as exc:
                stats["failed"] += 1
                manifest.write(json.dumps({
                    "id": doc_id,
                    "source_path": str(path),
                    "library_path": rel,
                    "status": "failed",
                    "error": str(exc),
                }, sort_keys=True) + "\n")
                continue
            if len(text) < min_chars:
                stats["skipped_short"] += 1
                continue
            target = write_doc(output, doc_id, text)
            stats["written"] += 1
            stats["bytes_written"] += target.stat().st_size
            manifest.write(json.dumps({
                "id": doc_id,
                "source_type": path.suffix.lower().lstrip(".") or "text",
                "source_path": str(path),
                "library_path": rel,
                "library_url": f"/library/{rel}",
                "corpus_path": str(target),
                "title": title or path.stem.replace("_", " ").replace("-", " "),
                "chars": len(text),
                "bytes": target.stat().st_size,
                "status": "ok",
            }, sort_keys=True) + "\n")
            if stats["written"] % 1000 == 0:
                print(f"extracted {stats['written']} documents...", flush=True)
    return stats


def zim_files(source):
    zim_root = source / "zims" / "content"
    if not zim_root.exists():
        return []
    return sorted(path for path in zim_root.glob("*.zim") if path.is_file())


def zim_inventory(source, include_zims, zim_limit):
    zims = zim_files(source)
    if zim_limit:
        zims = zims[:zim_limit]
    zimdump = shutil.which("zimdump")
    records = []
    for zim in zims:
        records.append({
            "name": zim.name,
            "path": str(zim),
            "size": zim.stat().st_size,
            "status": "pending" if include_zims and zimdump else "deferred",
            "reason": None if include_zims and zimdump else "zimdump is not installed on this host",
        })
    partials = []
    zim_root = source / "zims" / "content"
    if zim_root.exists():
        for partial in sorted(zim_root.glob(".*.zim.*")):
            if partial.is_file():
                partials.append({"name": partial.name, "path": str(partial), "size": partial.stat().st_size})
    return records, partials, zimdump


def extract_zims(source, output, include_zims, zim_limit):
    records, partials, zimdump = zim_inventory(source, include_zims, zim_limit)
    if not include_zims or not zimdump:
        return {"tool": zimdump, "records": records, "partials": partials, "extracted": 0, "failed": 0}

    raw_root = output / "zim_raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    extracted = 0
    failed = 0
    for record in records:
        zim_path = Path(record["path"])
        target = raw_root / zim_path.stem
        marker = target / ".guide-zimdump-complete"
        if marker.exists():
            record["status"] = "already_extracted"
            extracted += 1
            continue
        target.mkdir(parents=True, exist_ok=True)
        cmd = [zimdump, "dump", f"--dir={target}", str(zim_path)]
        try:
            subprocess.run(cmd, check=True)
            marker.write_text(utc_now() + "\n", encoding="utf-8")
            record["status"] = "extracted"
            record["raw_output"] = str(target)
            extracted += 1
        except Exception as exc:
            record["status"] = "failed"
            record["reason"] = str(exc)
            failed += 1
    return {"tool": zimdump, "records": records, "partials": partials, "extracted": extracted, "failed": failed}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path, source, output, file_stats, zim_stats):
    completed_with_warnings = bool(zim_stats["records"]) and not zim_stats["tool"]
    status = "Complete with Warnings" if completed_with_warnings else "Complete"
    lines = [
        "# RAG Corpus Extraction Report",
        "",
        f"Generated: {utc_now()}",
        "",
        f"Status: {status}",
        "",
        f"Source library: `{source}`",
        f"Corpus root: `{output}`",
        "",
        "## HTML and Text Extraction",
        "",
        f"- Files scanned: {file_stats['scanned']}",
        f"- Corpus documents written: {file_stats['written']}",
        f"- Short files skipped: {file_stats['skipped_short']}",
        f"- Large files skipped: {file_stats['skipped_large']}",
        f"- Failed files: {file_stats['failed']}",
        f"- Corpus bytes written: {file_stats['bytes_written']}",
        "",
        "## ZIM Extraction",
        "",
        f"- ZIM reader: `{zim_stats['tool'] or 'not available'}`",
        f"- ZIM files inventoried: {len(zim_stats['records'])}",
        f"- ZIM files extracted by this run: {zim_stats['extracted']}",
        f"- ZIM extraction failures: {zim_stats['failed']}",
        f"- Partial ZIM files detected: {len(zim_stats['partials'])}",
        "",
    ]
    if not zim_stats["tool"] and zim_stats["records"]:
        lines.extend([
            "ZIM article extraction is implemented through `zimdump`, but `zimdump` is not installed on this host.",
            "The corpus is still usable for HTML/text sources, and the manifest records every available ZIM as deferred.",
            "",
            "To extract native ZIM articles later without changing originals:",
            "",
            "```bash",
            "cd /mnt/usb/GUIDE",
            "INCLUDE_ZIMS=true ./scripts/extract-library-corpus.sh",
            "```",
            "",
        ])
    lines.extend([
        "## Outputs",
        "",
        f"- Manifest JSONL: `{output / 'manifest.jsonl'}`",
        f"- Corpus summary: `{output / 'library_manifest.json'}`",
        f"- Text files: `{output / 'files'}`",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Extract GUIDE IIAB library text into a RAG corpus.")
    parser.add_argument("--source", default=str(root / "library" / "iiab"))
    parser.add_argument("--output", default=str(root / "data" / "rag" / "corpus"))
    parser.add_argument("--include-zims", action="store_true", default=os.environ.get("INCLUDE_ZIMS") == "true")
    parser.add_argument("--zim-limit", type=int, default=int(os.environ.get("ZIM_LIMIT", "0")))
    parser.add_argument("--max-file-bytes", type=int, default=int(os.environ.get("MAX_FILE_BYTES", str(20 * 1024 * 1024))))
    parser.add_argument("--min-chars", type=int, default=int(os.environ.get("MIN_CORPUS_CHARS", "80")))
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    if not source.exists():
        print(f"ERROR: source library not found: {source}", file=sys.stderr)
        return 1
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "manifest.jsonl"

    zim_stats = extract_zims(source, output, args.include_zims, args.zim_limit)
    file_stats = extract_files(source, output, manifest_path, args.max_file_bytes, args.min_chars)

    summary = {
        "generated_at": utc_now(),
        "source_library": str(source),
        "corpus_root": str(output),
        "manifest_path": str(manifest_path),
        "file_extraction": file_stats,
        "zim_extraction": zim_stats,
        "status": "complete_with_warnings" if zim_stats["records"] and not zim_stats["tool"] else "complete",
    }
    write_json(output / "library_manifest.json", summary)
    write_report(root / "reports" / "rag_corpus_extraction_report.md", source, output, file_stats, zim_stats)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
