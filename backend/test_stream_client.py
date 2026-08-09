import requests
import json

url = "http://localhost:8000/api/interview_stream"
payload = {
    "sessionId": "test-session-stream",
    "message": ""
}

print("Starting request...")
with requests.post(url, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print("RECEIVED:", decoded_line)
