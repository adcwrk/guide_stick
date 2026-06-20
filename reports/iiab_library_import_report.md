# IIAB Library Import Report

Generated: 2026-06-20T20:21:00Z

## Summary

The mounted SD/eMMC Internet-in-a-Box style library at `/mnt/sdcard/rootfs/library` was incorporated into GUIDE on the USB at:

`/mnt/usb/GUIDE/library/iiab`

Current imported size on USB:

`96G`

USB capacity after import:

`/dev/sdb1` mounted at `/mnt/usb`, `938G` total, `102G` used, `837G` available.

## GUIDE WebUI Integration

The GUIDE WebUI now exposes the imported library through the existing LAN service:

- Library API: `http://10.20.20.167:8080/api/library`
- Library file root: `http://10.20.20.167:8080/library/`
- IIAB web root: `http://10.20.20.167:8080/library/www/html/`
- KA Lite content: `http://10.20.20.167:8080/library/ka-lite/content/`
- ZIM content: `http://10.20.20.167:8080/library/zims/content/`

The WebUI home page now includes a Library panel that reports imported content and links to common library locations.

## Copied Content

The import copied readable content from these source areas where available:

- `archiveorg/`
- `awstats/` metadata that was readable
- `calibre-web/`
- `dbdata/` metadata that was readable
- `downloads/`
- `games/`
- `gitea/` readable files
- `ka-lite/`
- `kolibri/`
- `mediawiki-1.42.3/`
- `moodle/`
- `pgsql-iiab/` directory shell only; protected database content needs privileged copy
- `public/`
- `transmission/`
- `wordpress/`
- `working/`
- `www/` except deferred map database
- `zims/library.xml`
- `zims/content/fas-military-medicine_en_2024-06.zim`

## Deferred Or Partial Content

Some content was intentionally deferred because the interactive copy became impractically slow:

- `www/html/common/html/urgentanswersbak/`
  - Backup duplicate subtree.
  - Initial pass stalled on `arcticshelter.mp4.hold.mp4`.
  - Primary `www/html/common/html/ua/videos/` content had already copied.

- `www/osm-vector-maps/`
  - Large offline map tile database.
  - Transfer of `osm-planet_z0-z10_2020.mbtiles` slowed to day-scale estimates.
  - Partial file remains on the USB and can be resumed.

- `zims/content/`
  - One complete ZIM copied: `fas-military-medicine_en_2024-06.zim`.
  - One partial ZIM exists: `.gutenberg_en_all_2023-08.zim.5pDJqr`.
  - Remaining large ZIM payload should be copied as a dedicated long-running job.

## Permission-Limited Content

The non-root session could not read protected service/database paths from the mounted root filesystem. These need a privileged copy if they are required:

- `awstats/`
- `dbdata/mongodb/`
- `gitea/data/`
- `gitea/indexers/`
- `gitea/log/`
- `pgsql-iiab/`

The public content import continued despite these permission warnings.

## Resume Commands

Default practical resume, excluding large maps, ZIM payload, and backup duplicates:

```bash
cd /mnt/usb/GUIDE
./scripts/import-iiab-library.sh
```

Include ZIM files as a long-running job:

```bash
cd /mnt/usb/GUIDE
INCLUDE_ZIMS=true ./scripts/import-iiab-library.sh
```

Include the offline map database as a long-running job:

```bash
cd /mnt/usb/GUIDE
INCLUDE_MAPS=true ./scripts/import-iiab-library.sh
```

Include backup duplicate content:

```bash
cd /mnt/usb/GUIDE
INCLUDE_BACKUPS=true ./scripts/import-iiab-library.sh
```

## Notes

The USB filesystem is exFAT, so Linux ownership, permissions, and symlinks are not preserved. The import dereferences symlinks and copies file contents for portable access.
