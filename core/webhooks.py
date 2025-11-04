# core/webhooks.py
import stripe
from threading import Thread
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .ai import generate_packing_recommendation
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_and_cache_recommendation(reserva_id: int, session_id: str):
    """
    Genera la recomendación en background y la guarda en cache con session_id como clave.
    """
    try:
        logger.info(f"🚀 Iniciando generación de recomendación - reserva_id: {reserva_id}, session_id: {session_id}")
        resultado = generate_packing_recommendation(reserva_id)
        
        # Guardar en cache por 1 hora usando session_id como clave
        cache_key = f'recommendation_{session_id}'
        cache.set(cache_key, resultado, timeout=3600)
        logger.info(f"✅ Recomendación guardada en cache - key: {cache_key}")
        
    except Exception as e:
        logger.error(f"❌ Error generando recomendación para reserva {reserva_id}: {e}")
        # Guardar error en cache para debugging
        cache_key = f'recommendation_{session_id}'
        cache.set(cache_key, {"estado": "ERROR", "error": str(e)}, timeout=3600)

@api_view(['POST'])
def stripe_webhook(request):
    """
    Maneja los webhooks de Stripe, específicamente el evento checkout.session.completed
    para generar recomendaciones de viaje.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        logger.info(f"📨 Webhook recibido - tipo: {event['type']}")
        
        # Verificar que es un checkout completado
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            session_id = session.get('id')  # ID de la sesión de Stripe
            reserva_id = session.get('metadata', {}).get('reserva_id')
            
            logger.info(f"💳 Pago completado - session_id: {session_id}, reserva_id: {reserva_id}")
            
            if reserva_id and session_id:
                # Iniciar thread para generar recomendación con ambos IDs
                thread = Thread(
                    target=generate_and_cache_recommendation,
                    args=(int(reserva_id), session_id),
                    daemon=True
                )
                thread.start()
                logger.info(f"🧵 Thread de recomendación iniciado para reserva {reserva_id}")
            else:
                logger.warning(f"⚠️ Metadata incompleto - reserva_id: {reserva_id}, session_id: {session_id}")
            
        return Response({'status': 'success'})
        
    except stripe.error.SignatureVerificationError:
        logger.error("❌ Error de firma del webhook de Stripe")
        return Response(
            {'error': 'Invalid signature'},
            status=400
        )
    except Exception as e:
        logger.error(f"❌ Error procesando webhook: {e}")
        return Response(
            {'error': str(e)},
            status=400
        )
