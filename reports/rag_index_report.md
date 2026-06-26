# RAG Index Report

Generated: 2026-06-26T03:25:02Z

Status: Complete

## Runtime

- ChromaDB installed under `data/rag/python-packages`
- ChromaDB persistent store: `data/chroma/library`
- Collection: `guide_library`
- Embedding model: `nomic-embed-text`
- Embedding provider: local Ollama `/api/embed`
- USB-local uv installed under `tools/uv/bin`
- USB-local zim-tools installed under `tools/zim-tools`

## Current Index State

- Corpus manifest: `data/rag/corpus/manifest.jsonl`
- Corpus documents available: 56,136
- Indexed chunks recorded: 213,850
- Chroma collection count: 213,850
- Indexing errors observed: 0

The full corpus index completed successfully. All 56,136 corpus documents were processed into 213,850 ChromaDB chunks with zero observed indexing errors.

## Rebuild Command

```bash
cd /mnt/usb/GUIDE
GUIDE_INDEX_BATCH_SIZE=64 ./scripts/build-rag-index.sh
```

The indexer is resumable and uses `data/chroma/library/indexed_ids.txt` to skip completed chunks on reruns.

## ZIM Tooling

`zimdump` is installed and validated:

```text
tools/zim-tools/zimdump
zim-tools 3.7.0
libzim 9.7.0
```

Native ZIM dumping is guarded by `ZIM_MAX_BYTES` to avoid accidentally expanding very large ZIM files into raw HTML all at once.
