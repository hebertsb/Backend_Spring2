"""
Script para verificar si Firebase realmente envió la notificación
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import CampanaNotificacion, Notificacion, FCMDevice, Usuario

print("=" * 70)
print("🔍 VERIFICACIÓN DE ENVÍO FCM")
print("=" * 70)

# Campaña 5
campana = CampanaNotificacion.objects.get(id=5)
print(f"\n📢 Campaña: {campana.nombre}")
print(f"   Estado: {campana.get_estado_display()}")
print(f"   Enviada: {campana.fecha_enviada}")

# Notificaciones enviadas
notificaciones = Notificacion.objects.filter(campana=campana)
print(f"\n📧 Notificaciones creadas: {notificaciones.count()}")

for notif in notificaciones:
    print(f"\n   📬 Notificación #{notif.id}")
    print(f"      Usuario: {notif.usuario.nombre}")
    print(f"      Título: {notif.titulo}")
    print(f"      Cuerpo: {notif.cuerpo}")
    print(f"      Leída: {notif.leida}")
    print(f"      Fecha creación: {notif.fecha_creacion}")

# Verificar dispositivos FCM
usuario = Usuario.objects.get(nombre__icontains='Luis Fernando')
dispositivos = FCMDevice.objects.filter(usuario=usuario, activo=True)

print(f"\n📱 Dispositivos FCM de {usuario.nombre}: {dispositivos.count()}")
for disp in dispositivos:
    print(f"   Token: {disp.token[:40]}...")
    print(f"   Tipo: {disp.tipo}")
    print(f"   Activo: {disp.activo}")
    print(f"   Última actividad: {disp.updated_at}")

# Métricas de campaña
print(f"\n📊 Métricas de Campaña:")
print(f"   Total destinatarios: {campana.total_destinatarios}")
print(f"   Total enviados: {campana.total_enviados}")
print(f"   Total errores: {campana.total_errores}")
print(f"   Total leídos: {campana.total_leidos}")

# Verificar Firebase Admin
print(f"\n🔥 Firebase Admin SDK:")
try:
    import firebase_admin
    if firebase_admin._apps:
        print(f"   ✅ Firebase inicializado")
        app = firebase_admin.get_app()
        print(f"   App name: {app.name}")
    else:
        print(f"   ⚠️  Firebase NO inicializado")
        print(f"   💡 El envío podría haber fallado")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("\n💡 Si total_enviados = 0:")
print("   1. Revisa logs del backend al activar campaña")
print("   2. Verifica que serviceAccountKey.json existe")
print("   3. Comprueba que el signal post_save de Notificacion funciona")
print("=" * 70)
