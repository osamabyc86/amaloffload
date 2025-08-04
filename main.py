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
if os.getenv("RENDER", "false") != "true":
    subprocess.Popen([PYTHON_EXE, "peer_server.py", "--port", str(CPU_PORT)])
CPU_PORT = int(os.getenv("PORT", "7520"))

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
  import os
import json
import torch
import subprocess
from transformers import AutoTokenizer, AutoModelForCausalLM
from responses import generate_reply

# إعداد نموذج TinyLlama
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.float16,
    device_map="auto"
)

# تحميل سجل المحادثة
history_path = "history.json"

if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# تنسيق المحادثة للنموذج
def format_chat(history):
    messages = [
        {"role": "system", "content": "أنت المساعدة نورا. تحدثي بلغة عربية فصحى بسيطة."}
    ]
    messages.extend(history)
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# توليد الرد باستخدام TinyLlama
def generate_llama_response(prompt, max_new_tokens=500):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=0.7,
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# البحث عن خوادم (محاكاة)
def simulate_server_scan():
    print("نورا: أبحث عن خوادم...")
    fake_servers = ["192.168.1.5", "192.168.1.10", "192.168.1.20"]
    for server in fake_servers:
        print(f"نورا: تم العثور على خادم مفتوح في {server}")

# بدء المحادثة
def chat():
    global chat_history

    print("""
    نظام نورا الذكي (الإصدار TinyLlama)
    أوامر خاصة:
    - scan: مسح الشبكة (محاكاة)
    - خروج/exit/quit: إنهاء المحادثة
    """)

    while True:
        try:
            user_input = input("أنت: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["خروج", "exit", "quit"]:
                break
                
            if user_input.lower() == "scan":
                simulate_server_scan()
                continue

            # أولاً: حاول استخدام الرد الذكي من responses.py
            custom_reply = generate_reply(user_input, username="أسامة")
            if custom_reply:
                print("نورا:", custom_reply)
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": custom_reply})
                continue

            # إذا لم يوجد رد ذكي، استخدم TinyLlama
            chat_history.append({"role": "user", "content": user_input})
            prompt = format_chat(chat_history)
            
            print("نورا: أفكر...")
            response = generate_llama_response(prompt)
            
            # استخراج آخر رسالة من الرد (لأن النموذج يعيد التاريخ كاملاً)
            assistant_response = response.split("assistant\n")[-1].strip()
            print("نورا:", assistant_response)
            
            chat_history.append({"role": "assistant", "content": assistant_response})

            # حفظ السجل كل 3 رسائل لتجنب الكتابة المستمرة
            if len(chat_history) % 3 == 0:
                with open(history_path, "w", encoding="utf-8") as f:
                    json.dump(chat_history, f, ensure_ascii=False, indent=2)

        except KeyboardInterrupt:
            print("\nنورا: تم إنهاء المحادثة.")
            break
        except Exception as e:
            print(f"نورا: حدث خطأ: {str(e)}")
            continue

    # حفظ السجل النهائي عند الخروج
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    chat()

