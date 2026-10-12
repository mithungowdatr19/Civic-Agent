import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Decision Agent")

    def execute(self, data):
        prompt = """You are the CivicAgent Decision Agent.
Combine vision, research, safety and debate into a final decision.
Return ONLY JSON:
priority, priority_score_0_to_100, authority, department,
confidence_0_to_1, rationale, recommended_sla."""
        user = f"""Vision: {data.get('vision',{})}
Research: {data.get('research',{})}
Safety: {data.get('safety',{})}
Debate: {data.get('debate',{})}"""

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[DecisionAgent] AI unavailable, using contextual fallback. Reason: %s", exc)

        # ── Deterministic contextual calculation ────────────────────────
        vision = data.get("vision", {})
        safety = data.get("safety", {})
        research = data.get("research", {})

        severity = int(vision.get("severity_1_to_10", 6))
        risk_score = int(safety.get("risk_score_0_to_100", 60))

        # Weighted calculation: 45% visual severity, 45% public safety risk, 10% base
        score = round((severity * 10 * 0.45) + (risk_score * 0.45) + 10)
        score = max(20, min(100, score))

        if score >= 85:
            priority = "CRITICAL"
            sla = "12 - 24 hours"
        elif score >= 65:
            priority = "HIGH"
            sla = "24 - 48 hours"
        elif score >= 45:
            priority = "MEDIUM"
            sla = "3 - 5 business days"
        else:
            priority = "LOW"
            sla = "5 - 7 business days"

        authority = research.get("authority") or "Municipal City Corporation"
        department = research.get("department") or "Public Works & Infrastructure"

        rationale = (
            f"Evaluated with priority score of {score}/100. Observed defect severity ({severity}/10) "
            f"and public hazard risk ({risk_score}/100) indicate {priority.lower()} civic exposure. "
            f"Assigned to {authority} under {department} with mandatory SLA of {sla}."
        )

        return {
            "priority": priority,
            "priority_score_0_to_100": score,
            "authority": authority,
            "department": department,
            "confidence_0_to_1": round(min(0.96, max(0.75, (severity * 0.05 + 0.45))), 2),
            "rationale": rationale,
            "recommended_sla": sla
        }
