# load_balancer.py
import peer_discovery, requests, time, smart_tasks, psutil, socket

def send(peer, func, *args, **kw):
    try:
        r = requests.post(peer, json={"func": func,
                                      "args": list(args),
                                      "kwargs": kw}, timeout=12)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def choose_peer():
    """اختيار أفضل جهاز - أولوية LAN ثم WAN"""
    import socket
    
    lan_peers = []
    wan_peers = []
    
    # تصنيف الأجهزة
    for p in list(peer_discovery.PEERS):
        ip = p.split('//')[1].split(':')[0] if '//' in p else p.split(':')[0]
        if is_local_ip(ip):
            lan_peers.append(p)
        else:
            wan_peers.append(p)
    
    # أولاً: جرب الأجهزة المحلية (LAN)
    best_lan = find_best_peer(lan_peers)
    if best_lan:
        return best_lan
    
    # ثانياً: إذا لم تتوفر أجهزة محلية، جرب WAN
    if internet_available():
        best_wan = find_best_peer(wan_peers)
        return best_wan
    
    return None

def find_best_peer(peers):
    """العثور على أفضل جهاز من قائمة معينة"""
    best = None
    for p in peers:
        try:
            cpu = requests.get(p.replace("/run", "/cpu"), timeout=2).json()["usage"]
            best = (p, cpu) if best is None or cpu < best[1] else best
        except: 
            continue
    return best[0] if best else None

def is_local_ip(ip):
    """فحص إذا كان IP محلي"""
    return (
        ip.startswith('192.168.') or 
        ip.startswith('10.') or 
        ip.startswith('172.') or
        ip == '127.0.0.1'
    )

def internet_available():
    """فحص توفر الإنترنت"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

while True:
    peer = choose_peer()
    if peer:
        print(f"\n🛰️  إرسال إلى {peer}")
        res = send(peer, "prime_calculation", 30000)
    else:
        print("\n⚙️  لا أقران؛ العمل محليّ على", socket.gethostname())
        res = smart_tasks.prime_calculation(30000)
    print("🔹 النتيجة (جزئية):", str(res)[:120])
    time.sleep(10)
