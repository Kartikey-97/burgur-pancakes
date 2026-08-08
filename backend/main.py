from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TurnInterviewRequest, InterviewResponse, Feedback, Candidate
import session
import data_loader
from orchestrator import process_turn

app = FastAPI(
    title="AI Interview Agent",
    description="Personalized technical interview agent for the AI Cohort.",
    version="1.0.0"
)

# CORS — allows Person C's frontend to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    """Quick connectivity test for Person C and Person B to verify the server is up."""
    return {
        "status": "ok",
        "curriculum_days_loaded": len(data_loader.CURRICULUM.get("days", [])),
        "candidates_loaded": len(data_loader.CANDIDATES.get("candidates", [])),
    }

@app.post("/api/interview", response_model=InterviewResponse, response_model_exclude_none=True)
async def interview_endpoint(req: TurnInterviewRequest):
    if not req.sessionId:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    # Load existing session state (returns {} for brand new sessions)
    session_state = session.load_session(req.sessionId) or {}

    # Resolve candidate data:
    # - If session already has candidate (turns 2+): use it from session
    # - If first turn with candidate in request: use it
    # - Fallback: use first candidate from the data file (useful for test_run.py)
    if session_state:
        candidate_data = session_state.get('candidate', {})
    elif req.candidate:
        candidate_data = req.candidate.model_dump()
    else:
        candidates_list = data_loader.CANDIDATES.get('candidates', [])
        if not candidates_list:
            raise HTTPException(status_code=503, detail="No candidate data available")
        try:
            candidate_data = Candidate(**candidates_list[0]).model_dump()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Invalid candidate data: {e}")

    # Persist the candidate data in the session so we don't need it on every request
    if not session_state:
        session_state['candidate'] = candidate_data

    curriculum = data_loader.CURRICULUM

    # Run the state machine
    result = process_turn(session_state, candidate_data, req.message or "", curriculum)

    # Persist updated session state
    session.save_session(req.sessionId, session_state)

    # Build the response
    feedback_dict = result.get("feedback")
    feedback_obj = Feedback(**feedback_dict) if feedback_dict else None

    return InterviewResponse(
        reply=result["reply"],
        done=result["done"],
        feedback=feedback_obj
    )
