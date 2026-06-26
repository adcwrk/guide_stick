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
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "data" / "guide_webui"
LIBRARY_DIR = ROOT / "library" / "iiab"
CHROMA_DIR = ROOT / "data" / "chroma" / "library"
PYTHON_PACKAGES = ROOT / "data" / "rag" / "python-packages"
PROFILE_DIR = ROOT / "data" / "guide" / "profile"
PROFILE_SCHEMA_PATH = PROFILE_DIR / "household_profile.schema.json"
PROFILE_EXAMPLE_PATH = PROFILE_DIR / "household_profile.example.json"
PROFILE_DATA_PATH = Path(os.environ.get("GUIDE_PROFILE_PATH") or PROFILE_DIR / "household_profile.json")
INVENTORY_DIR = ROOT / "data" / "guide" / "inventory"
INVENTORY_SCHEMA_PATH = INVENTORY_DIR / "inventory.schema.json"
INVENTORY_EXAMPLE_PATH = INVENTORY_DIR / "inventory.example.json"
INVENTORY_DATA_PATH = Path(os.environ.get("GUIDE_INVENTORY_PATH") or INVENTORY_DIR / "inventory.json")
INCIDENT_DIR = ROOT / "data" / "guide" / "incidents"
INCIDENT_SCHEMA_PATH = INCIDENT_DIR / "incidents.schema.json"
INCIDENT_EXAMPLE_PATH = INCIDENT_DIR / "incidents.example.json"
INCIDENT_DATA_PATH = Path(os.environ.get("GUIDE_INCIDENTS_PATH") or INCIDENT_DIR / "incidents.json")
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


def load_profile_schema():
    return json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))


def profile_template():
    return json.loads(PROFILE_EXAMPLE_PATH.read_text(encoding="utf-8"))


def profile_status():
    return {
        "schema": str(PROFILE_SCHEMA_PATH),
        "example": str(PROFILE_EXAMPLE_PATH),
        "path": str(PROFILE_DATA_PATH),
        "exists": PROFILE_DATA_PATH.exists(),
    }


def load_profile():
    if PROFILE_DATA_PATH.exists():
        return json.loads(PROFILE_DATA_PATH.read_text(encoding="utf-8"))
    return profile_template()


def validate_profile(profile):
    errors = []
    if not isinstance(profile, dict):
        return ["profile must be a JSON object"]
    required = [
        "schema_version",
        "profile_type",
        "household",
        "people",
        "pets",
        "medical",
        "power",
        "mobility",
        "communications",
        "preparedness_goals",
    ]
    for key in required:
        if key not in profile:
            errors.append(f"missing required field: {key}")
    if profile.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if profile.get("profile_type") not in ("household", "organization"):
        errors.append("profile_type must be household or organization")
    household = profile.get("household")
    if isinstance(household, dict):
        for key in ("name", "location_label", "primary_language", "planning_horizon_days"):
            if key not in household:
                errors.append(f"missing household field: {key}")
        horizon = household.get("planning_horizon_days")
        if not isinstance(horizon, int) or horizon < 1 or horizon > 365:
            errors.append("household.planning_horizon_days must be an integer from 1 to 365")
    elif "household" in profile:
        errors.append("household must be an object")
    for key in ("people", "pets", "preparedness_goals"):
        if key in profile and not isinstance(profile[key], list):
            errors.append(f"{key} must be an array")
    for key in ("medical", "power", "mobility", "communications"):
        if key in profile and not isinstance(profile[key], dict):
            errors.append(f"{key} must be an object")
    return errors


def save_profile(profile):
    errors = validate_profile(profile)
    if errors:
        return errors
    profile["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    PROFILE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = PROFILE_DATA_PATH.with_suffix(PROFILE_DATA_PATH.suffix + ".tmp")
    tmp_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(PROFILE_DATA_PATH)
    return []


def load_inventory_schema():
    return json.loads(INVENTORY_SCHEMA_PATH.read_text(encoding="utf-8"))


def inventory_template():
    return json.loads(INVENTORY_EXAMPLE_PATH.read_text(encoding="utf-8"))


def inventory_status():
    return {
        "schema": str(INVENTORY_SCHEMA_PATH),
        "example": str(INVENTORY_EXAMPLE_PATH),
        "path": str(INVENTORY_DATA_PATH),
        "exists": INVENTORY_DATA_PATH.exists(),
    }


def load_inventory():
    if INVENTORY_DATA_PATH.exists():
        return json.loads(INVENTORY_DATA_PATH.read_text(encoding="utf-8"))
    return inventory_template()


def validate_inventory(inventory):
    errors = []
    if not isinstance(inventory, dict):
        return ["inventory must be a JSON object"]
    for key in ("schema_version", "updated_at", "items", "notes"):
        if key not in inventory:
            errors.append(f"missing required field: {key}")
    if inventory.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    items = inventory.get("items")
    if not isinstance(items, list):
        errors.append("items must be an array")
        return errors
    allowed_categories = {
        "water", "food", "medical", "medication", "fuel", "power",
        "communications", "shelter", "sanitation", "tools", "other",
    }
    required_item_fields = ("id", "category", "name", "quantity", "unit", "location", "priority", "notes")
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{idx}] must be an object")
            continue
        for key in required_item_fields:
            if key not in item:
                errors.append(f"items[{idx}] missing required field: {key}")
        if item.get("category") not in allowed_categories:
            errors.append(f"items[{idx}].category is invalid")
        quantity = item.get("quantity")
        if not isinstance(quantity, (int, float)) or quantity < 0:
            errors.append(f"items[{idx}].quantity must be a non-negative number")
    return errors


def save_inventory(inventory):
    errors = validate_inventory(inventory)
    if errors:
        return errors
    inventory["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    INVENTORY_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = INVENTORY_DATA_PATH.with_suffix(INVENTORY_DATA_PATH.suffix + ".tmp")
    tmp_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(INVENTORY_DATA_PATH)
    return []


def load_incidents_schema():
    return json.loads(INCIDENT_SCHEMA_PATH.read_text(encoding="utf-8"))


def incidents_template():
    return json.loads(INCIDENT_EXAMPLE_PATH.read_text(encoding="utf-8"))


def incidents_status():
    return {
        "schema": str(INCIDENT_SCHEMA_PATH),
        "example": str(INCIDENT_EXAMPLE_PATH),
        "path": str(INCIDENT_DATA_PATH),
        "exists": INCIDENT_DATA_PATH.exists(),
    }


def load_incidents():
    if INCIDENT_DATA_PATH.exists():
        return json.loads(INCIDENT_DATA_PATH.read_text(encoding="utf-8"))
    return incidents_template()


def validate_incidents(incidents_doc):
    errors = []
    if not isinstance(incidents_doc, dict):
        return ["incidents must be a JSON object"]
    for key in ("schema_version", "updated_at", "incidents", "notes"):
        if key not in incidents_doc:
            errors.append(f"missing required field: {key}")
    if incidents_doc.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    incidents = incidents_doc.get("incidents")
    if not isinstance(incidents, list):
        errors.append("incidents must be an array")
        return errors
    allowed_types = {
        "medical", "power_outage", "severe_weather", "wildfire", "flood",
        "search_and_rescue", "communications_failure", "evacuation", "security", "other",
    }
    allowed_statuses = {"monitoring", "active", "stabilized", "resolved", "closed"}
    allowed_severities = {"low", "medium", "high", "critical"}
    allowed_event_types = {
        "observation", "decision", "action", "communication",
        "resource_update", "status_change", "note",
    }
    required_incident_fields = (
        "id", "title", "incident_type", "status", "severity", "started_at",
        "location", "summary", "objectives", "resources", "timeline",
        "documents", "recommendations", "notes",
    )
    for idx, incident in enumerate(incidents):
        if not isinstance(incident, dict):
            errors.append(f"incidents[{idx}] must be an object")
            continue
        for key in required_incident_fields:
            if key not in incident:
                errors.append(f"incidents[{idx}] missing required field: {key}")
        if incident.get("incident_type") not in allowed_types:
            errors.append(f"incidents[{idx}].incident_type is invalid")
        if incident.get("status") not in allowed_statuses:
            errors.append(f"incidents[{idx}].status is invalid")
        if incident.get("severity") not in allowed_severities:
            errors.append(f"incidents[{idx}].severity is invalid")
        if "location" in incident and not isinstance(incident["location"], dict):
            errors.append(f"incidents[{idx}].location must be an object")
        for key in ("objectives", "resources", "timeline", "documents", "recommendations"):
            if key in incident and not isinstance(incident[key], list):
                errors.append(f"incidents[{idx}].{key} must be an array")
        for event_idx, event in enumerate(incident.get("timeline") or []):
            if not isinstance(event, dict):
                errors.append(f"incidents[{idx}].timeline[{event_idx}] must be an object")
                continue
            for key in ("id", "timestamp", "event_type", "summary", "source", "actions_taken"):
                if key not in event:
                    errors.append(f"incidents[{idx}].timeline[{event_idx}] missing required field: {key}")
            if event.get("event_type") not in allowed_event_types:
                errors.append(f"incidents[{idx}].timeline[{event_idx}].event_type is invalid")
            if "actions_taken" in event and not isinstance(event["actions_taken"], list):
                errors.append(f"incidents[{idx}].timeline[{event_idx}].actions_taken must be an array")
    return errors


def save_incidents(incidents_doc):
    errors = validate_incidents(incidents_doc)
    if errors:
        return errors
    incidents_doc["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    INCIDENT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = INCIDENT_DATA_PATH.with_suffix(INCIDENT_DATA_PATH.suffix + ".tmp")
    tmp_path.write_text(json.dumps(incidents_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(INCIDENT_DATA_PATH)
    return []


def summarize_incidents(incidents_doc):
    incidents = incidents_doc.get("incidents") if isinstance(incidents_doc, dict) else []
    if not isinstance(incidents, list):
        incidents = []
    by_status = {}
    by_severity = {}
    by_type = {}
    timeline = []
    for incident in incidents:
        if not isinstance(incident, dict):
            continue
        status = incident.get("status") or "unknown"
        severity = incident.get("severity") or "unknown"
        incident_type = incident.get("incident_type") or "unknown"
        by_status[status] = by_status.get(status, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[incident_type] = by_type.get(incident_type, 0) + 1
        for event in incident.get("timeline") or []:
            if not isinstance(event, dict):
                continue
            timeline.append({
                "incident_id": incident.get("id") or "",
                "incident_title": incident.get("title") or "",
                "timestamp": event.get("timestamp") or "",
                "event_type": event.get("event_type") or "",
                "summary": event.get("summary") or "",
                "source": event.get("source") or "",
            })
    timeline.sort(key=lambda item: item["timestamp"], reverse=True)
    return {
        "total_incidents": len(incidents),
        "open_incidents": sum(by_status.get(key, 0) for key in ("monitoring", "active", "stabilized")),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_type": by_type,
        "timeline_events": len(timeline),
        "latest_timeline": timeline[:8],
    }


def household_people_count(profile):
    people = profile.get("people") if isinstance(profile, dict) else []
    if isinstance(people, list) and people:
        return len(people)
    return 1


def household_pet_count(profile):
    pets = profile.get("pets") if isinstance(profile, dict) else []
    if not isinstance(pets, list):
        return 0
    total = 0
    for pet in pets:
        if isinstance(pet, dict):
            total += int(pet.get("count") or 0)
    return total


def planning_horizon_days(profile):
    household = profile.get("household") if isinstance(profile, dict) else {}
    days = household.get("planning_horizon_days") if isinstance(household, dict) else None
    return days if isinstance(days, int) and days > 0 else 14


def inventory_quantity(item, factor_key, default_units):
    quantity = item.get("quantity") or 0
    factor = item.get(factor_key)
    if isinstance(factor, (int, float)) and factor > 0:
        return quantity * factor
    if item.get("unit") in default_units:
        return quantity
    return 0


def calculate_inventory(profile, inventory):
    items = inventory.get("items") if isinstance(inventory, dict) else []
    if not isinstance(items, list):
        items = []
    people = household_people_count(profile)
    pets = household_pet_count(profile)
    days = planning_horizon_days(profile)
    water_required = (people * 1.0 + pets * 0.25) * days
    food_required = people * 2000 * days
    water_available = 0.0
    food_calories = 0.0
    power_wh = 0.0
    medication_inventory = {}
    category_counts = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        category = item.get("category") or "other"
        category_counts[category] = category_counts.get(category, 0) + 1
        if category == "water":
            water_available += inventory_quantity(item, "gallons_per_unit", {"gallon"})
            if item.get("unit") == "liter":
                water_available += (item.get("quantity") or 0) * 0.264172
        elif category == "food":
            if isinstance(item.get("calories_per_unit"), (int, float)):
                food_calories += (item.get("quantity") or 0) * item["calories_per_unit"]
            elif item.get("unit") == "calorie":
                food_calories += item.get("quantity") or 0
        elif category == "power":
            power_wh += inventory_quantity(item, "watt_hours_per_unit", {"watt_hour"})
            if item.get("unit") == "kilowatt_hour":
                power_wh += (item.get("quantity") or 0) * 1000
        elif category == "medication":
            key = (item.get("person_id") or "", item.get("name") or "")
            medication_inventory[key] = max(medication_inventory.get(key, 0), item.get("days_on_hand") or 0)

    critical_loads = (((profile.get("power") or {}).get("critical_loads") or []) if isinstance(profile, dict) else [])
    daily_wh = 0.0
    for load in critical_loads:
        if isinstance(load, dict):
            daily_wh += (load.get("watts") or 0) * (load.get("hours_per_day") or 0)

    gaps = []
    def add_gap(category, severity, message, required, available, unit):
        gaps.append({
            "category": category,
            "severity": severity,
            "message": message,
            "required": round(required, 2),
            "available": round(available, 2),
            "shortfall": round(max(required - available, 0), 2),
            "unit": unit,
        })

    if water_available < water_required:
        severity = "critical" if water_available < water_required * 0.5 else "high"
        add_gap("water", severity, "Stored water is below the planning target.", water_required, water_available, "gallons")
    if food_calories < food_required:
        severity = "critical" if food_calories < food_required * 0.5 else "high"
        add_gap("food", severity, "Food calories are below the planning target.", food_required, food_calories, "calories")

    medications = (((profile.get("medical") or {}).get("medications") or []) if isinstance(profile, dict) else [])
    for med in medications:
        if not isinstance(med, dict):
            continue
        key = (med.get("person_id") or "", med.get("name") or "")
        profile_days = med.get("days_on_hand") or 0
        inventory_days = medication_inventory.get(key, 0)
        available_days = max(profile_days, inventory_days)
        if available_days < days:
            gaps.append({
                "category": "medication",
                "severity": "critical",
                "message": f"Medication supply below target: {med.get('name') or 'unnamed medication'}",
                "required": days,
                "available": available_days,
                "shortfall": round(days - available_days, 2),
                "unit": "days",
            })

    power_days = power_wh / daily_wh if daily_wh > 0 else None
    if daily_wh > 0 and power_days < days:
        gaps.append({
            "category": "power",
            "severity": "high" if power_days and power_days >= 1 else "critical",
            "message": "Backup power is below the critical load planning target.",
            "required": round(daily_wh * days, 2),
            "available": round(power_wh, 2),
            "shortfall": round(max(daily_wh * days - power_wh, 0), 2),
            "unit": "watt_hours",
        })

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda item: (severity_order.get(item["severity"], 9), item["category"]))
    return {
        "profile_context": {
            "people": people,
            "pets": pets,
            "planning_horizon_days": days,
        },
        "requirements": {
            "water_gallons": round(water_required, 2),
            "food_calories": round(food_required, 2),
            "critical_power_watt_hours": round(daily_wh * days, 2),
        },
        "available": {
            "water_gallons": round(water_available, 2),
            "food_calories": round(food_calories, 2),
            "power_watt_hours": round(power_wh, 2),
        },
        "duration_days": {
            "water": round(water_available / (people * 1.0 + pets * 0.25), 2) if people or pets else None,
            "food": round(food_calories / (people * 2000), 2) if people else None,
            "power": round(power_days, 2) if power_days is not None else None,
        },
        "category_counts": category_counts,
        "gaps": gaps,
    }


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
        "profile": profile_status(),
        "inventory": inventory_status(),
        "incidents": incidents_status(),
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

        if self.path == "/api/profile":
            try:
                profile = load_profile()
                self.send_json(200, {
                    "profile": profile,
                    "schema": load_profile_schema(),
                    "status": profile_status(),
                    "validation_errors": validate_profile(profile),
                })
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})
            return

        if self.path == "/api/inventory":
            try:
                profile = load_profile()
                inventory = load_inventory()
                self.send_json(200, {
                    "inventory": inventory,
                    "schema": load_inventory_schema(),
                    "status": inventory_status(),
                    "validation_errors": validate_inventory(inventory),
                    "calculations": calculate_inventory(profile, inventory),
                })
            except Exception as exc:
                self.send_json(500, {"error": str(exc)})
            return

        if self.path == "/api/incidents":
            try:
                incidents_doc = load_incidents()
                self.send_json(200, {
                    "incidents": incidents_doc,
                    "schema": load_incidents_schema(),
                    "status": incidents_status(),
                    "validation_errors": validate_incidents(incidents_doc),
                    "summary": summarize_incidents(incidents_doc),
                })
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

        if self.path not in ("/api/chat", "/api/ask-library", "/api/profile", "/api/inventory", "/api/incidents"):
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/api/inventory":
                inventory = incoming.get("inventory") if isinstance(incoming, dict) and "inventory" in incoming else incoming
                errors = save_inventory(inventory)
                if errors:
                    self.send_json(400, {"error": "inventory validation failed", "validation_errors": errors})
                    return
                saved = load_inventory()
                self.send_json(200, {
                    "inventory": saved,
                    "status": inventory_status(),
                    "validation_errors": [],
                    "calculations": calculate_inventory(load_profile(), saved),
                })
            elif self.path == "/api/incidents":
                incidents_doc = incoming.get("incidents") if isinstance(incoming, dict) and "incidents" in incoming else incoming
                errors = save_incidents(incidents_doc)
                if errors:
                    self.send_json(400, {"error": "incidents validation failed", "validation_errors": errors})
                    return
                saved = load_incidents()
                self.send_json(200, {
                    "incidents": saved,
                    "status": incidents_status(),
                    "validation_errors": [],
                    "summary": summarize_incidents(saved),
                })
            elif self.path == "/api/profile":
                profile = incoming.get("profile") if isinstance(incoming, dict) and "profile" in incoming else incoming
                errors = save_profile(profile)
                if errors:
                    self.send_json(400, {"error": "profile validation failed", "validation_errors": errors})
                    return
                self.send_json(200, {
                    "profile": load_profile(),
                    "status": profile_status(),
                    "validation_errors": [],
                })
            elif self.path == "/api/ask-library":
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
