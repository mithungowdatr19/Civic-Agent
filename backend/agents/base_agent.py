"""
CivicAgent v3.0 — BaseAgent
All specialized agents inherit from this. Provides:
  - run() with timing, error capture, and optional retry
  - execute() contract for subclasses
"""
import time
import logging
from typing import Any, Dict

from backend.core.ai_provider import AIProvider

logger = logging.getLogger(__name__)


class BaseAgent:
    """Abstract base for all CivicAgent specialized agents."""

    #: Override in subclasses to allow AI call retries on failure.
    max_retries: int = 1

    def __init__(self, name: str):
        self.name = name
        self.ai   = AIProvider()

    # ── Public API ─────────────────────────────────────────
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with timing and error handling."""
        started = time.perf_counter()
        attempt = 0
        last_exc: Exception | None = None

        while attempt < max(self.max_retries, 1):
            attempt += 1
            try:
                result = self.execute(input_data)
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                result["_meta"] = {
                    "agent":        self.name,
                    "status":       "completed",
                    "execution_ms": elapsed_ms,
                    "attempt":      attempt,
                }
                logger.debug("[%s] completed in %d ms (attempt %d)", self.name, elapsed_ms, attempt)
                return result
            except Exception as exc:
                last_exc = exc
                logger.warning("[%s] attempt %d failed: %s", self.name, attempt, exc)
                time.sleep(0.3 * attempt)  # brief back-off

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.error("[%s] all %d attempts failed. Last error: %s", self.name, attempt, last_exc)
        return {
            "_meta": {
                "agent":        self.name,
                "status":       "failed",
                "execution_ms": elapsed_ms,
                "attempts":     attempt,
                "error":        str(last_exc),
            }
        }

    # ── Subclass contract ──────────────────────────────────
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in each specialized agent."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")
