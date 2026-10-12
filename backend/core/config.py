"""
CivicAgent v3.0 — Application Configuration
Centralizes all environment-driven settings.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ── AI Settings ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
AI_ENABLED     = bool(OPENAI_API_KEY)

# ── App Settings ───────────────────────────────────────────
APP_NAME       = "CivicAgent"
APP_VERSION    = "3.0.0"
MAX_UPLOAD_MB  = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_RETRIES    = int(os.getenv("AGENT_MAX_RETRIES", "2"))

# ── Logging ────────────────────────────────────────────────
LOG_LEVEL      = os.getenv("LOG_LEVEL", "INFO").upper()
