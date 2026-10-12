import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SafetyAgent(BaseAgent):
    def __init__(self):
        super().__init__("Safety & Impact Agent")

    def execute(self, data):
        prompt = """You are the CivicAgent Safety & Impact Agent.
Assess public safety, urgency, affected groups and possible consequences.
Return ONLY JSON:
risk_level, risk_score_0_to_100, affected_groups, hazards,
urgency, reasoning, confidence_0_to_1."""
        user = f"Vision assessment: {data.get('vision',{})}\nDescription: {data.get('description','')}"

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[SafetyAgent] AI unavailable, using fallback. Reason: %s", exc)

        # ── Deterministic fallback ────────────────────────
        severity = int(data.get("vision", {}).get("severity_1_to_10", 6))
        score    = min(100, severity * 10 + 5)
        category = str(data.get("vision", {}).get("category", "")).lower()
        issue    = str(data.get("vision", {}).get("issue", "")).lower()

        if "road" in issue or "pothole" in issue:
            return {"risk_level": "HIGH" if score >= 75 else "MEDIUM",
                    "risk_score_0_to_100": score,
                    "affected_groups": ["drivers", "motorcyclists", "cyclists", "pedestrians"],
                    "hazards": ["vehicle collision", "tyre burst", "loss of vehicle control", "pedestrian injury"],
                    "urgency": "High",
                    "reasoning": "Road defects create immediate safety risks for all road users, especially two-wheelers.",
                    "confidence_0_to_1": 0.87}
        if "garbage" in issue or "sanitation" in category:
            return {"risk_level": "MEDIUM",
                    "risk_score_0_to_100": max(score, 60),
                    "affected_groups": ["residents", "children", "elderly", "animals"],
                    "hazards": ["disease spread", "vector breeding", "air pollution", "contamination"],
                    "urgency": "Medium",
                    "reasoning": "Uncollected garbage creates public health hazards and disease vectors.",
                    "confidence_0_to_1": 0.82}
        if "water" in issue or "drainage" in issue or "flood" in issue:
            return {"risk_level": "HIGH",
                    "risk_score_0_to_100": max(score, 70),
                    "affected_groups": ["pedestrians", "residents", "motorists", "children"],
                    "hazards": ["drowning risk", "waterborne disease", "property damage", "road damage"],
                    "urgency": "High",
                    "reasoning": "Waterlogging poses serious risks to safety and public health.",
                    "confidence_0_to_1": 0.85}
        return {"risk_level": "HIGH" if score >= 75 else "MEDIUM",
                "risk_score_0_to_100": score,
                "affected_groups": ["residents", "commuters", "pedestrians"],
                "hazards": ["public inconvenience", "safety risk", "property damage"],
                "urgency": "Medium",
                "reasoning": "Civic issue poses moderate public safety risk.",
                "confidence_0_to_1": 0.75}
