# GUIDE Path Reservation Report

Generated: 2026-06-27

## Summary

T015 is complete. The reserved GUIDE path exists and is now actively used by profile, inventory, incident, communications, and situational awareness stores.

## Evidence

- GUIDE data root: `data/guide`
- Lightweight WebUI: `scripts/guide-webui.py`
- WebUI frontend: `data/guide_webui/index.html`
- Service metadata: `config/services.json`
- GUIDE platform documentation:
  - `reports/guide_product_vision.md`
  - `reports/household_profile_schema_report.md`
  - `reports/inventory_schema_report.md`
  - `reports/incident_records_report.md`
  - `reports/communications_center_report.md`
  - `reports/situational_awareness_report.md`

## Notes

The original T015 backlog item asked to reserve the GUIDE path and update service metadata when GUIDE services were introduced. That condition is now satisfied by the implemented `data/guide` stores and `guide-*` service entries.
