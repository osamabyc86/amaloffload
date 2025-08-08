import subprocess
import GPUtil
import psutil
import logging
from peer_discovery import PORT, PORT

logging.getLogger().setLevel(logging.CRITICAL)  # صامت

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

    # ────────────── اكتشاف الكروت ──────────────
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
        # افتراض: في المستقبل يمكن إضافة اكتشاف حقيقي لـ FPGA/TPU
        return []

    # ────────────── فحص الحمل ──────────────
    def get_device_load(self, device_type, index=0):
        try:
            if device_type == "GPU" and self.devices["GPU"]:
                return self.devices["GPU"][index].load * 100
            elif device_type == "DSP" and self.devices["DSP"]:
                return 10  # افتراضي: ما في API للحمل
            elif device_type == "NIC" and self.devices["NIC"]:
                return psutil.net_io_counters().bytes_sent / (1024 * 1024)  # مثال بسيط
            elif device_type == "STORAGE" and self.devices["STORAGE"]:
                return psutil.disk_usage('/').percent
            elif device_type == "CAPTURE" and self.devices["CAPTURE"]:
                return 20  # افتراضي: حمل منخفض
            elif device_type == "ACCELERATOR" and self.devices["ACCELERATOR"]:
                return 15  # افتراضي
            return 0
        except:
            return 0

    # ────────────── منطق 30% / 70% ──────────────
    def can_receive(self, device_type, index=0):
        return self.get_device_load(device_type, index) <= 30

    def should_offload(self, device_type, index=0):
        return self.get_device_load(device_type, index) >= 70
