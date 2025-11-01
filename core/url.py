from django.urls import path
from .views import chatbot_turismo, crear_checkout_session, crear_checkout_session_suscripcion, verificar_pago

urlpatterns = [
    path('crear-checkout-session/', crear_checkout_session),
    path('crear-checkout-session-suscripcion/', crear_checkout_session_suscripcion),
    
    path("chatbot/turismo/", chatbot_turismo, name="chatbot-turismo"),
    path("api/verificar-pago/", verificar_pago, name="verificar_pago"),

]
