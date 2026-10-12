import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Agent")

    def execute(self, data):
        prompt = """You are the CivicAgent Research Agent.
Identify the likely responsible civic authority and relevant service category.
Return ONLY JSON:
authority, department, service_category, suggested_escalation,
confidence_0_to_1, reasoning."""
        user = f"Issue: {data.get('vision',{})}\nLocation: {data.get('location','')}"

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[ResearchAgent] AI unavailable, using fallback. Reason: %s", exc)

        # ── Deterministic fallback ────────────────────────
        issue = str(data.get("vision", {}).get("issue", "")).lower()
        category = str(data.get("vision", {}).get("category", "")).lower()

        if "pothole" in issue or "road" in issue or "infrastructure" in category:
            return {"authority": "Municipal Corporation / BBMP",
                    "department": "Roads & Public Works",
                    "service_category": "Road maintenance",
                    "suggested_escalation": "Ward-level road maintenance officer",
                    "confidence_0_to_1": 0.86,
                    "reasoning": "Road defects are handled by the local road/public works authority."}
        if "sanitation" in category or "garbage" in issue or "waste" in issue:
            return {"authority": "Municipal Corporation / Solid Waste Management",
                    "department": "Sanitation & Waste Management",
                    "service_category": "Solid waste collection",
                    "suggested_escalation": "Ward-level sanitation officer",
                    "confidence_0_to_1": 0.84,
                    "reasoning": "Garbage and waste issues are under municipal sanitation authority."}
        if "water" in issue or "drainage" in issue or "flood" in issue or "drainage" in category:
            return {"authority": "BWSSB / Municipal Water Authority",
                    "department": "Water & Drainage Board",
                    "service_category": "Drainage maintenance",
                    "suggested_escalation": "Drainage division engineer",
                    "confidence_0_to_1": 0.82,
                    "reasoning": "Drainage and flooding issues handled by water/drainage authority."}
        if "electricity" in category or "light" in issue or "streetlight" in issue:
            return {"authority": "BESCOM / State Electricity Board",
                    "department": "Street Lighting Division",
                    "service_category": "Street lighting maintenance",
                    "suggested_escalation": "Section lineman / electrical sub-division officer",
                    "confidence_0_to_1": 0.80,
                    "reasoning": "Street lighting is managed by the electricity distribution company."}
        return {"authority": "Local Municipal Civic Body",
                "department": "Public Services",
                "service_category": "Civic maintenance",
                "suggested_escalation": "Ward-level civic officer",
                "confidence_0_to_1": 0.70,
                "reasoning": "Generic civic maintenance routing selected."}
