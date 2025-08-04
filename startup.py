import subprocess
import time
import logging
import sys
from autostart_config import AutoStartManager
from distributed_executor import DistributedExecutor

PY = sys.executable  # مسار بايثون الحالي

SERVICES = [
    ("peer_server.py", "Peer‑Server"),
    ("rpc_server.py", "RPC‑Server"),
    ("server.py", "REST‑Server"),  # يعمل على 7521 حاليًا
    ("load_balancer.py", "Load‑Balancer"),
]


def launch_services():
    procs = []
    for script, name in SERVICES:
        try:
            p = subprocess.Popen([PY, script])
            logging.info(f"✅ {name} قيد التشغيل (PID={p.pid})")
            procs.append(p)
        except FileNotFoundError:
            logging.error(f"❌ لم يُعثَر على {script}; تخطَّيته")
            return procs


def main():
    # إعداد السجلات مع دعم وضع الخلفية
    import os

    # إنشاء مجلد السجلات
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/startup.log"),
            logging.StreamHandler()  # إظهار السجلات في وحدة التحكم أيضاً
        ]
    )

    try:
        cfg = AutoStartManager().config
        if not cfg.get("enabled", True):
            logging.info("التشغيل التلقائي مُعطل في الإعدادات")
            return

        # فحص إذا كانت الخدمة الخلفية متاحة
        background_service_available = os.path.exists("background_service.py")

        if background_service_available:
            logging.info("🔄 تشغيل الخدمة الخلفية المحسّنة...")
            # تشغيل الخدمة الخلفية الجديدة
            try:
                subprocess.Popen([PY, "background_service.py", "start"])
                logging.info("✅ تم بدء تشغيل الخدمة الخلفية المحسّنة")
                return
            except Exception as e:
                logging.warning(f"⚠️ فشل في تشغيل الخدمة الخلفية المحسّنة: {e}")
                logging.info("🔄 العودة إلى الطريقة التقليدية...")

        # الطريقة التقليدية (fallback)
        logging.info("🚀 تشغيل الخدمات بالطريقة التقليدية...")

        # 1) تشغيل الخدمات الخلفيّة
        procs = launch_services()

        # 2) تهيئة نظام التنفيذ الموزع (ليتعرّف على هذا الجهاز كعقدة)
        executor = DistributedExecutor("my_shared_secret_123")
        executor.peer_registry.register_service("auto_node", 7520)
        logging.info("🚀 العقدة auto_node مُسجّلة في الـRegistry على 7520")

        # 3) حلقة إبقاء حيّة مع فحص العمليات
        while True:
            time.sleep(30)
            for p, (script, name) in zip(procs, SERVICES):
                if p.poll() is not None:
                    logging.warning(f"⚠️ الخدمة {name} توقفت بشكل غير متوقع… إعادة تشغيل")
                    new_p = subprocess.Popen([PY, script])
                    procs[procs.index(p)] = new_p
                    logging.info(f"✅ {name} أُعيد تشغيلها (PID={new_p.pid})")

    except KeyboardInterrupt:
        logging.info("📴 إيقاف الخدمات يدويًا")
    except Exception as e:
        logging.error(f"خطأ في التشغيل التلقائي: {e}")
    finally:
        # إيقاف العمليات بأمان
        try:
            for p in procs:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        except:
            pass


if __name__ == "main":
    main()