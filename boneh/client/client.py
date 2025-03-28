import requests
import time
import json
import os

SERVER_URL = "http://server:5000"
CLIENT_ID = os.getenv("CLIENT_ID", "default_client")

def send_data():
    data = {
        "client_id": CLIENT_ID,
        "message": f"Hello from {CLIENT_ID}"
    }
    response = requests.post(SERVER_URL, json=data)
    print(f"Client {CLIENT_ID} sent data: {response.json()}")

def send_pp(N: int, t: int):
    data = {
        "client_id": CLIENT_ID,
        "N": N,
        "t": t
    }
    response = requests.post(f"{SERVER_URL}/send-public-parameters", json=data)
    print(f"Client {CLIENT_ID} set public parameters, response: {response.json()}")

def send_commitment(commitment: str, W: list[int]):
    data = {
        "client_id": CLIENT_ID,
        "commitment": commitment,
        "W": W
    }
    response = requests.post(f"{SERVER_URL}/send-commitment", json=data)
    print(f"Client {CLIENT_ID} sent commitment, response: {response.json()}")

def get_Cs():
    response = requests.get(f"{SERVER_URL}/get-Cs/{CLIENT_ID}")
    if response.status_code == 200:
        Cs = response.json().get("Cs")
        print(f"Client {CLIENT_ID} received Cs: {Cs}")
        return Cs
    else:
        print(f"Failed to get Cs: {response.json()}")
        return None

if __name__ == "__main__":
    send_pp(12345, 5)
    W = [1, 2, 3, 4, 5, 6]
    commitment = "1011101110"
    send_commitment(commitment, W)
    Cs = get_Cs()

