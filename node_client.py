 #!/usr/bin/env python3
# ================================================================
# node_client.py – عميل تسجيل العُقدة في نظام AmalOffload
# ---------------------------------------------------------------
# • يختار منفذًا (من ENV أو من مجموعة PORTS).
# • يجلب عنوان الـ IP المحلي.
# • يحاول التسجيل في خادم سجلٍّ مركزي واحد تِلو الآخر،
#   وعلى كل المنافذ، حتى ينجح.
# • عند النجاح يُرجع قائمة الأقران (Peers) من الخادم.
# ================================================================

import os
import socket
import time
import logging
import random
import requests
from typing import Iterable, Tuple, List

# ⬇️ منافذ مقترحة؛ يمكنك التعديل أو توليدها ديناميكيًا
DEFAULT_PORTS = {
    7520, 7384, 9021, 6998, 5810, 9274,
    8645, 7329, 7734, 8456, 6173, 7860,
}

# ⬇️ خوادم السجل الاحتياطية بالترتيب المفضَّل
DEFAULT_REGISTRY_SERVERS = [
    "https://cv4790811.regru.cloud",
    "https://amaloffload.onrender.com",
    "https://osamabyc86-offload.hf.space",
    "http://10.229.36.125",
    "http://10.229.228.178",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class NodeClient:
    """
    عميل خفيف يعتني بالتسجيل المتكرِّر في خادم سجل مركزي.
    يمكن استيراده في أي سكربت وتشغيله في خيط منفصل.
    """

    def __init__(
        self,
        PORTs: Iterable[int] | None = None,
        registry_servers: List[str] | None = None,
        node_id: str | None = None,
    ):
        self.PORTs = set(PORTs) if PORTs else DEFAULT_PORTS
        self.registry_servers = list(registry_servers) if registry_servers else DEFAULT_REGISTRY_SERVERS
        self.node_id = node_id or os.getenv("NODE_ID", socket.gethostname())

        # مبدئيًّا اختَر منفذًا (أولوية للمتغيّر البيئي إن وُجد)
        self.port: int = int(os.getenv("CPU_PORT", random.choice(list(self.PORTs))))
        self.current_server_index: int | None = None

    # -------------------------------------------------------------------------
    @staticmethod
    def get_local_ip() -> str:
        """يحاول معرفة أفضل عنوان IP محلي لاستخدامه في الشبكة."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # لا يهم أن ينجح الاتصال الفعلي، الهدف كشف IP واجهة الخروج
                s.connect(("10.255.255.255", 1))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def _register_once(self, server: str, port: int) -> List[str]:
        """مُحاولة واحدة للتسجيل؛ تُعيد peers أو ترفع استثناءً."""
        payload = {
            "node_id": self.node_id,
            "ip": self.get_local_ip(),
            "port": port,
        }
        resp = requests.post(f"{server}/register", json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json()  # توقّع أن الخادم يُرجع قائمة أقران

    # -------------------------------------------------------------------------
    def connect_until_success(self, retry_delay: int = 5) -> Tuple[str, List[str]]:
        """
        يدور على جميع المنافذ والخوادم حتى ينجح التسجيل.
        • عند النجاح يُرجع: (عنوان الخادم، قائمة الأقران)
        • لا يرفع استثناءات؛ إمّا ينجح أو يستمر في المحاولة إلى ما لا نهاية.
        """
        logging.info("🔄 بدء محاولات التسجيل للعقدة '%s'...", self.node_id)
        while True:
            for port in self.PORTs:
                for idx, server in enumerate(self.registry_servers):
                    try:
                        peers = self._register_once(server, port)
                        # سجّل النجاح واحفظ المعلومات
                        self.port = port
                        self.current_server_index = idx
                        logging.info("✅ متصل: %s على المنفذ %s", server, port)
                        return server, peers
                    except Exception as e:
                        logging.debug("❌ %s:%s -> %s", server, port, e)
            time.sleep(retry_delay)  # انتظر قليلًا ثم أعد المحاولة

    # -------------------------------------------------------------------------
    def run_background(self) -> None:
        """
        إطلاق التسجيل في خيط منفصل؛ مفيد إذا كنت تريد
        إبقاء Main Thread للمهام الأخرى.
        """
        import threading  # استيراد متأخر لتفادي الحمل الزائد عند import
        threading.Thread(target=self.connect_until_success, daemon=True).start()


# -----------------------------------------------------------------------------  
if __name__ == "__main__":
    """
    للتجربة المباشرة:
    $ python node_client.py
    """
    client = NodeClient()
    server, peer_list = client.connect_until_success()
    logging.info("🗂️ الأقران: %s", peer_list)
