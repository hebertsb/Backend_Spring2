# 🚀 Guía Rápida - Campañas de Notificaciones en Postman

## 📋 Índice Rápido
- [Importar Colección](#-importar-colección)
- [Flujo Completo 5 Minutos](#-flujo-completo-en-5-minutos)
- [Ejemplos por Caso de Uso](#-ejemplos-por-caso-de-uso)
- [Troubleshooting](#-troubleshooting)

---

## 📥 Importar Colección

1. **Abre Postman**
2. **Import** → Arrastra estos archivos:
   - `postman/Campanas_Notificaciones.postman_collection.json`
   - `postman/Campanas_Notificaciones.postman_environment.json`
3. **Selecciona el environment** en la esquina superior derecha

---

## ⚡ Flujo Completo en 5 Minutos

### 1️⃣ Registrar Admin (si no tienes uno)

```
POST {{base_url}}/api/register/
```

```json
{
    "nombres": "Admin",
    "apellidos": "Sistema",
    "email": "admin@sistema.com",
    "password": "admin12345",
    "password_confirm": "admin12345",
    "rol": 1
}
```

✅ **201 Created** → Admin creado

---

### 2️⃣ Hacer Login

```
POST {{base_url}}/api/login/
```

```json
{
    "email": "admin@sistema.com",
    "password": "admin12345"
}
```

✅ **200 OK** → Token guardado automáticamente en `{{auth_token}}`

---

### 3️⃣ Crear Campaña

```
POST {{base_url}}/api/campanas-notificacion/
Headers: Authorization: Token {{auth_token}}
```

```json
{
    "nombre": "Bienvenida Nuevos Usuarios",
    "titulo": "¡Bienvenido a nuestro sistema! 🎉",
    "cuerpo": "Explora nuestros servicios y encuentra las mejores ofertas.",
    "tipo_notificacion": "campana_marketing",
    "tipo_audiencia": "TODOS",
    "enviar_inmediatamente": false
}
```

✅ **201 Created** → Campaña creada en BORRADOR  
✅ `campana_id` guardado automáticamente

---

### 4️⃣ Ver Preview

```
GET {{base_url}}/api/campanas-notificacion/{{campana_id}}/preview/
Headers: Authorization: Token {{auth_token}}
```

✅ **200 OK** → Ver destinatarios antes de enviar

**Respuesta:**
```json
{
    "campana": {
        "id": 1,
        "nombre": "Bienvenida Nuevos Usuarios",
        "estado": "BORRADOR"
    },
    "contenido": {
        "titulo": "¡Bienvenido a nuestro sistema! 🎉",
        "cuerpo": "Explora nuestros servicios..."
    },
    "destinatarios": [
        {
            "id": 4,
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "rol": "Cliente"
        }
    ],
    "estadisticas": {
        "total_destinatarios": 15,
        "distribucion_roles": {
            "Cliente": 12,
            "Proveedor": 3
        }
    }
}
```

---

### 5️⃣ Enviar Prueba (a ti mismo)

```
POST {{base_url}}/api/campanas-notificacion/{{campana_id}}/enviar_test/
Headers: Authorization: Token {{auth_token}}
```

```json
{}
```

✅ **200 OK** → Notificación de prueba enviada a tu dispositivo  
✅ Título incluye **[TEST]** para diferenciarla

---

### 6️⃣ Activar Campaña (envío masivo)

⚠️ **IMPORTANTE:** Esto envía a TODOS los destinatarios

```
POST {{base_url}}/api/campanas-notificacion/{{campana_id}}/activar/
Headers: Authorization: Token {{auth_token}}
```

```json
{}
```

✅ **200 OK** → Campaña ejecutada  
✅ Estado cambia a **COMPLETADA**

**Respuesta:**
```json
{
    "mensaje": "Campaña activada y ejecutada exitosamente",
    "campana": {
        "id": 1,
        "nombre": "Bienvenida Nuevos Usuarios",
        "estado": "COMPLETADA",
        "total_destinatarios": 15,
        "total_enviados": 15,
        "total_errores": 0,
        "fecha_enviada": "2025-11-01T20:30:00Z"
    }
}
```

---

### 7️⃣ Ver Métricas

```
GET {{base_url}}/api/campanas-notificacion/{{campana_id}}/
Headers: Authorization: Token {{auth_token}}
```

✅ Ver resultados: enviados, leídos, errores

---

## 🎯 Ejemplos por Caso de Uso

### Caso 1: Promoción Solo para Clientes

**Crear campaña segmentada:**

```json
{
    "nombre": "Black Friday - Solo Clientes",
    "titulo": "🔥 Black Friday: 50% de descuento",
    "cuerpo": "Solo para ti: descuentos exclusivos en todos los paquetes turísticos",
    "tipo_notificacion": "promocion",
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente"
    },
    "enviar_inmediatamente": false
}
```

**Ver cuántos recibirán:**
```
GET /api/campanas-notificacion/{{campana_id}}/preview/
```

---

### Caso 2: Recordatorio para Viajeros Frecuentes

**Crear campaña con filtros avanzados:**

```json
{
    "nombre": "Programa VIP - Viajeros Frecuentes",
    "titulo": "✈️ ¡Eres parte de nuestro programa VIP!",
    "cuerpo": "Gracias por ser un cliente frecuente. Disfruta beneficios exclusivos.",
    "tipo_notificacion": "recordatorio",
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente",
        "num_viajes__gte": 3
    },
    "enviar_inmediatamente": false
}
```

**Filtros disponibles:**
- `rol__nombre`: "Cliente", "Proveedor", "Administrador"
- `num_viajes__gte`: Mayor o igual a X viajes
- `num_viajes__lte`: Menor o igual a X viajes
- `pais`: "Bolivia", "Perú", etc.
- `genero`: "M", "F"

---

### Caso 3: Notificación a Usuarios Específicos

**Lista de IDs:**

```json
{
    "nombre": "Mensaje Personalizado - Grupo Beta",
    "titulo": "📢 Invitación exclusiva al programa Beta",
    "cuerpo": "Has sido seleccionado para probar nuestras nuevas funcionalidades",
    "tipo_notificacion": "sistema",
    "tipo_audiencia": "USUARIOS",
    "usuarios_objetivo": [4, 5, 8, 12, 15],
    "enviar_inmediatamente": false
}
```

---

### Caso 4: Campaña Programada

**Enviar mañana a las 10 AM:**

```json
{
    "nombre": "Recordatorio Semanal",
    "titulo": "📅 Esta semana en tu destino favorito",
    "cuerpo": "Revisa las nuevas ofertas para tus destinos guardados",
    "tipo_notificacion": "recordatorio",
    "tipo_audiencia": "TODOS",
    "enviar_inmediatamente": false,
    "fecha_programada": "2025-11-02T10:00:00Z"
}
```

**Activar sin ejecutar inmediatamente:**
```
POST /api/campanas-notificacion/{{campana_id}}/activar/
```

Estado cambiará a: **PROGRAMADA**

**Ejecutar campañas programadas (en servidor):**
```bash
py manage.py ejecutar_campanas_programadas
```

O con **Task Scheduler (Windows)** / **Cron (Linux)** cada hora.

---

## 🔍 Consultas Útiles

### Listar todas las campañas

```
GET {{base_url}}/api/campanas-notificacion/
Headers: Authorization: Token {{auth_token}}
```

---

### Filtrar por estado

```
GET {{base_url}}/api/campanas-notificacion/?estado=BORRADOR
```

Estados disponibles:
- `BORRADOR` - Editable
- `PROGRAMADA` - Esperando fecha
- `EN_CURSO` - Enviando (temporal)
- `COMPLETADA` - Enviada
- `CANCELADA` - Cancelada

---

### Buscar por nombre

```
GET {{base_url}}/api/campanas-notificacion/?search=Black Friday
```

---

### Ordenar por fecha

```
GET {{base_url}}/api/campanas-notificacion/?ordering=-created_at
```

---

### Cancelar campaña

```
POST {{base_url}}/api/campanas-notificacion/{{campana_id}}/cancelar/
Headers: Authorization: Token {{auth_token}}
```

Solo funciona si está en **BORRADOR** o **PROGRAMADA**

---

### Actualizar métricas (recalcular leídos)

```
POST {{base_url}}/api/campanas-notificacion/{{campana_id}}/actualizar_metricas/
Headers: Authorization: Token {{auth_token}}
```

---

## 📊 Entender las Métricas

```json
{
    "total_destinatarios": 100,    // Usuarios objetivo
    "total_enviados": 98,           // Notificaciones enviadas exitosamente
    "total_errores": 2,             // Fallos (sin dispositivo FCM, etc.)
    "total_leidos": 45              // Notificaciones abiertas
}
```

**Cálculos útiles:**
- **Tasa de éxito:** `(total_enviados / total_destinatarios) * 100`
- **Tasa de apertura:** `(total_leidos / total_enviados) * 100`
- **Tasa de error:** `(total_errores / total_destinatarios) * 100`

---

## 🛠️ Troubleshooting

### ❌ Error 401 Unauthorized

**Problema:** No estás autenticado

**Solución:**
1. Ejecuta **Login Admin** primero
2. Verifica que el token se guardó en `{{auth_token}}`
3. Verifica el header: `Authorization: Token {{auth_token}}`

---

### ❌ Error 403 Forbidden

**Problema:** No tienes permisos de administrador

**Solución:**
1. Verifica que tu usuario tenga `rol: 1` (Administrador)
2. Verifica que `is_staff: true` en la respuesta de login
3. Re-registra el usuario con `rol: 1`

---

### ❌ "No se puede activar una campaña en estado X"

**Problema:** La campaña no está en BORRADOR

**Solución:**
- Solo puedes activar campañas en **BORRADOR**
- Si está **PROGRAMADA**, cancélala primero
- Si está **COMPLETADA**, crea una nueva campaña

---

### ❌ "La campaña no tiene destinatarios"

**Problema:** Los filtros no coinciden con ningún usuario

**Solución:**
1. Usa **Preview** para ver quiénes cumplen los filtros
2. Ajusta `segmento_filtros`
3. Verifica que hay usuarios con ese rol/características

---

### ❌ No llegan notificaciones al dispositivo

**Problema:** Configuración de Firebase o dispositivo sin token

**Solución:**
1. Verifica que `RUTA_CUENTA_SERVICIO_FIREBASE` esté configurada
2. Verifica que el usuario tenga dispositivos FCM registrados:
   ```
   GET {{base_url}}/api/fcm-dispositivos/
   ```
3. Registra un dispositivo desde tu app Flutter
4. Revisa logs del servidor para errores de FCM

---

### ❌ "total_errores" muy alto

**Problema:** Muchos usuarios sin dispositivos FCM

**Solución:**
- Normal si los usuarios no tienen la app instalada
- Usa filtros para enviar solo a usuarios activos
- Considera segmentar por fecha de última actividad (si está disponible)

---

## 🎨 Tipos de Notificación Disponibles

```json
{
    "tipo_notificacion": "..."
}
```

Valores permitidos:
- `campana_marketing` - Campañas publicitarias
- `promocion` - Ofertas y descuentos
- `recordatorio` - Recordatorios generales
- `sistema` - Mensajes del sistema
- `ticket_nuevo` - Nuevo ticket (reactivo)
- `ticket_respondido` - Ticket respondido (reactivo)
- `ticket_cerrado` - Ticket cerrado (reactivo)

💡 Los tipos `ticket_*` se usan automáticamente por el sistema de tickets.

---

## 🔔 Diferencia entre Notificaciones

### Campañas (Proactivas)
- Creadas manualmente por administrador
- Control total sobre audiencia y contenido
- Métricas detalladas
- Preview antes de enviar

### Notificaciones Reactivas (Automáticas)
- Generadas por eventos del sistema
- Tickets, reservas, pagos, etc.
- Se envían automáticamente vía signals
- No aparecen como campañas

**Identificar en app Flutter:**
```dart
// Campaña
notification.data['campana_id'] != null

// Reactiva
notification.data['ticket_id'] != null
```

---

## 📚 Recursos Adicionales

- **Documentación completa:** `docs/CAMPANAS_NOTIFICACIONES_GUIA.md`
- **Registro de admin:** `postman/REGISTRO_ADMINISTRADOR.md`
- **Resumen técnico:** `docs/RESUMEN_IMPLEMENTACION_CAMPANAS.md`
- **Django Admin:** `http://127.0.0.1:8000/admin/condominio/campananotificacion/`

---

## 🎯 Checklist de Testing Completo

- [ ] Registrar administrador
- [ ] Hacer login y guardar token
- [ ] Crear campaña para todos
- [ ] Ver preview de destinatarios
- [ ] Enviar notificación de prueba
- [ ] Verificar notificación en dispositivo
- [ ] Activar campaña (envío masivo)
- [ ] Ver métricas de la campaña
- [ ] Crear campaña segmentada (solo clientes)
- [ ] Crear campaña con usuarios específicos
- [ ] Crear campaña programada
- [ ] Cancelar una campaña
- [ ] Actualizar métricas de campaña
- [ ] Filtrar campañas por estado
- [ ] Buscar campañas por texto

---

## 🚀 Scripts Útiles

### Iniciar servidor
```bash
py manage.py runserver
```

### Ejecutar campañas programadas (dry-run)
```bash
py manage.py ejecutar_campanas_programadas --dry-run
```

### Ejecutar campaña específica
```bash
py manage.py ejecutar_campanas_programadas --force-id 5
```

### Crear superuser (desde consola)
```bash
py manage.py createsuperuser
```

### Ver usuarios en DB
```bash
py manage.py shell -c "from condominio.models import Usuario; print(f'Total usuarios: {Usuario.objects.count()}')"
```

---

## 🎉 ¡Listo para Producción!

El sistema está completamente funcional y listo para usar. Sigue el flujo de 5 minutos arriba para tu primera campaña.

**¿Preguntas?** Revisa la documentación en `docs/` o consulta los ejemplos en la colección de Postman.
