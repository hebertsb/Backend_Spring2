# core/url.py
from django.urls import path
from .views import (
    chatbot_turismo,
    crear_checkout_session,
    crear_checkout_session_suscripcion,  # ← ESTE IMPORT FALTABA
    obtener_recomendacion,
    verificar_pago,  # si no lo usas, puedes quitar esta línea y su path
)
from .webhooks import stripe_webhook

urlpatterns = [
    path('crear-checkout-session/', crear_checkout_session, name='crear-checkout-session'),
    path('crear-checkout-session-suscripcion/', crear_checkout_session_suscripcion, name='crear-checkout-session-suscripcion'),
    
    path('chatbot/turismo/', chatbot_turismo, name='chatbot-turismo'),
    path('recomendacion/', obtener_recomendacion, name='obtener-recomendacion'),
    path('verificar-pago/', verificar_pago, name='verificar-pago'),  # opcional
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
