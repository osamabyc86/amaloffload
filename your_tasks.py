import math
import numpy as np
from offload_lib import offload
from peer_discovery import PORT, PORT

# الدوال الأساسية (محليّة)
def prime_calculation(n: int):
    """ترجع قائمة الأعداد الأوليّة حتى n مع عددها"""
    primes = [num for num in range(2, n + 1)
              if all(num % p != 0 for p in range(2, int(math.sqrt(num)) + 1))]
    return {"count": len(primes), "primes": primes}

def matrix_multiply(size: int):
    """ضرب مصفوفات عشوائيّة (size × size)"""
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    return {"result": (A @ B).tolist()}

def data_processing(data_size: int):
    """تنفيذ معالجة بيانات بسيطة كتجربة"""
    data = np.random.rand(data_size)
    return {"mean": float(np.mean(data)), "std_dev": float(np.std(data))}

# المهام القابلة للتوزيع
@offload
def distributed_matrix_multiply(size):
    """ضرب المصفوفات (قابل للتوزيع)"""
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    return {"result": (A @ B).tolist()}

@offload
def distributed_prime_calculation(n):
    """حساب الأعداد الأولية (قابل للتوزيع)"""
    primes = [num for num in range(2, n + 1)
              if all(num % p != 0 for p in range(2, int(math.sqrt(num)) + 1))]
    return {"count": len(primes), "primes": primes}

@offload
def distributed_data_processing(size):
    """معالجة بيانات كبيرة (قابل للتوزيع)"""
    data = np.random.rand(size)
    return {"mean": float(np.mean(data)), "std_dev": float(np.std(data))}

@offload
def complex_operation(x):
    """مهمة معقدة قابلة للتوزيع"""
    result = sum(i ** 2 for i in range(x * 1000))
    return result

# مهام الفيديو
@offload
def video_format_conversion(duration_seconds, quality_level, input_format="mp4", output_format="avi"):
    """تحويل صيغة الفيديو"""
    from video_processing import video_format_conversion as vfc
    return vfc(duration_seconds, quality_level, input_format, output_format)

@offload
def video_effects_processing(video_length, effects_count, resolution="1080p"):
    """معالجة تأثيرات الفيديو"""
    from video_processing import video_effects_processing as vep
    return vep(video_length, effects_count, resolution)

@offload
def render_3d_scene(objects_count, resolution_width, resolution_height,
                    lighting_quality="medium", texture_quality="high"):
    """رندر مشهد ثلاثي الأبعاد"""
    from video_processing import render_3d_scene as r3d
    return r3d(objects_count, resolution_width, resolution_height,
               lighting_quality, texture_quality)

@offload
def physics_simulation(objects_count, frames_count, physics_quality="medium"):
    """محاكاة الفيزياء"""
    from video_processing import physics_simulation as ps
    return ps(objects_count, frames_count, physics_quality)

@offload
def game_ai_processing(ai_agents_count, decision_complexity, game_state_size):
    """معالجة ذكاء الألعاب"""
    import time
    start_time = time.time()
    total_operations = ai_agents_count * decision_complexity * game_state_size
    processing_time = total_operations / 100_000
    time.sleep(min(processing_time, 1))
    return {
        "status": "success",
        "ai_agents": ai_agents_count,
        "decision_complexity": decision_complexity,
        "total_operations": total_operations,
        "processing_time": time.time() - start_time,
        "server_processed": True
    }

# مهام البث المباشر
@offload
def process_game_stream(stream_data, fps, resolution, enhancements=None):
    from live_streaming import process_game_stream as pgs
    return pgs(stream_data, fps, resolution, enhancements)

@offload
def real_time_video_enhancement(enhancement_types, video_quality="1080p", target_fps=60):
    from live_streaming import real_time_video_enhancement as rtve
    return rtve(enhancement_types, video_quality, target_fps)

@offload
def multi_stream_processing(streams_data, processing_mode="parallel"):
    from live_streaming import multi_stream_processing as msp
    return msp(streams_data, processing_mode)

@offload
def ai_commentary_generation(game_events, commentary_length, language="ar"):
    from live_streaming import ai_commentary_generation as acg
    return acg(game_events, commentary_length, language)

@offload
def stream_quality_optimization(stream_metadata, target_bandwidth, viewer_count):
    from live_streaming import stream_quality_optimization as sqo
    return sqo(stream_metadata, target_bandwidth, viewer_count)

