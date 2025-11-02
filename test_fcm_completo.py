"""
🧪 SCRIPT DE PRUEBA COMPLETA - Sistema FCM en Railway
Verifica que el sistema de notificaciones push esté funcionando correctamente.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Usuario, FCMDevice, CampanaNotificacion
from django.utils import timezone
from datetime import timedelta
import json

print("="*80)
print("🧪 PRUEBA COMPLETA DEL SISTEMA FCM")
print("="*80)
print()

# ============================================
# 1. VERIFICAR FIREBASE
# ============================================
print("📋 PASO 1: Verificando Firebase...")
try:
    from core.firebase import iniciar_firebase
    app = iniciar_firebase()
    print(f"   ✅ Firebase inicializado: {app.name}")
except Exception as e:
    print(f"   ❌ Error en Firebase: {e}")
    exit(1)

# ============================================
# 2. VERIFICAR USUARIO
# ============================================
print("\n📋 PASO 2: Verificando usuario de prueba...")
try:
    # Buscar usuario Hebert (tu usuario)
    usuario = Usuario.objects.filter(nombre__icontains='hebert').first()
    
    if not usuario:
        # Si no existe, buscar cualquier usuario
        usuario = Usuario.objects.first()
    
    if not usuario:
        print("   ❌ No hay usuarios en la base de datos")
        exit(1)
    
    print(f"   ✅ Usuario encontrado: {usuario.nombre} (ID: {usuario.id})")
    print(f"      Email: {usuario.user.email if hasattr(usuario, 'user') else 'N/A'}")
    print(f"      Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
except Exception as e:
    print(f"   ❌ Error buscando usuario: {e}")
    exit(1)

# ============================================
# 3. VERIFICAR/CREAR DISPOSITIVO FCM
# ============================================
print("\n📋 PASO 3: Verificando dispositivo FCM...")
try:
    # Verificar si ya tiene dispositivos FCM
    dispositivos = FCMDevice.objects.filter(usuario=usuario, activo=True)
    
    if dispositivos.exists():
        dispositivo = dispositivos.first()
        print(f"   ✅ Dispositivo FCM existente encontrado:")
        print(f"      ID: {dispositivo.id}")
        print(f"      Tipo: {dispositivo.tipo_dispositivo}")
        print(f"      Token (primeros 50 chars): {dispositivo.registration_id[:50]}...")
        print(f"      Activo: {dispositivo.activo}")
        print(f"      Última actualización: {dispositivo.ultima_vez}")
    else:
        print("   ⚠️  No se encontró dispositivo FCM activo para este usuario")
        print("      Para recibir notificaciones, debes:")
        print("      1. Abrir la app Flutter")
        print("      2. Iniciar sesión")
        print("      3. El token se registrará automáticamente")
        
        # Crear un dispositivo de prueba (SOLO PARA TESTING)
        print("\n   🔧 Creando dispositivo FCM de prueba...")
        dispositivo = FCMDevice.objects.create(
            usuario=usuario,
            registration_id="TEST_TOKEN_SIMULADO_" + str(usuario.id),
            tipo_dispositivo='android',
            nombre='Dispositivo de Prueba',
            activo=True
        )
        print(f"   ✅ Dispositivo de prueba creado (ID: {dispositivo.id})")
        print("   ⚠️  NOTA: Este es un token simulado, NO recibirás notificación real")
        print("      Usa un token real desde la app Flutter para pruebas completas")
        
except Exception as e:
    print(f"   ❌ Error con dispositivo FCM: {e}")
    exit(1)

# ============================================
# 4. CREAR CAMPAÑA DE PRUEBA
# ============================================
print("\n📋 PASO 4: Creando campaña de notificación de prueba...")
try:
    # Eliminar campañas de prueba anteriores
    CampanaNotificacion.objects.filter(nombre__startswith='[PRUEBA]').delete()
    
    campana = CampanaNotificacion.objects.create(
        nombre=f'[PRUEBA] Test FCM - {timezone.now().strftime("%H:%M:%S")}',
        descripcion='Campaña de prueba automática para validar el sistema FCM',
        titulo='🧪 Notificación de Prueba',
        cuerpo='¡El sistema de notificaciones FCM está funcionando correctamente! ✅',
        tipo_notificacion='informativa',
        tipo_audiencia='USUARIOS',
        enviar_inmediatamente=True,
        estado='BORRADOR'
    )
    
    # Agregar el usuario como destinatario
    campana.usuarios_objetivo.add(usuario)
    
    # Calcular destinatarios
    total = campana.calcular_destinatarios()
    
    print(f"   ✅ Campaña creada exitosamente:")
    print(f"      ID: {campana.id}")
    print(f"      Nombre: {campana.nombre}")
    print(f"      Título: {campana.titulo}")
    print(f"      Mensaje: {campana.cuerpo}")
    print(f"      Destinatarios: {total}")
    print(f"      Estado: {campana.estado}")
    
except Exception as e:
    print(f"   ❌ Error creando campaña: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================
# 5. EJECUTAR CAMPAÑA
# ============================================
print("\n📋 PASO 5: Ejecutando campaña...")
try:
    from condominio.tasks import ejecutar_campana_notificacion
    
    resultado = ejecutar_campana_notificacion(campana.id)
    
    print(f"\n   📊 RESULTADO DE LA EJECUCIÓN:")
    print(f"      Success: {resultado['success']}")
    print(f"      Total enviados: {resultado['total_enviados']}")
    print(f"      Total errores: {resultado['total_errores']}")
    print(f"      Total destinatarios: {resultado.get('total_destinatarios', 0)}")
    print(f"      Mensaje: {resultado.get('mensaje', 'N/A')}")
    
    if resultado['success']:
        print("\n   ✅ ¡Campaña ejecutada exitosamente!")
    else:
        print("\n   ⚠️  La campaña se ejecutó con errores")
        
except Exception as e:
    print(f"   ❌ Error ejecutando campaña: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================
# 6. VERIFICAR ESTADO FINAL
# ============================================
print("\n📋 PASO 6: Verificando estado final...")
try:
    # Refrescar campaña desde DB
    campana.refresh_from_db()
    
    print(f"\n   📊 ESTADO FINAL DE LA CAMPAÑA:")
    print(f"      ID: {campana.id}")
    print(f"      Estado: {campana.get_estado_display()}")
    print(f"      Fecha enviada: {campana.fecha_enviada}")
    print(f"      Total enviados: {campana.total_enviados}")
    print(f"      Total errores: {campana.total_errores}")
    
    # Verificar notificaciones creadas
    from condominio.models import Notificacion
    notificaciones = Notificacion.objects.filter(
        usuario=usuario,
        datos__campana_id=str(campana.id)
    ).order_by('-created_at')
    
    print(f"\n   📬 NOTIFICACIONES CREADAS:")
    print(f"      Total: {notificaciones.count()}")
    
    for notif in notificaciones[:3]:
        print(f"\n      Notificación #{notif.id}:")
        print(f"         Usuario: {notif.usuario.nombre}")
        print(f"         Tipo: {notif.tipo}")
        print(f"         Leída: {notif.leida}")
        print(f"         Título: {notif.datos.get('titulo', 'N/A')}")
        print(f"         Mensaje: {notif.datos.get('mensaje', 'N/A')}")
        print(f"         Fecha: {notif.created_at}")
    
except Exception as e:
    print(f"   ❌ Error verificando estado: {e}")
    import traceback
    traceback.print_exc()

# ============================================
# 7. VERIFICAR SEÑALES FCM
# ============================================
print("\n📋 PASO 7: Verificando señales FCM...")
try:
    import os
    habilitar_fcm = os.getenv('HABILITAR_SEÑAL_FCM', '')
    
    print(f"   HABILITAR_SEÑAL_FCM = '{habilitar_fcm}'")
    
    if habilitar_fcm and habilitar_fcm.lower() in ('1', 'true', 'si', 'yes'):
        print("   ✅ Señales FCM ACTIVADAS")
        print("      Las notificaciones se enviarán automáticamente via Firebase")
    else:
        print("   ⚠️  Señales FCM DESACTIVADAS")
        print("      Las notificaciones NO se enviarán automáticamente")
        print("      Para activarlas, configura: HABILITAR_SEÑAL_FCM=true")
        
except Exception as e:
    print(f"   ⚠️  Error verificando señales: {e}")

# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "="*80)
print("📊 RESUMEN DE LA PRUEBA")
print("="*80)
print(f"✅ Firebase: Inicializado correctamente")
print(f"✅ Usuario: {usuario.nombre} (ID: {usuario.id})")
print(f"✅ Dispositivo FCM: {'Activo' if dispositivo.activo else 'Inactivo'}")
print(f"✅ Campaña: Creada y ejecutada (ID: {campana.id})")
print(f"✅ Estado: {campana.get_estado_display()}")
print(f"✅ Enviados: {campana.total_enviados}")
print(f"❌ Errores: {campana.total_errores}")
print()

if campana.estado == 'COMPLETADA' and campana.total_enviados > 0:
    print("🎉 ¡SISTEMA FCM FUNCIONANDO CORRECTAMENTE!")
    print()
    print("📱 PRÓXIMOS PASOS:")
    print("   1. Abre la app Flutter en tu dispositivo")
    print("   2. Inicia sesión con tu usuario")
    print("   3. Verifica que aparezca la notificación")
    print("   4. Si no aparece, revisa los logs de Railway")
else:
    print("⚠️  ADVERTENCIA: La campaña no se completó exitosamente")
    print("   Revisa los errores arriba para más detalles")

print("="*80)
