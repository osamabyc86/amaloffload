#!/usr/bin/env python3
import os
import socket
import threading
import time
import logging
import requests
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
import random

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# منفذ الخدمة
PORT = int(os.getenv("CPU_PORT", random.randint(1000, 9999)))
SERVICE = "_tasknode._tcp.local."
PEERS = set()  # مجموعة عناوين الأقران كسلاسل نصية
PEERS_INFO = {}  # معلومات إضافية عن الأقران

# قائمة السيرفرات المركزية
CENTRAL_SERVERS = [
    "https://cv4790811.regru.cloud",
    "https://amaloffload.onrender.com",
    "https://osamabyc86-offload.hf.space"
]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def register_peer(ip, port):
    peer_url = f"http://{ip}:{port}/run"
    if peer_url not in PEERS:
        PEERS.add(peer_url)
        logger.info(f"تم تسجيل قرين جديد: {peer_url}")

def discover_lan_peers():
    class Listener:
        def add_service(self, zc, type_, name):
            info = zc.get_service_info(type_, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                register_peer(ip, info.port)

    zeroconf = Zeroconf()
    ServiceBrowser(zeroconf, SERVICE, Listener())
    return zeroconf

def main():
    logger.info("🚀 بدء نظام اكتشاف الأقران...")
    
    # تسجيل الخدمة المحلية
    zeroconf = Zeroconf()
    info = ServiceInfo(
        SERVICE,
        f"{socket.gethostname()}.{SERVICE}",
        socket.inet_aton(get_local_ip()),
        PORT,
        properties={b'version': b'1.0'}
    )
    zeroconf.register_service(info)
    
    # بدء اكتشاف الأقران
    discover_lan_peers()
    
    try:
        while True:
            logger.info(f"عدد الأقران المكتشفين: {len(PEERS)}")
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("🛑 إيقاف النظام...")
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()

if __name__ == "__main__":
    main()
