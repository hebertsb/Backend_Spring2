# 🚀 Guía Rápida - Testing con Postman

## 📥 Importar Colección en Postman

### Paso 1: Importar archivos
1. Abre **Postman**
2. Clic en **Import** (botón superior izquierdo)
3. Arrastra o selecciona estos archivos:
   - `Campanas_Notificaciones.postman_collection.json`
   - `Campanas_Notificaciones.postman_environment.json`

### Paso 2: Configurar Environment
1. En la esquina superior derecha, selecciona el environment: **"Campañas Notificaciones - Local"**
2. Verifica que `base_url` esté en `http://127.0.0.1:8000`

---

## 🚀 Flujo de Prueba Recomendado

### ✅ PASO 0: Registrar Administrador (Solo si no tienes uno)

**Request:** `1. Autenticación y Registro > Registrar Administrador`
- **Método:** POST
- **URL:** `{{base_url}}/api/register/`
- **Body:**
```json
{
    "nombres": "Admin",
    "apellidos": "Campañas",
    "email": "admin.campanas@sistema.com",
    "password": "AdminCamp2024!",
    "password_confirm": "AdminCamp2024!",
    "rol": 1
}
```

**Roles Disponibles:**
- `1` = Administrador (para crear campañas)
- `2` = Cliente
- `3` = Proveedor
- `4` = Soporte

**Resultado esperado:**
- Status: 201 Created
- El usuario admin se crea con `is_staff: true`
- Guarda el email y password para hacer login

**💡 Nota:** Si ya tienes un usuario admin, salta al PASO 1.

---

### ✅ PASO 1: Autenticación

**Request:** `1. Autenticación y Registro > Login Admin`
- **Método:** POST
- **URL:** `{{base_url}}/api/login/`
- **Body:**
```json
{
    "email": "admin@admin.com",
    "password": "admin123"
}
```

**Nota:** Si no tienes un usuario admin, créalo con:
```bash
py manage.py createsuperuser
```

**Resultado esperado:**
- Status: 200 OK
- El token se guarda automáticamente en `{{auth_token}}`

---

### ✅ PASO 2: Crear Campaña de Prueba

**Request:** `2. Campañas - CRUD Básico > Crear Campaña - Todos los Usuarios`
- **Método:** POST
- **URL:** `{{base_url}}/api/campanas-notificacion/`
- **Headers:** `Authorization: Token {{auth_token}}`

**Resultado esperado:**
- Status: 201 Created
- `campana_id` se guarda automáticamente
- Estado: "BORRADOR"
- `puede_activarse: true`

---

### ✅ PASO 3: Ver Preview de Destinatarios

**Request:** `3. Acciones de Campaña > Preview - Ver Destinatarios`
- **Método:** GET
- **URL:** `{{base_url}}/api/campanas-notificacion/{{campana_id}}/preview/`

**Qué verás:**
- Contenido completo de la notificación
- Lista de destinatarios (primeros 50)
- Estadísticas de segmentación
- Distribución por roles

---

### ✅ PASO 4: Enviar Notificación de Prueba

**Request:** `3. Acciones de Campaña > Enviar Notificación de Prueba`
- **Método:** POST
- **URL:** `{{base_url}}/api/campanas-notificacion/{{campana_id}}/enviar_test/`
- **Body (opcional):**
```json
{
    "usuario_id": 4
}
```

**Nota:** Si no especificas `usuario_id`, se envía al usuario actual (el admin que está autenticado).

**Resultado esperado:**
- La notificación llega a tu dispositivo
- Puedes verificar cómo se ve antes de enviarla masivamente

---

### ✅ PASO 5: Activar Campaña (Envío Real)

**Request:** `3. Acciones de Campaña > Activar Campaña (Envío Inmediato)`
- **Método:** POST
- **URL:** `{{base_url}}/api/campanas-notificacion/{{campana_id}}/activar/`

**⚠️ IMPORTANTE:** Esta acción envía la notificación a TODOS los destinatarios.

**Resultado esperado:**
- Status: 200 OK
- Estado cambia a "COMPLETADA"
- `total_enviados` muestra cuántas notificaciones se enviaron
- `total_errores` debe ser 0

---

### ✅ PASO 6: Verificar en Dispositivo Flutter

1. Abre tu app Flutter
2. Deberías ver la notificación en la bandeja
3. Al tocar, la app debería abrirse (si configuraste deep link)

---

### ✅ PASO 7: Ver Métricas

**Request:** `2. Campañas - CRUD Básico > Ver Detalle de Campaña`
- **Método:** GET
- **URL:** `{{base_url}}/api/campanas-notificacion/{{campana_id}}/`

**Métricas disponibles:**
- `total_destinatarios`: Usuarios objetivo
- `total_enviados`: Notificaciones enviadas exitosamente
- `total_errores`: Fallos en el envío
- `total_leidos`: Notificaciones leídas (actualizar con acción correspondiente)

---

## 🎨 Otros Casos de Uso

### Campaña Segmentada (Solo Clientes)

**Request:** `2. Campañas - CRUD Básico > Crear Campaña - Solo Clientes`

**Segmentación:**
```json
{
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente"
    }
}
```

### Campaña Programada

**Request:** `5. Ejemplos Avanzados > Campaña Programada para Mañana`

**Configuración:**
```json
{
    "enviar_inmediatamente": false,
    "fecha_programada": "2025-11-02T10:00:00Z"
}
```

**Nota:** Necesitas tener el scheduler corriendo:
```bash
py manage.py ejecutar_campanas_programadas
```

### Usuarios Específicos

**Request:** `5. Ejemplos Avanzados > Campaña - Lista de Usuarios Específicos`

**Configuración:**
```json
{
    "tipo_audiencia": "USUARIOS",
    "usuarios_objetivo": [4, 5, 6]
}
```

---

## 🔍 Filtros y Búsquedas

### Filtrar por Estado
```
GET {{base_url}}/api/campanas-notificacion/?estado=BORRADOR
```

Estados disponibles:
- `BORRADOR`
- `PROGRAMADA`
- `EN_CURSO`
- `COMPLETADA`
- `CANCELADA`

### Buscar por Texto
```
GET {{base_url}}/api/campanas-notificacion/?search=Postman
```

Busca en: nombre, título, descripción

### Ordenar Resultados
```
GET {{base_url}}/api/campanas-notificacion/?ordering=-created_at
```

Campos ordenables:
- `created_at` (fecha de creación)
- `fecha_programada`
- `fecha_enviada`
- Usar `-` para orden descendente

---

## 📊 Tipos de Notificación Disponibles

```json
{
    "tipo_notificacion": "sistema" | "promocion" | "recordatorio" | "campana_marketing" | "ticket_nuevo" | "ticket_respondido" | "ticket_cerrado"
}
```

---

## 🎯 Tipos de Audiencia

### TODOS
```json
{
    "tipo_audiencia": "TODOS"
}
```
Envía a todos los usuarios activos del sistema.

### USUARIOS (Lista específica)
```json
{
    "tipo_audiencia": "USUARIOS",
    "usuarios_objetivo": [1, 2, 3, 4]
}
```
Envía solo a los IDs especificados.

### SEGMENTO (Filtros dinámicos)
```json
{
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente",
        "num_viajes__gte": 5,
        "pais": "Bolivia"
    }
}
```

**Filtros comunes:**
- `rol__nombre`: "Cliente", "Administrador", "Proveedor"
- `num_viajes__gte`: Mayor o igual a X viajes
- `num_viajes__lte`: Menor o igual a X viajes
- `pais`: País del usuario
- `genero`: "M" o "F"

---

## 🛠️ Troubleshooting

### Error 401 Unauthorized
- Verifica que hayas hecho login
- Verifica que el token esté en el header: `Authorization: Token {{auth_token}}`

### Error 403 Forbidden
- Solo usuarios admin pueden crear/modificar campañas
- Verifica que tu usuario tenga `is_staff=True`

### "No se puede activar una campaña en estado X"
- Solo puedes activar campañas en estado BORRADOR
- Si está PROGRAMADA, cancélala primero

### "La campaña no tiene destinatarios"
- Verifica los filtros de segmentación
- Usa el endpoint de Preview para ver quiénes recibirán la notificación

### No llegan notificaciones al dispositivo
- Verifica que Firebase esté configurado: `RUTA_CUENTA_SERVICIO_FIREBASE`
- Verifica que el usuario tenga dispositivos FCM activos
- Revisa logs del servidor

---

## 📚 Recursos Adicionales

- **Documentación completa:** `docs/CAMPANAS_NOTIFICACIONES_GUIA.md`
- **Resumen técnico:** `docs/RESUMEN_IMPLEMENTACION_CAMPANAS.md`
- **Django Admin:** `http://127.0.0.1:8000/admin/condominio/campananotificacion/`

---

## 🎉 Flujo Completo de Ejemplo

```
1. Login Admin
   ↓
2. Crear Campaña → Guarda campana_id automáticamente
   ↓
3. Ver Preview → Verificar destinatarios
   ↓
4. Enviar Prueba → Verificar en tu dispositivo
   ↓
5. Ajustar si es necesario → Editar campaña
   ↓
6. Activar Campaña → Envío masivo
   ↓
7. Verificar Métricas → Ver resultados
```

---

## 🔔 Variables de Environment Automáticas

Estas variables se actualizan automáticamente al ejecutar los requests:

- `{{auth_token}}` - Se guarda al hacer login
- `{{user_id}}` - ID del usuario autenticado
- `{{campana_id}}` - ID de la última campaña creada (TODOS)
- `{{campana_segmentada_id}}` - ID de la última campaña segmentada

---

**¡Listo para probar!** 🚀

Comienza con el flujo recomendado arriba y explora los demás endpoints según tus necesidades.
