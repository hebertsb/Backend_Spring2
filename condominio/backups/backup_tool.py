import os
import time
import schedule
import threading
import platform
from datetime import datetime
from .backup_full import run_backup, cleanup_old_automatic_backups

# =====================================================
# 🌎 Zona horaria (America/La_Paz)
# =====================================================
os.environ['TZ'] = 'America/La_Paz'
if platform.system() != "Windows":  
    time.tzset()

# =====================================================
# ⏰ Programador de Backups Automáticos
# =====================================================

def run_automatic_backup():
    """
    Ejecuta un backup automático usando la función principal existente
    """
    print(f"🤖 [BACKUP AUTOMÁTICO] Iniciando backup automático...")
    try:
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


#####usado para los test

# def start_automatic_backups():
#     """Inicia el programador de backups automáticos en un hilo separado"""
    
#     schedule.clear('backups')

#     # 🧪 Modo testing: crear exactamente 3 backups
#     if os.getenv("BACKUP_TEST_MODE") == "1":
#         print("🧪 MODO TEST ACTIVADO - Creando 3 backups automáticos")
        
#         # Crear 3 backups inmediatamente con intervalos
#         def create_test_backups():
#             backup_count = 0
#             max_backups = 3
            
#             while backup_count < max_backups:
#                 backup_count += 1
#                 print(f"🧪 [BACKUP TEST {backup_count}/{max_backups}] Iniciando...")
                
#                 try:
#                     run_backup(
#                         include_backend=True,
#                         include_db=True, 
#                         include_frontend=True,  
#                         db_type="postgres",
#                         automatic=True
#                     )
#                     print(f"✅ [BACKUP TEST {backup_count}/{max_backups}] Completado")
                    
#                     # Esperar 2 minutos entre backups (excepto el último)
#                     if backup_count < max_backups:
#                         print("⏰ Esperando 2 minutos para próximo backup...")
#                         time.sleep(120)  # 2 minutos
                        
#                 except Exception as e:
#                     print(f"❌ [BACKUP TEST {backup_count}/{max_backups}] Error: {e}")
#                     break
            
#             print("🎯 MODO TEST COMPLETADO - Se crearon 3 backups de prueba")
#             print("⚡ Recuerda desactivar BACKUP_TEST_MODE en Railway")
        
#         # Ejecutar en un hilo separado
#         test_thread = threading.Thread(target=create_test_backups, daemon=True)
#         test_thread.start()
#         return test_thread

#     else:
#         # 🕒 Modo normal: ejecutar los sábados a las 17:30 hora local
#         schedule.every().saturday.at("19:00").tag('backups').do(run_automatic_backup)
#         print("🤖 Backup programado para sábados 17:30")

#     print("🤖 Programador de backups automáticos iniciado")
#     print("🕒 Zona horaria activa:", time.tzname, "| Hora actual:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
#     for job in schedule.get_jobs('backups'):
#         print("📅 Backup programado:", job, "| Próxima ejecución:", job.next_run.strftime("%Y-%m-%d %H:%M:%S"))

#     # Iniciar scheduler en segundo plano (solo para modo normal)
#     def run_scheduler():
#         while True:
#             schedule.run_pending()
#             time.sleep(60)

#     scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     scheduler_thread.start()
#     return scheduler_thread


def start_automatic_backups():
    """Inicia el programador de backups automáticos en un hilo separado"""
    
    # Evitar duplicados si esta función se llama más de una vez
    schedule.clear('backups')

    # 🕒 Backups automáticos programados - sábados 17:30 hora Bolivia
    schedule.every().saturday.at("20:00").tag('backups').do(run_automatic_backup)

    print("🤖 Programador de backups automáticos iniciado")
    print("🕒 Zona horaria activa:", time.tzname, "| Hora actual:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for job in schedule.get_jobs('backups'):
        print("📅 Backup programado:", job, "| Próxima ejecución:", job.next_run.strftime("%Y-%m-%d %H:%M:%S"))

    # Iniciar scheduler en segundo plano
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    return scheduler_thread