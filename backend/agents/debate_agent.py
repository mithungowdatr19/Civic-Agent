import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DebateAgent(BaseAgent):
    def __init__(self):
        super().__init__("Multi-Agent Debate")

    def execute(self, data):
        prompt = """You are a debate coordinator for civic issue agents.
Create a concise debate between two viewpoints using the evidence supplied.
Return ONLY JSON:
position_a, position_b, consensus, unresolved_questions, debate_confidence_0_to_1."""
        user = f"""Vision: {data.get('vision',{})}
Research: {data.get('research',{})}
Safety: {data.get('safety',{})}"""

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[DebateAgent] AI unavailable, using contextual fallback. Reason: %s", exc)

        # ── Deterministic contextual fallback ────────────────────────
        vision = data.get("vision", {})
        issue = str(vision.get("issue", "")).lower()
        category = str(vision.get("category", "")).lower()

        if "road" in issue or "pothole" in issue or "infrastructure" in category:
            return {
                "position_a": "Prioritize rapid emergency hot-mix / cold-mix pothole sealing within 24 hours to prevent immediate vehicle tire blowouts, bike skids, and traffic gridlocks.",
                "position_b": "Advocate comprehensive pavement milling and stormwater culvert grading to prevent water seepage from breaking the road substrate repeatedly.",
                "consensus": "Execute emergency asphalt patch immediately to protect public safety, while scheduling ward road division for structural resurfacing and edge drainage inspection.",
                "unresolved_questions": ["Subsurface water pipe integrity underneath the crater", "Clarification on municipal ward vs. state highway arterial jurisdiction"],
                "debate_confidence_0_to_1": 0.88
            }
        elif "garbage" in issue or "waste" in issue or "sanitation" in category:
            return {
                "position_a": "Immediate deployment of compactor truck and health inspection squad to eliminate disease vector risks.",
                "position_b": "Address systemic root cause by installing designated waste bins, street signage, and citizen monitoring to halt recurrent midnight dumping.",
                "consensus": "Execute emergency spot sanitation clearance within 12 hours, followed by ward health inspector notices and scheduled twice-daily collection rounds.",
                "unresolved_questions": ["Commercial bulk generators nearby lacking licensed disposal", "Night patrol feasibility in the perimeter"],
                "debate_confidence_0_to_1": 0.85
            }
        elif "water" in issue or "drainage" in issue or "flood" in issue:
            return {
                "position_a": "Immediate suction tankers and dewatering pumps required to clear standing water from road corridors and pedestrian pathways.",
                "position_b": "Inspect downstream arterial stormwater drains and remove blockages/plastic waste rather than treating surface symptoms.",
                "consensus": "Deploy immediate mobile dewatering pump to restore vehicular passage, coupled with emergency desilting of connecting roadside drain chambers.",
                "unresolved_questions": ["Downstream canal discharge capacity", "Presence of cross-utility cable trenching obstructing flow"],
                "debate_confidence_0_to_1": 0.86
            }
        elif "light" in issue or "electricity" in category or "street" in issue:
            return {
                "position_a": "Fast-track replacement of failed luminaires and faulty circuit breakers to prevent dark zones and anti-social hazards.",
                "position_b": "Inspect junction feeder box and underground cable continuity to prevent repeated power surges tripping the phase.",
                "consensus": "Deploy ward electrical utility lineman for immediate fixture check and phase balancing within 24 hours.",
                "unresolved_questions": ["Availability of automated timer or smart feeder controller", "Tree foliage obstructing light throw"],
                "debate_confidence_0_to_1": 0.83
            }
        else:
            return {
                "position_a": "Prioritize immediate site investigation and safety barrier placement to minimize civic exposure.",
                "position_b": "Ensure proper jurisdictional ownership and statutory notices before assigning specialized municipal machinery.",
                "consensus": "Issue provisional high-priority notice to ward junior engineer for on-site inspection while logging complaint into central municipal portal.",
                "unresolved_questions": ["Exact ward boundary demarcations", "Applicable departmental capital budget allocation"],
                "debate_confidence_0_to_1": 0.82
            }
