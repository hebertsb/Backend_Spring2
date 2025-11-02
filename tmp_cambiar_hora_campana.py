"""
Script para cambiar la hora programada de la campaña 5 a las 10:40 PM
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import CampanaNotificacion
from django.utils import timezone
from datetime import datetime

# Obtener campaña 5
campana = CampanaNotificacion.objects.get(id=5)

print("=" * 70)
print("⏰ CAMBIAR HORA PROGRAMADA DE CAMPAÑA")
print("=" * 70)

print(f"\n📢 Campaña: {campana.nombre}")
print(f"   Estado actual: {campana.get_estado_display()}")
print(f"   Hora programada actual: {campana.fecha_programada}")

# Nueva fecha: Hoy 1 de noviembre de 2025 a las 10:40 PM
# Zona horaria: America/La_Paz (Bolivia UTC-4)
nueva_fecha = timezone.make_aware(
    datetime(2025, 11, 1, 22, 40, 0),  # 10:40 PM
    timezone.get_current_timezone()
)

campana.fecha_programada = nueva_fecha
campana.save(update_fields=['fecha_programada'])

print(f"\n✅ Hora programada cambiada:")
print(f"   Nueva hora: {campana.fecha_programada}")
print(f"   Hora local: 1 de noviembre 2025, 10:40 PM")

print(f"\n⏳ Hora actual del servidor: {timezone.now()}")
print(f"   Faltan aproximadamente: {(nueva_fecha - timezone.now()).total_seconds() / 60:.1f} minutos")

print("\n" + "=" * 70)
print("💡 INSTRUCCIONES:")
print("=" * 70)
print("1. ✅ Conecta tu dispositivo Android a WiFi (misma red que tu PC)")
print("2. ✅ Mantén la app abierta o en segundo plano")
print("3. ⏰ A las 10:40 PM el scheduler ejecutará la campaña automáticamente")
print("4. 📱 Deberías recibir la notificación en tu dispositivo")
print("\nAlternativamente, ejecuta AHORA con:")
print("   py manage.py ejecutar_campanas_programadas --force-id 5")
print("=" * 70)
