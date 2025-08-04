#!/usr/bin/env python3
"""
external_server.py — سيرفر مركزي لتوزيع المهام + Dashboard تفاعلي
"""
import logging
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from peer_discovery import PEERS

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

connected_peers = {}  # {node_id: {"cpu":%, "ram":%, "gpu":%}}

# ─────────────── اختيار أفضل Peer ───────────────
def select_best_peer():
    peers_list = list(PEERS)
    if not peers_list:
        logging.warning("⚠️ لا توجد أجهزة مسجلة حالياً.")
        return None
    
    try:
        peer_loads = []
        for peer_url in peers_list:
            try:
                resp = requests.get(f"{peer_url.replace('/run_task','')}/status", timeout=2)
                if resp.ok:
                    data = resp.json()
                    peer_loads.append((peer_url, data.get("cpu_load", 100)))
            except:
                continue
        
        if not peer_loads:
            return None
        
        peer_loads.sort(key=lambda x: x[1])
        return peer_loads[0][0]
    except Exception as e:
        logging.error(f"❌ خطأ في اختيار الـ Peer: {e}")
        return None

# ─────────────── API توزيع المهام ───────────────
@app.route("/submit_task", methods=["POST"])
def submit_task():
    data = request.get_json()
    if not data or "task_id" not in data:
        return jsonify({"error": "يجب تحديد task_id"}), 400

    peer = select_best_peer()
    if not peer:
        return jsonify({"error": "لا توجد أجهزة متاحة حالياً"}), 503
    
    try:
        resp = requests.post(peer, json=data, timeout=10)
        if resp.ok:
            return jsonify({"status": "success", "result": resp.json()})
        else:
            return jsonify({"error": "فشل إرسال المهمة"}), 500
    except Exception as e:
        logging.error(f"❌ خطأ في إرسال المهمة: {e}")
        return jsonify({"error": str(e)}), 500

# ─────────────── API تحديث حالة الأجهزة ───────────────
@app.route("/update_status", methods=["POST"])
def update_status():
    data = request.json
    node_id = data.get("node_id")
    if not node_id:
        return jsonify({"error": "node_id مطلوب"}), 400
    
    connected_peers[node_id] = {
        "cpu": data.get("cpu"),
        "ram": data.get("ram"),
        "gpu": data.get("gpu")
    }
    socketio.emit("update_peers", connected_peers, broadcast=True)
    return jsonify({"status": "ok"})

# ─────────────── صفحة Dashboard ───────────────
@app.route("/")
def index():
    return render_template("dashboard.html")

# ─────────────── دردشة ───────────────
@socketio.on("send_message")
def handle_message(data):
    socketio.emit("receive_message", data, broadcast=True)

# ─────────────── تشغيل السيرفر ───────────────
if __name__ == "__main__":
    logging.info("🚀 بدء السيرفر المركزي مع Dashboard ودردشة")
    socketio.run(app, host="0.0.0.0", port=8000, allow_unsafe_werkzeug=True)


