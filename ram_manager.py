import os
import psutil
import time
import threading
import socket
import base64
import uuid
from typing import Dict, List

try:
    from flask import Flask, request, jsonify
except ImportError as exc:
    raise RuntimeError("Flask غير مُثبّت. نفِّذ: pip install flask") from exc

try:
    import peer_registry
except ImportError:
    peer_registry = None

# الإعدادات
RAM_PORT        = int(os.getenv("RAM_PORT", "8765"))
CHUNK_MB        = int(os.getenv("RAM_CHUNK_MB", "64"))
CHECK_INTERVAL  = int(os.getenv("RAM_CHECK_INTERVAL", "5"))

# حدود نسب الرام
SEND_THRESHOLD  = float(os.getenv("SEND_THRESHOLD", "90.0"))   # % للإرسال
RECV_THRESHOLD  = float(os.getenv("RECV_THRESHOLD", "70.0"))   # % للاستقبال

app = Flask(__name__)
remote_chunks: Dict[str, bytes] = {}

def get_ram_usage_percent() -> float:
    """إرجاع نسبة استخدام الرام"""
    return psutil.virtual_memory().percent

def get_free_ram_mb() -> int:
    """إرجاع الرام الحرة بالميغابايت"""
    return psutil.virtual_memory().available // (1024 * 1024)

# ─────────────── واجهة HTTP ───────────────
@app.route("/ram_status", methods=["GET"])
def ram_status():
    return jsonify({
        "free_mb": get_free_ram_mb(),
        "usage_percent": get_ram_usage_percent()
    })

@app.route("/ram_store", methods=["POST"])
def ram_store():
    """تخزين كتلة بيانات لو الرام يسمح"""
    usage = get_ram_usage_percent()
    if usage > RECV_THRESHOLD:
        return jsonify({"error": f"الرام مشغول بنسبة {usage:.1f}%، لا يمكن التخزين الآن"}), 503

    payload = request.get_json(force=True)
    cid     = payload["id"]
    blob_b64= payload["data"]
    remote_chunks[cid] = base64.b64decode(blob_b64)
    return jsonify({"status": "stored", "id": cid})

@app.route("/ram_fetch/<cid>", methods=["GET"])
def ram_fetch(cid):
    blob = remote_chunks.get(cid)
    if blob is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": cid, "data": base64.b64encode(blob).decode()})

# ─────────────── وظائف ───────────────
def start_api():
    from werkzeug.serving import make_server
    server = make_server("0.0.0.0", RAM_PORT, app)
    server.serve_forever()

def discover_peers() -> List[str]:
    peers: List[str] = []
    if peer_registry and hasattr(peer_registry, "list_peers"):
        try:
            peers_info = peer_registry.list_peers()
            peers = [p["ip"] for p in peers_info if p.get("ip")]
        except Exception:
            pass
    else:
        central_env = os.getenv("CENTRAL_PEERS", "")
        if central_env:
            peers = central_env.split(",")
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        peers = [ip for ip in peers if ip != local_ip]
    except Exception:
        pass
    return peers

def offload_chunk(blob: bytes, peer_ip: str) -> bool:
    import requests
    try:
        resp = requests.post(
            f"http://{peer_ip}:{RAM_PORT}/ram_store",
            json={"id": str(uuid.uuid4()), "data": base64.b64encode(blob).decode()},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False

def monitor_loop():
    while True:
        usage = get_ram_usage_percent()
        if usage >= SEND_THRESHOLD:
            peers = discover_peers()
            if peers:
                blob = bytes(CHUNK_MB * 1024 * 1024)
                for ip in peers:
                    if offload_chunk(blob, ip):
                        print(f"[RAM]‎ أرسلت ‎{CHUNK_MB}‎MB إلى ‎{ip} (الاستهلاك {usage:.1f}%)")
                        break
                else:
                    print("[RAM] كل الأقران رفضوا التخزين أو حدث خطأ.")
            else:
                print("[RAM] لا يوجد أقران متاحون.")
        time.sleep(CHECK_INTERVAL)

def main():
    threading.Thread(target=start_api, daemon=True).start()
    monitor_loop()

if __name__ == "__main__":
    main()
