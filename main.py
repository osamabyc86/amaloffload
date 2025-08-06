#!/usr/bin/env python3
"""
main.py — نقطة تشغيل نظام OffloadHelper في ملف واحد
خيارات سطر الأوامر:
  -s / --stats-interval  ثواني بين كل طباعة لإحصائية الأقران (0 = مرة واحدة فقط)
  --no-cli               تشغيل بلا قائمة تفاعلية حتى مع وجود TTY
"""
import os
import sys
import time
import threading
import subprocess
import logging
import argparse
from pathlib import Path
from typing import Any

from flask import Flask, request, jsonify
from flask_cors import CORS

# تشغيل external_server.py تلقائيًا
def start_external_server():
    try:
        logging.info("🚀 تشغيل external_server.py تلقائيًا...")
        subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "external_server.py")])
    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل external_server.py: {e}")

# ─────────────── ضبط المسارات ───────────────
FILE = Path(__file__).resolve()
BASE_DIR = FILE.parent
PROJECT_ROOT = BASE_DIR.parent
for p in (BASE_DIR, PROJECT_ROOT):
    sys.path.insert(0, str(p))

# ─────────────── إعداد السجلات ───────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/main.log", mode="a")
    ]
)

# ─────────────── تحميل متغيرات البيئة (اختياري) ───────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("🔧 تم تحميل متغيرات البيئة من ‎.env")
except ImportError:
    logging.warning("🔧 python-dotenv غير مثبَّت؛ تَخطّي .env")

# ─────────────── وحدات المشروع الداخلية ────────────────
try:
    from peer_discovery import (
        register_service_lan,
        discover_lan_loop,
        register_with_central,
        fetch_central_loop,
        PEERS
    )
    from your_tasks import matrix_multiply, prime_calculation, data_processing
    from distributed_executor import DistributedExecutor
    from auto_offload import AutoOffloadExecutor
    from peer_statistics import print_peer_statistics
    from processor_manager import ResourceMonitor
except ImportError as e:
    logging.error(f"❌ تعذّر استيراد وحدة: {e}")
    sys.exit(1)

# ─────────────── ثابتات التهيئة ───────────────
CPU_PORT = int(os.getenv("CPU_PORT", "7521"))
SHARED_SECRET = os.getenv("SHARED_SECRET", "my_shared_secret_123")
PYTHON_EXE = sys.executable

# ─────────────── خيارات سطر الأوامر ───────────────
parser = argparse.ArgumentParser()
parser.add_argument(
    "--stats-interval", "-s",
    type=int,
    default=0,
    help="ثواني بين كل طباعة لإحصائية الأقران (0 = مرة واحدة فقط)"
)
parser.add_argument(
    "--no-cli",
    action="store_true",
    help="تعطيل القائمة التفاعلية حتى عند وجود TTY"
)
args = parser.parse_args()

# ─────────────── خادم Flask ───────────────
flask_app = Flask(__name__)
CORS(flask_app, resources={r"/*": {"origins": "*"}})

@flask_app.route("/run_task", methods=["POST"])
def run_task():
    try:
        data = request.get_json() if request.is_json else request.form
        task_id = data.get("task_id")
        
        if not task_id:
            return jsonify(error="يجب تحديد task_id"), 400

        if task_id == "1":
            result = matrix_multiply(500)
        elif task_id == "2":
            result = prime_calculation(100_000)
        elif task_id == "3":
            result = data_processing(10_000)
        else:
            return jsonify(error="معرف المهمة غير صحيح"), 400

        return jsonify(result=result)

    except Exception as e:
        logging.error(f"خطأ في معالجة المهمة: {str(e)}", exc_info=True)
        return jsonify(error="حدث خطأ داخلي في الخادم"), 500

def start_flask_server():
    ip_public = os.getenv("PUBLIC_IP", "127.0.0.1")
    logging.info(f"🌐 Flask متوفر على: http://{ip_public}:{CPU_PORT}/run_task")
    flask_app.run(host="0.0.0.0", port=CPU_PORT, debug=False)

# ─────────────── خدمات خلفية محلية ───────────────
def start_services():
    try:
        subprocess.Popen([PYTHON_EXE, "peer_server.py", "--port", str(CPU_PORT)])
        subprocess.Popen([PYTHON_EXE, "load_balancer.py"])
        logging.info("✅ تم تشغيل الخدمات الخلفيّة")
    except Exception as exc:
        logging.error(f"❌ خطأ بتشغيل الخدمات الخلفية: {exc}")

# ─────────────── مهام مثالية محلية ───────────────
def example_task(x: int) -> int:
    return x * x

def benchmark(fn, *args):
    t0 = time.time()
    res = fn(*args)
    return time.time() - t0, res

# ─────────────── مراقبة الحمل التلقائية ───────────────
def auto_monitor(auto_executor):
    while True:
        try:
            monitor = ResourceMonitor().current_load()
            avg_cpu = monitor["average"]["cpu"]
            avg_mem = monitor["average"]["mem_percent"] if "mem_percent" in monitor["average"] else 0

            if avg_cpu > 0.7 or avg_mem > 85:
                logging.info("⚠️ الحمل مرتفع - أوفلود تلقائي")
                auto_executor.submit_auto(example_task, 42, task_type="video")
            elif avg_cpu < 0.3:
                logging.info("✅ الحمل منخفض - استقبال مهام")
            time.sleep(5)
        except Exception as e:
            logging.error(f"خطأ في المراقبة التلقائية: {e}")
            time.sleep(5)

# ─────────────── القائمة التفاعلية CLI ───────────────
def menu(executor: DistributedExecutor):
    tasks = {
        "1": ("ضرب المصفوفات", matrix_multiply, 500),
        "2": ("حساب الأعداد الأولية", prime_calculation, 100_000),
        "3": ("معالجة البيانات", data_processing, 10_000),
        "5": ("مهمة موزعة (مثال)", example_task, 42),
    }

    while True:
        print("\n🚀 نظام توزيع المهام الذكي")
        for k, (title, _, _) in tasks.items():
            print(f"{k}: {title}")
        print("q: خروج")
        choice = input("اختر المهمة: ").strip().lower()

        if choice == "q":
            print("🛑 تم إنهاء البرنامج.")
            break
        if choice not in tasks:
            print("⚠️ اختيار غير صحيح.")
            continue

        name, fn, arg = tasks[choice]
        print(f"\nتشغيل: {name}…")

        try:
            if choice == "5":
                logging.info("📡 إرسال المهمة إلى العقد الموزَّعة…")
                future = executor.submit(fn, arg)
                print(f"✅ النتيجة (موزعة): {future.result()}")
            else:
                dur, res = benchmark(fn, arg)
                print(f"✅ النتيجة: {res}\n⏱️ الوقت: {dur:.3f} ث")
        except Exception as exc:
            print(f"❌ خطأ في تنفيذ المهمة: {exc}")
def start_ram_manager(
        ram_limit_mb: int = 2048,
        chunk_mb: int = 64,
        interval: int = 5,
        port: int = 8765
    ):
    """
    شغّل ram_manager كخيط داخل المشروع.

    :param ram_limit_mb:  الحد الأدنى للرام الحرّة قبل الترحيل
    :param chunk_mb:      حجم الكتلة المنقولة بالميغابايت
    :param interval:      زمن الانتظار بين كل فحص (ثانية)
    :param port:          البورت الذي يستمع عليه واجهة Flask
    """
    # ضبط المتغيّرات البيئيّة بحيث يقرأها ram_manager.py
    import os
    os.environ["RAM_THRESHOLD_MB"]   = str(ram_limit_mb)
    os.environ["RAM_CHUNK_MB"]       = str(chunk_mb)
    os.environ["RAM_CHECK_INTERVAL"] = str(interval)
    os.environ["RAM_PORT"]           = str(port)

    # استيراد الملف (يُنفَّذ كـموديول) مرة واحدة
    ram_manager = importlib.import_module("ram_manager")

    # تشغيله في خيط منفصل حتى لا يحجب main loop
    threading.Thread(target=ram_manager.main, daemon=True).start()
    print(f"[MAIN] ram_manager شغَّال على البورت {port}")

# ─────────────── الدالة الرئيسية ───────────────
def main():
    # تشغيل external_server مع النظام
    start_external_server()

    start_services()

    executor = DistributedExecutor(SHARED_SECRET)
    auto_executor = AutoOffloadExecutor(executor)
    executor.peer_registry.register_service("node_main", CPU_PORT)

    for peer_url in list(PEERS):
        try:
            host, port_str = peer_url.split("//")[1].split("/run")[0].split(":")
            executor.peer_registry.register_service(
                f"peer_{host.replace('.', '_')}",
                int(port_str)
            )
        except Exception as exc:
            logging.warning(f"⚠️ تخطّي peer ({peer_url}): {exc}")

    initial_peers = [
        {"ip": host, "port": int(port)}
        for peer_url in PEERS
        if (hp := peer_url.split("//")[1].split("/run")[0]).count(":") == 1
        for host, port in [hp.split(":")]
    ]
    print_peer_statistics(initial_peers)

    if args.stats_interval > 0:
        threading.Thread(
            target=stats_loop,
            args=(args.stats_interval, executor),
            daemon=True
        ).start()

    logging.info("✅ النظام جاهز للعمل")

    threading.Thread(target=auto_monitor, args=(auto_executor,), daemon=True).start()

    if not args.no_cli and sys.stdin.isatty():
        menu(executor)
    else:
        logging.info("ℹ️ القائمة التفاعلية معطّلة (no TTY أو --no-cli)")

# ─────────────── تشغيل البرنامج ───────────────
if __name__ == "__main__":
    threading.Thread(target=register_service_lan, daemon=True).start()
    threading.Thread(target=discover_lan_loop, daemon=True).start()

    register_with_central()
    threading.Thread(target=fetch_central_loop, daemon=True).start()

    try:
        from internet_scanner import internet_scanner
        threading.Thread(
            target=internet_scanner.start_continuous_scan,
            daemon=True
        ).start()
        logging.info("🔍 بدء المسح المستمر للإنترنت")
    except ImportError:
        logging.warning("🔍 internet_scanner غير متوافر – تم التخطي")

    threading.Thread(target=start_flask_server, daemon=True).start()

    try:
        from your_control import control
        control.start()
    except ImportError:
        logging.info("🛈 your_control غير متوفّر – تشغيل افتراضي")

    main()
