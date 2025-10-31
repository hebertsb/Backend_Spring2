from django.apps import AppConfig

class CondominioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'condominio'

    def ready(self):
        # Importar y registrar señales
        import condominio.signals
        
        # Iniciar el programador de backups automáticos (SOLO UNA VEZ)
        self.start_automatic_backups()

    def start_automatic_backups(self):
        """
        Inicia el programador de backups automáticos una sola vez
        """
        # Verificar que no se haya iniciado ya (evitar duplicados en desarrollo)
        if not hasattr(self, '_backup_scheduler_started'):
            self._backup_scheduler_started = True
            
            # Solo iniciar en producción o cuando se especifique
            import os
            if os.environ.get('RUN_MAIN') == 'true':  # Solo en el proceso principal
                try:
                    from condominio.backups.backup_tool import start_automatic_backups
                    start_automatic_backups()
                    print("🤖 Programador de backups automáticos iniciado correctamente")
                except Exception as e:
                    print(f"⚠️ Error al iniciar backups automáticos: {e}")