# core/views.py
from datetime import timedelta, timezone
from django.http import HttpResponse
import stripe
from django.conf import settings
from condominio.models import Paquete, Servicio
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from dotenv import load_dotenv
from rest_framework import status
from django.core.cache import cache
from .openai_client import get_openai_client  # ← cliente centralizado

load_dotenv()
stripe.api_key = settings.STRIPE_SECRET_KEY
url_frontend = os.getenv("URL_FRONTEND", "http://127.0.0.1:3000")

@api_view(["GET"])
def obtener_recomendacion(request):
    """Obtiene la recomendación generada para una sesión de pago específica."""
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response(
            {"error": "Se requiere el parámetro session_id"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Intentar obtener la recomendación del caché
    cache_key = f"recommendation_{session_id}"
    recommendation = cache.get(cache_key)
    
    if recommendation is None:
        return Response(
            {"error": "No se encontró una recomendación para esta sesión"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        "recommendation": recommendation,
        "session_id": session_id
    })

# @permission_classes([IsAuthenticated])
@api_view(["POST"])
def crear_checkout_session(request):
    try:
        data = request.data
        nombre = data.get("nombre", "Reserva")
        precio = float(data.get("precio", 0))
        cantidad = int(data.get("cantidad", 1))

        if precio <= 0:
            return Response({"error": "Precio inválido"}, status=status.HTTP_400_BAD_REQUEST)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "bob",
                        "product_data": {"name": nombre},
                        "unit_amount": int(precio),  # se asume centavos enviados desde frontend
                    },
                    "quantity": cantidad,
                }
            ],
            success_url=f"{url_frontend}/pago-exitoso?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{url_frontend}/pago-cancelado/",
            metadata={
                "usuario_id": str(request.user.id) if request.user.is_authenticated else "anonimo",
                "recommendation_url": f"{request.build_absolute_uri('/api/recomendacion/')}?session_id={{CHECKOUT_SESSION_ID}}"
            },
        )

        return Response({"checkout_url": session.url})

    except Exception as e:
        print("❌ Error Stripe:", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================================================
# SUSCRIPCIONES - ENDPOINT DESHABILITADO
# =====================================================
@api_view(["POST"])
def crear_checkout_session_suscripcion(request):
    """
    Endpoint deshabilitado - Requiere modelos Proveedor y Suscripcion eliminados.
    """
    return Response({
        "error": "Funcionalidad temporalmente deshabilitada. Modelos Proveedor y Suscripcion fueron eliminados."
    }, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(["GET"])
def verificar_pago(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        return Response({"error": "Falta session_id"}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        pago_exitoso = session.payment_status == "paid"

        # extraer metadata
        metadata = getattr(session, "metadata", {}) or {}
        payment_type = metadata.get("payment_type", "venta")
        usuario_id_meta = metadata.get("usuario_id", None)
        titulo_meta = metadata.get("titulo", None)

        # NOTA: Funcionalidad de suscripciones deshabilitada (modelo Suscripcion eliminado)

        return Response({
            "pago_exitoso": pago_exitoso,
            "cliente_email": session.customer_details.email if session.customer_details else None,
            "monto_total": session.amount_total,
            "moneda": session.currency,
            "payment_type": payment_type,
        })

    except Exception as e:
        print("❌ Error verificando sesión:", e)
        return Response({"error": str(e)}, status=500)

@api_view(["POST"])
def chatbot_turismo(request):
    pregunta = request.data.get("pregunta", "")
    if not pregunta:
        return Response({"error": "Debes enviar el campo 'pregunta'."}, status=400)

    paquetes = Paquete.objects.all().values(
        "nombre", "descripcion", "precio_base", "duracion"
    )
    servicios = Servicio.objects.all().values(
        "titulo", "descripcion", "precio_usd", "categoria__nombre"
    )

    contexto = "Paquetes turísticos:\n"
    for p in paquetes:
        contexto += f"- {p['nombre']} ({p['duracion']}) por ${p['precio_base']}: {p['descripcion']}\n"
    contexto += "\nServicios:\n"
    for s in servicios:
        contexto += f"- {s['titulo']} ({s['categoria__nombre']}): ${s['precio_usd']} — {s['descripcion']}\n"

    prompt = f"""
Eres un asesor turístico boliviano que trabaja en una agencia de viajes de Bolivia.
Tu tarea es recomendar paquetes y servicios turísticos basados en la información real que te proporcionaré.

Usa siempre el siguiente contexto para responder de forma amable, breve y precisa:
- Los datos incluyen paquetes turísticos, servicios, precios, duración, ubicación o ciudad, y descripciones.
- Si el usuario menciona lugares, ciudades o regiones (por ejemplo: "La Paz", "Uyuni", "Santa Cruz", "Cochabamba"), 
  busca entre los paquetes o servicios que coincidan con esa ubicación o tengan relación.
- Si el usuario pregunta por precios, muestra opciones económicas o menciona el precio en dólares.
- Si el usuario pide recomendaciones de aventura, cultura, gastronomía, o naturaleza, 
  filtra según la categoría o descripción más relacionada.

**Reglas obligatorias:**
1. Tus respuestas deben ser cortas, claras y sin adornos innecesarios.
2. Solo responde con información real de los paquetes o servicios que existen en el contexto.  
   Si no tienes la información, di literalmente: “No tengo información disponible sobre eso.”
3. Debes incluir **exactamente una URL válida** al final de tu respuesta.  
   - Si es un paquete, usa: {url_frontend}paquetes/{{id}}/
   - Si es un servicio, usa: {url_frontend}destinos/{{id}}/
   Ejemplo:  
   > Te recomiendo el paquete “Aventura Andina”, ideal para conocer el Salar de Uyuni. Cuesta 480 USD y dura 3 días.  
   > {url_frontend}paquetes/1/
4. **No inventes URLs ni IDs.** Usa solo los que estén en el contexto recibido.
5. No hables de otros países, únicamente de lugares dentro de Bolivia.
6. Si el usuario pide un lugar que no está en el contexto, responde:  
   > “No tengo información sobre ese destino en Bolivia.”

Recuerda: Responde como un asistente amable y profesional de turismo boliviano.

    {contexto}

    Usuario: {pregunta}
    Asistente:
    """

    try:
        client = get_openai_client()  # ← cliente centralizado

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Asistente turístico experto en Bolivia."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        respuesta = completion.choices[0].message.content
        return Response({"respuesta": respuesta})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def verificar_proveedor(request, usuario_id):
    """
    Endpoint deshabilitado - Requiere modelo Proveedor eliminado.
    """
    return Response({
        "error": "Funcionalidad temporalmente deshabilitada. Modelo Proveedor fue eliminado.",
        "existe": False
    }, status=status.HTTP_501_NOT_IMPLEMENTED)
