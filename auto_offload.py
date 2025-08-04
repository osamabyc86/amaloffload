import subprocess
import torch
import GPUtil
import psutil
import logging

logging.getLogger().setLevel(logging.CRITICAL)  # صامت تمامًا

class DeviceManager:
    def __init__(self):
        self.gpus = self._detect_gpus()
        self.dsps = self._detect_dsps()
        # في المستقبل يمكن إضافة كروت أخرى بنفس النمط

    def _detect_gpus(self):
        """اكتشاف جميع الـ GPUs المتاحة"""
        try:
            return GPUtil.getGPUs()
        except Exception:
            return []

    def _detect_dsps(self):
        """تحقق من وجود DSP أو كروت صوتية"""
        try:
            output = subprocess.check_output(["aplay", "-l"], stderr=subprocess.DEVNULL).decode()
            if "card" in output.lower():
                return ["DSP_Audio"]
            return []
        except Exception:
            return []

    def get_device_load(self, device_type, index=0):
        """إرجاع نسبة الحمل للجهاز"""
        if device_type == "GPU" and self.gpus:
            try:
                return self.gpus[index].load * 100  # نسبة مئوية
            except Exception:
                return 0
        elif device_type == "DSP" and self.dsps:
            # هنا ما في API رسمية، نفترض DSP قليل الحمل دائمًا كمثال
            return 10
        return 0

class AutoOffloadExecutor:
    def __init__(self, executor):
        self.executor = executor
        self.devices = DeviceManager()

    def _should_offload(self, device_type, index=0):
        load = self.devices.get_device_load(device_type, index)
        return load >= 70

    def _can_receive(self, device_type, index=0):
        load = self.devices.get_device_load(device_type, index)
        return load <= 30

    def submit_auto(self, task_func, *args, task_type=None, **kwargs):
        """إرسال تلقائي حسب حالة الكروت"""
        device_type = "CPU"  # افتراضي
        if task_type == "video" and self.devices.gpus:
            device_type = "GPU"
        elif task_type == "audio" and self.devices.dsps:
            device_type = "DSP"

        if self._should_offload(device_type):
            # حمل عالي → أرسل
            self.executor.submit(task_func, *args, **kwargs)
        elif self._can_receive(device_type):
            # حمل منخفض → نفذ محليًا
            task_func(*args, **kwargs)
        else:
            # حمل متوسط → نفذ محليًا
            task_func(*args, **kwargs)
