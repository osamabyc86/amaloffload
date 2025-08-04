# peer_server.py

from flask import Flask, request, jsonify  # استيراد request و jsonify مع Flask
import psutil
import smart_tasks
import time
import socket
import peer_discovery  # إذا كان يستخدم لاحقًا

app = Flask(__name__)  # إنشاء التطبيق

@app.route("/cpu")
def cpu():
    # يعيد نسبة استخدام المعالج
    return jsonify(usage=psutil.cpu_percent(interval=0.3))

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(force=True)
    fn_name = data.get("func")
    fn = getattr(smart_tasks, fn_name, None)
    if not fn:
        return jsonify(error="function-not-found"), 404
    try:
        start = time.time()
        result = fn(*data.get("args", []), **data.get("kwargs", {}))
        return jsonify(
            result=result,
            host=socket.gethostname(),
            took=round(time.time() - start, 3)
        )
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":  # التصحيح هنا
    app.run(host="0.0.0.0", port=7520)

