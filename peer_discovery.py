#!/usr/bin/env python3
import os
import socket
import threading
import time
import logging
import requests
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser

# 👇 إعداد الـ peer discovery عبر LAN وInternet
SERVICE = "_tasknode._tcp.local."
PORT = int(os.getenv("CPU_PORT", "7520"))
PEERS = set()  # مجموعة URLs للأقران (/run)

# 🌐 قائمة السيرفرات (Failover List)
CENTRAL_REGISTRY_SERVERS = [
    "https://cv4790811.regru.cloud",
    "http://176.28.159.25:7520",
    "http://44.209.54.138:7520",
    "http://10.229.36.125:7520"
]
current_server_index = 0


# 🟢 الحصول على IP العام أو المحلي
def get_local_ip():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=3)
        r.raise_for_status()
        return r.json().get("ip", "127.0.0.1")
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            try: s.close()
            except: pass

# 🔄 اختيار السيرفر المتاح
def get_active_central_server():
    global current_server_index
    for i in range(len(CENTRAL_REGISTRY_SERVERS)):
        server = CENTRAL_REGISTRY_SERVERS[(current_server_index + i) % len(CENTRAL_REGISTRY_SERVERS)]
        try:
            resp = requests.get(f"{server}/peers", timeout=3)
            if resp.ok:
                current_server_index = (current_server_index + i) % len(CENTRAL_REGISTRY_SERVERS)
                return server
        except:
            continue
    return None

# ❶ تسجيل الخدمة في شبكة LAN
def register_service_lan():
    zc = Zeroconf()
    local_ip = get_local_ip()
    info = ServiceInfo(
        SERVICE,
        f"{socket.gethostname()}.{SERVICE}",
        addresses=[socket.inet_aton(local_ip)],
        port=PORT,
        properties={b'load': b'0'}
    )
    try:
        zc.register_service(info)
        print(f"✅ LAN service registered: {local_ip}:{PORT}")
    except Exception as e:
        print(f"❌ LAN registration failed: {e}")

# ❷ مستمع اكتشاف LAN
class Listener:
    def add_service(self, zc, t, name):
        info = zc.get_service_info(t, name)
        if info and info.addresses:
            ip = socket.inet_ntoa(info.addresses[0])
            peer_url = f"http://{ip}:{info.port}/run"
            if peer_url not in PEERS:
                PEERS.add(peer_url)
                print(f"🔗 LAN peer discovered: {peer_url}")
    def update_service(self, zc, t, name):
        self.add_service(zc, t, name)
    def remove_service(self, zc, t, name):
        print(f"❌ LAN peer removed: {name}")

def discover_lan_loop():
    zc = Zeroconf()
    ServiceBrowser(zc, SERVICE, Listener())
    print(f"🔍 Started LAN discovery for {SERVICE}")
    while True:
        time.sleep(5)

# ❸ التسجيل في الخادم المركزي (مع Failover)
def register_with_central():
    node_id = os.getenv("NODE_ID", socket.gethostname())
    info = {"node_id": node_id, "ip": get_local_ip(), "port": PORT}
    server = get_active_central_server()
    if not server:
        print("❌ لا يوجد أي سيرفر مركزي متاح حالياً")
        return
    try:
        resp = requests.post(f"{server}/register", json=info, timeout=5)
        resp.raise_for_status()
        peers_list = resp.json()
        for p in peers_list:
            peer_url = f"http://{p['ip']}:{p['port']}/run"
            if peer_url not in PEERS:
                PEERS.add(peer_url)
                print(f"🌐 Registered and discovered central peer: {peer_url}")
    except Exception as e:
        print(f"❌ Central registration failed on {server}: {e}")

# ❹ مزامنة الأقران مع السيرفر المركزي (مع Failover)
def fetch_central_loop():
    print("🔄 Central registry sync loop started")
    while True:
        server = get_active_central_server()
        if not server:
            print("⚠️ لا يوجد سيرفر مركزي متاح للمزامنة")
            time.sleep(30)
            continue
        try:
            resp = requests.get(f"{server}/peers", timeout=5)
            resp.raise_for_status()
            peers_list = resp.json()
            for p in peers_list:
                peer_url = f"http://{p['ip']}:{p['port']}/run"
                if peer_url not in PEERS:
                    PEERS.add(peer_url)
                    print(f"🌐 Central peer discovered: {peer_url}")
        except Exception as e:
            print(f"⚠️ Fetch central peers failed on {server}: {e}")
        time.sleep(300)

# 🚀 Main
def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Peer Discovery System starting...")

    threading.Thread(target=register_service_lan, daemon=True).start()
    threading.Thread(target=discover_lan_loop, daemon=True).start()

    register_with_central()
    threading.Thread(target=fetch_central_loop, daemon=True).start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Exiting...")

if __name__ == "__main__":
    main()
