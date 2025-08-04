
#!/usr/bin/env python3
"""
أيقونة شريط النظام للتحكم في الخدمة الخلفية
"""

import sys
import threading
import requests
import webbrowser
from pathlib import Path

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("⚠️ pystray غير متوفر، تشغيل بدون أيقونة النظام")

class SystemTrayController:
    def __init__(self):
        self.base_url = "http://localhost:8888"
        self.icon = None
        
    def create_icon_image(self):
        """إنشاء صورة الأيقونة"""
        # إنشاء صورة بسيطة 64x64
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        
        # رسم دائرة بسيطة
        draw.ellipse([16, 16, 48, 48], fill='white')
        draw.ellipse([20, 20, 44, 44], fill='blue')
        
        return image
        
    def get_service_status(self):
        """الحصول على حالة الخدمة"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=2)
            return response.json()
        except:
            return None
            
    def start_services(self, icon, item):
        """بدء تشغيل الخدمات"""
        try:
            requests.post(f"{self.base_url}/start", timeout=5)
            self.update_menu()
        except Exception as e:
            print(f"فشل في بدء الخدمات: {e}")
            
    def stop_services(self, icon, item):
        """إيقاف الخدمات"""
        try:
            requests.post(f"{self.base_url}/stop", timeout=5)
            self.update_menu()
        except Exception as e:
            print(f"فشل في إيقاف الخدمات: {e}")
            
    def show_ui(self, icon, item):
        """إظهار الواجهة التفاعلية"""
        try:
            requests.post(f"{self.base_url}/show-ui", timeout=5)
            # فتح المتصفح
            webbrowser.open('http://localhost:5173')
        except Exception as e:
            print(f"فشل في إظهار الواجهة: {e}")
            
    def hide_ui(self, icon, item):
        """إخفاء الواجهة التفاعلية"""
        try:
            requests.post(f"{self.base_url}/hide-ui", timeout=5)
        except Exception as e:
            print(f"فشل في إخفاء الواجهة: {e}")
            
    def open_dashboard(self, icon, item):
        """فتح لوحة التحكم"""
        webbrowser.open('http://localhost:5173/dashboard')
        
    def show_status(self, icon, item):
        """إظهار حالة النظام"""
        status = self.get_service_status()
        if status:
            status_text = f"حالة النظام: {status['status']}\n"
            status_text += f"الخدمات النشطة: {len([s for s in status['services'].values() if s == 'running'])}\n"
            status_text += f"وقت التشغيل: {int(status['uptime'])} ثانية"
            print(status_text)
        else:
            print("❌ لا يمكن الوصول للخدمة")
            
    def quit_app(self, icon, item):
        """إنهاء التطبيق"""
        self.stop_services(icon, item)
        icon.stop()
        
    def update_menu(self):
        """تحديث قائمة الأيقونة"""
        if self.icon:
            status = self.get_service_status()
            is_running = status and status['status'] == 'running'
            
            menu = pystray.Menu(
                item('حالة النظام', self.show_status),
                item('---'),
                item('إظهار الواجهة', self.show_ui),
                item('إخفاء الواجهة', self.hide_ui),
                item('لوحة التحكم', self.open_dashboard),
                item('---'),
                item('بدء الخدمات', self.start_services, enabled=not is_running),
                item('إيقاف الخدمات', self.stop_services, enabled=is_running),
                item('---'),
                item('إنهاء', self.quit_app)
            )
            
            self.icon.menu = menu
            
    def create_menu(self):
        """إنشاء قائمة الأيقونة"""
        return pystray.Menu(
            item('حالة النظام', self.show_status),
            item('---'),
            item('إظهار الواجهة', self.show_ui),
            item('إخفاء الواجهة', self.hide_ui),
            item('لوحة التحكم', self.open_dashboard),
            item('---'),
            item('بدء الخدمات', self.start_services),
            item('إيقاف الخدمات', self.stop_services),
            item('---'),
            item('إنهاء', self.quit_app)
        )
        
    def run(self):
        """تشغيل أيقونة شريط النظام"""
        if not TRAY_AVAILABLE:
            print("❌ مكتبة pystray غير متوفرة")
            return
            
        # إنشاء الأيقونة
        image = self.create_icon_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "نظام توزيع المهام",
            image,
            menu=menu
        )
        
        # تحديث دوري للقائمة
        def update_loop():
            import time
            while True:
                time.sleep(5)
                if self.icon and hasattr(self.icon, '_running') and self.icon._running:
                    self.update_menu()
                else:
                    break
                    
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        print("🖱️ تشغيل أيقونة شريط النظام...")
        self.icon.run()

def main():
    controller = SystemTrayController()
    controller.run()

if __name__ == "__main__":
    main()
