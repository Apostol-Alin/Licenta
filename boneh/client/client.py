import requests
from TC import *
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

def send_commitment(commitment: dict, W: list[int]):
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
    
def send_pairs(pairs: list[list[int]]):
    data = {
        "client_id": CLIENT_ID,
        "pairs": client.pairs
    }
    response = requests.post(f"{SERVER_URL}/send-pairs", json=data)
    print(f"Client {CLIENT_ID} sent pairs, response: {response.json()}")

if __name__ == "__main__":
    lambda_ = 128
    t = 22
    client = Commiter(128, 22)
    send_pp(client.N, client.t)
    message = "110011" # 27
    commitment = client.commit(message)
    g, u, S = commitment.g, commitment.u, commitment.S
    commitment_dict = {'g': g, 'u': u, 'S': S}
    client.compute_W()
    send_commitment(commitment_dict, client.W)
    Cs = get_Cs()
    client.compute_pairs()
    send_pairs(client.pairs)

