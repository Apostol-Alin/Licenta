import requests
import time
import json
import os

SERVER_URL = "http://server:5000/receive"
CLIENT_ID = os.getenv("CLIENT_ID", "default_client")

def send_data():
    data = {
        "client_id": CLIENT_ID,
        "message": f"Hello from {CLIENT_ID}"
    }
    response = requests.post(SERVER_URL, json=data)
    print(f"Client {CLIENT_ID} sent data: {response.json()}")

if __name__ == "__main__":
    send_data()
