"""
CivicAgent v3.0 — Orchestrator
Coordinates 6 specialized agents in a sequential pipeline,
collecting per-agent timing and metadata.
"""
import uuid
import time
from .vision_agent   import VisionAgent
from .research_agent import ResearchAgent
from .safety_agent   import SafetyAgent
from .debate_agent   import DebateAgent
from .decision_agent import DecisionAgent
from .action_agent   import ActionAgent


class Orchestrator:
    """Single-instance orchestrator; re-use across requests."""

    def __init__(self):
        self.vision   = VisionAgent()
        self.research = ResearchAgent()
        self.safety   = SafetyAgent()
        self.debate   = DebateAgent()
        self.decision = DecisionAgent()
        self.action   = ActionAgent()

    # ── helpers ───────────────────────────────────────────
    @staticmethod
    def _strip_meta(result: dict) -> dict:
        return {k: v for k, v in result.items() if k != "_meta"}

    @staticmethod
    def _run_timed(agent, data: dict) -> tuple:
        """Run an agent and return (result_dict, execution_ms)."""
        t0     = time.perf_counter()
        result = agent.run(data)
        ms     = int((time.perf_counter() - t0) * 1000)
        return result, ms

    # ── main pipeline ─────────────────────────────────────
    def analyze(self, description: str, location: str = "", image_name: str = "") -> dict:
        case_id   = "CA-" + uuid.uuid4().hex[:8].upper()
        pipeline_start = time.perf_counter()

        # Stage 1: Vision
        vision, t_vision = self._run_timed(
            self.vision,
            {"description": description, "location": location, "image_name": image_name},
        )
        vision_data = self._strip_meta(vision)

        # Stage 2: Research  (depends on vision)
        research, t_research = self._run_timed(
            self.research,
            {"vision": vision_data, "location": location},
        )
        research_data = self._strip_meta(research)

        # Stage 3: Safety  (depends on vision + description)
        safety, t_safety = self._run_timed(
            self.safety,
            {"vision": vision_data, "description": description},
        )
        safety_data = self._strip_meta(safety)

        # Stage 4: Debate  (depends on vision + research + safety)
        debate, t_debate = self._run_timed(
            self.debate,
            {"vision": vision_data, "research": research_data, "safety": safety_data},
        )
        debate_data = self._strip_meta(debate)

        # Stage 5: Decision  (depends on all previous stages)
        decision, t_decision = self._run_timed(
            self.decision,
            {
                "vision": vision_data, "research": research_data,
                "safety": safety_data,  "debate":   debate_data,
            },
        )
        decision_data = self._strip_meta(decision)

        # Stage 6: Action  (depends on vision + decision)
        action, t_action = self._run_timed(
            self.action,
            {
                "vision": vision_data, "decision": decision_data,
                "location": location,  "description": description,
            },
        )
        action_data = self._strip_meta(action)

        total_ms = int((time.perf_counter() - pipeline_start) * 1000)

        return {
            "case_id":  case_id,
            "ai_mode":  self.vision.ai.enabled,
            "pipeline": {
                "total_ms": total_ms,
                "agent_ms": {
                    "vision":   t_vision,
                    "research": t_research,
                    "safety":   t_safety,
                    "debate":   t_debate,
                    "decision": t_decision,
                    "action":   t_action,
                },
            },
            "agents": {
                "vision":   vision,
                "research": research,
                "safety":   safety,
                "debate":   debate,
                "decision": decision,
                "action":   action,
            },
            "decision": decision_data,
            "debate":   debate_data,
            "action":   action_data,
        }
