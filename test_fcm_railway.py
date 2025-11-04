"""
🧪 PRUEBA RÁPIDA FCM - Para ejecutar en Railway
Este script verifica rápidamente el estado del sistema FCM en producción.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Usuario, FCMDevice, CampanaNotificacion, Notificacion
from django.utils import timezone

print("="*60)
print("🧪 PRUEBA RÁPIDA FCM - Railway")
print("="*60)

# 1. Verificar Firebase
print("\n1️⃣ Firebase:")
try:
    from core.firebase import iniciar_firebase
    app = iniciar_firebase()
    print(f"   ✅ Inicializado: {app.name}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar señales FCM
print("\n2️⃣ Señales FCM:")
habilitar = os.getenv('HABILITAR_SEÑAL_FCM', '')
if habilitar.lower() in ('1', 'true', 'si', 'yes'):
    print(f"   ✅ ACTIVADAS (valor: '{habilitar}')")
else:
    print(f"   ⚠️  DESACTIVADAS (valor: '{habilitar}')")

# 3. Contar modelos
print("\n3️⃣ Estadísticas:")
print(f"   Usuarios: {Usuario.objects.count()}")
print(f"   Dispositivos FCM: {FCMDevice.objects.count()}")
print(f"   Dispositivos activos: {FCMDevice.objects.filter(activo=True).count()}")
print(f"   Campañas: {CampanaNotificacion.objects.count()}")
print(f"   Notificaciones: {Notificacion.objects.count()}")

# 4. Última campaña
print("\n4️⃣ Última Campaña:")
ultima = CampanaNotificacion.objects.order_by('-created_at').first()
if ultima:
    print(f"   ID: {ultima.id}")
    print(f"   Nombre: {ultima.nombre}")
    print(f"   Estado: {ultima.get_estado_display()}")
    print(f"   Enviados: {ultima.total_enviados}")
    print(f"   Errores: {ultima.total_errores}")
    print(f"   Fecha: {ultima.created_at}")
else:
    print("   ⚠️  No hay campañas creadas")

# 5. Usuarios con FCM
print("\n5️⃣ Usuarios con dispositivos FCM:")
usuarios_fcm = Usuario.objects.filter(dispositivos_fcm__activo=True).distinct()
for usuario in usuarios_fcm[:5]:
    dispositivos = usuario.dispositivos_fcm.filter(activo=True)
    print(f"   • {usuario.nombre} ({dispositivos.count()} dispositivo(s))")

print("\n" + "="*60)
print("✅ Prueba completada")
print("="*60)
