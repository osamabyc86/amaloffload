from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from your_tasks import *
from project_identifier import create_project_endpoint, get_project_info
import logging

app = Flask(__name__)
CORS(app)

@app.route('/multiply', methods=['POST'])
def multiply():
    try:
        data = request.get_json()
        a = data.get("a", 0)
        b = data.get("b", 0)
        result_dict = multiply_task(a, b)  # دالة offload
        return jsonify({"result": result_dict["result"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "port": 7520})

@app.route('/project_info', methods=['GET'])
def project_info():
    return create_project_endpoint()

if __name__ == "__main__":
    # هذا العنوان يسمح بالاستماع على IP خارجي لتلقي الاتصالات من الإنترنت
    app.run(host="0.0.0.0", port=7520)