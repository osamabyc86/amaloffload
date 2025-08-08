import threading
import queue
import time
from typing import Callable, Dict, List
import socket
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo
import logging
import requests
import subprocess
import psutil
import GPUtil
from processor_manager import ResourceMonitor
from peer_discovery import PORT, PORT


logging.basicConfig(level=logging.INFO)

# ─────────────── Device Manager عام ───────────────
class DeviceManager:
    def __init__(self):
        self.devices = {
            "GPU": self._detect_gpus(),
            "DSP": self._detect_dsps(),
            "NIC": self._detect_nics(),
            "STORAGE": self._detect_storage(),
            "CAPTURE": self._detect_capture(),
            "ACCELERATOR": self._detect_accelerators()
        }

    # اكتشاف الأجهزة
    def _detect_gpus(self):
        try:
            return GPUtil.getGPUs()
        except:
            return []

    def _detect_dsps(self):
        try:
            output = subprocess.check_output(["aplay", "-l"], stderr=subprocess.DEVNULL).decode()
            return ["DSP_Audio"] if "card" in output.lower() else []
        except:
            return []

    def _detect_nics(self):
        try:
            return list(psutil.net_if_addrs().keys())
        except:
            return []

    def _detect_storage(self):
        try:
            output = subprocess.check_output(["lsblk", "-o", "NAME"], stderr=subprocess.DEVNULL).decode()
            return output.split() if output else []
        except:
            return []

    def _detect_capture(self):
        try:
            output = subprocess.check_output(["v4l2-ctl", "--list-devices"], stderr=subprocess.DEVNULL).decode()
            return output.split(":")[0::2] if output else []
        except:
            return []

    def _detect_accelerators(self):
        # افتراضي: يمكن إضافة اكتشاف حقيقي مستقبلاً
        return ["Accelerator_Device"]

    # قياس الحمل
    def get_device_load(self, device_type, index=0):
        try:
            if device_type == "GPU" and self.devices["GPU"]:
                return self.devices["GPU"][index].load * 100
            elif device_type == "DSP" and self.devices["DSP"]:
                return 10  # افتراضي
            elif device_type == "NIC" and self.devices["NIC"]:
                return psutil.net_io_counters().bytes_sent / (1024 * 1024)  # MB sent كمثال
            elif device_type == "STORAGE" and self.devices["STORAGE"]:
                return psutil.disk_usage('/').percent
            elif device_type == "CAPTURE" and self.devices["CAPTURE"]:
                return 20  # افتراضي
            elif device_type == "ACCELERATOR" and self.devices["ACCELERATOR"]:
                return 15  # افتراضي
            return 0
        except:
            return 0

    # منطق الاستقبال/الإرسال
    def can_receive(self, device_type, index=0):
        return self.get_device_load(device_type, index) <= 30

    def should_offload(self, device_type, index=0):
        return self.get_device_load(device_type, index) >= 70

# ─────────────── Peer Registry ───────────────
class PeerRegistry:
    def __init__(self):
        self._peers = {}
        self._zeroconf = Zeroconf()
        self.local_node_id = socket.gethostname()

    def register_service(self, name: str, port: int, load: float = 0.0):
        service_info = ServiceInfo(
            "_tasknode._tcp.local.",
            f"{name}._tasknode._tcp.local.",
            addresses=[socket.inet_aton(self._get_local_ip())],
            port=port,
            properties={
                b'load': str(load).encode(),
                b'node_id': self.local_node_id.encode()
            },
            server=f"{name}.local."
        )
        self._zeroconf.register_service(service_info)
        logging.info(f"✅ Service registered: {name} @ {self._get_local_ip()}:{port}")

    def discover_peers(self, timeout: int = 3) -> List[Dict]:
        class Listener:
            def __init__(self):
                self.peers = []

            def add_service(self, zc, type_, name):
                try:
                    info = zc.get_service_info(type_, name, timeout=3000)
                    if info:
                        ip = socket.inet_ntoa(info.addresses[0])
                        peer_data = {
                            'ip': ip,
                            'port': info.port,
                            'load': float(info.properties.get(b'load', b'0')),
                            'node_id': info.properties.get(b'node_id', b'unknown').decode(),
                            'last_seen': time.time()
                        }
                        if peer_data not in self.peers:
                            self.peers.append(peer_data)
                        logging.info(f"✅ تمت إضافة نظير جديد: {peer_data}")
                    else:
                        logging.warning(f"⚠️ لم يتم العثور على معلومات الخدمة: {name}")
                except Exception as e:
                    logging.error(f"❌ خطأ أثناء جلب معلومات الخدمة {name}: {e}")

            def update_service(self, zc, type_, name):
                self.add_service(zc, type_, name)

            def remove_service(self, zc, type_, name):
                pass

        listener = Listener()
        ServiceBrowser(self._zeroconf, "_tasknode._tcp.local.", listener)
        time.sleep(timeout)
        return sorted(listener.peers, key=lambda x: x['load'])

    def _get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

# ─────────────── Distributed Executor ───────────────
class DistributedExecutor:
    def __init__(self, shared_secret: str):
        self.peer_registry = PeerRegistry()
        self.shared_secret = shared_secret
        self.task_queue = queue.PriorityQueue()
        self.result_cache = {}
        self.available_peers = []
        self.devices = DeviceManager()
        self._init_peer_discovery()

    def _init_peer_discovery(self):
        def discovery_loop():
            while True:
                self.available_peers = self.peer_registry.discover_peers()
                logging.info(f"✅ Discovered peers: {self.available_peers}")
                time.sleep(10)

        threading.Thread(target=discovery_loop, daemon=True).start()

    def submit(self, task_func: Callable, *args, task_type=None, **kwargs):
        monitor = ResourceMonitor().current_load()
        avg_cpu = monitor["average"]["cpu"]
        avg_mem = monitor["average"]["mem_percent"] if "mem_percent" in monitor["average"] else 0

        # تحديد نوع الجهاز
        device_type = task_type.upper() if task_type else "CPU"

        # فحص الحمل
        if (avg_cpu > 0.6 or avg_mem > 85 or self.devices.should_offload(device_type)):
            logging.info(f"⚠️ الحمل مرتفع على {device_type} - إرسال المهمة للأقران")
            self._offload_task(task_func, *args, **kwargs)
        elif (avg_cpu <= 0.3 and self.devices.can_receive(device_type)):
            logging.info(f"✅ الحمل منخفض على {device_type} - تنفيذ المهمة محلياً")
            return task_func(*args, **kwargs)
        else:
            logging.info(f"ℹ️ الحمل متوسط على {device_type} - تنفيذ المهمة محلياً")
            return task_func(*args, **kwargs)

    def _offload_task(self, task_func: Callable, *args, **kwargs):
        task_id = f"{task_func.__name__}_{time.time()}"

        task = {
            'task_id': task_id,
            'function': task_func.__name__,
            'args': args,
            'kwargs': kwargs,
            'sender_id': self.peer_registry.local_node_id
        }

        if self.available_peers:
            lan_peers = [p for p in self.available_peers if self._is_local_ip(p['ip'])]
            wan_peers = [p for p in self.available_peers if not self._is_local_ip(p['ip'])]

            if lan_peers:
                peer = min(lan_peers, key=lambda x: x['load'])
                logging.info(f"✅ Sending task {task_id} to LAN peer {peer['node_id']}")
            else:
                peer = min(wan_peers, key=lambda x: x['load'])
                logging.info(f"✅ Sending task {task_id} to WAN peer {peer['node_id']}")

            self._send_to_peer(peer, task)
        else:
            logging.warning("⚠️ لا توجد أجهزة متاحة - سيتم تنفيذ المهمة محلياً")
            task_func(*args, **kwargs)

    def _is_local_ip(self, ip: str) -> bool:
        return (
            ip.startswith('192.168.') or 
            ip.startswith('10.') or 
            ip.startswith('172.') or
            ip == '127.0.0.1'
        )

    def _send_to_peer(self, peer: Dict, task: Dict):
        try:
            url = f"http://{peer['ip']}:{peer['port']}/run"
            response = requests.post(url, json=task, timeout=10)
            response.raise_for_status()
            logging.info(f"✅ Response from peer: {response.text}")
            return response.json()
        except Exception as e:
            logging.error(f"❌ فشل إرسال المهمة لـ {peer['node_id']}: {e}")
            return None

# ─────────────── تشغيل رئيسي ───────────────
if __name__ == "__main__":
    executor = DistributedExecutor("my_secret_key")
    executor.peer_registry.register_service("node1", PORT, load=0.1)
    print("✅ نظام توزيع المهام جاهز...")

    def example_task(x):
        return x * x

    executor.submit(example_task, 5, task_type="GPU")
