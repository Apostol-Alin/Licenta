from flask import Flask, request, jsonify
from enum import Enum
from TC import *

class protocol_states(Enum):
    PP_PROVIDED = 1
    CW_PROVIDED = 2
    CS_SENT = 3
    PAIRS_PROVIDED = 4



app = Flask(__name__)

client_data = {
    # "client_id": {
        # "N": ,
        # "t": ,
        # "state": ,
        # "commitment": ,
        # "W": ,
        # "pairs": ,
        # "Ys": 
        # "verifier"
    # }
}

# First step of the protocol
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

        client_data[client_id] = {
            "N": N,
            "t": t,
            "state": protocol_states.PP_PROVIDED,
            "commitment": {}, # g, u, S
            "W": None,
            "pairs": None,
            "Ys": None,
            "verifier": Verifier(N, t, 128) # make R=128 default value
        }
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
        if client_id not in client_data.keys():
            raise ValueError("Client ID not found.")
        if client_data[client_id]["state"] != protocol_states.PP_PROVIDED:
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
            if len(W) != client_data[client_id]["t"] + 1:
                raise ValueError("W must be of length t + 1.")

        client_data[client_id]["commitment"]["g"] = int(commitment["g"])
        client_data[client_id]["commitment"]["u"] = int(commitment["u"])
        client_data[client_id]["commitment"]["S"] = commitment["S"]
        client_data[client_id]["W"] = W
        client_data[client_id]["state"] = protocol_states.CW_PROVIDED
        return jsonify({"message": "Commitment received", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/get-Cs/<client_id>', methods=['GET'])
def get_Cs(client_id):
    """
    The server sends a list of commited values c to the client.
    These are used for commitment verification."""
    try:
        if client_id not in client_data.keys():
            raise ValueError("Client ID not found.")
        if client_data[client_id]["state"] != protocol_states.CW_PROVIDED:
            raise ValueError("Commitment and W must be provided first.")

        verifier = client_data[client_id]["verifier"]
        verifier.commit_to_cs()
        Cs = [c[1] for c in verifier.Cs] # Cs is a list of tuples (c, commitment, opening)
        dict = {"Cs": Cs}
        client_data[client_id]["state"] = protocol_states.CS_SENT

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
        if client_id not in client_data.keys():
            raise ValueError("Client ID not found.")
        if client_data[client_id]["state"] != protocol_states.CS_SENT:
            raise ValueError("Cs must be requested before sending (z, w) pairs.")
        pairs = req_json.get("pairs")
        if not pairs:
            raise ValueError("Pairs must be provided.")
        else:
            if type(pairs) != list:
                raise ValueError("Pairs must be a list.")
            if len(pairs) != client_data[client_id]["t"]:
                raise ValueError("Pairs must be of length t.")
        client_data[client_id]["pairs"] = pairs
        client_data[client_id]["state"] = protocol_states.PAIRS_PROVIDED
        return jsonify({"message": "Pairs received", "client_id": client_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/get-openings/<client_id>', methods=['GET'])
def get_openings(client_id):
    """
    The server sends the openings of the commitments of Cs to the client.
    """
    try:
        if client_id not in client_data.keys():
            raise ValueError("Client ID not found.")
        if client_data[client_id]["state"] != protocol_states.PAIRS_PROVIDED:
            raise ValueError("Commitment and W must be provided first.")

        verifier = client_data[client_id]["verifier"]
        openings = []
        for c in verifier.Cs:
            commitment = c[0]
            opening = c[2]
            openings.append(opening)
        dict = {"openings": openings, "g": verifier.pp.g, "N": verifier.pp.N}
        print(f"Commitment: {commitment}, Opening: {opening}")
        client_data[client_id]["state"] = protocol_states.CS_SENT

        return jsonify(dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/app-tester', methods=['GET'])
def app_tester():
    return jsonify({"message": "App ok"}), 200

@app.route('/get/<client_id>', methods=['GET'])
def get_client_data(client_id):
    if client_id not in client_data.keys():
        return jsonify({"error": "Client ID not found"}), 404
    data = client_data.get(client_id)
    new_data = {    
        "N": data["N"],
        "t": data["t"],
        "state": data["state"].name,
        "commitment": data["commitment"],
        "W": data["W"],
        "pairs": data.get("pairs"),
        "Ys": data.get("Ys")
    }
    return jsonify(new_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
