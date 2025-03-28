from flask import Flask, request, jsonify
from enum import Enum

class protocol_states(Enum):
    PP_PROVIDED = 1
    CW_PROVIDED = 2
    CS_SENT = 3



app = Flask(__name__)

client_data = {
    # "client_id": {
    #     "N": 0,
    #     "t": 0,
    #     "state": protocol_states.PP_PROVIDED
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
            "commitment": None,
            "W": None,
            "pairs": None,
            "Ys": None
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
        if not W:
            raise ValueError("W must be provided.")
        else:
            if type(W) != list:
                raise ValueError("W must be a list.")
            if len(W) != client_data[client_id]["t"] + 1:
                raise ValueError("W must be of length t + 1.")

        client_data[client_id]["commitment"] = commitment
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

        Cs = [100,200,300]
        dict = {"Cs": Cs}
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
