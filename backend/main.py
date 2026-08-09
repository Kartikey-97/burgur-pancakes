from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TurnInterviewRequest, InterviewResponse, Feedback, Candidate
import session
import data_loader
from fastapi.responses import StreamingResponse
from orchestrator import process_turn_stream

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

@app.post("/api/interview_stream")
def interview_stream_endpoint(req: TurnInterviewRequest):
    if not req.sessionId:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    session_state = session.load_session(req.sessionId) or {}

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

    if not session_state:
        session_state['candidate'] = candidate_data

    curriculum = data_loader.CURRICULUM

    def event_generator():
        # Stream the response events from the orchestrator
        generator = process_turn_stream(session_state, candidate_data, req.message or "", curriculum)
        for event in generator:
            yield event
        
        # After the stream is fully complete, persist the updated session state
        session.save_session(req.sessionId, session_state)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

