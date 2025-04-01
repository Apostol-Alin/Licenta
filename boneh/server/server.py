from flask import Flask, request, jsonify
from enum import Enum
from TC import *
import redis
import pickle

class protocol_states(Enum):
    PP_PROVIDED = 1
    CW_PROVIDED = 2
    CS_SENT = 3
    PAIRS_PROVIDED = 4
    OPENINGS_SENT = 5
    ACCEPTED = 6
    REJECTED = 7

app = Flask(__name__)

# client_data = {
#     # "client_id": {
#         # "N": ,
#         # "t": ,
#         # "state": ,
#         # "commitment": ,
#         # "W": ,
#         # "pairs": ,
#         # "Ys": 
#         # "verifier"
#     # }
# }

redis_client = redis.Redis(host='redis', port=6379, db=0)

def save_client_data(client_id, data):
    """
    Save client data to Redis."""
    redis_client.set(client_id, pickle.dumps(data))

def get_client_data(client_id):
    """
    Get client data from Redis."""
    data = redis_client.get(client_id)
    if data:
        return pickle.loads(data)
    return None

@app.route('/send-public-parameters', methods=['POST'])
def send_public_parameters():
    """
    The client sends public parameters (N and t) to the server."""
    try:
        req_json = request.get_json()
        client_id = req_json.get("client_id")
        N = int(req_json.get('N'))
        t = int(req_json.get('t'))
        if not client_id:
            raise ValueError("Client ID must be provided.")
        if not N or not t:
            raise ValueError("Both N and t must be provided.")
        client_data = {
            "N": N,
            "t": t,
            "state": protocol_states.PP_PROVIDED,
            "commitment": {}, # g, u, S
            "W": None,
            "pairs": None,
            "Ys": None,
            "verifier": Verifier(N, t, 128) # make R=128 default value
        }
        save_client_data(client_id, client_data)
        return jsonify({"message": "Public parameters received", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/send-commitment', methods=['POST'])
def send_commitment():
    """
    The client sends a commitment to the server."""
    try:
        req_json = request.get_json()
        client_id = req_json.get("client_id")
        commitment = req_json.get("commitment")
        W = req_json.get("W")
        if not client_id:
            raise ValueError("Client ID must be provided.")
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.PP_PROVIDED:
            raise ValueError("Public parameters must be provided first.")
        if not commitment:
            raise ValueError("Commitment must be provided.")
        else:
            keys = commitment.keys()
            if "g" not in keys or "u" not in keys or "S" not in keys:
                raise ValueError("Commitment must contain g, u, and S.")
        if not W:
            raise ValueError("W must be provided.")
        else:
            if type(W) != list:
                raise ValueError("W must be a list.")
            if len(W) != client_data["t"] + 1:
                raise ValueError("W must be of length t + 1.")

        client_data["commitment"]["g"] = int(commitment["g"])
        client_data["commitment"]["u"] = int(commitment["u"])
        client_data["commitment"]["S"] = commitment["S"]
        client_data["W"] = W
        client_data["state"] = protocol_states.CW_PROVIDED
        save_client_data(client_id, client_data)
        return jsonify({"message": "Commitment received", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/get-Cs/<client_id>', methods=['GET'])
def get_Cs(client_id):
    """
    The server sends a list of commited values c to the client.
    These are used for commitment verification."""
    try:
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.CW_PROVIDED:
            raise ValueError("Commitment and W must be provided first.")

        verifier = client_data["verifier"]
        verifier.commit_to_cs()
        Cs = []
        for c in verifier.Cs:
            commitment_Jacobi = c[1]
            commitment_affine = commitment_Jacobi.to_affine()
            commitment_affine_x = commitment_affine.x()
            commitment_affine_y = commitment_affine.y()
            commitment = {
                "x": commitment_affine_x,
                "y": commitment_affine_y
            }
            Cs.append(commitment)
        dict = {"Cs": Cs}
        client_data["state"] = protocol_states.CS_SENT
        save_client_data(client_id, client_data)
        return jsonify(dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/send-pairs', methods=['POST'])
def send_pairs():
    """
    The client sends t pairs (z, w) to the server.
    """
    try:
        req_json = request.get_json()
        client_id = req_json.get("client_id")
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.CS_SENT:
            raise ValueError("Cs must be requested before sending (z, w) pairs.")
        pairs = req_json.get("pairs")
        if not pairs:
            raise ValueError("Pairs must be provided.")
        else:
            if type(pairs) != list:
                raise ValueError("Pairs must be a list.")
            if len(pairs) != client_data["t"]:
                raise ValueError("Pairs must be of length t.")
        client_data["pairs"] = pairs
        client_data["state"] = protocol_states.PAIRS_PROVIDED
        save_client_data(client_id, client_data)
        return jsonify({"message": "Pairs received", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/get-openings/<client_id>', methods=['GET'])
def get_openings(client_id):
    """
    The server sends the openings of the commitments of Cs to the client.
    """
    try:
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.PAIRS_PROVIDED:
            raise ValueError("Pairs <zi, wi> must be provided first.")

        verifier = client_data["verifier"]
        openings = []
        for c in verifier.Cs:
            value = c[0]
            opening = c[2]
            # to open a Pedersen commitment, we need to send the value and the opening
            openings.append([value, opening])
        g_affine = verifier.pp.g.to_affine()
        h_affine = verifier.pp.h.to_affine()
        g_x = g_affine.x()
        g_y = g_affine.y()
        h_x = h_affine.x()
        h_y = h_affine.y()
        g = {
            "x": g_x,
            "y": g_y
        }
        h = {
            "x": h_x,
            "y": h_y
        }
        dict = {"openings": openings, "g": g, "h": h, "N": verifier.pp.N}
        client_data["state"] = protocol_states.OPENINGS_SENT
        save_client_data(client_id, client_data)
        return jsonify(dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """
    The server deletes the client data.
    """
    try:
        redis_client.delete(client_id)
        return jsonify({"message": "Client data deleted", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/send-Ys', methods=['POST'])
def send_Ys():
    """
    The client sends the Ys to the server. yi = ci * 2 ** (2 ** (i-1)) + alphai
    """
    try:
        req_json = request.get_json()
        client_id = req_json.get("client_id")
        Ys = req_json.get("Ys")
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.OPENINGS_SENT:
            raise ValueError("Openings must be requested first.")
        else:
            if type(Ys) != list:
                raise ValueError("Ys must be a list.")
            if len(Ys) != client_data["t"]:
                raise ValueError("Ys must be of length t.")
        client_data["Ys"] = Ys
        verifier = client_data["verifier"]
        if verifier.check_validity(client_data["W"], client_data["pairs"], Ys, client_data["commitment"]["g"]):
            client_data["state"] = protocol_states.ACCEPTED
            save_client_data(client_id, client_data)
            return jsonify({"message": "Ys received; accepted to auction", "client_id": client_id}), 200
        else:
            client_data["state"] = protocol_states.REJECTED
            save_client_data(client_id, client_data)
            return jsonify({"message": "Ys received; not accepted to auction", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/open', methods=['POST'])
def open():
    """
    The client opens the timmed commitment, providing v to the server.
    """
    try:
        req_json = request.get_json()
        client_id = req_json.get("client_id")
        v = req_json.get("v")
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.ACCEPTED:
            raise ValueError("Client must be first accepted to the auction in order to open his commitment.")
        verifier = client_data["verifier"]
        commitment = Commitment(client_data["commitment"]["g"], client_data["commitment"]["u"], client_data["commitment"]["S"])
        message = verifier.open(commitment, v)
        client_data["message"] = message
        save_client_data(client_id, client_data)
        return jsonify({"message": "Commitment opened to " + message, "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/force-open/<client_id>', methods=['GET'])
def force_open(client_id):
    try:
        client_data = get_client_data(client_id)
        if client_data is None:
            raise ValueError("Client ID not found.")
        if client_data["state"] != protocol_states.ACCEPTED:
            raise ValueError("A client must be accepted to the auction in order to force open the commitment")
        verifier = client_data["verifier"]
        commitment = Commitment(client_data["commitment"]["g"], client_data["commitment"]["u"], client_data["commitment"]["S"])
        force_opened_message = verifier.force_open(commitment)
        client_data["force_opened_message"] = force_opened_message
        save_client_data(client_id, client_data)
        return jsonify({"message": "Force open of the commitment started", "client_id": client_id}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/app-tester', methods=['GET'])
def app_tester():
    return jsonify({"message": "App ok"}), 200

@app.route('/get/<client_id>', methods=['GET'])
def get_client(client_id):
    client_data = get_client_data(client_id)
    if client_data is None:
        return jsonify({"error": "Client ID not found"}), 404
    new_data = {    
        "N": client_data["N"],
        "t": client_data["t"],
        "state": client_data["state"].name,
        "commitment": client_data["commitment"],
        "W": client_data["W"],
        "pairs": client_data.get("pairs"),
        "Ys": client_data.get("Ys"),
        "message": client_data.get("message", None),
        "force_opened_message": client_data.get("force_opened_message", None)
    }
    return jsonify(new_data), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
