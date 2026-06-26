# RAG Operations Report

Generated: 2026-06-26T06:10:22Z

Status: `complete_with_warnings`

## Summary

- Passed: 15
- Warnings: 2
- Failed: 0
- Corpus documents: 56136
- Indexed chunks: 213850
- Live Chroma count: 213850

## Coverage

- Corpus source types: css: 1179, csv: 1, html: 969, json: 52365, md: 727, rst: 51, txt: 662, xml: 129, yaml: 10, yml: 43
- ZIM source statuses: deferred: 18
- Current zimdump: /mnt/usb/GUIDE/tools/zim-tools/zimdump
- Deferred ZIM files: 18
- Partial ZIM imports: 1

## Checks

| Status | Check | Detail |
|---|---|---|
| PASS | Corpus summary manifest | /mnt/usb/GUIDE/data/rag/corpus/library_manifest.json |
| PASS | Corpus JSONL manifest | 56136 rows, 56136 ok rows |
| PASS | Corpus file references | all ok rows point to readable text files |
| PASS | Corpus document count | 56136 ok rows match extraction summary |
| PASS | ZIM source inventory | 18 recorded ZIM source files present |
| PASS | ZIM source sizes | recorded ZIM sizes match current files |
| WARN | Native ZIM article extraction | 18 ZIM files deferred |
| WARN | Partial ZIM imports | 1 partial ZIM import file(s) recorded |
| PASS | zimdump current availability | /mnt/usb/GUIDE/tools/zim-tools/zimdump |
| PASS | Index manifest | /mnt/usb/GUIDE/data/chroma/library/guide_index_manifest.json |
| PASS | Index status | complete |
| PASS | Indexed IDs ledger | 213850 chunk IDs |
| PASS | Indexed chunk ledger count | 213850 matches chunks_seen |
| PASS | Indexed document count | 56136 matches corpus ok rows |
| PASS | ChromaDB live collection | guide_library has 213850 chunks |
| PASS | Chroma/index count agreement | 213850 chunks |
| PASS | Index freshness | index completed at 2026-06-25T10:59:09Z after corpus generated at 2026-06-21T15:57:52Z |

## Artifacts

- Consolidated manifest: `/mnt/usb/GUIDE/data/rag/library_manifest.json`
- Corpus summary: `/mnt/usb/GUIDE/data/rag/corpus/library_manifest.json`
- Corpus JSONL: `/mnt/usb/GUIDE/data/rag/corpus/manifest.jsonl`
- Index manifest: `/mnt/usb/GUIDE/data/chroma/library/guide_index_manifest.json`
