
#!/usr/bin/env python3
"""
مشغل موحد لنظام توزيع المهام
يوفر خيارات متعددة للتشغيل
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

def check_requirements():
    """فحص المتطلبات والاعتماديات"""
    required_files = [
        'background_service.py',
        'main.py',
        'peer_server.py',
        'rpc_server.py',
        'load_balancer.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            
    if missing_files:
        print(f"❌ ملفات مفقودة: {', '.join(missing_files)}")
        return False
        
    return True

def install_tray_dependencies():
    """تثبيت اعتماديات أيقونة شريط النظام"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pystray', 'Pillow'])
        print("✅ تم تثبيت اعتماديات أيقونة شريط النظام")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت اعتماديات أيقونة شريط النظام")
        return False

def start_background_service():
    """بدء تشغيل الخدمة في الخلفية"""
    print("🚀 بدء تشغيل الخدمة في الخلفية...")
    
    # تشغيل الخدمة الخلفية
    process = subprocess.Popen(
        [sys.executable, 'background_service.py', 'start'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # انتظار قليل للتأكد من بدء التشغيل
    time.sleep(2)
    
    if process.poll() is None:
        print("✅ تم بدء تشغيل الخدمة الخلفية بنجاح")
        return process
    else:
        print("❌ فشل في بدء تشغيل الخدمة الخلفية")
        return None

def start_with_tray():
    """تشغيل النظام مع أيقونة شريط النظام"""
    print("🖱️ تشغيل النظام مع أيقونة شريط النظام...")
    
    # بدء الخدمة الخلفية أولاً
    bg_process = start_background_service()
    if not bg_process:
        return False
        
    time.sleep(3)  # انتظار حتى تصبح الخدمة جاهزة
    
    try:
        # تشغيل أيقونة شريط النظام
        subprocess.run([sys.executable, 'system_tray.py'])
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        # إيقاف الخدمة الخلفية
        try:
            import requests
            requests.post('http://localhost:8888/stop', timeout=5)
        except:
            bg_process.terminate()
            
    return True

def start_interactive():
    """تشغيل النظام في الوضع التفاعلي"""
    print("🖥️ تشغيل النظام في الوضع التفاعلي...")
    
    # بدء الخدمة الخلفية
    bg_process = start_background_service()
    if not bg_process:
        return False
        
    time.sleep(3)
    
    # تشغيل الواجهة التفاعلية
    try:
        import requests
        requests.post('http://localhost:8888/show-ui', timeout=5)
        print("✅ تم تشغيل الواجهة التفاعلية")
        
        # فتح المتصفح
        import webbrowser
        time.sleep(2)
        webbrowser.open('http://localhost:5173')
        
        # انتظار إنهاء المستخدم
        input("اضغط Enter لإيقاف النظام...")
        
    except KeyboardInterrupt:
        pass
    finally:
        print("🛑 إيقاف النظام...")
        try:
            import requests
            requests.post('http://localhost:8888/stop', timeout=5)
        except:
            bg_process.terminate()
            
    return True

def start_headless():
    """تشغيل النظام بدون واجهة (للخوادم)"""
    print("⚙️ تشغيل النظام بدون واجهة...")
    
    try:
        # تشغيل الخدمة الخلفية والانتظار
        subprocess.run([sys.executable, 'background_service.py', 'start'])
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        
    return True

def show_status():
    """عرض حالة النظام"""
    subprocess.run([sys.executable, 'background_service.py', 'status'])

def stop_system():
    """إيقاف النظام"""
    subprocess.run([sys.executable, 'background_service.py', 'stop'])

def main():
    parser = argparse.ArgumentParser(
        description="مشغل نظام توزيع المهام الذكي",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python launcher.py --tray           # تشغيل مع أيقونة شريط النظام
  python launcher.py --interactive    # تشغيل تفاعلي مع واجهة
  python launcher.py --headless       # تشغيل بدون واجهة (للخوادم)
  python launcher.py --status         # عرض حالة النظام
  python launcher.py --stop           # إيقاف النظام
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tray', action='store_true', 
                      help='تشغيل مع أيقونة شريط النظام')
    group.add_argument('--interactive', action='store_true',
                      help='تشغيل تفاعلي مع واجهة')
    group.add_argument('--headless', action='store_true',
                      help='تشغيل بدون واجهة (للخوادم)')
    group.add_argument('--status', action='store_true',
                      help='عرض حالة النظام')
    group.add_argument('--stop', action='store_true',
                      help='إيقاف النظام')
    
    parser.add_argument('--install-deps', action='store_true',
                       help='تثبيت الاعتماديات المطلوبة')
    
    args = parser.parse_args()
    
    # فحص المتطلبات
    if not check_requirements():
        return 1
        
    # تثبيت الاعتماديات إذا طُلب ذلك
    if args.install_deps:
        install_tray_dependencies()
        return 0
        
    # تنفيذ الأمر المطلوب
    if args.status:
        show_status()
    elif args.stop:
        stop_system()
    elif args.headless:
        success = start_headless()
    elif args.interactive:
        success = start_interactive()
    elif args.tray:
        # تثبيت اعتماديات أيقونة شريط النظام إذا لم تكن موجودة
        try:
            import pystray
        except ImportError:
            print("📦 تثبيت اعتماديات أيقونة شريط النظام...")
            if not install_tray_dependencies():
                print("❌ فشل في تثبيت الاعتماديات، التشغيل في الوضع التفاعلي...")
                success = start_interactive()
            else:
                success = start_with_tray()
        else:
            success = start_with_tray()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
