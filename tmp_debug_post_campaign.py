"""
Script para debuggear el error 400 en POST /api/campanas-notificacion/
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Usuario
from condominio.serializer import CampanaNotificacionSerializer
from django.utils import timezone

# Simulemos el payload que envía el frontend
payload = {
    "nombre": "Test Campaña",
    "titulo": "Título de prueba",
    "cuerpo": "Cuerpo de prueba",
    "tipo_notificacion": "campana_marketing",
    "tipo_audiencia": "USUARIOS",
    "usuarios_objetivo": [4],  # ID de Luis Fernando
    "enviar_inmediatamente": False,
    "fecha_programada": "2025-11-03T10:00"  # Formato sin timezone
}

print("=" * 70)
print("🔍 DEBUGGING CREACIÓN DE CAMPAÑA")
print("=" * 70)
print(f"\n📝 Payload enviado:")
for key, value in payload.items():
    print(f"   {key}: {value}")

print(f"\n⏰ Hora actual del servidor:")
print(f"   timezone.now(): {timezone.now()}")
print(f"   Zona horaria: {timezone.get_current_timezone()}")

print(f"\n🔄 Intentando validar con serializer...")
serializer = CampanaNotificacionSerializer(data=payload)

if serializer.is_valid():
    print("\n✅ VALIDACIÓN EXITOSA")
    print(f"   Datos validados: {serializer.validated_data}")
else:
    print("\n❌ VALIDACIÓN FALLIDA")
    print(f"   Errores: {serializer.errors}")
    print(f"\n📋 Detalle de cada error:")
    for field, errors in serializer.errors.items():
        print(f"   Campo: {field}")
        for error in errors:
            print(f"      - {error}")

print("\n" + "=" * 70)
