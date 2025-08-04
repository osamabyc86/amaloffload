import socket
import time
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo

class Listener:
    def __init__(self):
        self.peers = []

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            peer_data = {
                'ip': ip,
                'port': info.port,
                'load': float(info.properties.get(b'load', 0)),
                'node_id': info.properties.get(b'node_id', b'unknown').decode(),
                'last_seen': time.time()
            }
            if peer_data not in self.peers:
                self.peers.append(peer_data)

    def update_service(self, zc, type_, name):
        """مطلوب بواسطة Zeroconf"""
        self.add_service(zc, type_, name)

    def remove_service(self, zc, type_, name):
        """اختياري"""
        pass

def register_service(ip: str, port: int, load: float = 0.0):
    zc = Zeroconf()
    service_name = f"{socket.gethostname()}-{int(time.time())}._tasknode._tcp.local."
    service_info = ServiceInfo(
        "_tasknode._tcp.local.",
        service_name,
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            b'load': str(load).encode(),
            b'node_id': socket.gethostname().encode()
        }
    )
    zc.register_service(service_info)
    print(f"✅ Service registered: {service_name} @ {ip}:{port}")
    return zc  # أبقِ المرجع حياً

def discover_peers(timeout=2):
    zc = Zeroconf()
    listener = Listener()
    ServiceBrowser(zc, "_tasknode._tcp.local.", listener)
    time.sleep(timeout)
    zc.close()
    return listener.peers

if __name__ == "__main__":
    local_ip = socket.gethostbyname(socket.gethostname())
    port = 7520

    zc = register_service(local_ip, port, load=0.1)

    peers = discover_peers()
    print("✅ Available peers:", peers)

    input("🔵 Press Enter to exit...\n")
    zc.close()

