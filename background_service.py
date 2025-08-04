
#!/usr/bin/env python3
"""
خدمة العمل في الخلفية - تشغيل النظام كخدمة خلفية
يمكن التحكم بها عبر HTTP API أو إشارات النظام
"""

import os
import sys
import time
import signal
import logging
import threading
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request
import json
from datetime import datetime

class BackgroundService:
    def __init__(self):
        self.app = Flask(__name__)
        self.is_running = False
        self.services = {}
        self.setup_routes()
        self.setup_logging()
        
    def setup_logging(self):
        """إعداد نظام السجلات"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'background_service.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('BackgroundService')
        
    def setup_routes(self):
        """إعداد مسارات HTTP API للتحكم في الخدمة"""
        
        @self.app.route('/status')
        def status():
            """حالة الخدمة"""
            return jsonify({
                'status': 'running' if self.is_running else 'stopped',
                'services': {name: service['status'] for name, service in self.services.items()},
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            })
            
        @self.app.route('/start', methods=['POST'])
        def start_services():
            """بدء تشغيل الخدمات"""
            self.start_all_services()
            return jsonify({'message': 'Services started successfully'})
            
        @self.app.route('/stop', methods=['POST'])
        def stop_services():
            """إيقاف الخدمات"""
            self.stop_all_services()
            return jsonify({'message': 'Services stopped successfully'})
            
        @self.app.route('/restart', methods=['POST'])
        def restart_services():
            """إعادة تشغيل الخدمات"""
            self.stop_all_services()
            time.sleep(2)
            self.start_all_services()
            return jsonify({'message': 'Services restarted successfully'})
            
        @self.app.route('/show-ui', methods=['POST'])
        def show_ui():
            """إظهار الواجهة التفاعلية"""
            self.launch_ui()
            return jsonify({'message': 'UI launched'})
            
        @self.app.route('/hide-ui', methods=['POST'])
        def hide_ui():
            """إخفاء الواجهة التفاعلية"""
            self.hide_ui_windows()
            return jsonify({'message': 'UI hidden'})
            
    def start_all_services(self):
        """بدء تشغيل جميع الخدمات الخلفية"""
        self.is_running = True
        self.start_time = time.time()
        
        services_to_start = [
            ('peer_server', 'peer_server.py'),
            ('rpc_server', 'rpc_server.py'),
            ('load_balancer', 'load_balancer.py'),
            ('distributed_executor', 'main.py')
        ]
        
        for service_name, script_file in services_to_start:
            try:
                process = subprocess.Popen(
                    [sys.executable, script_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                self.services[service_name] = {
                    'process': process,
                    'status': 'running',
                    'started_at': datetime.now().isoformat(),
                    'script': script_file
                }
                
                self.logger.info(f"✅ بدء تشغيل {service_name} (PID: {process.pid})")
                
            except Exception as e:
                self.logger.error(f"❌ فشل في بدء تشغيل {service_name}: {e}")
                self.services[service_name] = {
                    'process': None,
                    'status': 'failed',
                    'error': str(e)
                }
                
    def stop_all_services(self):
        """إيقاف جميع الخدمات"""
        self.is_running = False
        
        for service_name, service_info in self.services.items():
            if service_info.get('process'):
                try:
                    service_info['process'].terminate()
                    service_info['process'].wait(timeout=5)
                    service_info['status'] = 'stopped'
                    self.logger.info(f"🛑 تم إيقاف {service_name}")
                except Exception as e:
                    # إجبار الإيقاف
                    service_info['process'].kill()
                    self.logger.warning(f"⚠️ تم إجبار إيقاف {service_name}: {e}")
                    
    def launch_ui(self):
        """تشغيل الواجهة التفاعلية عند الحاجة"""
        try:
            # تشغيل خادم الواجهة الأمامية
            ui_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.services['ui_server'] = {
                'process': ui_process,
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
            
            self.logger.info("🖥️ تم تشغيل الواجهة التفاعلية")
            
            # فتح المتصفح تلقائياً (اختياري)
            import webbrowser
            time.sleep(3)  # انتظار حتى يصبح الخادم جاهزاً
            webbrowser.open('http://localhost:5173')
            
        except Exception as e:
            self.logger.error(f"❌ فشل في تشغيل الواجهة التفاعلية: {e}")
            
    def hide_ui_windows(self):
        """إخفاء نوافذ الواجهة التفاعلية"""
        if 'ui_server' in self.services and self.services['ui_server'].get('process'):
            try:
                self.services['ui_server']['process'].terminate()
                self.services['ui_server']['status'] = 'stopped'
                self.logger.info("🔒 تم إخفاء الواجهة التفاعلية")
            except Exception as e:
                self.logger.error(f"❌ فشل في إخفاء الواجهة التفاعلية: {e}")
                
    def health_check_loop(self):
        """فحص دوري لحالة الخدمات وإعادة تشغيلها عند الحاجة"""
        while self.is_running:
            for service_name, service_info in self.services.items():
                if service_info.get('process') and service_info['status'] == 'running':
                    if service_info['process'].poll() is not None:
                        # الخدمة توقفت بشكل غير متوقع
                        self.logger.warning(f"⚠️ الخدمة {service_name} توقفت، إعادة تشغيل...")
                        self.restart_single_service(service_name)
                        
            time.sleep(30)  # فحص كل 30 ثانية
            
    def restart_single_service(self, service_name):
        """إعادة تشغيل خدمة واحدة"""
        service_info = self.services.get(service_name)
        if not service_info:
            return
            
        script_file = service_info.get('script')
        if script_file:
            try:
                process = subprocess.Popen(
                    [sys.executable, script_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.services[service_name].update({
                    'process': process,
                    'status': 'running',
                    'restarted_at': datetime.now().isoformat()
                })
                
                self.logger.info(f"✅ تم إعادة تشغيل {service_name}")
                
            except Exception as e:
                self.logger.error(f"❌ فشل في إعادة تشغيل {service_name}: {e}")
                
    def setup_signal_handlers(self):
        """إعداد معالجات الإشارات للتحكم في الخدمة"""
        def signal_handler(signum, frame):
            self.logger.info(f"تلقي إشارة {signum}, إيقاف الخدمة...")
            self.stop_all_services()
            sys.exit(0)
            
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
    def run_as_daemon(self):
        """تشغيل الخدمة كخدمة خلفية"""
        self.logger.info("🚀 بدء تشغيل الخدمة في الخلفية...")
        
        # بدء الخدمات
        self.start_all_services()
        
        # بدء حلقة الفحص الصحي
        health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        health_thread.start()
        
        # إعداد معالجات الإشارات
        self.setup_signal_handlers()
        
        # تشغيل خادم HTTP API للتحكم
        self.logger.info("🌐 تشغيل HTTP API على المنفذ 8888")
        self.app.run(host='0.0.0.0', port=8888, debug=False)

def main():
    service = BackgroundService()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            service.run_as_daemon()
        elif command == 'status':
            # فحص حالة الخدمة
            import requests
            try:
                response = requests.get('http://localhost:8888/status')
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print("❌ الخدمة غير متاحة")
        elif command == 'stop':
            # إيقاف الخدمة
            import requests
            try:
                response = requests.post('http://localhost:8888/stop')
                print(response.json()['message'])
            except:
                print("❌ فشل في إيقاف الخدمة")
        elif command == 'show-ui':
            # إظهار الواجهة التفاعلية
            import requests
            try:
                response = requests.post('http://localhost:8888/show-ui')
                print(response.json()['message'])
            except:
                print("❌ فشل في إظهار الواجهة التفاعلية")
        else:
            print("الأوامر المتاحة: start, status, stop, show-ui")
    else:
        print("استخدام: python background_service.py [start|status|stop|show-ui]")

if __name__ == "__main__":
    main()
