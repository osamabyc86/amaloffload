import os
import requests

FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "Cairo-Regular.ttf")

# 🔥 رابط مباشر من Google Fonts CDN - Cairo Regular وزن 400
URL = "https://fonts.cdnfonts.com/s/12667/Cairo-Regular.woff"

os.makedirs(FONT_DIR, exist_ok=True)

print("[+] تحميل الخط Cairo-Regular...")
response = requests.get(URL)
if response.status_code == 200:
    with open(FONT_PATH, "wb") as f:
        f.write(response.content)
    print(f"[✅] تم حفظ الخط في {FONT_PATH}")
else:
    print(f"[❌] فشل تحميل الخط! كود الحالة: {response.status_code}")

