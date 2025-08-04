#!/usr/bin/env python3
# offload_lib.py

import time
import math
import random
import psutil
import requests
import socket
from functools import wraps
from zeroconf import Zeroconf, ServiceBrowser
import logging

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# إعدادات التحميل
MAX_CPU = 0.6  # عتبة استخدام CPU فقط

class PeerListener:
    def __init__(self):
        self.peers = []

    def add_service(self, zc, type, name):
        info = zc.get_service_info(type, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            self.peers.append(f"{ip}:{info.port}")
            logging.info(f"🔗 جهاز مكتشف: {ip}:{info.port}")

    def update_service(self, zc, type, name):
        logging.debug(f"🔄 تم تحديث الخدمة: {name}")
        pass  # هنا فقط لتفادي التحذير

def discover_peers(timeout=1.5):
    """اكتشاف الأجهزة المتاحة - أولوية LAN ثم WAN ثم الإنترنت مع فحص المشروع"""
    import peer_discovery
    from project_identifier import verify_project_compatibility

    zc = Zeroconf()
    listener = PeerListener()
    ServiceBrowser(zc, "_http._tcp.local.", listener)
    time.sleep(timeout)
    zc.close()

    lan_peers = []
    wan_peers = []
    internet_peers = []

    for peer in listener.peers:
        ip = peer.split(':')[0]
        if verify_peer_project(ip):
            if is_local_network(ip):
                lan_peers.append(peer)
            else:
                wan_peers.append(peer)

    all_discovered = list(peer_discovery.PEERS)
    for peer_url in all_discovered:
        peer_ip = peer_url.split("://")[1].split(":")[0]
        if verify_peer_project(peer_ip):
            if is_local_network(peer_ip):
                if peer_url not in lan_peers:
                    lan_peers.append(peer_url)
            else:
                if peer_url not in wan_peers:
                    internet_peers.append(peer_url)

    all_peers = lan_peers + wan_peers + internet_peers
    logging.info(f"اكتُشف {len(all_peers)} جهاز DTS متوافق - LAN: {len(lan_peers)}, WAN: {len(wan_peers)}, Internet: {len(internet_peers)}")

    return all_peers

def verify_peer_project(ip, port=7520):
    """فحص إذا كان الجهاز يحتوي على نفس المشروع"""
    try:
        from project_identifier import verify_project_compatibility

        project_url = f"http://{ip}:{port}/project_info"
        response = requests.get(project_url, timeout=2)

        if response.status_code == 200:
            remote_info = response.json()
            return verify_project_compatibility(remote_info)

    except:
        pass
    return False

def is_local_network(ip):
    """فحص إذا كان IP في الشبكة المحلية"""
    try:
        import ipaddress
        addr = ipaddress.ip_address(ip)
        return (
            addr.is_private or
            str(addr).startswith('192.168.') or
            str(addr).startswith('10.') or
            str(addr).startswith('172.')
        )
    except:
        return False

def try_offload(peer, payload, max_retries=3):
    """محاولة إرسال المهمة إلى جهاز آخر"""
    url = f"http://{peer}/run"
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.warning(f"فشل المحاولة {attempt + 1} لـ {peer}: {str(e)}")
            time.sleep(0.5 * (attempt + 1))
    raise ConnectionError(f"فشل جميع المحاولات لـ {peer}")

def estimate_complexity(func, args, kwargs):
    """تقدير تعقيد المهمة"""
    if func.__name__ == "matrix_multiply":
        return args[0] ** 2
    elif func.__name__ == "prime_calculation":
        return args[0] / 100
    elif func.__name__ == "data_processing":
        return args[0] / 10
    elif func.__name__ == "image_processing_emulation":
        return args[0] * 5
    return 1  # قيمة افتراضية

def offload(func):
    """ديكوراتور لتوزيع المهام"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cpu = psutil.cpu_percent(interval=0.5) / 100.0
        mem = psutil.virtual_memory().available / (1024**2)
        complexity = estimate_complexity(func, args, kwargs)

        logging.info(f"حمل النظام - CPU: {cpu:.2f}, الذاكرة: {mem:.1f}MB, تعقيد المهمة: {complexity}")

        if complexity > 50 or cpu > MAX_CPU:
            try:
                peers = discover_peers()
                if peers:
                    payload = {
                        "func": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                        "complexity": complexity
                    }
                    selected_peer = random.choice(peers)
                    logging.info(f"إرسال المهمة إلى {selected_peer}")
                    return try_offload(selected_peer, payload)
            except Exception as e:
                logging.error(f"خطأ في التوزيع: {str(e)}")

        logging.info("تنفيذ المهمة محلياً")
        return func(*args, **kwargs)
    return wrapper

# المهام القابلة للتوزيع:

@offload
def matrix_multiply(size):
    """ضرب مصفوفتين عشوائيتين بالحجم"""
    import numpy as np
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    return np.dot(A, B).tolist()

@offload
def prime_calculation(n):
    """حساب الأعداد الأولية"""
    primes = []
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return {"primes_count": len(primes), "primes": primes}

@offload
def data_processing(data_size):
    """معالجة بيانات كبيرة"""
    processed_data = []
    for i in range(data_size):
        result = sum(math.sin(x) * math.cos(x) for x in range(i, i + 100))
        processed_data.append(result)
    return {"processed_items": len(processed_data)}

@offload
def image_processing_emulation(iterations):
    """محاكاة معالجة الصور"""
    results = []
    for i in range(iterations):
        fake_processing = sum(math.sqrt(x) for x in range(i * 100, (i + 1) * 100))
        results.append(fake_processing)
        time.sleep(0.01)
    return {"iterations": iterations, "results": results}
