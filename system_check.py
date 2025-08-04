
#!/usr/bin/env python3
# system_check.py - فحص سريع لحالة النظام

import time
import requests
import psutil
import threading
from offload_lib import discover_peers

def check_local_system():
    """فحص النظام المحلي"""
    print("🔍 فحص النظام المحلي...")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    print(f"⚡ CPU: {cpu}%")
    print(f"💾 الذاكرة: {memory.percent}%")
    
    return cpu < 80 and memory.percent < 90

def check_server_running():
    """فحص إذا كان الخادم المحلي يعمل"""
    print("🌐 فحص الخادم المحلي...")
    try:
        response = requests.get("http://localhost:7520/health", timeout=3)
        if response.status_code == 200:
            print("✅ الخادم المحلي يعمل بشكل صحيح")
            return True
        else:
            print("⚠️ الخادم يستجيب لكن بخطأ")
            return False
    except:
        print("❌ الخادم المحلي غير متاح")
        return False

def check_peer_discovery():
    """فحص اكتشاف الأجهزة"""
    print("🔍 فحص اكتشاف الأجهزة...")
    try:
        peers = discover_peers(timeout=2)
        if peers:
            print(f"✅ تم اكتشاف {len(peers)} جهاز:")
            for peer in peers[:3]:  # عرض أول 3 أجهزة فقط
                print(f"   📱 {peer}")
            return True
        else:
            print("⚠️ لم يتم اكتشاف أجهزة أخرى")
            return False
    except Exception as e:
        print(f"❌ خطأ في اكتشاف الأجهزة: {e}")
        return False

def quick_task_test():
    """اختبار مهمة سريعة"""
    print("⚡ اختبار مهمة سريعة...")
    try:
        from offload_lib import matrix_multiply
        start_time = time.time()
        result = matrix_multiply(3)  # مصفوفة صغيرة
        duration = time.time() - start_time
        
        print(f"✅ تمت المعالجة في {duration:.2f} ثانية")
        return True
    except Exception as e:
        print(f"❌ فشل في تنفيذ المهمة: {e}")
        return False

def main():
    """الفحص الرئيسي"""
    print("🚀 فحص سريع لحالة النظام")
    print("=" * 40)
    
    checks = [
        ("النظام المحلي", check_local_system),
        ("الخادم المحلي", check_server_running),
        ("اكتشاف الأجهزة", check_peer_discovery),
        ("تنفيذ المهام", quick_task_test)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 40)
    print("📊 نتائج الفحص:")
    
    all_good = True
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if not result:
            all_good = False
    
    if all_good:
        print("\n🎉 كل شيء يعمل بشكل ممتاز!")
        print("💡 يمكنك الآن تشغيل: python test_distributed_system.py")
    else:
        print("\n⚠️ هناك مشاكل تحتاج إصلاح:")
        print("   1. تأكد من تشغيل: python server.py")
        print("   2. تحقق من الاتصال بالشبكة")
        print("   3. راجع ملفات السجل")

if __name__ == "__main__":
    main()
