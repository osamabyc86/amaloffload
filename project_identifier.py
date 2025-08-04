
"""
project_identifier.py - معرف المشروع للتحقق من الهوية
"""
import json
from flask import jsonify

PROJECT_INFO = {
    "project_name": "distributed-task-system",
    "version": "1.0",
    "description": "نظام توزيع المهام الذكي",
    "author": "DTS Team",
    "features": [
        "matrix_multiply",
        "prime_calculation", 
        "data_processing",
        "video_processing",
        "live_streaming",
        "enhanced_ai"
    ],
    "signature": "DTS_2024_SMART_DISTRIBUTION"
}

def get_project_info():
    """إرجاع معلومات المشروع"""
    return PROJECT_INFO

def verify_project_compatibility(remote_info):
    """التحقق من توافق المشروع مع جهاز آخر"""
    if not isinstance(remote_info, dict):
        return False
        
    return (
        remote_info.get("project_name") == PROJECT_INFO["project_name"] and
        remote_info.get("version") == PROJECT_INFO["version"] and
        remote_info.get("signature") == PROJECT_INFO["signature"]
    )

def create_project_endpoint():
    """إنشاء endpoint لمعلومات المشروع"""
    return jsonify(PROJECT_INFO)
