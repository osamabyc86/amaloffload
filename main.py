#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — نظام توزيع المهام الذكي
"""
import os
import sys
import time
import threading
import subprocess
import logging
import argparse
import socket
import random
import requests
import importlib.util
from pathlib import Path
from typing import Any
from flask import Flask, request, jsonify
from flask_cors import CORS

# ─────────────── إعدادات المسارات ───────────────
FILE = Path(__file__).resolve()
BASE_DIR = FILE.parent
sys.path.insert(0, str(BASE_DIR))

# ─────────────── إعداد السجلات ───────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/main.log", mode="a", encoding="utf-8")
    ]
)

# ─────────────── تحميل متغيرات البيئة ───────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("تم تحميل متغيرات البيئة من .env")
except ImportError:
    logging.warning("python-dotenv غير مثبَّت؛ تَخطّي .env")

# ─────────────── ثوابت التهيئة ───────────────
CPU_PORT = int(os.getenv("CPU_PORT", "5297"))
SHARED_SECRET = os.getenv("SHARED_SECRET", "my_shared_secret_123")
PYTHON_EXE = sys.executable

# ─────────────── خيارات سطر الأوامر ───────────────
parser = argparse.ArgumentParser(description="نظام توزيع المهام الذكي")
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

# ─────────────── متغيرات النظام ───────────────
PEERS = set()  # مجموعة عناوين الأقران كسلاسل نصية
PEERS_INFO = {}  # قاموس لحفظ معلومات الأقران الكاملة
current_server_index = 0

# ─────────────── دوال اكتشاف الأقران ───────────────
def register_service_lan():
    """تسجيل الخدمة على الشبكة المحلية"""
    while True:
        try:
            logging.info("جارٍ تسجيل الخدمة على الشبكة المحلية...")
            time.sleep(10)
        except Exception as e:
            logging.error(f"خطأ في تسجيل الخدمة: {e}")

def discover_lan_loop():
    """اكتشاف الأقران على الشبكة المحلية"""
    while True:
        try:
            logging.info("جارٍ مسح الشبكة المحلية...")
            time.sleep(15)
        except Exception as e:
            logging.error(f"خطأ في اكتشاف الأقران: {e}")

def fetch_central_loop():
    """جلب تحديثات من السيرفر المركزي"""
    while True:
        try:
            logging.info("جارٍ تحديث قائمة الأقران...")
            time.sleep(30)
        except Exception as e:
            logging.error(f"خطأ في جلب التحديثات: {e}")

# ─────────────── دوال مساعدة ───────────────
def get_local_ip():
    """الحصول على عنوان IP المحلي"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def add_peer(peer_data):
    """إضافة قرين جديد إلى النظام"""
    peer_url = f"http://{peer_data['ip']}:{peer_data['port']}/run"
    if peer_url not in PEERS:
        PEERS.add(peer_url)
        PEERS_INFO[peer_url] = peer_data
        logging.info(f"تمت إضافة قرين جديد: {peer_url}")
    return peer_url

def benchmark(fn, *args):
    """قياس زمن تنفيذ الدالة"""
    t0 = time.time()
    res = fn(*args)
    return time.time() - t0, res

def load_and_run_peer_discovery():
    """تحميل وتشغيل ملف peer_discovery.py"""
    try:
        peer_discovery_path = Path(__file__).parent / "peer_discovery.py"
        if not peer_discovery_path.exists():
            raise FileNotFoundError("ملف peer_discovery.py غير موجود")
        
        spec = importlib.util.spec_from_file_location("peer_discovery_module", peer_discovery_path)
        peer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(peer_module)
        
        logging.info("تم تحميل peer_discovery.py بنجاح")
        return peer_module
    except Exception as e:
        logging.error(f"خطأ في تحميل peer_discovery.py: {str(e)}")
        return None

# ─────────────── دوال المهام ───────────────
def example_task(x: int) -> int:
    """دالة مثال بديلة إذا لم تكن موجودة في your_tasks.py"""
    return x * x

def matrix_multiply(size: int) -> list:
    """ضرب المصفوفات (بديل مؤقت)"""
    return [[i*j for j in range(size)] for i in range(size)]

def prime_calculation(limit: int) -> list:
    """حساب الأعداد الأولية (بديل مؤقت)"""
    primes = []
    for num in range(2, limit):
        if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            primes.append(num)
    return primes

def data_processing(size: int) -> dict:
    """معالجة البيانات (بديل مؤقت)"""
    return {i: i**2 for i in range(size)}

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
    logging.info(f"Flask متوفر على: http://{ip_public}:{CPU_PORT}/run_task")
    flask_app.run(host="0.0.0.0", port=CPU_PORT, debug=False)

# ─────────────── دوال النظام الأساسية ───────────────
def connect_until_success():
    global CPU_PORT, current_server_index
    
    peer_module = load_and_run_peer_discovery()
    if peer_module is None:
        logging.warning("سيستمر التشغيل بدون peer_discovery.py")
        return None, []
    
    CENTRAL_REGISTRY_SERVERS = getattr(peer_module, 'CENTRAL_REGISTRY_SERVERS', [])
    if not CENTRAL_REGISTRY_SERVERS:
        logging.error("قائمة السيرفرات المركزية فارغة")
        return None, []
    
    while True:
        for port in [CPU_PORT, 5298, 5299]:
            for idx, server in enumerate(CENTRAL_REGISTRY_SERVERS):
                info = {
                    "node_id": os.getenv("NODE_ID", socket.gethostname()),
                    "ip": get_local_ip(),
                    "port": port
                }
                try:
                    resp = requests.post(f"{server}/register", json=info, timeout=5)
                    resp.raise_for_status()
                    CPU_PORT = port
                    current_server_index = idx
                    logging.info(f"تم الاتصال بالسيرفر: {server} على المنفذ {CPU_PORT}")
                    
                    # معالجة قائمة الأقران المستلمة
                    peers_list = resp.json()
                    peer_urls = []
                    for p in peers_list:
                        peer_url = add_peer(p)
                        peer_urls.append(peer_url)
                    return server, peer_urls
                    
                except Exception as e:
                    logging.warning(f"فشل الاتصال بـ {server}: {str(e)}")
        time.sleep(5)

def main():
    """الدالة الرئيسية لتشغيل النظام"""
    # تشغيل الخدمات الأساسية
    try:
        subprocess.Popen([PYTHON_EXE, "peer_server.py", "--port", str(CPU_PORT)])
        subprocess.Popen([PYTHON_EXE, "load_balancer.py"])
        logging.info("تم تشغيل الخدمات الخلفيّة")
    except Exception as exc:
        logging.error(f"خطأ بتشغيل الخدمات الخلفية: {exc}")

    # الاتصال بالسيرفر المركزي
    server, initial_peers = connect_until_success()
    
    # تشغيل خادم Flask
    threading.Thread(target=start_flask_server, daemon=True).start()

    # البقاء في حلقة رئيسية
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("تم إنهاء البرنامج.")

if __name__ == "__main__":
    # إضافة القرين المحلي
    add_peer({"ip": "127.0.0.1", "port": CPU_PORT})
    
    # تشغيل خدمات اكتشاف الأقران
    threading.Thread(target=register_service_lan, daemon=True).start()
    threading.Thread(target=discover_lan_loop, daemon=True).start()
    threading.Thread(target=fetch_central_loop, daemon=True).start()

    # بدء النظام الرئيسي
    main()
