# core/webhooks.py
import stripe
from threading import Thread
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .ai import generate_packing_recommendation

stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_and_cache_recommendation(reserva_id: int):
    """
    Genera la recomendación en background y la guarda en cache.
    """
    try:
        resultado = generate_packing_recommendation(reserva_id)
        # Guardar en cache por 1 hora
        cache_key = f'recomendacion_{reserva_id}'
        cache.set(cache_key, resultado, timeout=3600)
    except Exception as e:
        print(f"❌ Error generando recomendación: {e}")
        cache_key = f'recomendacion_error_{reserva_id}'
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
        
        # Verificar que es un checkout completado
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            reserva_id = session.get('metadata', {}).get('reserva_id')
            
            if reserva_id:
                # Iniciar thread para generar recomendación
                thread = Thread(
                    target=generate_and_cache_recommendation,
                    args=(int(reserva_id),),
                    daemon=True
                )
                thread.start()
            
        return Response({'status': 'success'})
        
    except stripe.error.SignatureVerificationError:
        return Response(
            {'error': 'Invalid signature'},
            status=400
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=400
        )
