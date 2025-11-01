import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notificacion, FCMDevice
from core.notifications import enviar_tokens_push

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notificacion)
def notificacion_post_save_fcm(sender, instance, created, **kwargs):
    """Envía notificación push vía FCM cuando se crea una Notificacion.

    Esta señal solo será importada/activada si la variable de entorno
    `HABILITAR_SEÑAL_FCM` está presente y no es falsey.
    """
    if not created:
        return

    try:
        # recolectar tokens activos del usuario destinatario (traer tipo_dispositivo)
        dispositivos = FCMDevice.objects.filter(usuario=instance.usuario, activo=True)
        tokens = []
        for d in dispositivos:
            tokens.append({'token': d.registration_id, 'tipo': d.tipo_dispositivo})
        if not tokens:
            return

        # Preparar contenido de la notificación
        titulo = 'Nueva notificación'
        cuerpo = None
        datos_extra = {'notificacion_id': str(instance.id)}

        # Si en `datos` hay un campo `mensaje`, usarlo
        if isinstance(instance.datos, dict):
            cuerpo = instance.datos.get('mensaje') or instance.datos.get('body')
            # exportar el objeto datos como string si existe
            datos_extra.update({k: str(v) for k, v in instance.datos.items()})

        if not cuerpo:
            cuerpo = instance.tipo

        # Enviar
        resp = enviar_tokens_push(tokens, titulo, cuerpo, datos_extra)
        logger.info('FCM send result for Notificacion %s: %s', instance.id, resp)
    except Exception as e:
        logger.exception('Error al enviar FCM para Notificacion %s: %s', instance.id, e)
