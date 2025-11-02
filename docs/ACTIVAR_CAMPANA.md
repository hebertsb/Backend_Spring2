# 🚀 Activar Campaña - Request de Postman

## Endpoint
```
POST http://127.0.0.1:8000/api/campanas-notificacion/4/activar/
```

## Headers
```
Authorization: Token {tu_token_aqui}
Content-Type: application/json
```

## Body
```json
{}
```

## Response Esperada (200 OK)
```json
{
    "mensaje": "Campaña activada y ejecutada exitosamente",
    "campana": {
        "id": 4,
        "nombre": "Bienvenida",
        "estado": "COMPLETADA",
        "total_destinatarios": 1,
        "total_enviados": 1,
        "total_errores": 0,
        "fecha_enviada": "2025-11-02T02:00:00Z"
    }
}
```

## ¿Cómo obtener el token?

### 1. Hacer login:
```
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
    "email": "admin@sistema.com",
    "password": "admin12345"
}
```

### 2. Copiar el token de la respuesta:
```json
{
    "token": "a1b2c3d4e5f6g7h8..."  ← Este valor
}
```

### 3. Usarlo en el header:
```
Authorization: Token a1b2c3d4e5f6g7h8...
```

---

## 📱 Verificar en tu móvil

Después de activar:
1. Deberías recibir la notificación push inmediatamente
2. La notificación aparecerá en la bandeja de Android
3. Al tocarla, debería abrir tu app Flutter

---

## ⚠️ Si no llega la notificación

### Verificar que Firebase esté configurado:
```bash
py manage.py shell -c "import os; print('Firebase configurado:', os.getenv('RUTA_CUENTA_SERVICIO_FIREBASE'))"
```

### Ver logs del servidor:
Busca en la terminal del servidor mensajes como:
```
✓ Notificación enviada a Luis Fernando Blanco Bautista
✓ Token FCM: fs8XwZk...
```

### Verificar dispositivo FCM activo:
```bash
py scripts/ver_dispositivos_fcm.py
```

---

## 🔄 Enviar Prueba Primero (Recomendado)

Antes de activar, envía una notificación de prueba:

```
POST http://127.0.0.1:8000/api/campanas-notificacion/4/enviar_test/
Authorization: Token {tu_token}
Content-Type: application/json

{}
```

La notificación de prueba incluirá **[TEST]** en el título para diferenciarla.
