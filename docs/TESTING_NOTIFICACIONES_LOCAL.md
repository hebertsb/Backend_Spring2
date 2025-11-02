# 🧪 Testing de Notificaciones Push en Desarrollo Local

## ⚠️ Problema: Dispositivo USB no recibe notificaciones

Cuando tu dispositivo Android/iOS está conectado por **USB para debugging**, las notificaciones push de Firebase **NO llegarán** porque:

1. Firebase Cloud Messaging (FCM) requiere conexión a internet activa
2. El dispositivo debe poder comunicarse con los servidores de Firebase/Google
3. USB solo proporciona debugging, no conexión a internet

---

## ✅ Soluciones para Testing Local

### Opción 1: Conectar Dispositivo a WiFi (RECOMENDADO)

```bash
# 1. Mantén el USB conectado para logs
# 2. Activa WiFi en tu dispositivo
# 3. Conéctate a la misma red que tu PC
# 4. La app seguirá funcionando y recibirá notificaciones
```

**Verificar que funciona:**
- El token FCM debe seguir activo
- El backend debe poder enviar a los servidores de Firebase
- Firebase enviará la notificación al dispositivo vía WiFi

---

### Opción 2: Usar Emulador Android con Google Play Services

```bash
# Android Studio Emulator con Google Play
# 1. Crear AVD con imagen "Google APIs" o "Google Play"
# 2. El emulador tiene conexión a internet
# 3. Instalar tu app en el emulador
# 4. Registrar token FCM desde el emulador
```

---

### Opción 3: Testing con Postman/cURL (Sin Dispositivo)

Puedes verificar que el backend **SÍ está enviando** correctamente:

```bash
# Ver respuesta de Firebase al enviar notificación
py scripts/test_fcm_send.py
```

Esto mostrará:
- ✅ Token válido
- ✅ Mensaje enviado a Firebase
- ✅ Respuesta de Firebase (success/failure)
- ❌ El dispositivo NO la recibirá si no tiene internet

---

## 🔍 Diagnóstico Actual

### 1. Verificar Token FCM Activo

```bash
py scripts/ver_dispositivos_fcm.py
```

**Salida esperada:**
```
✅ Dispositivos activos: 1
   Luis Fernando Blanco Bautista
   Token: fs8XwZkqRP2bOTt3Bpw78H...
   Tipo: android
   Última actividad: 2025-11-01 20:15:23
```

### 2. Verificar Campaña Programada

```bash
py scripts/verificar_campana.py 5
```

**Verifica:**
- Estado: PROGRAMADA ✅
- Destinatarios: 1 usuario con dispositivo activo ✅
- Fecha programada: Futura ✅

### 3. Activar Campaña Manualmente (Prueba Inmediata)

```bash
# Desde Python shell
py manage.py shell
```

```python
from condominio.models import CampanaNotificacion
from condominio.tasks import ejecutar_campana_notificacion

# Campaña "Dia de Muertos" (ID 5)
campana = CampanaNotificacion.objects.get(id=5)

# Cambiar a envío inmediato
campana.enviar_inmediatamente = True
campana.save()

# Activar campaña
from condominio.api import CampanaNotificacionViewSet
# O desde Postman: POST /api/campanas-notificacion/5/activar/
```

---

## 🛠️ Debugging: ¿Realmente se envió?

### Script para ver respuesta de Firebase:

```python
# tmp_test_firebase_response.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import DispositivoFCM, Usuario
from firebase_admin import messaging
import firebase_admin

# Inicializar Firebase si no está ya
if not firebase_admin._apps:
    import json
    from pathlib import Path
    
    cred_path = Path(__file__).parent / 'serviceAccountKey.json'
    if cred_path.exists():
        cred = firebase_admin.credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)

# Obtener dispositivo de Luis Fernando
usuario = Usuario.objects.get(nombre__icontains='Luis Fernando')
dispositivo = DispositivoFCM.objects.filter(usuario=usuario, activo=True).first()

if not dispositivo:
    print("❌ No hay dispositivo FCM activo")
    exit()

print(f"📱 Dispositivo: {dispositivo.tipo}")
print(f"🔑 Token: {dispositivo.token[:30]}...")

# Crear mensaje de prueba
mensaje = messaging.Message(
    notification=messaging.Notification(
        title="🧪 Test Local",
        body="Si recibes esto, FCM funciona ✅"
    ),
    token=dispositivo.token
)

try:
    response = messaging.send(mensaje)
    print(f"\n✅ Mensaje enviado a Firebase")
    print(f"   Response: {response}")
    print(f"\n💡 Ahora espera 5-10 segundos...")
    print(f"   Si tu dispositivo tiene INTERNET, debería llegar")
except Exception as e:
    print(f"\n❌ Error al enviar: {e}")
```

```bash
py tmp_test_firebase_response.py
```

---

## 🔥 Verificar Configuración Firebase

### 1. Archivo `serviceAccountKey.json` existe?

```bash
ls serviceAccountKey.json
```

### 2. Credenciales válidas?

```python
# Verificar en Python shell
py manage.py shell
```

```python
import firebase_admin
from firebase_admin import credentials

# Ver apps inicializadas
print(firebase_admin._apps)

# Si está vacío, inicializar
if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    print("✅ Firebase inicializado")
else:
    print("✅ Firebase ya estaba inicializado")
```

---

## 📊 Logs de Backend al Activar Campaña

Cuando actives la campaña desde el frontend, deberías ver en el terminal del backend:

```bash
# Logs esperados:
[02/Nov/2025 02:03:01] "POST /api/campanas-notificacion/5/activar/ HTTP/1.1" 200 134

# Si el envío falla, verás:
ERROR: No se pudo enviar notificación a dispositivo xxx
Razón: [detalle del error]
```

---

## ✅ Checklist de Debugging

- [ ] Dispositivo tiene **WiFi o datos móviles** activados
- [ ] App tiene permisos de notificaciones
- [ ] Token FCM registrado en base de datos (`ver_dispositivos_fcm.py`)
- [ ] Campaña en estado PROGRAMADA o EN_CURSO
- [ ] Usuario es destinatario de la campaña
- [ ] Backend muestra logs de envío exitoso
- [ ] `serviceAccountKey.json` existe y es válido
- [ ] Firebase Admin SDK inicializado correctamente

---

## 🎯 Prueba Rápida: Envío Manual Directo

```bash
py manage.py shell
```

```python
from condominio.models import Usuario, DispositivoFCM, Notificacion
from condominio.tasks import enviar_notificacion_push

# Obtener usuario
usuario = Usuario.objects.get(nombre__icontains='Luis Fernando')

# Crear notificación de prueba
notif = Notificacion.objects.create(
    usuario=usuario,
    titulo="🧪 Test Manual",
    cuerpo="Prueba de notificación directa",
    tipo="campana_marketing"
)

# Enviar
resultado = enviar_notificacion_push(notif.id)
print(f"Resultado: {resultado}")
```

**Si retorna `True`**: El mensaje se envió a Firebase ✅  
**Si retorna `False`**: Hubo un error en el envío ❌

---

## 💡 Solución Temporal: Simular Recepción

Si no puedes conectar el dispositivo a internet, puedes:

1. **Ver en logs del backend** que SÍ se envió
2. **Verificar en Firebase Console** que el mensaje llegó a Firebase
3. **Confiar en que funcionará** cuando el dispositivo tenga internet

```bash
# Firebase Console
https://console.firebase.google.com/
# → Cloud Messaging → Logs
```

---

## 🚀 Alternativa: Usar Expo Push Notification Tool

Si usas Expo en tu app móvil:

```bash
# Instalar expo-cli
npm install -g expo-cli

# Enviar notificación de prueba
expo push:send \
  --to="ExponentPushToken[xxxxx]" \
  --title="Test" \
  --body="Prueba desde CLI"
```

---

## 📝 Resumen

| Método | Requiere Internet | Funciona en USB | Recomendación |
|--------|-------------------|-----------------|---------------|
| USB solo | ❌ No | ❌ No | No usar para FCM |
| USB + WiFi | ✅ Sí | ✅ Sí | **MEJOR OPCIÓN** |
| Emulador | ✅ Sí | N/A | Buena alternativa |
| Script Python | ✅ Sí (backend) | N/A | Solo para verificar envío |

---

## 🎯 Próximo Paso RECOMENDADO

1. **Conecta tu dispositivo a WiFi** (misma red que tu PC)
2. **Mantén USB conectado** para ver logs de Android Studio
3. **Activa la campaña** desde el frontend
4. **Espera 5-10 segundos** para que llegue la notificación

Si sigue sin llegar con WiFi, entonces es un problema de:
- Configuración de Firebase
- Permisos de la app
- Token FCM inválido
