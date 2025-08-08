# remote_executor.py (مُحدَّث: يدعم التشفير والتوقيع واختيار السيرفر ديناميكياً)
# ============================================================
# يرسل المهمّة إلى سيرفر RPC خارجي مع تشفير + توقيع،
# أو يعمل بوضع JSON صافٍ لو لم يكن SecurityManager مفعَّل.
# يستخدم قائمة الأقران المكتشفة لاختيار الـ endpoint بدل IP ثابت.
# ============================================================

import requests
import json
import os
from typing import Any

# قائمة الأقران (URLs) المستخرجة من peer_discovery
from peer_discovery import PEERS
from peer_discovery import PORT, PORT

# عنوان افتراضي احتياطي (يمكن تغييره بمتغير بيئي REMOTE_SERVER)
FALLBACK_SERVER = os.getenv(
    "REMOTE_SERVER",
    "http://89.111.171.92:PORT/run"
)

# محاولة استيراد SecurityManager (اختياري)
try:
    from security_layer import SecurityManager
    security = SecurityManager(os.getenv("SHARED_SECRET", "my_shared_secret_123"))
    SECURITY_ENABLED = True
except ImportError:
    security = None
    SECURITY_ENABLED = False


def _choose_remote_server() -> str:
    """
    يختار عنوان السيرفر الذي سترسل إليه المهمة:
    1) إذا عُيّن متغير بيئي REMOTE_SERVER، يُستخدم.
    2) وإلا إذا اكتشفنا أقران عبر LAN/Internet، نأخذ أولهم.
    3) وإلا نعود إلى FALLBACK_SERVER.
    """
    env_url = os.getenv("REMOTE_SERVER")
    if env_url:
        return env_url.rstrip('/') + '/run'
    # PEERS يحوي عناوين كاملة من نوع http://ip:port/run
    if PEERS:
        # نختار الحد الأدنى من التحميل (اختياري) أو أول عنصر
        # هنا ببساطة نأخذ أول URL
        return next(iter(PEERS))
    # استخدام الافتراضي
    return FALLBACK_SERVER.rstrip('/') + '/run'


def execute_remotely(
    func_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None
) -> Any:
    """إرسال استدعاء دالة إلى الخادم البعيد وإرجاع النتيجة."""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    task = {
        "func": func_name,
        "args": args,
        "kwargs": kwargs,
        "sender_id": "client_node"
    }

    # اختيار السيرفر الصحيح ديناميكياً
    target_url = _choose_remote_server()

    try:
        if SECURITY_ENABLED:
            # 1) وقّع المهمة ثم شفّرها
            signed_task = security.sign_task(task)
            encrypted   = security.encrypt_data(json.dumps(signed_task).encode())

            headers = {
                "X-Signature": security.signature_hex,
                "Content-Type": "application/octet-stream"
            }
            payload = encrypted  # خام ثنائي
            resp = requests.post(
                target_url,
                headers=headers,
                data=payload,
                timeout=15
            )
        else:
            # وضع التطوير: أرسل JSON صريح
            headers = {"Content-Type": "application/json"}
            resp = requests.post(
                target_url,
                headers=headers,
                json=task,
                timeout=15
            )

        resp.raise_for_status()
        data = resp.json()
        return data.get("result", "⚠️ لا يوجد نتيجة")

    except Exception as e:
        return f"❌ فشل التنفيذ البعيد على {target_url}: {e}"
