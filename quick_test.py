
#!/usr/bin/env python3
# quick_test.py - اختبار سريع لنظام التوزيع

import requests
import time
from offload_lib import discover_peers

def quick_connectivity_test():
    """اختبار سريع للاتصال والتوزيع"""
    print("🚀 اختبار سريع لنظام التوزيع")
    print("-" * 40)
    
    # 1. اكتشاف الأجهزة
    print("🔍 البحث عن الأجهزة...")
    peers = discover_peers(timeout=2)
    
    if not peers:
        print("❌ لم يتم العثور على أجهزة أخرى")
        return False
    
    print(f"✅ تم العثور على {len(peers)} جهاز:")
    for peer in peers:
        print(f"   📱 {peer}")
    
    # 2. اختبار الاتصال السريع
    working_peers = []
    for peer in peers:
        try:
            response = requests.get(f"{peer}/health", timeout=3)
            if response.status_code == 200:
                working_peers.append(peer)
                print(f"✅ {peer} - متصل ويعمل")
            else:
                print(f"⚠️ {peer} - يستجيب لكن بخطأ")
        except:
            print(f"❌ {peer} - غير متصل")
    
    if not working_peers:
        print("❌ لا توجد أجهزة تعمل بشكل صحيح")
        return False
    
    # 3. اختبار إرسال مهمة بسيطة
    print(f"\n📡 اختبار إرسال مهمة إلى {working_peers[0]}...")
    
    task = {
        "func": "matrix_multiply",
        "args": [5],
        "kwargs": {}
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{working_peers[0]}/run", json=task, timeout=10)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ تمت المعالجة بنجاح في {duration:.2f} ثانية")
            print(f"📊 النتيجة: تم ضرب مصفوفة 5x5")
            return True
        else:
            print(f"❌ فشل في المعالجة - كود الخطأ: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_connectivity_test()
    
    if success:
        print("\n🎉 النظام يعمل بشكل صحيح!")
        print("💡 يمكنك الآن تشغيل الاختبار الشامل: python test_distributed_system.py")
    else:
        print("\n⚠️ هناك مشاكل في النظام، تحقق من:")
        print("   1. تشغيل الخادم على الأجهزة الأخرى")
        print("   2. الاتصال بالشبكة")
        print("   3. إعدادات الجدار الناري")
