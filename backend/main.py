"""
CivicAgent v3.0 — Application-Level Backend
FastAPI server with case persistence, analytics API, and enhanced routing.
"""
import json
import os
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.agents.orchestrator import Orchestrator

load_dotenv(override=True)

# ── Paths ──────────────────────────────────────────────────
BASE     = Path(__file__).resolve().parent.parent
FRONTEND = BASE / "frontend"
UPLOADS  = BASE / "uploads"
DATA     = BASE / "data"
CASES_DB = DATA / "cases.json"

UPLOADS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

# ── Helpers ────────────────────────────────────────────────
def load_cases() -> list:
    if not CASES_DB.exists() or CASES_DB.stat().st_size == 0:
        return []
    try:
        return json.loads(CASES_DB.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_case(case: dict) -> None:
    cases = load_cases()
    # Update if exists, else append
    idx = next((i for i, c in enumerate(cases) if c.get("case_id") == case.get("case_id")), None)
    if idx is not None:
        cases[idx] = case
    else:
        cases.append(case)
    CASES_DB.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")


def build_analytics(cases: list) -> dict:
    priority_counts: dict = defaultdict(int)
    category_counts: dict = defaultdict(int)
    authority_counts: dict = defaultdict(int)
    department_counts: dict = defaultdict(int)
    risk_scores: list = []
    timeline: dict = defaultdict(int)

    for c in cases:
        dec    = c.get("decision") or {}
        agents = c.get("agents")   or {}
        vis    = agents.get("vision") or {}
        saf    = agents.get("safety") or {}

        # Priority
        p = (dec.get("priority") or "UNKNOWN").upper()
        priority_counts[p] += 1

        # Category
        cat = vis.get("category") or "Other"
        category_counts[cat] += 1

        # Authority
        auth = dec.get("authority") or "Unknown"
        authority_counts[auth] += 1

        # Department
        dept = dec.get("department") or "Unknown"
        department_counts[dept] += 1

        # Risk score
        rs = saf.get("risk_score_0_to_100")
        if rs is not None:
            risk_scores.append(int(rs))

        # Timeline (by date)
        ts = c.get("timestamp")
        if ts:
            from datetime import datetime
            try:
                dt = datetime.fromtimestamp(ts)
                key = f"{dt.month}/{dt.day}"
                timeline[key] += 1
            except Exception:
                pass

    # Build risk distribution buckets
    risk_distribution = [
        {"bucket": "0-25",   "count": sum(1 for s in risk_scores if s <= 25)},
        {"bucket": "26-50",  "count": sum(1 for s in risk_scores if 25 < s <= 50)},
        {"bucket": "51-75",  "count": sum(1 for s in risk_scores if 50 < s <= 75)},
        {"bucket": "76-100", "count": sum(1 for s in risk_scores if s > 75)},
    ]

    # Timeline sorted
    tl_sorted = [{"date": k, "count": v} for k, v in sorted(timeline.items(), key=lambda x: x[0])]

    avg_score = None
    all_scores = [
        c.get("decision", {}).get("priority_score_0_to_100")
        for c in cases
        if c.get("decision", {}).get("priority_score_0_to_100") is not None
    ]
    if all_scores:
        avg_score = round(sum(all_scores) / len(all_scores), 1)

    return {
        "total_cases":        len(cases),
        "priority_counts":    dict(priority_counts),
        "category_counts":    dict(category_counts),
        "authority_counts":   dict(authority_counts),
        "department_counts":  dict(department_counts),
        "risk_distribution":  risk_distribution,
        "timeline":           tl_sorted,
        "avg_priority_score": avg_score,
        "total_critical":     priority_counts.get("CRITICAL", 0),
        "total_high":         priority_counts.get("HIGH", 0),
    }


# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="CivicAgent",
    version="3.0.0",
    description="Autonomous Civic Intelligence Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")

orchestrator = Orchestrator()


# ── Routes ─────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health():
    ai_live = orchestrator.vision.ai.enabled and orchestrator.vision.ai.is_available()
    return {
        "status":        "online",
        "version":       "3.0.0",
        "ai_configured": ai_live,
        "mode":          "Live AI" if ai_live else "Civic Intelligence Engine",
        "model":         os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        "total_cases":   len(load_cases()),
    }


@app.post("/api/analyze")
async def analyze(
    description: str       = Form(...),
    location:    str       = Form(""),
    image:       Optional[UploadFile] = File(None),
):
    """Run the 6-agent pipeline and persist the resulting case."""
    if not description.strip():
        raise HTTPException(status_code=422, detail="Description is required.")

    # Save uploaded image
    image_name = ""
    if image and image.filename:
        ext       = Path(image.filename).suffix.lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        image_name = safe_name
        content   = await image.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image must be under 10 MB.")
        (UPLOADS / safe_name).write_bytes(content)

    try:
        result              = orchestrator.analyze(description.strip(), location.strip(), image_name)
        result["timestamp"] = int(time.time())
        result["description"] = description.strip()
        result["location"]    = location.strip()
        result["image_name"]  = image_name

        # Persist case
        save_case(result)

        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/cases")
def get_cases(
    priority: Optional[str] = None,
    limit:    int = 100,
    offset:   int = 0,
):
    """Return all persisted cases, optionally filtered by priority."""
    cases = load_cases()
    if priority:
        cases = [c for c in cases if (c.get("decision") or {}).get("priority", "").upper() == priority.upper()]
    total  = len(cases)
    paged  = cases[offset: offset + limit]
    return JSONResponse({"cases": paged, "total": total, "limit": limit, "offset": offset})


@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    """Return a single case by ID."""
    cases = load_cases()
    case  = next((c for c in cases if c.get("case_id") == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return JSONResponse(case)


@app.delete("/api/cases/{case_id}")
def delete_case(case_id: str):
    """Delete a case by ID."""
    cases = load_cases()
    new_cases = [c for c in cases if c.get("case_id") != case_id]
    if len(new_cases) == len(cases):
        raise HTTPException(status_code=404, detail="Case not found.")
    CASES_DB.write_text(json.dumps(new_cases, indent=2, ensure_ascii=False), encoding="utf-8")
    return JSONResponse({"deleted": case_id})


@app.get("/api/analytics")
def analytics():
    """Return aggregated analytics over all cases."""
    cases = load_cases()
    return JSONResponse(build_analytics(cases))


@app.get("/api/stats")
def stats():
    """Lightweight stats endpoint for the overview page."""
    cases = load_cases()
    priorities = [(c.get("decision") or {}).get("priority", "UNKNOWN").upper() for c in cases]
    scores     = [(c.get("decision") or {}).get("priority_score_0_to_100") for c in cases if (c.get("decision") or {}).get("priority_score_0_to_100") is not None]
    return {
        "total":       len(cases),
        "critical":    priorities.count("CRITICAL"),
        "high":        priorities.count("HIGH"),
        "medium":      priorities.count("MEDIUM"),
        "avg_score":   round(sum(scores) / len(scores), 1) if scores else None,
        "ai_enabled":  orchestrator.vision.ai.enabled,
    }
