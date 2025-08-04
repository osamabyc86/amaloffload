#!/usr/bin/env python3
# central_manager.py

import time
import threading
from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---- إعداد FastAPI ----------------------------------------------------------
app = FastAPI(title="Central Task Manager")

# ---- نماذج البيانات --------------------------------------------------------

class RegisterRequest(BaseModel):
    """تسجيل أو تجديد ظهور العقدة."""
    url: str          # مثلاً: "http://203.0.113.45:7520/run"
    load: float = 0.0 # نسبة تحميل العقدة (0.0 - 1.0)، اختياري

class TaskRequest(BaseModel):
    func: str
    args: List       = []
    kwargs: Dict     = {}
    complexity: float = 0.0

# ---- سجلّ العقد ------------------------------------------------------------
# بنخزّن للعقدة: آخر timestamp و load
peers: Dict[str, Dict] = {}

HEARTBEAT_TTL = 60      # ثواني قبل اعتبار العقدة متوقفة
HEALTH_CHECK_FREQ = 30  # ثواني بين فحوص الصحة الداخلية

# ---- API للعقد لتسجيل نفسها -----------------------------------------------

@app.post("/register")
async def register_peer(req: RegisterRequest):
    """العقدة تستدعي هذه النقطة كلما انطلقت أو دورياً لتجديد ظهورها."""
    peers[req.url] = {"last_seen": time.time(), "load": req.load}
    return {"status": "ok", "peers_count": len(peers)}

# ---- API للعمليات ---------------------------------------------------------

@app.get("/peers", response_model=List[str])
async def list_peers():
    """يعيد قائمة بالعقد الصالحة بعد تنقية المتوقفة."""
    now = time.time()
    # حذف العقد المتوقفة
    for url, info in list(peers.items()):
        if now - info["last_seen"] > HEARTBEAT_TTL:
            peers.pop(url)
    return list(peers.keys())

@app.post("/dispatch")
async def dispatch_task(task: TaskRequest):
    """يتلقى مهمة ويعيد توجيهها لأفضل عقدة أو ينفذ محليّاً."""
    available = await list_peers()
    if not available:
        raise HTTPException(503, "لا توجد عقد متاحة حاليّاً")

    # خوارزمية بسيطة: الاختيار بناءً على أقل تحميل معلن
    # أو تدوير دائري إذا لم يعلن أحد عن تحميله
    best = None
    best_load = 1.1
    for url in available:
        load = peers[url].get("load", None)
        if load is None:
            best = url
            break
        if load < best_load:
            best, best_load = url, load

    if not best:
        best = available[0]

    # إعادة توجيه الطلب
    try:
        resp = requests.post(best, json=task.dict(), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"فشل التوجيه إلى {best}: {e}")

# ---- فحص دوري لصحة العقد ---------------------------------------------------

def health_check_loop():
    while True:
        now = time.time()
        for url in list(peers.keys()):
            health_url = url.replace("/run", "/health")
            try:
                r = requests.get(health_url, timeout=3)
                if r.status_code == 200:
                    peers[url]["last_seen"] = now
                    # يمكنك تحديث load من رد /health إذا وفّرته
                else:
                    peers.pop(url)
            except:
                peers.pop(url)
        time.sleep(HEALTH_CHECK_FREQ)

# ---- تشغيل الخلفيات وخادم FastAPI ------------------------------------------

if __name__ == "__main__":
    # شغل لوب الفحص الطبي في الخلفية
    threading.Thread(target=health_check_loop, daemon=True).start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1500)

