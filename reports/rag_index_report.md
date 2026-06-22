# RAG Index Report

Generated: 2026-06-22T04:22:15Z

Status: In Progress

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
- Indexed chunks recorded: 15,744
- Chroma collection count: 15,744
- Indexing errors observed: 0

The full corpus index is resumable. The first smoke run indexed 143 chunks from 100 documents. Follow-up indexing has advanced the collection to 15,744 verified chunks with zero observed indexing errors.

## Resume Command

```bash
cd /mnt/usb/GUIDE
GUIDE_INDEX_BATCH_SIZE=64 ./scripts/build-rag-index.sh
```

The indexer uses `data/chroma/library/indexed_ids.txt` to skip completed chunks on reruns.

## ZIM Tooling

`zimdump` is installed and validated:

```text
tools/zim-tools/zimdump
zim-tools 3.7.0
libzim 9.7.0
```

Native ZIM dumping is guarded by `ZIM_MAX_BYTES` to avoid accidentally expanding very large ZIM files into raw HTML all at once.
