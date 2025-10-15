from django.urls import path
from .views import chatbot_turismo, crear_checkout_session

urlpatterns = [
    path('crear-checkout-session/', crear_checkout_session),
    path("chatbot/turismo/", chatbot_turismo, name="chatbot-turismo"),

]
