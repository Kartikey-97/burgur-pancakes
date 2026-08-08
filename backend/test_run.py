import requests
import uuid
import time

API_URL = "http://localhost:8000/api/interview"

def run_simulation():
    session_id = str(uuid.uuid4())
    print(f"Starting simulation with Session ID: {session_id}\n")

    # Turn 1: Init (No message)
    payload = {
        "sessionId": session_id,
        "message": ""
    }
    
    print("--- TURN 1 (INIT) ---")
    response = requests.post(API_URL, json=payload)
    data = response.json()
    print(f"Agent: {data.get('reply')}\n")
    
    turn = 2
    while not data.get("done") and turn <= 12:
        print(f"--- TURN {turn} ---")
        user_message = f"Simulated user answer for turn {turn}. I used Python and Docker."
        print(f"User: {user_message}")
        
        payload = {
            "sessionId": session_id,
            "message": user_message
        }
        
        response = requests.post(API_URL, json=payload)
        data = response.json()
        print(f"Agent: {data.get('reply')}\n")
        
        if data.get("done"):
            print("Interview Completed!")
            print("Feedback Report:")
            print(data.get("feedback"))
            break
            
        time.sleep(0.5)
        turn += 1

if __name__ == "__main__":
    run_simulation()
