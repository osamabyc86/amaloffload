import logging
import socket
import threading
import psutil
import GPUtil
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from peer_discovery import PEERS
from peer_discovery import PORT, PORT


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

node_id = socket.gethostname()
connected_peers_data = {}

# ─────────────── جمع بيانات الحمل ───────────────
def get_system_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu_load = 0
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_load = gpus[0].load * 100
    except:
        pass
    return {"cpu": cpu, "ram": ram, "gpu": gpu_load}

# ─────────────── إرسال التحديثات ───────────────
def broadcast_status():
    while True:
        status = get_system_status()
        socketio.emit("status_update", {node_id: status}, broadcast=True)
        socketio.sleep(5)

# ─────────────── صفحة الواجهة ───────────────
@app.route("/")
def index():
    return render_template("dashboard.html", peers=connected_peers_data)

# ─────────────── استقبال تحديثات الحالة ───────────────
@socketio.on("status_update")
def handle_status_update(data):
    connected_peers_data.update(data)
    emit("update_peers", connected_peers_data, broadcast=True)

# ─────────────── دردشة ───────────────
@socketio.on("send_message")
def handle_message(data):
    emit("receive_message", data, broadcast=True)

# ─────────────── تشغيل ───────────────
if __name__ == "__main__":
    threading.Thread(target=broadcast_status).start()
    logging.info(f"🚀 تشغيل Dashboard على {node_id}")
    socketio.run(app, host="0.0.0.0", port=7000)
