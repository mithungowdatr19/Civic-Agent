import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Vision Agent")

    def execute(self, data):
        prompt = """You are the CivicAgent Vision Agent.
Analyze the supplied civic issue description and image filename/context.
Return ONLY JSON with:
issue, category, objects_detected, visual_evidence, severity_1_to_10,
confidence_0_to_1, reasoning.
Do not invent precise facts not supported by the input."""
        user = f"Description: {data.get('description','')}\nImage: {data.get('image_name','none')}"

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[VisionAgent] AI unavailable, using fallback. Reason: %s", exc)

        # ── Deterministic fallback ────────────────────────
        text = data.get("description", "").lower()
        if any(x in text for x in ["pothole", "road", "crater", "highway", "street"]):
            return {"issue": "Pothole / damaged road", "category": "Infrastructure",
                    "objects_detected": ["road damage", "pothole"],
                    "visual_evidence": ["depression or damaged road surface"],
                    "severity_1_to_10": 8, "confidence_0_to_1": 0.88,
                    "reasoning": "Description indicates significant road damage."}
        if any(x in text for x in ["garbage", "waste", "dump", "trash", "litter"]):
            return {"issue": "Garbage / waste dumping", "category": "Sanitation",
                    "objects_detected": ["waste material", "garbage dump"],
                    "visual_evidence": ["visible waste accumulation"],
                    "severity_1_to_10": 7, "confidence_0_to_1": 0.85,
                    "reasoning": "Description indicates illegal waste dumping."}
        if any(x in text for x in ["water", "flood", "drainage", "drain", "sewage"]):
            return {"issue": "Drainage / flooding issue", "category": "Water & Drainage",
                    "objects_detected": ["water logging", "blocked drain"],
                    "visual_evidence": ["standing water", "overflow"],
                    "severity_1_to_10": 7, "confidence_0_to_1": 0.82,
                    "reasoning": "Description indicates a drainage or flooding problem."}
        if any(x in text for x in ["light", "streetlight", "lamp", "dark", "electricity"]):
            return {"issue": "Street light / electricity failure", "category": "Electricity",
                    "objects_detected": ["non-functional streetlight"],
                    "visual_evidence": ["no light output observed"],
                    "severity_1_to_10": 5, "confidence_0_to_1": 0.78,
                    "reasoning": "Description indicates a street lighting failure."}
        return {"issue": "Civic infrastructure issue", "category": "Public Services",
                "objects_detected": ["reported civic issue"],
                "visual_evidence": ["citizen-provided evidence"],
                "severity_1_to_10": 6, "confidence_0_to_1": 0.72,
                "reasoning": "Issue requires further civic assessment."}

