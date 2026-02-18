"""Incident data models."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class IncidentMetrics(BaseModel):
    """Metrics associated with an incident."""
    data: Dict[str, float] = Field(default_factory=dict)


class IncidentAlert(BaseModel):
    """Incident alert data structure."""
    incident_id: str
    timestamp: str
    source: str
    alert_name: str
    description: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    affected_services: List[str] = Field(default_factory=list)
    environment: str = "production"
    tags: List[str] = Field(default_factory=list)


class IncidentContext(BaseModel):
    """Full incident context including alert and logs."""
    alert: IncidentAlert
    logs: Optional[str] = None
    additional_context: Optional[str] = None


class TriageResult(BaseModel):
    """Result of incident triage."""
    incident_id: str
    severity: str
    category: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    root_causes: List[str]
    mitigation_plan: str
    relevant_runbooks: List[Dict[str, Any]]  # Changed from Dict[str, str] to allow float similarity
    citations: List[str]
    reasoning: Optional[str] = None
    processing_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
