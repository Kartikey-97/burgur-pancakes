from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Candidate Models
class CandidateMember(BaseModel):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str

class CandidateMission(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = False
    skipped: Optional[bool] = False
    attempts: Optional[int] = 0

class CandidateSignals(BaseModel):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int

class Candidate(BaseModel):
    member: CandidateMember
    missions: List[CandidateMission]
    signals: CandidateSignals

# API Request/Response Models
class TurnInterviewRequest(BaseModel):
    sessionId: str
    message: Optional[str] = Field(default=None, max_length=5000)
    candidate: Optional[Candidate] = None # First request has this; subsequent requests might also send it defensively
    mcq_enabled: bool = False # First request has this; subsequent requests might also send it defensively


class Feedback(BaseModel):
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]
    topicScores: Optional[Dict[str, float]] = None  # Person B's radar chart data

class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None
