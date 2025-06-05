from time import sleep
import requests
from TC import *
import os
import ecdsa

SERVER_URL = "https://server"
CLIENT_ID = os.getenv("CLIENT_ID", "default_client")
message = os.getenv("MESSAGE", 500)
message = bin(int(message))[2:]
message = message.zfill(64)

def send_pp(N: int):
    data = {
        "client_id": CLIENT_ID,
        "N": N,
    }
    response = requests.post(f"{SERVER_URL}/send-public-parameters", json=data, verify='certs/server.crt')
    print(f"Client {CLIENT_ID} set public parameters, response: {response.json()}")

def send_commitment(commitment: dict, W: list[int]):
    data = {
        "client_id": CLIENT_ID,
        "commitment": commitment,
        "W": W
    }
    response = requests.post(f"{SERVER_URL}/send-commitment", json=data, verify='certs/server.crt')
    print(f"Client {CLIENT_ID} sent commitment, response: {response.json()}")

def get_Cs():
    response = requests.get(f"{SERVER_URL}/get-Cs/{CLIENT_ID}", verify='certs/server.crt')
    if response.status_code == 200:
        Cs_affine_points = response.json().get("Cs")
        p=115792089237316195423570985008687907853269984665640564039457584007908834671663
        a=0
        b=7
        h=1
        curve = ecdsa.ellipticcurve.CurveFp(p=p, a=a, b=b, h=h)
        Cs = []
        for pt in Cs_affine_points:
            x = pt['x']
            y = pt['y']
            c = ecdsa.ellipticcurve.PointJacobi.from_affine(point=ecdsa.ellipticcurve.Point(curve, x, y))
            Cs.append(c)
        print(f"Client {CLIENT_ID} received Cs: {Cs}")
        return Cs
    else:
        print(f"Failed to get Cs: {response.json()}")
        return None
    
def get_Cs_openings():
    response = requests.get(f"{SERVER_URL}/get-openings/{CLIENT_ID}", verify='certs/server.crt')
    if response.status_code == 200:
        openings = response.json().get("openings")
        g = response.json().get("g")
        h = response.json().get("h")
        N = response.json().get("N")
        g_x = g['x']
        g_y = g['y']
        h_x = h['x']
        h_y = h['y']
        p=115792089237316195423570985008687907853269984665640564039457584007908834671663
        a=0
        b=7
        h=1
        curve = ecdsa.ellipticcurve.CurveFp(p=p, a=a, b=b, h=h)
        g = ecdsa.ellipticcurve.PointJacobi.from_affine(point=ecdsa.ellipticcurve.Point(curve, g_x, g_y))
        h = ecdsa.ellipticcurve.PointJacobi.from_affine(point=ecdsa.ellipticcurve.Point(curve, h_x, h_y))
        print(f"Client {CLIENT_ID} received openings: {openings}")
        return openings, g, h, N
    else:
        print(f"Failed to get openings: {response.json()}")
        return None
    
def open_Cs(Cs: list[ecdsa.ellipticcurve.PointJacobi], openings: list[list[int]], pp: PedersenCommitmentPublicParams):
    values = []
    for i in range(len(Cs)):
        c = Cs[i]
        opening = openings[i]
        value = opening[0]
        opening_value = opening[1]
        if pedersen_open(c, value, opening_value, pp):
            values.append(value)
        else:
            raise ValueError(f"Failed to open commitment {i}")
    return values
    
def send_pairs(pairs: list[tuple[int, int]]):
    data = {
        "client_id": CLIENT_ID,
        "pairs": pairs
    }
    response = requests.post(f"{SERVER_URL}/send-pairs", json=data, verify='certs/server.crt')
    print(f"Client {CLIENT_ID} sent pairs, response: {response.json()}")

def quit_auction():
    response = requests.delete(f"{SERVER_URL}/delete-client/{CLIENT_ID}", verify='certs/server.crt')
    print(f"Client {CLIENT_ID} quit auction, response: {response.json()}")

def send_Ys(Ys: list[tuple[int, int]]):
    data = {
        "client_id": CLIENT_ID,
        "Ys": Ys
    }
    response = requests.post(f"{SERVER_URL}/send-Ys", json=data, verify='certs/server.crt')
    print(f"Client {CLIENT_ID} sent Ys, response: {response.json()}")

def open(v: int):
    data = {
        "client_id": CLIENT_ID,
        "v": v
    }
    response = requests.post(f"{SERVER_URL}/open", json=data, verify='certs/server.crt')
    if response.status_code == 200:
        print(f"Client {CLIENT_ID} opened commitment, response: {response.json()}")
    else:
        print(f"Failed to open commitment: {response.json()}")

def check_auction_over():
    response = requests.get(f"{SERVER_URL}/check-auction-over", verify='certs/server.crt')
    return response.json().get("message")

if __name__ == "__main__":
    try:
        lambda_ = 128
        t = int(requests.get(f"{SERVER_URL}/get-time-parameter", verify='certs/server.crt').json().get("t"))
        B = int(requests.get(f"{SERVER_URL}/get-B", verify='certs/server.crt').json().get("B"))
        client = Commiter(lambda_, t, B)
        send_pp(client.N)
        commitment = client.commit(message)
        g, u, S = commitment.g, commitment.u, commitment.S
        commitment_dict = {'g': g, 'u': u, 'S': S}
        client.compute_W()
        send_commitment(commitment_dict, client.W)

        Cs = get_Cs()
        client.compute_pairs()
        send_pairs(client.pairs)
        openings, g, h, N = get_Cs_openings()
        pp = PedersenCommitmentPublicParams()
        pp.g = g
        pp.h = h
        pp.N = N
        Cs = open_Cs(Cs, openings, pp)
        client.compute_Ys(Cs)
        send_Ys(client.Ys)
        a = pow(2, (2 ** t - len(message)), (client.p1 - 1) * (client.p2 - 1))
        v = pow(client.h, a, client.N)
        while check_auction_over() == "no": # only proceed to send opening if auction is over
            sleep(5)
        if CLIENT_ID != "client2": # make client2 refuse to open his timmed commitment
            open(v)
    except Exception as e:
        quit_auction()
        print(e)

