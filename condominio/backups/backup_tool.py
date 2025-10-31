import schedule
import time
import threading
from .backup_full import run_backup, cleanup_old_automatic_backups

# =====================================================
# ⏰ Programador de Backups Automáticos
# =====================================================

def run_automatic_backup():
    """
    Ejecuta un backup automático usando la función principal existente
    """
    print(f"🤖 [BACKUP AUTOMÁTICO] Iniciando backup semanal...")
    
    try:
        # Ejecutar backup con parámetros automáticos
        run_backup(
            include_backend=True,
            include_db=True, 
            include_frontend=True,
            db_type="postgres",
            automatic=True
        )
        
        print("✅ Backup automático completado correctamente")
        
    except Exception as e:
        print(f"❌ Error en backup automático: {e}")

def start_automatic_backups():
    """Inicia el programador de backups automáticos en un hilo separado"""
    
    # Programar backup todos los domingos a las 02:00 AM
    schedule.every().friday.at("23:00").do(run_automatic_backup)
    
    # Para testing: ejecutar cada 2 minutos (opcional, comentar en producción)
    # schedule.every(2).minutes.do(run_automatic_backup)
    
    print("🤖 Programador de backups automáticos iniciado")
    print("📅 Backups programados: Domingos 02:00 AM")
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Revisar cada minuto
    
    # Ejecutar en un hilo separado para no bloquear la aplicación
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return scheduler_thread