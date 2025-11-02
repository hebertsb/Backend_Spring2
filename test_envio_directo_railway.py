"""
🚀 ENVÍO DIRECTO DE NOTIFICACIÓN - Railway
Ejecuta esto directamente en Railway para enviar una notificación de prueba.

INSTRUCCIONES:
1. Ve a Railway Dashboard
2. Abre la consola del servicio
3. Ejecuta: python test_envio_directo_railway.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Usuario, FCMDevice, CampanaNotificacion
from condominio.tasks import ejecutar_campana_notificacion
from django.utils import timezone

print("🚀 ENVÍO DIRECTO DE NOTIFICACIÓN - Railway")
print("="*60)

# Buscar usuario con dispositivo FCM
print("\n1️⃣ Buscando usuario con dispositivo FCM activo...")
usuarios_con_fcm = Usuario.objects.filter(
    dispositivos_fcm__activo=True
).distinct()

if not usuarios_con_fcm.exists():
    print("   ❌ No hay usuarios con dispositivos FCM activos")
    print("   💡 Abre la app Flutter y registra un dispositivo primero")
    exit(1)

usuario = usuarios_con_fcm.first()
dispositivos = usuario.dispositivos_fcm.filter(activo=True)

print(f"   ✅ Usuario: {usuario.nombre}")
print(f"   📱 Dispositivos activos: {dispositivos.count()}")
for disp in dispositivos:
    print(f"      • {disp.tipo_dispositivo} - Token: {disp.registration_id[:50]}...")

# Crear campaña
print("\n2️⃣ Creando campaña de prueba...")
campana = CampanaNotificacion.objects.create(
    nombre=f'[RAILWAY TEST] {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
    descripcion='Prueba automática desde Railway',
    titulo='🎯 ¡Notificación desde Railway!',
    cuerpo='Tu sistema FCM está funcionando perfectamente en producción ✅',
    tipo_notificacion='informativa',
    tipo_audiencia='USUARIOS',
    enviar_inmediatamente=True,
    estado='BORRADOR'
)
campana.usuarios_objetivo.add(usuario)
campana.calcular_destinatarios()

print(f"   ✅ Campaña creada (ID: {campana.id})")

# Ejecutar
print("\n3️⃣ Ejecutando campaña...")
resultado = ejecutar_campana_notificacion(campana.id)

print("\n📊 RESULTADO:")
print(f"   Success: {resultado['success']}")
print(f"   Enviados: {resultado['total_enviados']}")
print(f"   Errores: {resultado['total_errores']}")

if resultado['success'] and resultado['total_enviados'] > 0:
    print("\n🎉 ¡NOTIFICACIÓN ENVIADA EXITOSAMENTE!")
    print(f"📱 Revisa tu dispositivo: {usuario.nombre}")
else:
    print("\n⚠️  Hubo un problema. Revisa los logs arriba.")

print("="*60)
