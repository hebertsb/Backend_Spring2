import stripe
from django.conf import settings
from condominio.models import Paquete, Servicio
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from condominio.models import Paquete, Servicio

stripe.api_key = settings.STRIPE_SECRET_KEY
url_frontend = os.getenv("URL_FRONTEND")

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
                        "unit_amount": int(precio),
                    },
                    "quantity": cantidad,
                }
            ],
            success_url=f"{url_frontend}/pago-exitoso?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{url_frontend}/pago-cancelado/",
            metadata={"usuario_id": str(request.user.id) if request.user.is_authenticated else "anonimo"},
        )

        return Response({"checkout_url": session.url})

    except Exception as e:
        print("❌ Error Stripe:", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)


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
   - Si es un paquete, usa: {url_frontend}/paquetes/{id}/
   - Si es un servicio, usa: {url_frontend}/destinos/{id}/
   Ejemplo:  
   > Te recomiendo el paquete “Aventura Andina”, ideal para conocer el Salar de Uyuni. Cuesta 480 USD y dura 3 días.  
   > {url_frontend}/paquetes/1/
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
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Asistente turístico experto en Bolivia.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        respuesta = completion.choices[0].message.content
        return Response({"respuesta": respuesta})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
