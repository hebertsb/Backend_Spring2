from django.urls import path
from .views import chatbot_turismo, crear_checkout_session, obtener_recomendacion
from .webhooks import stripe_webhook

urlpatterns = [
    path('crear-checkout-session/', crear_checkout_session),
    path("chatbot/turismo/", chatbot_turismo, name="chatbot-turismo"),
    path("recomendacion/", obtener_recomendacion, name="obtener-recomendacion"),
    # Webhook de Stripe (se expone bajo /api/webhook/stripe/)
    path("webhook/stripe/", stripe_webhook, name="stripe-webhook"),
]
