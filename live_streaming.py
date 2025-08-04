
# live_streaming.py - نظام البث المباشر للألعاب والفيديو

import cv2
import numpy as np
import time
import threading
import logging
import asyncio
import base64
import json
from datetime import datetime
from processor_manager import should_offload
from remote_executor import execute_remotely
from functools import wraps

logging.basicConfig(level=logging.INFO)

class LiveStreamManager:
    def __init__(self):
        self.active_streams = {}
        self.processing_nodes = []
        self.load_balancer = StreamLoadBalancer()
        
    def register_processing_node(self, node_id, capabilities):
        """تسجيل عقدة معالجة جديدة"""
        self.processing_nodes.append({
            "id": node_id,
            "capabilities": capabilities,
            "load": 0.0,
            "last_ping": datetime.now()
        })
        logging.info(f"📡 تم تسجيل عقدة معالجة: {node_id}")

class StreamLoadBalancer:
    def __init__(self):
        self.node_loads = {}
        
    def get_best_node(self, task_type, nodes):
        """اختيار أفضل عقدة للمعالجة"""
        suitable_nodes = [n for n in nodes if task_type in n.get("capabilities", [])]
        if not suitable_nodes:
            return None
        return min(suitable_nodes, key=lambda x: x["load"])

def stream_offload(func):
    """ديكوراتور خاص بالبث المباشر"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        complexity = estimate_stream_complexity(func, args, kwargs)
        
        if complexity > 70 or should_offload(complexity):
            logging.info(f"📺 إرسال مهمة البث {func.__name__} للمعالجة الموزعة")
            return execute_remotely(func.__name__, args, kwargs)
        
        logging.info(f"📺 معالجة البث محلياً: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def estimate_stream_complexity(func, args, kwargs):
    """تقدير تعقيد معالجة البث"""
    if func.__name__ == "process_game_stream":
        return args[1] * args[2] / 10000  # FPS × الدقة
    elif func.__name__ == "real_time_video_enhancement":
        return args[0] * 20  # عدد التحسينات × 20
    elif func.__name__ == "multi_stream_processing":
        return len(args[0]) * 25  # عدد البثوث × 25
    elif func.__name__ == "ai_commentary_generation":
        return args[1] * 15  # طول النص × 15
    return 40

# ═══════════════════════════════════════════════════════════════
# معالجة بث الألعاب المباشر
# ═══════════════════════════════════════════════════════════════

@stream_offload
def process_game_stream(stream_data, fps, resolution, enhancements=None):
    """معالجة بث الألعاب في الوقت الفعلي"""
    start_time = time.time()
    
    if enhancements is None:
        enhancements = ["noise_reduction", "color_enhancement"]
    
    logging.info(f"🎮 معالجة بث الألعاب - FPS: {fps}, الدقة: {resolution}")
    logging.info(f"🔧 التحسينات: {enhancements}")
    
    # محاكاة معالجة الإطارات
    frame_count = len(stream_data) if isinstance(stream_data, list) else 60
    processing_per_frame = 0.01 + (len(enhancements) * 0.005)
    total_processing_time = frame_count * processing_per_frame
    
    # محاكاة المعالجة
    time.sleep(min(total_processing_time, 2))
    
    # حساب جودة البث
    quality_score = min(100, 60 + (len(enhancements) * 8) + (fps / 2))
    latency = max(50, 200 - (fps * 2))  # أقل تأخير مع FPS أعلى
    
    result = {
        "status": "success",
        "stream_type": "game",
        "fps_processed": fps,
        "resolution": resolution,
        "frames_processed": frame_count,
        "enhancements_applied": enhancements,
        "quality_score": round(quality_score, 1),
        "latency_ms": latency,
        "processing_time": time.time() - start_time,
        "bandwidth_optimized": True
    }
    
    logging.info(f"✅ تمت معالجة بث اللعبة - جودة: {result['quality_score']}%")
    return result

@stream_offload
def real_time_video_enhancement(enhancement_types, video_quality="1080p", target_fps=60):
    """تحسين الفيديو في الوقت الفعلي"""
    start_time = time.time()
    
    available_enhancements = {
        "upscaling": "تحسين الدقة",
        "noise_reduction": "إزالة التشويش",
        "color_grading": "تصحيح الألوان",
        "motion_smoothing": "تنعيم الحركة",
        "hdr_enhancement": "تحسين HDR",
        "sharpening": "زيادة الحدة",
        "stabilization": "تثبيت الصورة"
    }
    
    quality_multiplier = {"720p": 1, "1080p": 2, "1440p": 3, "4K": 5}
    multiplier = quality_multiplier.get(video_quality, 2)
    
    processing_time = len(enhancement_types) * multiplier * target_fps * 0.0001
    
    logging.info(f"📹 تحسين الفيديو المباشر - الجودة: {video_quality}")
    logging.info(f"🎯 التحسينات: {enhancement_types}")
    
    # محاكاة التحسين
    time.sleep(min(processing_time, 1.5))
    
    enhancements_applied = {}
    for enhancement in enhancement_types:
        if enhancement in available_enhancements:
            enhancements_applied[enhancement] = {
                "name": available_enhancements[enhancement],
                "improvement": round(np.random.uniform(15, 35), 1),
                "processing_cost": round(processing_time / len(enhancement_types), 4)
            }
    
    result = {
        "status": "success",
        "video_quality": video_quality,
        "target_fps": target_fps,
        "enhancements": enhancements_applied,
        "total_improvement": round(np.mean([e["improvement"] for e in enhancements_applied.values()]), 1),
        "processing_time": time.time() - start_time,
        "real_time_capable": processing_time < (1/target_fps)
    }
    
    logging.info(f"✅ تم تحسين الفيديو - تحسن: {result['total_improvement']}%")
    return result

# ═══════════════════════════════════════════════════════════════
# معالجة متعددة البثوث
# ═══════════════════════════════════════════════════════════════

@stream_offload
def multi_stream_processing(streams_data, processing_mode="parallel"):
    """معالجة عدة بثوث في نفس الوقت"""
    start_time = time.time()
    
    logging.info(f"📡 معالجة متعددة البثوث - العدد: {len(streams_data)}")
    logging.info(f"⚙️ وضع المعالجة: {processing_mode}")
    
    results = {}
    
    if processing_mode == "parallel":
        # محاكاة المعالجة المتوازية
        max_processing_time = max([s.get("complexity", 1) for s in streams_data]) * 0.1
        time.sleep(min(max_processing_time, 2))
        
        for i, stream in enumerate(streams_data):
            stream_id = f"stream_{i+1}"
            results[stream_id] = {
                "status": "processed",
                "quality": stream.get("quality", "1080p"),
                "fps": stream.get("fps", 30),
                "enhancement_applied": True,
                "processing_node": f"node_{(i % 3) + 1}"  # توزيع على 3 عقد
            }
    else:
        # معالجة تسلسلية
        total_time = sum([s.get("complexity", 1) for s in streams_data]) * 0.05
        time.sleep(min(total_time, 3))
        
        for i, stream in enumerate(streams_data):
            stream_id = f"stream_{i+1}"
            results[stream_id] = {
                "status": "processed",
                "quality": stream.get("quality", "1080p"),
                "fps": stream.get("fps", 30),
                "processing_order": i + 1
            }
    
    result = {
        "status": "success",
        "streams_processed": len(streams_data),
        "processing_mode": processing_mode,
        "results": results,
        "total_processing_time": time.time() - start_time,
        "average_quality": round(np.mean([30, 45, 60, 55]), 1),  # محاكاة متوسط الجودة
        "nodes_utilized": len(set([r.get("processing_node", "main") for r in results.values()]))
    }
    
    logging.info(f"✅ تمت معالجة {len(streams_data)} بث - العقد المستخدمة: {result['nodes_utilized']}")
    return result

# ═══════════════════════════════════════════════════════════════
# ذكاء اصطناعي للبث
# ═══════════════════════════════════════════════════════════════

@stream_offload
def ai_commentary_generation(game_events, commentary_length, language="ar"):
    """توليد تعليق ذكي للألعاب"""
    start_time = time.time()
    
    logging.info(f"🤖 توليد تعليق ذكي - الطول: {commentary_length} كلمة")
    
    # قوالب التعليق
    commentary_templates = {
        "ar": [
            "حركة رائعة من اللاعب!",
            "هذا هدف مذهل!",
            "دفاع قوي في هذه اللحظة",
            "استراتيجية ممتازة",
            "أداء استثنائي!"
        ],
        "en": [
            "Amazing move by the player!",
            "What a fantastic goal!",
            "Strong defense right there",
            "Excellent strategy",
            "Outstanding performance!"
        ]
    }
    
    processing_time = commentary_length * 0.02  # 0.02 ثانية لكل كلمة
    time.sleep(min(processing_time, 1))
    
    # توليد التعليق
    templates = commentary_templates.get(language, commentary_templates["ar"])
    generated_commentary = []
    
    for i in range(min(commentary_length // 5, len(game_events))):
        template = np.random.choice(templates)
        generated_commentary.append(template)
    
    result = {
        "status": "success",
        "language": language,
        "commentary_length": len(generated_commentary),
        "generated_text": generated_commentary,
        "game_events_analyzed": len(game_events),
        "processing_time": time.time() - start_time,
        "emotion_detection": "excited",  # محاكاة كشف المشاعر
        "context_awareness": True
    }
    
    logging.info(f"✅ تم توليد التعليق - {len(generated_commentary)} جملة")
    return result

@stream_offload
def stream_quality_optimization(stream_metadata, target_bandwidth, viewer_count):
    """تحسين جودة البث حسب النطاق الترددي وعدد المشاهدين"""
    start_time = time.time()
    
    logging.info(f"📊 تحسين جودة البث - المشاهدين: {viewer_count}")
    logging.info(f"🌐 النطاق المستهدف: {target_bandwidth} Mbps")
    
    # حساب الجودة المثلى
    base_quality = min(target_bandwidth * 200, 1080)  # حد أقصى 1080p
    
    # تعديل حسب عدد المشاهدين
    if viewer_count > 1000:
        quality_adjustment = 0.8  # تقليل الجودة للأعداد الكبيرة
    elif viewer_count > 100:
        quality_adjustment = 0.9
    else:
        quality_adjustment = 1.0
    
    optimized_quality = int(base_quality * quality_adjustment)
    
    # تحديد FPS مناسب
    if optimized_quality >= 1080:
        optimal_fps = 60
    elif optimized_quality >= 720:
        optimal_fps = 45
    else:
        optimal_fps = 30
    
    time.sleep(0.5)  # محاكاة المعالجة
    
    result = {
        "status": "success",
        "original_quality": stream_metadata.get("quality", "1080p"),
        "optimized_quality": f"{optimized_quality}p",
        "optimal_fps": optimal_fps,
        "target_bandwidth": target_bandwidth,
        "viewer_count": viewer_count,
        "bandwidth_saved": round(max(0, (1080 - optimized_quality) / 1080 * 100), 1),
        "processing_time": time.time() - start_time,
        "adaptive_streaming": True
    }
    
    logging.info(f"✅ تم تحسين البث - الجودة: {result['optimized_quality']}")
    return result

# ═══════════════════════════════════════════════════════════════
# إدارة البث المباشر
# ═══════════════════════════════════════════════════════════════

class LiveStreamCoordinator:
    def __init__(self):
        self.active_streams = {}
        self.processing_history = []
        
    def start_stream(self, stream_id, config):
        """بدء بث مباشر جديد"""
        self.active_streams[stream_id] = {
            "config": config,
            "start_time": datetime.now(),
            "status": "active",
            "processing_nodes": [],
            "viewers": 0
        }
        logging.info(f"🔴 بدء البث: {stream_id}")
        
    def distribute_processing(self, stream_id, task_type, data):
        """توزيع معالجة البث على العقد المختلفة"""
        if stream_id not in self.active_streams:
            return {"error": "البث غير موجود"}
            
        # اختيار العقدة المناسبة
        best_node = self._select_processing_node(task_type)
        
        # تنفيذ المعالجة
        if best_node:
            result = execute_remotely(task_type, [data], {})
            self.active_streams[stream_id]["processing_nodes"].append(best_node)
            return result
        else:
            # معالجة محلية
            return self._process_locally(task_type, data)
            
    def _select_processing_node(self, task_type):
        """اختيار أفضل عقدة للمعالجة"""
        # منطق اختيار العقدة (مبسط)
        return f"node_gpu_{np.random.randint(1, 4)}"
        
    def _process_locally(self, task_type, data):
        """معالجة محلية احتياطية"""
        return {"status": "processed_locally", "task": task_type}

# دالة اختبار شاملة للبث المباشر
def run_live_streaming_benchmark():
    """اختبار شامل لنظام البث المباشر"""
    print("\n📺🎮 اختبار نظام البث المباشر للألعاب والفيديو")
    print("=" * 70)
    
    # بيانات تجريبية
    game_stream_data = [f"frame_{i}" for i in range(60)]  # 60 إطار
    game_events = ["goal", "save", "foul", "corner", "yellow_card"]
    
    multi_streams = [
        {"quality": "1080p", "fps": 60, "complexity": 3},
        {"quality": "720p", "fps": 30, "complexity": 2},
        {"quality": "1440p", "fps": 45, "complexity": 4}
    ]
    
    tests = [
        ("معالجة بث لعبة", lambda: process_game_stream(game_stream_data, 60, "1920x1080", ["noise_reduction", "color_enhancement", "sharpening"])),
        ("تحسين فيديو مباشر", lambda: real_time_video_enhancement(["upscaling", "noise_reduction", "hdr_enhancement"], "1080p", 60)),
        ("معالجة متعددة البثوث", lambda: multi_stream_processing(multi_streams, "parallel")),
        ("توليد تعليق ذكي", lambda: ai_commentary_generation(game_events, 50, "ar")),
        ("تحسين جودة البث", lambda: stream_quality_optimization({"quality": "1080p"}, 5.0, 500))
    ]
    
    coordinator = LiveStreamCoordinator()
    
    for test_name, test_func in tests:
        print(f"\n🔄 تشغيل: {test_name}")
        try:
            result = test_func()
            print(f"✅ نجح: {test_name}")
            if "processing_time" in result:
                print(f"⏱️ وقت المعالجة: {result['processing_time']:.2f}s")
            if "quality_score" in result:
                print(f"⭐ جودة: {result['quality_score']}%")
        except Exception as e:
            print(f"❌ فشل: {test_name} - {str(e)}")
    
    print("\n🏁 انتهى اختبار البث المباشر")

if __name__ == "__main__":
    run_live_streaming_benchmark()
