"""
Script para probar envío inmediato de notificación
"""
import os
import django

# Configurar variable de entorno ANTES de inicializar Django
os.environ['RUTA_CUENTA_SERVICIO_FIREBASE'] = r'D:\Sis2\Final\Backend_Spring2\CredencialFirebase\notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.firebase import iniciar_firebase
from condominio.models import Usuario, FCMDevice
from firebase_admin import messaging

print("=" * 70)
print("🧪 PRUEBA DE ENVÍO DIRECTO FCM")
print("=" * 70)

# 1. Inicializar Firebase
try:
    app = iniciar_firebase()
    print(f"\n✅ Firebase inicializado correctamente")
    print(f"   App name: {app.name}")
except Exception as e:
    print(f"\n❌ Error al inicializar Firebase: {e}")
    exit()

# 2. Obtener dispositivo de Luis Fernando
usuario = Usuario.objects.get(nombre__icontains='Luis Fernando')
dispositivo = FCMDevice.objects.filter(usuario=usuario, activo=True).first()

if not dispositivo:
    print("\n❌ No hay dispositivo FCM activo para Luis Fernando")
    exit()

# Obtener el token correctamente
token = None
for field in ['registration_token', 'token', 'registration_id']:
    if hasattr(dispositivo, field):
        token = getattr(dispositivo, field)
        if token:
            break

if not token:
    print("\n❌ No se pudo obtener el token del dispositivo")
    exit()

print(f"\n📱 Dispositivo encontrado:")
print(f"   Usuario: {usuario.nombre}")
print(f"   Token: {token[:50]}...")

# 3. Crear mensaje de prueba
mensaje = messaging.Message(
    notification=messaging.Notification(
        title="🧪 PRUEBA DIRECTA",
        body="Si recibes esto, Firebase funciona correctamente ✅"
    ),
    data={
        'tipo': 'test',
        'timestamp': str(django.utils.timezone.now())
    },
    token=token
)

# 4. Enviar
print(f"\n🚀 Enviando notificación...")
try:
    response = messaging.send(mensaje)
    print(f"\n✅ ¡NOTIFICACIÓN ENVIADA EXITOSAMENTE!")
    print(f"   Response ID: {response}")
    print(f"\n💡 Ahora espera 5-10 segundos...")
    print(f"   ⚠️  IMPORTANTE: Tu dispositivo DEBE estar conectado a WiFi o datos móviles")
    print(f"   ⚠️  El USB solo sirve para debugging, no para recibir notificaciones")
except Exception as e:
    print(f"\n❌ Error al enviar: {e}")
    print(f"\n💡 Posibles causas:")
    print(f"   - Token inválido o expirado")
    print(f"   - Credenciales incorrectas")
    print(f"   - Proyecto Firebase incorrecto")

print("\n" + "=" * 70)
