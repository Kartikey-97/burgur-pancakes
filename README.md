# AI Interview Agent

An adaptive, multi-turn technical interview agent built for the AI Cohort hackathon. This project is divided into three main components: a Backend core orchestrator, an ML/AI layer, and a Frontend UI.

## Architecture

* **Backend (`backend/`)**: The "spine" of the app. Managed by Person A. It features a stateful FastAPI endpoint (`POST /api/interview`) backed by a single-instance SQLite WAL database to maintain conversation state. It uses deterministic item response logic and an orchestrated state machine to evaluate candidates.
* **ML / AI Layer (`ml/`)**: Managed by Person B. Responsible for embedding-based memory retrieval, context augmentation, and dynamic follow-up generation.
* **Frontend (`frontend/`)**: Managed by Person C. The chat UI and radar chart results dashboard for the candidates.

## Backend Quickstart (Person A)

### Setup

Navigate to the backend directory and install the requirements (FastAPI, Uvicorn, Pydantic, etc.).

```bash
cd backend
pip install fastapi uvicorn pydantic requests
```

### Running the API

Start the backend server on `http://localhost:8000`:

```bash
uvicorn main:app --reload
```

The API docs will be available at `http://localhost:8000/docs`.

### Running the Simulation

You can verify that the orchestrator state machine is working from start to finish by running the automated mock interview script:

```bash
cd backend
python test_run.py
```

## Team Integration

* **Person B (ML)**: Please implement the real LangChain/LlamaIndex code inside `backend/ai_layer_interface.py` to replace the mock AI functions.
* **Person C (Frontend)**: Point your fetch requests to `POST http://localhost:8000/api/interview`. You must send a unique `sessionId` (e.g., a client-generated UUID) on every request!
