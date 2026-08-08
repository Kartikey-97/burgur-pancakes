from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TurnInterviewRequest, InterviewResponse, Feedback, Candidate
import session
import data_loader
from orchestrator import process_turn

app = FastAPI(title="AI Interview Agent")

# Add CORS Middleware so Frontend (Person C) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to localhost:3000 / frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/interview", response_model=InterviewResponse, response_model_exclude_none=True)
async def interview_endpoint(req: TurnInterviewRequest):
    if not req.sessionId:
        raise HTTPException(status_code=400, detail="Missing sessionId")
    
    # Load session state (synchronous DB call, fine for hackathon scale)
    session_state = session.load_session(req.sessionId) or {}
    
    # Candidate data is needed to process turn.
    if not session_state and not req.candidate:
        # Default to first candidate if not provided in first request
        candidates_data = data_loader.CANDIDATES
        candidate_list = candidates_data.get('candidates', []) if isinstance(candidates_data, dict) else candidates_data
        if candidate_list and isinstance(candidate_list, list):
            req.candidate = Candidate(**candidate_list[0])
            
    candidate_data = req.candidate.model_dump() if req.candidate else session_state.get('candidate', {})

    
    if not session_state:
        session_state['candidate'] = candidate_data
        
    curriculum = data_loader.CURRICULUM

    
    # Process turn
    result = process_turn(session_state, candidate_data, req.message, curriculum)
    
    # Save state
    session.save_session(req.sessionId, session_state)
    
    feedback_dict = result.get("feedback")
    feedback_obj = Feedback(**feedback_dict) if feedback_dict else None
    
    return InterviewResponse(
        reply=result["reply"],
        done=result["done"],
        feedback=feedback_obj
    )
