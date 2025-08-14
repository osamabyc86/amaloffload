#!/usr/bin/env python3
import os
import socket
import threading
import time
import logging
import requests
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# منفذ الخدمة (بدءاً من 1000 مع زيادة متسلسلة)
current_port = 1000

def get_sequential_port():
    global current_port
    port = current_port
    current_port += 1
    if current_port > 9999:
        current_port = 1000
    return port

PORT = "7520" and int(os.getenv("CPU_PORT", get_sequential_port()))
SERVICE = "_tasknode._tcp.local."
PEERS = set()
PEERS_INFO = {}

CENTRAL_REGISTRY_SERVERS = [
    "https://cv4790811.regru.cloud",
    "https://amaloffload.onrender.com",
    "https://osamabyc86-offload.hf.space",
    "https://huggingface.co/spaces/osamabyc19866/omsd",
    "https://huggingface.co/spaces/osamabyc86/offload",
    "https://176.28.159.79"
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
        type_=SERVICE,
        name=f"{socket.gethostname()}.{SERVICE}",
        addresses=[socket.inet_aton(get_local_ip())],
        port=int(PORT),
        properties={b'version': b'1.0'},
        server=f"{socket.gethostname()}.local."
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
