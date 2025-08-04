# processor_manager.py

import psutil
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)

class ResourceMonitor:
    def __init__(self):
        self.cpu_history = deque(maxlen=10)
        self.mem_history = deque(maxlen=10)
        # حد استقبال المهمات الآن 40% CPU بدل 30%
        self.receive_cpu_threshold = 0.40  

    def current_load(self):
        cpu = psutil.cpu_percent(interval=0.5) / 100.0    # كنسبة (0.0 - 1.0)
        mem = psutil.virtual_memory().available / (1024**2)  # متاح بالـ MB

        self.cpu_history.append(cpu)
        self.mem_history.append(mem)

        avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
        avg_mem = sum(self.mem_history) / len(self.mem_history)

        logging.info(f"Instant CPU: {cpu:.2%}, Instant MEM: {mem:.1f}MB")
        logging.info(f"Avg CPU: {avg_cpu:.2%}, Avg MEM: {avg_mem:.1f}MB")

        recommendation = "offload" if (avg_cpu > 0.5 or avg_mem < 2048) else "local"
        can_receive = avg_cpu <= self.receive_cpu_threshold

        return {
            "instant": {"cpu": cpu, "mem": mem},
            "average": {"cpu": avg_cpu, "mem": avg_mem},
            "recommendation": recommendation,
            "can_receive": can_receive
        }

def trigger_offload():
    """عملية توزيع المهام التجريبية"""
    print("⚠️ تم استدعاء توزيع المهام (اختباري)")

def should_offload(task_complexity=0):
    monitor = ResourceMonitor()
    status = monitor.current_load()

    avg_cpu = status['average']['cpu']
    avg_mem = status['average']['mem']

    if avg_cpu > 0.6 or avg_mem < 2048 or task_complexity > 75:
        trigger_offload()
        return True

    return False

def can_receive_task():
    """
    يعيد True إذا كان بالإمكان استقبال مهمة جديدة،
    أي عندما يكون متوسط استهلاك الـ CPU ≤ 40%.
    """
    return ResourceMonitor().current_load()["can_receive"]

if __name__ == "__main__":
    status = ResourceMonitor().current_load()
    if not status["can_receive"]:
        print(f"🚫 لا يمكن استقبال مهام جديدة (Avg CPU: {status['average']['cpu']:.0%})")
    else:
        print(f"✅ يمكن استقبال مهام جديدة (Avg CPU: {status['average']['cpu']:.0%})")

    if should_offload(80):
        print("💡 ينصح بتوزيع المهمة")
    else:
        print("✅ يمكن تنفيذ المهمة محلياً")
