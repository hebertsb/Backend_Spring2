"""
Script para diagnosticar por qué no llegó la notificación
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import CampanaNotificacion, Notificacion, FCMDevice, Usuario
import firebase_admin

print("=" * 70)
print("🔍 DIAGNÓSTICO COMPLETO - CAMPAÑA 5")
print("=" * 70)

# 1. Estado de la campaña
try:
    campana = CampanaNotificacion.objects.get(id=5)
    print(f"\n📢 CAMPAÑA #{campana.id}: {campana.nombre}")
    print(f"   Estado: {campana.get_estado_display()}")
    print(f"   Fecha programada: {campana.fecha_programada}")
    print(f"   Fecha enviada: {campana.fecha_enviada}")
    print(f"   Enviar inmediatamente: {campana.enviar_inmediatamente}")
    print(f"\n📊 Métricas:")
    print(f"   Total destinatarios: {campana.total_destinatarios}")
    print(f"   Total enviados: {campana.total_enviados}")
    print(f"   Total errores: {campana.total_errores}")
    print(f"   Total leídos: {campana.total_leidos}")
except CampanaNotificacion.DoesNotExist:
    print("❌ Campaña 5 no existe")
    exit()

# 2. Notificaciones creadas
notificaciones = Notificacion.objects.filter(
    tipo='campana_marketing',
    created_at__gte=campana.created_at
).order_by('-created_at')[:5]

print(f"\n📧 NOTIFICACIONES RECIENTES (últimas 5):")
if notificaciones.exists():
    for notif in notificaciones:
        print(f"   #{notif.id} - {notif.usuario.nombre}")
        print(f"      Tipo: {notif.tipo}")
        print(f"      Datos: {notif.datos}")
        print(f"      Leída: {notif.leida}")
        print(f"      Creada: {notif.created_at}")
else:
    print("   ⚠️  No hay notificaciones creadas")

# 3. Dispositivos FCM
usuario = Usuario.objects.get(nombre__icontains='Luis Fernando')
dispositivos = FCMDevice.objects.filter(usuario=usuario, activo=True)

print(f"\n📱 DISPOSITIVOS FCM DE {usuario.nombre}:")
if dispositivos.exists():
    for disp in dispositivos:
        token_field = getattr(disp, 'registration_token', None) or getattr(disp, 'token', None) or getattr(disp, 'registration_id', None)
        print(f"   ✅ Token: {str(token_field)[:50] if token_field else 'No disponible'}...")
        print(f"      Tipo: {getattr(disp, 'tipo', getattr(disp, 'type', 'N/A'))}")
        print(f"      Activo: {disp.activo}")
        print(f"      Última actualización: {disp.updated_at}")
else:
    print("   ❌ NO hay dispositivos activos")

# 4. Firebase Admin SDK
print(f"\n🔥 FIREBASE ADMIN SDK:")
if firebase_admin._apps:
    print(f"   ✅ Firebase está inicializado")
    print(f"   Apps activas: {len(firebase_admin._apps)}")
else:
    print(f"   ❌ Firebase NO está inicializado")
    print(f"   💡 Las notificaciones NO se pueden enviar sin Firebase")

# 5. Verificar archivo serviceAccountKey.json
from pathlib import Path
service_key = Path('serviceAccountKey.json')
print(f"\n🔑 CREDENCIALES FIREBASE:")
if service_key.exists():
    print(f"   ✅ serviceAccountKey.json existe")
    print(f"   Tamaño: {service_key.stat().st_size} bytes")
else:
    print(f"   ❌ serviceAccountKey.json NO EXISTE")
    print(f"   💡 Firebase no puede enviar notificaciones sin credenciales")

print("\n" + "=" * 70)
print("💡 POSIBLES CAUSAS:")
print("=" * 70)
print("1. ❌ Firebase no inicializado → No se envían notificaciones")
print("2. ❌ Dispositivo sin internet → Firebase no puede entregar")
print("3. ❌ Token FCM inválido o expirado")
print("4. ❌ Permisos de notificaciones desactivados en la app")
print("5. ❌ Signal de Notificacion no se ejecutó")
print("6. ❌ Error silencioso en el envío (revisar logs)")
print("=" * 70)
