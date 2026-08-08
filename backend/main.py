from fastapi import FastAPI, HTTPException
from models import TurnInterviewRequest, InterviewResponse, Feedback

app = FastAPI(title="AI Interview Agent")

@app.post("/api/interview", response_model=InterviewResponse, response_model_exclude_none=True)
async def interview_endpoint(req: TurnInterviewRequest):
    if not req.sessionId:
        raise HTTPException(status_code=400, detail="Missing sessionId")
    
    # TODO(Phase 4): Delegate to orchestrator
    raise NotImplementedError("Phase 1 stub: The interview loop is not yet implemented.")
