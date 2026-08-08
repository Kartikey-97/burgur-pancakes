import requests
import uuid
import time
import json

API_URL = "http://localhost:8000/api/interview"
HEALTH_URL = "http://localhost:8000/api/health"

def run_simulation():
    # --- Health Check ---
    try:
        health = requests.get(HEALTH_URL, timeout=3).json()
        print(f"Server Health: {json.dumps(health, indent=2)}\n")
    except Exception as e:
        print(f"ERROR: Could not reach server at {HEALTH_URL}\n  -> {e}")
        print("Make sure uvicorn is running: uvicorn main:app --reload")
        return

    session_id = str(uuid.uuid4())
    print(f"Starting simulation with Session ID: {session_id}\n")

    # Turn 1: Init (empty message triggers INIT phase)
    payload = {"sessionId": session_id, "message": ""}
    print("--- TURN 1 (INIT) ---")
    response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        print(f"FAILED (HTTP {response.status_code}): {response.text}")
        return

    data = response.json()
    print(f"Agent: {data.get('reply')}\n")

    turn = 2
    while not data.get("done") and turn <= 15:
        print(f"--- TURN {turn} ---")

        # Simulate different answer lengths to test cheat detection
        if turn == 4:
            # This answer is >150 chars and will be sent instantly — should trigger cheat detection
            user_message = "I built a RAG pipeline using LangChain and ChromaDB. I chunked the PDFs with RecursiveCharacterTextSplitter, embedded with OpenAI's text-embedding-3-small, stored vectors in Chroma, and used MMR retrieval to reduce redundancy before prompting GPT-4o."
        else:
            user_message = f"Simulated user answer for turn {turn}. I used Python and Docker."

        print(f"User: {user_message[:80]}{'...' if len(user_message) > 80 else ''}")

        payload = {"sessionId": session_id, "message": user_message}
        response = requests.post(API_URL, json=payload)

        if response.status_code != 200:
            print(f"FAILED (HTTP {response.status_code}): {response.text}")
            break

        data = response.json()
        print(f"Agent: {data.get('reply')}\n")

        if data.get("done"):
            print("=" * 50)
            print("Interview Completed!")
            print("Feedback Report:")
            print(json.dumps(data.get("feedback"), indent=2))
            print("=" * 50)
            break

        time.sleep(0.2)
        turn += 1

    if not data.get("done"):
        print(f"\nWARNING: Interview did not complete within {turn - 1} turns!")

if __name__ == "__main__":
    run_simulation()
