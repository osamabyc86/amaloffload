from collections import Counter
import ipaddress

def print_peer_statistics(discovered_peers):
    ips = [peer['ip'] for peer in discovered_peers]
    ip_counts = Counter(ips)

    def classify_ip(ip):
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return 'داخلي'
            else:
                return 'خارجي'
        except ValueError:
            return 'محلي'

    print("\n📊 إحصائية عدد الأجهزة حسب النوع:\n")
    for ip, count in ip_counts.items():
        category = classify_ip(ip)
        print(f"• {ip} ({category}): {count} جهاز")