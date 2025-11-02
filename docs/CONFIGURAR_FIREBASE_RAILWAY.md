# 🚀 Configurar Firebase en Railway (Producción)

## ⚠️ Problema
Las credenciales de Firebase (`CredencialFirebase/*.json`) NO deben subirse a GitHub por seguridad, pero Railway necesita acceder a ellas para enviar notificaciones push.

## ✅ Solución: Variables de Entorno

---

## 📋 Paso 1: Copiar el Contenido del JSON

Abre tu archivo de credenciales:
```
d:\Sis2\Final\Backend_Spring2\CredencialFirebase\notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json
```

**Copia TODO el contenido** (debería verse así):
```json
{
  "type": "service_account",
  "project_id": "notiguiaturistica",
  "private_key_id": "91d541d103c76b67a4f595b169b45a9ba77999a6",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@notiguiaturistica.iam.gserviceaccount.com",
  ...
}
```

---

## 🔧 Paso 2: Configurar en Railway

### 2.1 Ir a Variables de Entorno
1. Abre tu proyecto en [Railway Dashboard](https://railway.app/)
2. Selecciona tu servicio de backend
3. Ve a la pestaña **"Variables"**

### 2.2 Agregar Variable
1. Click en **"New Variable"**
2. **Nombre:** `FIREBASE_CREDENTIALS_JSON`
3. **Valor:** Pega TODO el contenido del JSON (el que copiaste en el Paso 1)
4. Click en **"Add"**

### 2.3 Verificar
Debería verse algo así:
```
FIREBASE_CREDENTIALS_JSON = {"type":"service_account","project_id":"notiguiaturistica",...}
```

---

## 🧪 Paso 3: Probar Localmente (Simular Railway)

Para probar que funciona antes de hacer deploy:

### Windows PowerShell:
```powershell
# Leer el archivo y asignarlo a variable
$json = Get-Content "CredencialFirebase\notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json" -Raw
$env:FIREBASE_CREDENTIALS_JSON = $json

# Quitar la variable de ruta (para forzar usar JSON)
Remove-Item Env:RUTA_CUENTA_SERVICIO_FIREBASE -ErrorAction SilentlyContinue

# Iniciar servidor
py manage.py runserver
```

### Linux/Mac:
```bash
export FIREBASE_CREDENTIALS_JSON=$(cat CredencialFirebase/notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json)
unset RUTA_CUENTA_SERVICIO_FIREBASE
python manage.py runserver
```

---

## 📝 Paso 4: Commit y Deploy

### 4.1 Verificar .gitignore
Asegúrate que tu `.gitignore` tenga:
```
CredencialFirebase/
serviceAccountKey.json
*.json
```

### 4.2 Commit el código actualizado
```bash
git add core/firebase.py
git commit -m "feat: Soporte para Firebase credentials en Railway"
git push origin main
```

### 4.3 Railway hace deploy automático
Railway detectará el push y hará deploy automáticamente.

---

## 🔍 Paso 5: Verificar que Funciona en Railway

### 5.1 Ver Logs de Railway
1. En Railway Dashboard → Tu servicio
2. Click en **"Deployments"**
3. Click en el último deployment
4. Revisa los logs

**Busca este mensaje:**
```
✅ Firebase inicializado correctamente
```

### 5.2 Probar Envío de Notificación
Desde Postman o tu frontend:
```http
POST https://tu-dominio.railway.app/api/campanas-notificacion/
Authorization: Token tu_token_de_admin

{
  "nombre": "Prueba Railway",
  "titulo": "Test desde producción",
  "cuerpo": "Si recibes esto, Firebase funciona en Railway ✅",
  "tipo_notificacion": "campana_marketing",
  "tipo_audiencia": "USUARIOS",
  "usuarios_objetivo": [4],
  "enviar_inmediatamente": true
}
```

---

## 🎯 Resumen de Configuración

| Entorno | Variable a Usar | Dónde Configurar |
|---------|-----------------|------------------|
| **Desarrollo Local** | `RUTA_CUENTA_SERVICIO_FIREBASE` | PowerShell / Terminal |
| **Producción (Railway)** | `FIREBASE_CREDENTIALS_JSON` | Railway Variables |

---

## 🛠️ Configuración Local para Desarrollo

Para tu desarrollo local diario, sigue usando la ruta:

### Opción 1: PowerShell cada vez
```powershell
$env:RUTA_CUENTA_SERVICIO_FIREBASE = 'D:\Sis2\Final\Backend_Spring2\CredencialFirebase\notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json'
py manage.py runserver
```

### Opción 2: Crear archivo `.env` (RECOMENDADO)
1. Crea archivo `.env` en la raíz del proyecto
2. Agrega:
```env
RUTA_CUENTA_SERVICIO_FIREBASE=D:\Sis2\Final\Backend_Spring2\CredencialFirebase\notiguiaturistica-firebase-adminsdk-fbsvc-91d541d103.json
```
3. Instala python-decouple:
```bash
pip install python-decouple
```
4. En `config/settings.py`, al inicio:
```python
from decouple import config

# ... más abajo donde se use
RUTA_CUENTA_SERVICIO_FIREBASE = config('RUTA_CUENTA_SERVICIO_FIREBASE', default=None)
```

---

## ❌ Errores Comunes

### Error 1: "RuntimeError: No se encontró configuración de Firebase"
**Causa:** No configuraste ninguna variable de entorno  
**Solución:** Configura `FIREBASE_CREDENTIALS_JSON` en Railway

### Error 2: "JSONDecodeError"
**Causa:** El JSON está mal formateado o incompleto  
**Solución:** 
- Verifica que copiaste TODO el contenido del archivo
- Incluye las llaves `{` `}` al inicio y final
- No modifiques nada del contenido

### Error 3: "The caller does not have permission"
**Causa:** Las credenciales son de otro proyecto Firebase  
**Solución:** 
- Verifica que el `project_id` sea `notiguiaturistica`
- Descarga credenciales nuevas desde Firebase Console

### Error 4: "Invalid registration token"
**Causa:** El token FCM del dispositivo es inválido o expiró  
**Solución:** 
- El usuario debe abrir la app nuevamente
- La app debe registrar el token FCM nuevamente

---

## 🔒 Seguridad

### ✅ HACER:
- ✅ Usar variables de entorno en producción
- ✅ Mantener `CredencialFirebase/` en `.gitignore`
- ✅ Rotar credenciales si se exponen accidentalmente
- ✅ Usar credenciales diferentes para dev y prod

### ❌ NO HACER:
- ❌ Commitear el archivo JSON a GitHub
- ❌ Compartir credenciales por chat/email
- ❌ Usar las mismas credenciales en múltiples proyectos
- ❌ Hardcodear credenciales en el código

---

## 📚 Referencias

- [Firebase Admin SDK - Python](https://firebase.google.com/docs/admin/setup)
- [Railway Variables](https://docs.railway.app/develop/variables)
- [Python Decouple](https://github.com/HBNetwork/python-decouple)

---

## 🆘 Troubleshooting

Si sigues teniendo problemas:

1. **Verificar que Firebase esté instalado:**
   ```bash
   pip show firebase-admin
   ```

2. **Probar inicialización manual:**
   ```bash
   py manage.py shell
   ```
   ```python
   from core.firebase import iniciar_firebase
   app = iniciar_firebase()
   print(f"✅ Firebase OK: {app.name}")
   ```

3. **Ver logs detallados de Railway:**
   - Railway Dashboard → Deployments → View Logs

4. **Contactar soporte:**
   - Si nada funciona, revisa los logs completos del servidor
   - Verifica que `firebase-admin` esté en `requirements.txt`
