
#!/usr/bin/env python3
# test_distributed_system.py - اختبار شامل لنظام التوزيع

import time
import json
import requests
import psutil
import logging
from offload_lib import discover_peers, matrix_multiply, prime_calculation, data_processing
from your_tasks import complex_operation

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_system_status():
    """فحص حالة النظام المحلي"""
    print("🔍 فحص حالة النظام المحلي...")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    print(f"⚡ استخدام المعالج: {cpu}%")
    print(f"💾 استخدام الذاكرة: {memory.percent}%")
    print(f"💿 الذاكرة المتاحة: {memory.available / (1024**2):.1f} MB")
    
    return cpu, memory.percent

def test_peer_discovery():
    """اختبار اكتشاف الأجهزة"""
    print("\n🔍 اختبار اكتشاف الأجهزة...")
    peers = discover_peers(timeout=3)
    
    if peers:
        print(f"✅ تم اكتشاف {len(peers)} جهاز:")
        for i, peer in enumerate(peers, 1):
            print(f"   {i}. {peer}")
    else:
        print("⚠️ لم يتم اكتشاف أي أجهزة")
    
    return peers

def test_direct_connection(peer_url):
    """اختبار الاتصال المباشر بجهاز"""
    print(f"\n🔗 اختبار الاتصال المباشر مع {peer_url}...")
    
    try:
        # اختبار health check
        health_url = f"{peer_url}/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ الجهاز متاح ويستجيب")
            data = response.json()
            print(f"   الحالة: {data.get('status', 'غير معروف')}")
            return True
        else:
            print(f"❌ فشل الاتصال - كود الخطأ: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return False

def test_task_execution(task_name, task_func, *args):
    """اختبار تنفيذ مهمة محددة"""
    print(f"\n⚙️ اختبار تنفيذ المهمة: {task_name}")
    
    start_time = time.time()
    try:
        result = task_func(*args)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ تم تنفيذ المهمة بنجاح")
        print(f"⏱️ الوقت المستغرق: {duration:.2f} ثانية")
        
        # طباعة النتيجة (مختصرة)
        if isinstance(result, dict):
            if "result" in result:
                result_preview = str(result["result"])[:100] + "..." if len(str(result["result"])) > 100 else str(result["result"])
                print(f"📊 النتيجة: {result_preview}")
            else:
                print(f"📊 النتيجة: {result}")
        else:
            print(f"📊 النتيجة: {result}")
            
        return True, duration, result
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ فشل تنفيذ المهمة: {str(e)}")
        return False, duration, None

def test_manual_offload(peer_url, task_data):
    """اختبار الإرسال اليدوي لمهمة"""
    print(f"\n📡 اختبار الإرسال اليدوي إلى {peer_url}")
    
    try:
        url = f"{peer_url}/run"
        response = requests.post(url, json=task_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ تم إرسال ومعالجة المهمة بنجاح")
            print(f"📊 النتيجة: {result}")
            return True, result
        else:
            print(f"❌ فشل الإرسال - كود الخطأ: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {str(e)}")
        return False, None

def comprehensive_test():
    """اختبار شامل للنظام مع تحسينات السرعة"""
    print("🚀 بدء الاختبار الشامل المحسن لنظام التوزيع")
    print("=" * 50)
    
    # إضافة مراقب الوقت
    start_total = time.time()
    
    # 1. فحص النظام المحلي
    cpu, memory = test_system_status()
    
    # 2. اكتشاف الأجهزة
    peers = test_peer_discovery()
    
    # 3. اختبار الاتصال المباشر
    available_peers = []
    for peer in peers:
        if test_direct_connection(peer):
            available_peers.append(peer)
    
    print(f"\n📊 الأجهزة المتاحة للاختبار: {len(available_peers)}")
    
    # 4. اختبار المهام المحلية
    print("\n" + "="*30 + " اختبار المهام المحلية " + "="*30)
    
    local_tests = [
        ("ضرب المصفوفات الصغيرة", matrix_multiply, 10),
        ("حساب الأعداد الأولية", prime_calculation, 100),
        ("معالجة البيانات", data_processing, 1000),
        ("العملية المعقدة", complex_operation, 5)
    ]
    
    local_results = []
    for name, func, arg in local_tests:
        success, duration, result = test_task_execution(name, func, arg)
        local_results.append((name, success, duration))
    
    # 5. اختبار الإرسال اليدوي إذا توفرت أجهزة
    if available_peers:
        print("\n" + "="*30 + " اختبار الإرسال اليدوي " + "="*30)
        
        manual_tests = [
            {"func": "matrix_multiply", "args": [15], "kwargs": {}},
            {"func": "prime_calculation", "args": [200], "kwargs": {}},
            {"func": "data_processing", "args": [500], "kwargs": {}}
        ]
        
        manual_results = []
        for test_data in manual_tests:
            peer = available_peers[0]  # استخدام أول جهاز متاح
            success, result = test_manual_offload(peer, test_data)
            manual_results.append((test_data["func"], success))
    
    # 6. اختبار التوزيع التلقائي
    print("\n" + "="*30 + " اختبار التوزيع التلقائي " + "="*30)
    
    auto_tests = [
        ("مصفوفات كبيرة (قد يتم توزيعها)", matrix_multiply, 100),
        ("أعداد أولية كثيرة (قد يتم توزيعها)", prime_calculation, 10000),
        ("بيانات كبيرة (قد يتم توزيعها)", data_processing, 50000)
    ]
    
    auto_results = []
    for name, func, arg in auto_tests:
        success, duration, result = test_task_execution(name, func, arg)
        auto_results.append((name, success, duration))
    
    # 7. تقرير النتائج النهائي
    print("\n" + "="*20 + " تقرير النتائج النهائي " + "="*20)
    
    print(f"🖥️ حالة النظام: CPU {cpu}%, Memory {memory}%")
    print(f"🌐 الأجهزة المكتشفة: {len(peers)}")
    print(f"✅ الأجهزة المتاحة: {len(available_peers)}")
    
    print("\n📊 نتائج المهام المحلية:")
    for name, success, duration in local_results:
        status = "✅" if success else "❌"
        print(f"   {status} {name}: {duration:.2f}s")
    
    if available_peers:
        print("\n📡 نتائج الإرسال اليدوي:")
        for name, success in manual_results:
            status = "✅" if success else "❌"
            print(f"   {status} {name}")
    
    print("\n🤖 نتائج التوزيع التلقائي:")
    for name, success, duration in auto_results:
        status = "✅" if success else "❌"
        print(f"   {status} {name}: {duration:.2f}s")
    
    # حساب الوقت الإجمالي
    total_duration = time.time() - start_total
    print(f"\n⏱️ الوقت الإجمالي للاختبار: {total_duration:.2f} ثانية ({total_duration/60:.1f} دقيقة)")
    print("\n🎉 اكتمل الاختبار الشامل!")

if __name__ == "__main__":
    try:
        comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع: {str(e)}")
        logging.exception("خطأ في الاختبار الشامل")
