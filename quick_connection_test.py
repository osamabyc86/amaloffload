
#!/usr/bin/env python3
# اختبار سريع للتحقق من حالة النظام

import requests
import time
import json
from offload_lib import discover_peers, matrix_multiply

def test_connection():
    """اختبار سريع للاتصال"""
    print("🚀 اختبار اتصال سريع...")
    
    # 1. فحص الخادم المحلي
    try:
        response = requests.get("http://localhost:7520/health", timeout=3)
        if response.status_code == 200:
            print("✅ الخادم المحلي يعمل")
        else:
            print("❌ مشكلة في الخادم المحلي")
            return False
    except:
        print("❌ الخادم المحلي غير متاح")
        return False
    
    # 2. اختبار اكتشاف الأجهزة
    print("🔍 البحث عن الأجهزة...")
    peers = discover_peers(timeout=2)
    print(f"📱 تم اكتشاف {len(peers)} جهاز")
    
    # 3. اختبار مهمة بسيطة
    print("⚙️ اختبار مهمة بسيطة...")
    start_time = time.time()
    try:
        result = matrix_multiply(5)
        duration = time.time() - start_time
        print(f"✅ تمت المعالجة في {duration:.2f} ثانية")
        print(f"📊 النتيجة: مصفوفة {len(result)}x{len(result[0])}")
        return True
    except Exception as e:
        print(f"❌ فشل في المعالجة: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n🎉 النظام يعمل بشكل جيد!")
        print("💡 يمكنك الآن تشغيل: python test_distributed_system.py")
    else:
        print("\n⚠️ هناك مشاكل تحتاج إصلاح")
