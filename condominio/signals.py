# condominio/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from django.apps import apps
import os
import logging
logger = logging.getLogger(__name__)


# Código existente para cargar fixtures está comentado; se mantiene.

# Importar señales FCM condicionalmente para evitar envíos automáticos por defecto.
# La variable de entorno en español 'HABILITAR_SEÑAL_FCM' controla esto.
if os.getenv('HABILITAR_SEÑAL_FCM', '').lower() in ('1', 'true', 'si', 'yes'):
	try:
		import condominio.signals_fcm  # noqa: F401
		logger.info('⚙️ Señales FCM activadas (HABILITAR_SEÑAL_FCM=1)')
	except Exception as e:
		logger.exception('⚠️ No se pudo activar condominio.signals_fcm: %s', e)

