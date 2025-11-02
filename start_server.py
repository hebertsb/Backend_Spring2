#!/usr/bin/env python
"""
Script de inicio que ejecuta Gunicorn y el scheduler de campañas en paralelo.
"""
import os
import sys
import subprocess
import signal
from multiprocessing import Process

def run_gunicorn():
    """Ejecutar Gunicorn"""
    # Ejecutar gunicorn como subproceso
    cmd = ['gunicorn', 'config.wsgi:application']
    subprocess.run(cmd)

def run_scheduler():
    """Ejecutar el scheduler de campañas"""
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    django.setup()
    
    # Importar y ejecutar el scheduler
    from condominio.scheduler_campanas import ejecutar_campanas_job
    import schedule
    import time
    
    # Programar ejecución cada minuto
    schedule.every(1).minutes.do(ejecutar_campanas_job)
    
    print("🤖 [SCHEDULER] Iniciado. Verificando campañas cada 1 minuto...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # Verificar cada 30 segundos
        except Exception as e:
            print(f"❌ [SCHEDULER] Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    # Crear proceso para el scheduler
    scheduler_process = Process(target=run_scheduler, daemon=False)
    scheduler_process.start()
    
    print(f"✅ Scheduler iniciado en proceso PID: {scheduler_process.pid}", flush=True)
    print(f"🚀 Iniciando Gunicorn...", flush=True)
    
    # Ejecutar Gunicorn en el proceso principal
    def handle_signal(signum, frame):
        print("🛑 Deteniendo servicios...", flush=True)
        scheduler_process.terminate()
        scheduler_process.join(timeout=5)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    try:
        run_gunicorn()
    finally:
        # Asegurar que el scheduler se detenga al salir
        scheduler_process.terminate()
        scheduler_process.join(timeout=5)
