
# نظام العمل في الخلفية

## نظرة عامة
يوفر هذا النظام إمكانية تشغيل التطبيق كخدمة خلفية دون إظهار واجهات تفاعلية إلا عند الحاجة. مناسب للخوادم والأجهزة التي تعمل على مدار الساعة.

## المكونات الجديدة

### 1. خدمة العمل في الخلفية (`background_service.py`)
- تدير جميع الخدمات الأساسية في الخلفية
- توفر HTTP API للتحكم عن بُعد
- فحص دوري وإعادة تشغيل الخدمات المتوقفة
- نظام سجلات شامل

### 2. أيقونة شريط النظام (`system_tray.py`)
- تحكم سريع من شريط النظام
- إظهار/إخفاء الواجهة التفاعلية حسب الحاجة
- مراقبة حالة النظام في الوقت الفعلي

### 3. المشغل الموحد (`launcher.py`)
- واجهة موحدة لجميع أوضاع التشغيل
- تثبيت تلقائي للاعتماديات
- خيارات تشغيل متعددة

## طرق التشغيل

### التشغيل مع أيقونة شريط النظام (موصى به)
```bash
python launcher.py --tray
```

### التشغيل التفاعلي (مع واجهة)
```bash
python launcher.py --interactive
```

### التشغيل بدون واجهة (للخوادم)
```bash
python launcher.py --headless
```

### عرض حالة النظام
```bash
python launcher.py --status
```

### إيقاف النظام
```bash
python launcher.py --stop
```

## التحكم عبر HTTP API

الخدمة توفر HTTP API على المنفذ 8888:

### فحص الحالة
```bash
curl http://localhost:8888/status
```

### بدء الخدمات
```bash
curl -X POST http://localhost:8888/start
```

### إيقاف الخدمات
```bash
curl -X POST http://localhost:8888/stop
```

### إظهار الواجهة التفاعلية
```bash
curl -X POST http://localhost:8888/show-ui
```

### إخفاء الواجهة التفاعلية
```bash
curl -X POST http://localhost:8888/hide-ui
```

## الاعتماديات الإضافية

للتشغيل مع أيقونة شريط النظام:
```bash
pip install pystray Pillow
```

أو استخدم:
```bash
python launcher.py --install-deps
```

## التشغيل التلقائي

### Windows
```bash
python control.py --enable
```

### Linux (systemd)
إنشاء ملف خدمة:
```bash
sudo nano /etc/systemd/system/distributed-tasks.service
```

محتوى الملف:
```ini
[Unit]
Description=Distributed Task System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 launcher.py --headless
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

تفعيل الخدمة:
```bash
sudo systemctl enable distributed-tasks.service
sudo systemctl start distributed-tasks.service
```

### macOS
```bash
python control.py --enable
```

## المزايا

1. **العمل في الخلفية**: النظام يعمل دون إزعاج المستخدم
2. **تحكم مرن**: إظهار الواجهة عند الحاجة فقط
3. **مراقبة تلقائية**: إعادة تشغيل الخدمات المتوقفة
4. **تحكم عن بُعد**: HTTP API للتحكم من أي مكان
5. **سجلات شاملة**: تتبع جميع الأحداث والأخطاء
6. **دعم منصات متعددة**: Windows, Linux, macOS

## الاستكشاف والإصلاح

### فحص السجلات
```bash
tail -f logs/background_service.log
```

### فحص حالة الخدمات
```bash
python launcher.py --status
```

### إعادة تشغيل النظام
```bash
python launcher.py --stop
python launcher.py --tray
```

## التخصيص

يمكن تخصيص الخدمة عبر تعديل:
- منافذ الشبكة في `background_service.py`
- قائمة الخدمات المُدارة
- فترات الفحص الدوري
- مسارات السجلات
