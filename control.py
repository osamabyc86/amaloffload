import argparse
from autostart_config import AutoStartManager

def main():
    parser = argparse.ArgumentParser(description="نظام التحكم في التشغيل التلقائي")
    parser.add_argument('--enable', action='store_true', help="تفعيل التشغيل التلقائي")
    parser.add_argument('--disable', action='store_true', help="تعطيل التشغيل التلقائي")
    parser.add_argument('--status', action='store_true', help="عرض حالة التشغيل التلقائي")
    
    args = parser.parse_args()
    manager = AutoStartManager()
    
    if args.enable:
        manager.enable_autostart()
        print("✓ تم تفعيل التشغيل التلقائي")
    elif args.disable:
        manager.disable_autostart()
        print("✗ تم تعطيل التشغيل التلقائي")
    elif args.status:
        status = "مفعل" if manager.config['enabled'] else "معطل"
        print(f"حالة التشغيل التلقائي: {status}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
