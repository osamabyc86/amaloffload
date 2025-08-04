# security_layer.py (مُحدَّث)
# ============================================================
# إدارة التشفير والتوقيع وتبادل المفاتيح بين العقد
# ============================================================

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os, base64, json
from typing import Dict


class SecurityManager:
    """طبقة أمان موحّدة لكل العقد."""

    def __init__(self, shared_secret: str):
        # مفتاح متماثل لاستخدام Fernet
        self._key = self._derive_key(shared_secret)
        self._cipher = Fernet(self._key)

        # زوج مفاتيح غير متماثل للتوقيع الرقمي
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self._public_pem = (
            self._private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )
        # مفاتيح العقد الأخرى {peer_id: public_key_obj}
        self._peer_keys: Dict[str, rsa.RSAPublicKey] = {}

    # ------------------------------------------------------------
    # تشفير / فك تشفير متماثل
    # ------------------------------------------------------------
    def encrypt_data(self, data: bytes) -> bytes:
        return self._cipher.encrypt(data)

    def decrypt_data(self, encrypted: bytes) -> bytes:
        return self._cipher.decrypt(encrypted)

    # ------------------------------------------------------------
    # توقيع/تحقّق رقمي غير متماثل
    # ------------------------------------------------------------
    def sign_task(self, task: Dict) -> Dict:
        """يُرجع نسخة موقّعة من الـtask مضافًا إليها المفتاح العام والمعرّف."""
        signature = self._private_key.sign(
            json.dumps(task, separators=(",", ":")).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        task_signed = task.copy()
        task_signed.update(
            {
                "_signature": base64.b64encode(signature).decode(),
                "sender_id": os.getenv("NODE_ID", "unknown"),
                "sender_key": self._public_pem,
            }
        )
        return task_signed

    def verify_task(self, signed_task: Dict) -> bool:
        """يتحقق من صحة التوقيع باستخدام المفتاح العام للمرسل."""
        if "_signature" not in signed_task or "sender_id" not in signed_task:
            return False
        sig = base64.b64decode(signed_task["_signature"])
        task_copy = {k: v for k, v in signed_task.items() if k not in {"_signature", "sender_key"}}

        peer_id = signed_task["sender_id"]
        if peer_id not in self._peer_keys:
            # حاول إضافة المفتاح المرسل إن وجد
            if "sender_key" in signed_task:
                self.add_peer_key(peer_id, signed_task["sender_key"])
            else:
                return False
        try:
            self._peer_keys[peer_id].verify(
                sig,
                json.dumps(task_copy, separators=(",", ":")).encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    # ------------------------------------------------------------
    # إدارة المفاتيح العامة للأقران
    # ------------------------------------------------------------
    def add_peer_key(self, peer_id: str, public_key_pem: str):
        """تخزين/تحديث المفتاح العام لعقدة أخرى."""
        self._peer_keys[peer_id] = serialization.load_pem_public_key(
            public_key_pem.encode()
        )

    # ------------------------------------------------------------
    # أدوات داخلية
    # ------------------------------------------------------------
    @staticmethod
    def _derive_key(password: str) -> bytes:
        salt = b"nora_salt_2025"  # ◀️ عدِّل في الإنتاج
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=150_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

