import requests
import json

url = "http://localhost:8000/api/interview_stream"
payload = {
    "sessionId": "test-session-stream",
    "message": "I would use broadcast joins if one of the dataframes is small. Or I would add a salt to the join key to skew it, and then broadcast the smaller table with exploded keys."
}

print("Starting request...")
with requests.post(url, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print("RECEIVED:", decoded_line)
