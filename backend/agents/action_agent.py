import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Action Agent")

    def execute(self, data):
        prompt = """You are the CivicAgent Action Agent.
Generate an actionable civic response and formal complaint draft.
Return ONLY JSON:
action_steps, complaint_subject, complaint_body, evidence_checklist,
follow_up, citizen_message."""
        user = f"""Issue: {data.get('vision',{})}
Decision: {data.get('decision',{})}
Location: {data.get('location','')}
Description: {data.get('description','')}"""

        if self.ai.enabled and self.ai.is_available():
            try:
                return self.ai.complete_json(prompt, user)
            except Exception as exc:
                logger.warning("[ActionAgent] AI unavailable, using contextual fallback. Reason: %s", exc)

        # ── Deterministic contextual fallback ────────────────────────
        vision = data.get("vision", {})
        decision = data.get("decision", {})
        location = data.get("location") or "the reported ward location"
        issue = vision.get("issue") or "Civic infrastructure defect"
        authority = decision.get("authority") or "Municipal Civic Authority"
        department = decision.get("department") or "Public Works Department"
        sla = decision.get("recommended_sla") or "24-48 hours"
        priority = decision.get("priority") or "HIGH"

        steps = [
            f"Dispatch electronic ticket directly to {authority} ({department}).",
            f"Deploy ward field engineer to {location} for physical inspection within {sla.split()[0]} hours.",
            "Install reflective safety bollards and caution tape around the hazard zone.",
            "Initiate civil repair work with documented pre- and post-repair photographic records.",
            "Validate completion and close ticket on central municipal citizen registry."
        ]

        complaint_subject = f"Urgent Civic Grievance: {issue} at {location} [{priority} Priority]"
        complaint_body = (
            f"To,\n"
            f"The Executive Engineer / Competent Authority,\n"
            f"{department},\n"
            f"{authority}.\n\n"
            f"Subject: Formal complaint regarding {issue.lower()} at {location}.\n\n"
            f"Respected Sir/Madam,\n\n"
            f"This is an automated verified complaint regarding an unresolved civic defect located at {location}. "
            f"Citizen grievance report: \"{data.get('description', '').strip()}\".\n\n"
            f"The automated multi-agent assessment has categorized this defect as {priority} priority (SLA: {sla}). "
            f"The current condition poses immediate danger to road commuters, pedestrians, and public property. "
            f"Kindly arrange an immediate site inspection and execute required restoration works at the earliest.\n\n"
            f"Inspection report and resolution status are requested to be updated on the civic portal.\n\n"
            f"Yours faithfully,\n"
            f"Civic Intelligence System (Citizen Grievance Desk)"
        )

        evidence_checklist = [
            "Geotagged site photograph with timestamp",
            "Observed dimension and road clearance measurement",
            "Ward jurisdictional verification code",
            "Initial on-site engineer verification report",
            "Post-restoration photo verification certificate"
        ]

        follow_up = f"Automatic escalation to Ward Assistant Executive Engineer if unresolved within {sla}."
        citizen_message = (
            f"Your report regarding '{issue}' at {location} has been registered and routed to "
            f"{authority} ({department}). Recommended resolution timeframe is {sla}. You can track this case anytime."
        )

        return {
            "action_steps": steps,
            "complaint_subject": complaint_subject,
            "complaint_body": complaint_body,
            "evidence_checklist": evidence_checklist,
            "follow_up": follow_up,
            "citizen_message": citizen_message
        }
