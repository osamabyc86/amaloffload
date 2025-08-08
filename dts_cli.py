# dts_cli.py
import click
from dashboard import app
from rpc_server import app as rpc_app
import threading
from peer_discovery import PORT, PORT
@click.group()
def cli():
    pass

@cli.command()
def start():
    """بدء النظام الموزع"""
    print("جارِ تشغيل النظام الموزع...")
    
    # تشغيل واجهة التحكم في خيط منفصل
    dashboard_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000)
    )
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # تشغيل خادم RPC
    rpc_app.run(host="0.0.0.0", port=PORT)

@cli.command()
from flask import Flask, render_template, request

# ... (الكود الحالي)

@flask_app.route("/")
def home():
    tasks = {
        "1": ("ضرب المصفوفات", "matrix"),
        "2": ("حساب الأعداد الأولية", "prime"),
        "3": ("معالجة البيانات", "data"),
    }
    return render_template("index.html", tasks=tasks)

@flask_app.route("/run_task", methods=["POST"])
def run_task():
    task_id = request.form.get("task_id")
    result = None
    
    if task_id == "1":
        result = matrix_multiply(500)  # استبدل بمعاملاتك الفعلية
    elif task_id == "2":
        result = prime_calculation(100_000)
    elif task_id == "3":
        result = data_processing(10_000)
    
    return render_template("index.html", tasks={
        "1": ("ضرب المصفوفات", "matrix"),
        "2": ("حساب الأعداد الأولية", "prime"),
        "3": ("معالجة البيانات", "data"),
    }, result=result)
def discover():
    """عرض الأجهزة المتصلة"""
    from peer_discovery import discover_peers
    peers = discover_peers()
    print("الأجهزة المتصلة:")
    for i, peer in enumerate(peers, 1):
        print(f"{i}. {peer}")

if __name__ == "__main__":
    cli()
