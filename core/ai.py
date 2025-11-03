import os
from core.views import get_openai_client
from condominio.models import Reserva, Paquete, Servicio
from rest_framework.response import Response
import json

def generate_packing_recommendation(reserva_id: int) -> dict:
    """
    Genera recomendaciones de qué llevar para un viaje basado en la reserva.
    Similar al chatbot turístico pero especializado en recomendaciones de equipaje.
    """
    try:
        # Cargar datos de la reserva y sus relaciones
        reserva = Reserva.objects.select_related('cliente', 'paquete', 'servicio').get(id=reserva_id)
        
        # Determinar si es paquete o servicio y obtener datos
        if reserva.paquete:
            item = reserva.paquete
            nombre = item.nombre
            descripcion = item.descripcion
            duracion = item.duracion
            incluye = item.incluye if hasattr(item, 'incluye') else []
            no_incluye = item.no_incluye if hasattr(item, 'no_incluye') else []
        else:
            item = reserva.servicio
            nombre = item.titulo
            descripcion = item.descripcion
            duracion = item.duracion
            incluye = item.servicios_incluidos if hasattr(item, 'servicios_incluidos') else []
            no_incluye = []

        prompt = f"""
Eres un experto guía de viajes boliviano. Tu tarea es generar una lista detallada y personalizada de qué debe llevar el viajero para este viaje específico.

INFORMACIÓN DEL VIAJE:
- Destino/Experiencia: {nombre}
- Duración: {duracion}
- Descripción: {descripcion}
- Servicios incluidos: {', '.join(incluye) if isinstance(incluye, list) else incluye}
- No incluido: {', '.join(no_incluye) if isinstance(no_incluye, list) else no_incluye}

Genera un JSON con el siguiente formato exacto (no incluyas explicaciones fuera del JSON):
{{
    "texto": "Un mensaje amigable y personalizado de 2-3 líneas explicando las recomendaciones principales",
    "items": [
        {{
            "categoria": "Ropa",
            "items": ["item1", "item2", "item3"],
            "prioridad": "alta/media/baja"
        }},
        {{
            "categoria": "Documentos",
            "items": ["item1", "item2"],
            "prioridad": "alta"
        }},
        {{
            "categoria": "Equipo",
            "items": ["item1", "item2"],
            "prioridad": "media"
        }},
        {{
            "categoria": "Otros",
            "items": ["item1", "item2"],
            "prioridad": "baja"
        }}
    ]
}}

Asegúrate de:
1. Adaptar los items según el tipo de viaje y duración
2. Considerar el clima y geografía del destino
3. Mencionar elementos de seguridad según la actividad
4. Incluir documentos necesarios
5. Sugerir equipo específico si el viaje lo requiere
"""

        # Usar el mismo cliente OpenAI que el chatbot
        client = get_openai_client()
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Experto en planificación de viajes por Bolivia.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Intentar parsear la respuesta como JSON
        try:
            recomendacion = json.loads(completion.choices[0].message.content)
            return {
                "estado": "OK",
                "recomendacion": recomendacion
            }
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver el texto como está
            return {
                "estado": "ERROR",
                "error": "Formato inválido en la respuesta",
                "texto_original": completion.choices[0].message.content
            }
            
    except Reserva.DoesNotExist:
        return {
            "estado": "ERROR",
            "error": f"No se encontró la reserva con ID {reserva_id}"
        }
    except Exception as e:
        return {
            "estado": "ERROR",
            "error": str(e)
        }