# rpc_server.py (مُحدَّث بحيث يدعم التشفير الاختياري)
# ============================================================
# خادِم يستقبل مهام عن بُعد:
#   • إن وصلته بيانات خام (Encrypted) في Body → يفك تشفيرها ويتحقق من التوقيع.
#   • وإلا إن وصل JSON خام في Content‑Type: application/json → ينفّذ مباشرة (وضع تطويـر).
# ============================================================

from flask import Flask, request, jsonify
import smart_tasks  # «your_tasks» تمّ استيراده تحت هذا الاسم فى main.py
import logging, json
from security_layer import SecurityManager

SECURITY = SecurityManager("my_shared_secret_123")

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(name)

# ------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify(status="ok")

# ------------------------------------------------------------------
@app.route("/run", methods=["POST"])
def run():
    try:
        # 1) حاول قراءة كـ JSON مباشر (وضع التطويـر)
        if request.is_json:
            data = request.get_json()
        else:
            # 2) وإلا اعتبره Payload مُشفَّر (وضع الإنتاج)
            encrypted = request.get_data()
            try:
                decrypted = SECURITY.decrypt_data(encrypted)
                data = json.loads(decrypted.decode())
            except Exception as e:
                logging.error(f"⚠️ فشل فك التشفير: {e}")
                return jsonify(error="Decryption failed"), 400

        # 3) التحقّق من التوقيع إن وُجد
        if "_signature" in data:
            if not SECURITY.verify_task(data):
                logging.warning("❌ توقيع غير صالح")
                return jsonify(error="Invalid signature"), 403
            # أزل عناصر موقّعة إضافية
            data = {k: v for k, v in data.items() if k not in ("_signature", "sender_id")}

        func_name = data.get("func")
        args      = data.get("args", [])
        kwargs    = data.get("kwargs", {})

        fn = getattr(smart_tasks, func_name, None)
        if not fn:
            logging.warning(f"❌ لم يتم العثور على الدالة: {func_name}")
            return jsonify(error="Function not found"), 404

        logging.info(f"⚙️ تنفيذ الدالة: {func_name} من جهاز آخر")
        result = fn(*args, **kwargs)
        return jsonify(result=result)

    except Exception as e:
        logging.error(f"🔥 خطأ أثناء تنفيذ المهمة: {str(e)}")
        return jsonify(error=str(e)), 500

# ------------------------------------------------------------------
if name == "main":
    # تأكد أن المنفذ 7520 مفتوح
    app.run(host="0.0.0.0", port=7520)
