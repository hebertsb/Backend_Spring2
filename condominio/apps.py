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
            
            # SOLO EN PRODUCCIÓN o cuando se especifique explícitamente
            import os
            if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('ENABLE_AUTOMATIC_BACKUPS'):  
                try:
                    from condominio.backups.backup_tool import start_automatic_backups
                    start_automatic_backups()
                    print("🤖 Programador de backups automáticos iniciado en producción")
                except Exception as e:
                    print(f"⚠️ Error al iniciar backups automáticos: {e}")