# RAG Corpus Extraction Report

Generated: 2026-06-21T15:57:52Z

Status: Complete with Warnings

Source library: `/mnt/usb/GUIDE/library/iiab`
Corpus root: `/mnt/usb/GUIDE/data/rag/corpus`

## HTML and Text Extraction

- Files scanned: 58313
- Corpus documents written: 56136
- Short files skipped: 2177
- Large files skipped: 0
- Failed files: 0
- Corpus bytes written: 316418454

## ZIM Extraction

- ZIM reader: `not available`
- ZIM files inventoried: 18
- ZIM files extracted by this run: 0
- ZIM extraction failures: 0
- Partial ZIM files detected: 1

ZIM article extraction is implemented through `zimdump`, but `zimdump` is not installed on this host.
The corpus is still usable for HTML/text sources, and the manifest records every available ZIM as deferred.

To extract native ZIM articles later without changing originals:

```bash
cd /mnt/usb/GUIDE
INCLUDE_ZIMS=true ./scripts/extract-library-corpus.sh
```

## Outputs

- Manifest JSONL: `/mnt/usb/GUIDE/data/rag/corpus/manifest.jsonl`
- Corpus summary: `/mnt/usb/GUIDE/data/rag/corpus/library_manifest.json`
- Text files: `/mnt/usb/GUIDE/data/rag/corpus/files`
