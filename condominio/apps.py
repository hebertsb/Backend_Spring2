from django.apps import AppConfig

class CondominioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'condominio'

    def ready(self):
        # Importar y registrar señales
        import condominio.signals
        
        # Iniciar el programador de backups automáticos (SOLO UNA VEZ)
        self.start_automatic_backups()

    def start_automatic_backups(self):  # ✅ DENTRO de la clase
        """
        Inicia el programador de backups automáticos una sola vez
        """
        if not hasattr(self, '_backup_scheduler_started'):
            self._backup_scheduler_started = True
            
            import os
            print("🎯 APPS.PY - ENABLE_AUTOMATIC_BACKUPS =", os.environ.get('ENABLE_AUTOMATIC_BACKUPS'))
            
            if os.environ.get('ENABLE_AUTOMATIC_BACKUPS') == 'true':
                try:
                    from condominio.backups.backup_tool import start_automatic_backups
                    print("🎯 APPS.PY - Iniciando scheduler...")
                    start_automatic_backups()
                    print("🎯 APPS.PY - Scheduler iniciado")
                except Exception as e:
                    print(f"🎯 APPS.PY - Error: {e}")