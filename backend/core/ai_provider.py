"""
CivicAgent v3.0 — AIProvider
Central AI gateway. Agents never call the SDK directly.
Features:
  - Fast timeout & circuit-breaker for quota exhaustion / auth errors
  - Automatic fallback mode when quota is depleted or key is invalid
  - Robust JSON parsing with multi-layer fallback
"""
import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError
from .config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


class AIProvider:
    """Thread-safe AI gateway with circuit-breaker protection."""

    # Class-level circuit breaker so all agents share quota status
    _circuit_open: bool = False
    _circuit_reason: str = ""

    def __init__(self):
        self.enabled = bool(OPENAI_API_KEY)
        self.model   = OPENAI_MODEL
        self.client  = (
            OpenAI(api_key=OPENAI_API_KEY, timeout=12)
            if self.enabled else None
        )
        if self.enabled:
            logger.info("AIProvider initialized with model=%s", self.model)
        else:
            logger.info("AIProvider running in architecture mode (no API key).")

    @classmethod
    def is_available(cls) -> bool:
        """Check if AI is enabled and circuit breaker is closed."""
        return bool(OPENAI_API_KEY) and not cls._circuit_open

    @classmethod
    def trip_circuit(cls, reason: str):
        cls._circuit_open = True
        cls._circuit_reason = reason
        logger.warning("[AIProvider] Circuit breaker tripped: %s", reason)

    # ── Public API ─────────────────────────────────────────
    def complete_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call the model and return a parsed JSON dict.
        Raises RuntimeError on failure or if circuit breaker is tripped.
        """
        if not self.enabled:
            raise RuntimeError("AI provider is not configured.")

        if self._circuit_open:
            raise RuntimeError(f"AI circuit open: {self._circuit_reason}")

        try:
            # Prefer chat completions for universal compatibility
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt},
                    ],
                    response_format={"type": "json_object"} if "gpt" in self.model else None,
                    temperature=0.2,
                )
                raw = response.choices[0].message.content.strip()
            except AttributeError:
                # Fallback to responses.create if older/custom SDK
                response = self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt},
                    ],
                )
                raw = response.output_text.strip()

            logger.debug("[AIProvider] raw response received (%d chars)", len(raw))
            return self._parse_json(raw)

        except AuthenticationError as e:
            self.trip_circuit("Invalid OpenAI API key")
            raise RuntimeError(f"Authentication failed: {e}")
        except RateLimitError as e:
            err_msg = str(e)
            if "insufficient_quota" in err_msg or "credit_balance_exhausted" in err_msg:
                self.trip_circuit("API credit balance exhausted")
            raise RuntimeError(f"Rate limit / Quota error: {e}")
        except APITimeoutError as e:
            raise RuntimeError(f"AI request timed out: {e}")
        except APIError as e:
            err_msg = str(e)
            if "insufficient_quota" in err_msg or "credit_balance_exhausted" in err_msg:
                self.trip_circuit("API credit balance exhausted")
            raise RuntimeError(f"AI API error: {e}")

    # ── Helpers ────────────────────────────────────────────
    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Parse JSON with multiple fallbacks."""
        # 1. Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Extract {...} block
        start = text.find("{")
        end   = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start: end + 1])
            except json.JSONDecodeError:
                pass

        # 3. Extract [...] block
        start = text.find("[")
        end   = text.rfind("]")
        if start >= 0 and end > start:
            try:
                return {"items": json.loads(text[start: end + 1])}
            except json.JSONDecodeError:
                pass

        raise ValueError(f"AI returned non-JSON text: {text[:200]!r}")
