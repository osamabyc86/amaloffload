"""
ram_manager.py – Distributed RAM Offload Agent
================================================

❖ الغرض
------------
يوفِّر هذا الملف إضافة مستقلة إلى مشروع **AmalOffload** من أجل مشاركة الذاكرة (RAM) بين جميع العُقد التي تشغِّل المشروع. عندما ينخفض مقدار الذاكرة الحرة على إحدى العُقد إلى أقل من 2 جيجابايت (أو أي قيمة تحدّدها)، تُنقل كتل بيانات إلى عُقد أخرى ما تزال تملك ذاكرة حرّة.

❖ المزايا الرئيسة
------------------
* يراقب استهلاك الذاكرة محليًّا بانتظام.
* يعلن عن نفسه ويكتشف الأقران (Peers) تلقائيًّا بالاعتماد على `peer_registry` إن وُجد، أو على قائمة في المتغيّر البيئي `CENTRAL_PEERS` كحلّ احتياطي.
* يعرض واجهة HTTP بسيطة (`Flask`) بثلاث مسارات:
  * `GET  /ram_status`  → يُرجِع مقدار الذاكرة الحرّة بالعُقدة.
  * `POST /ram_store`   → يستقبل كتلة بيانات (Base64) ويحجزها في الذاكرة.
  * `GET  /ram_fetch/<id>` → يُرجِع كتلة بيانات مُخزّنة بحسب معرّفها.

❖ طريقة التشغيل
----------------
```bash
python ram_manager.py --ram-limit 2048 --chunk 64 --interval 5
```
أو اكتفِ بالتشغيل بدون وسائط واعتمد على القيم الافتراضيّة أو على متغيّرات البيئة:
```bash
export RAM_THRESHOLD_MB=2048
export RAM_CHUNK_MB=64
python ram_manager.py
```

❖ التعليمات البرمجيّة
----------------------
"""
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

# محاولة استيراد مُسجِّل الأقران الحالي من المشروع
try:
    import peer_registry  # يتوقع أن يحتوي على list_peers()
except ImportError:
    peer_registry = None

# الإعدادات – قابلة للتعديل عبر متغيّرات البيئة
RAM_LIMIT_MB    = int(os.getenv("RAM_THRESHOLD_MB", "2048"))  # الحد الأدنى للرام الحرّة قبل الت offload
CHUNK_MB        = int(os.getenv("RAM_CHUNK_MB", "64"))       # حجم الكتلة المُرسَلة
CHECK_INTERVAL  = int(os.getenv("RAM_CHECK_INTERVAL", "5"))  # ثواني بين كل فحص
RAM_PORT        = int(os.getenv("RAM_PORT", "8765"))          # بورت واجهة الذاكرة

app = Flask(__name__)

# مخزن الكتل الواردة
remote_chunks: Dict[str, bytes] = {}

def get_free_ram_mb() -> int:
    """الذاكرة الحرّة بالميغابايت"""
    return psutil.virtual_memory().available // (1024 * 1024)

# ─────────────────── واجهة HTTP ────────────────────
@app.route("/ram_status", methods=["GET"])
def ram_status():
    """إرجاع كميّة الذاكرة الحرّة بالعُقدة."""
    return jsonify({"free_mb": get_free_ram_mb()})

@app.route("/ram_store", methods=["POST"])
def ram_store():
    """تلقّي كتلة بيانات وتخزينها."""
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

# ─────────────────── وظائف داخليّة ───────────────────

def start_api():
    """تشغيل خادم Flask في خيط منفصل."""
    from werkzeug.serving import make_server
    server = make_server("0.0.0.0", RAM_PORT, app)
    server.serve_forever()


def discover_peers() -> List[str]:
    """الحصول على قائمة IPs للأقران، باستثناء عنوان الجهاز الحالي."""
    peers: List[str] = []

    if peer_registry and hasattr(peer_registry, "list_peers"):
        try:
            peers_info = peer_registry.list_peers()  # متوقع: [{"ip": "..."}, ...]
            peers = [p["ip"] for p in peers_info if p.get("ip")]
        except Exception:
            pass
    else:
        central_env = os.getenv("CENTRAL_PEERS", "")
        if central_env:
            peers = central_env.split(",")

    # إزالة عنوان الجهاز المحلي
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        peers = [ip for ip in peers if ip != local_ip]
    except Exception:
        pass

    return peers


def offload_chunk(blob: bytes, peer_ip: str) -> bool:
    """إرسال كتلة بيانات إلى peer محدّد."""
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
    """مراقبة الذاكرة واستدعاء offload عند الحاجة."""
    while True:
        free_mb = get_free_ram_mb()
        if free_mb < RAM_LIMIT_MB:
            peers = discover_peers()
            if not peers:
                print("[RAM] لا يوجد أقران متاحون حاليًا.")
            else:
                blob = bytes(CHUNK_MB * 1024 * 1024)  # كتلة وهميّة – استبدلها ببيانات حقيقيّة عند الدمج
                for ip in peers:
                    if offload_chunk(blob, ip):
                        print(f"[RAM]‎ أرسلت ‎{CHUNK_MB}‎MB إلى ‎{ip}")
                        break
                else:
                    print("[RAM] كل الأقران رفضوا التخزين أو حدث خطأ.")
        time.sleep(CHECK_INTERVAL)


def main():
    threading.Thread(target=start_api, daemon=True).start()
    monitor_loop()

if __name__ == "__main__":
    main()
