
#!/usr/bin/env python3
# test_monitor.py - مراقب للاختبارات الطويلة

import time
import threading
import psutil
import signal
import sys

class TestMonitor:
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        
    def monitor_system(self):
        """مراقبة النظام أثناء الاختبار"""
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                elapsed = time.time() - self.start_time
                
                print(f"\r⏱️ {elapsed/60:.1f}min | CPU: {cpu:5.1f}% | RAM: {memory.percent:5.1f}% | Press Ctrl+C to stop", end="", flush=True)
                
                # تحذير إذا كانت الموارد عالية
                if cpu > 90:
                    print(f"\n⚠️ تحذير: استخدام CPU عالي ({cpu}%)")
                if memory.percent > 90:
                    print(f"\n⚠️ تحذير: استخدام الذاكرة عالي ({memory.percent}%)")
                    
                time.sleep(5)
            except Exception as e:
                print(f"\n❌ خطأ في المراقبة: {e}")
                break
    
    def stop(self):
        """إيقاف المراقبة"""
        self.running = False
        elapsed = time.time() - self.start_time
        print(f"\n\n🛑 تم إيقاف المراقبة بعد {elapsed/60:.1f} دقيقة")

def signal_handler(signum, frame):
    """معالج إشارة الإيقاف"""
    print("\n\n🛑 تم طلب الإيقاف...")
    monitor.stop()
    sys.exit(0)

if __name__ == "__main__":
    print("🔍 بدء مراقبة النظام...")
    print("📊 سيتم عرض إحصائيات النظام كل 5 ثواني")
    print("🛑 اضغط Ctrl+C للإيقاف\n")
    
    monitor = TestMonitor()
    signal.signal(signal.SIGINT, signal_handler)
    
    # بدء المراقبة
    monitor_thread = threading.Thread(target=monitor.monitor_system, daemon=True)
    monitor_thread.start()
    
    try:
        monitor_thread.join()
    except KeyboardInterrupt:
        monitor.stop()
