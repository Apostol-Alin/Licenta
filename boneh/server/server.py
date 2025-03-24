from flask import Flask, request, jsonify

app = Flask(__name__)

clients_data = {}

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.get_json()
    client_id = data.get("client_id")
    clients_data[client_id] = data
    return jsonify({"message": "Data received", "data": data}), 200

@app.route('/app-tester', methods=['GET'])
def app_tester():
    return jsonify({"message": "App ok"}), 200

@app.route('/get/<client_id>', methods=['GET'])
def get_client_data(client_id):
    data = clients_data.get(client_id, {})
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
