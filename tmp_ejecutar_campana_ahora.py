"""
Script para ejecutar la campaña INMEDIATAMENTE sin esperar
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.tasks import ejecutar_campana_notificacion
from condominio.models import CampanaNotificacion

# Ejecutar campaña 5
print("🚀 EJECUTANDO CAMPAÑA 5 INMEDIATAMENTE...")
print("=" * 70)

resultado = ejecutar_campana_notificacion(campana_id=5, ejecutor_id=5)

print(f"\n📊 RESULTADO:")
print(f"   Success: {resultado.get('success')}")
print(f"   Total enviados: {resultado.get('total_enviados', 0)}")
print(f"   Total errores: {resultado.get('total_errores', 0)}")

if resultado.get('errores'):
    print(f"\n❌ Errores encontrados:")
    for error in resultado['errores']:
        print(f"   - {error}")

if resultado.get('success'):
    print("\n✅ ¡Notificación enviada! Revisa tu dispositivo")
else:
    print("\n❌ Hubo errores al enviar")

print("=" * 70)

# Verificar estado final
campana = CampanaNotificacion.objects.get(id=5)
print(f"\n📢 Estado final de campaña:")
print(f"   Estado: {campana.get_estado_display()}")
print(f"   Fecha enviada: {campana.fecha_enviada}")
print(f"   Total enviados: {campana.total_enviados}")
print(f"   Total errores: {campana.total_errores}")
