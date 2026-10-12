"""
CivicAgent v3.0 — Pydantic Schemas
Request and response models for the API layer.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentMeta(BaseModel):
    agent:        str
    status:       str = "completed"
    execution_ms: int = 0
    attempt:      int = 1
    error:        Optional[str] = None


class PipelineTiming(BaseModel):
    total_ms: int = 0
    agent_ms: Dict[str, int] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    description: str
    location:    str = ""


class DecisionResult(BaseModel):
    priority:                str = "MEDIUM"
    priority_score_0_to_100: int = 50
    authority:               str = ""
    department:              str = ""
    confidence_0_to_1:       float = 0.0
    rationale:               str = ""
    recommended_sla:         str = ""


class DebateResult(BaseModel):
    position_a:               str = ""
    position_b:               str = ""
    consensus:                str = ""
    unresolved_questions:     List[str] = Field(default_factory=list)
    debate_confidence_0_to_1: float = 0.0


class ActionResult(BaseModel):
    action_steps:      List[str] = Field(default_factory=list)
    complaint_subject: str = ""
    complaint_body:    str = ""
    evidence_checklist:List[str] = Field(default_factory=list)
    follow_up:         str = ""
    citizen_message:   str = ""


class CivicCase(BaseModel):
    case_id:     str
    description: str
    location:    str = ""
    image_name:  str = ""
    timestamp:   Optional[int] = None
    ai_mode:     bool = False
    pipeline:    Optional[PipelineTiming] = None
    agents:      Dict[str, Any] = Field(default_factory=dict)
    debate:      Dict[str, Any] = Field(default_factory=dict)
    decision:    Dict[str, Any] = Field(default_factory=dict)
    action:      Dict[str, Any] = Field(default_factory=dict)


class AnalyticsResponse(BaseModel):
    total_cases:        int = 0
    priority_counts:    Dict[str, int] = Field(default_factory=dict)
    category_counts:    Dict[str, int] = Field(default_factory=dict)
    authority_counts:   Dict[str, int] = Field(default_factory=dict)
    department_counts:  Dict[str, int] = Field(default_factory=dict)
    risk_distribution:  List[Dict[str, Any]] = Field(default_factory=list)
    timeline:           List[Dict[str, Any]] = Field(default_factory=list)
    avg_priority_score: Optional[float] = None
    total_critical:     int = 0
    total_high:         int = 0


class HealthResponse(BaseModel):
    status:        str = "online"
    version:       str = "3.0.0"
    ai_configured: bool = False
    model:         str = ""
    total_cases:   int = 0
