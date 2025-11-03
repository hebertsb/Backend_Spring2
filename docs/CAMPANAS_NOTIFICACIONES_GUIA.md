# 📢 Sistema de Campañas de Notificaciones Push - Guía de Uso

## 🎯 Descripción General

Sistema completo para gestión administrativa de campañas de notificaciones push con las siguientes capacidades:

- ✅ **Control administrativo** de campañas
- ✅ **Segmentación avanzada** de usuarios
- ✅ **Preview** antes de enviar
- ✅ **Envío de prueba** a dispositivos específicos
- ✅ **Programación** de envíos futuros
- ✅ **Métricas** de envío y lectura
- ✅ **Integración transparente** con sistema FCM existente

---

## 📊 Arquitectura

```
┌─────────────────────────────────────────┐
│  Admin crea CampañaNotificacion         │
│  (segmentación, contenido, scheduling)  │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│  Admin activa campaña                   │
│  - Inmediata: ejecuta ahora             │
│  - Programada: espera fecha             │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│  tasks.ejecutar_campana_notificacion()  │
│  Crea Notificacion por cada usuario     │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│  Signal notificacion_post_save_fcm      │
│  Envía push automáticamente             │
└─────────────────────────────────────────┘
```

---

## 🚀 Endpoints Disponibles

### Base URL: `/api/campanas-notificacion/`

#### 1️⃣ Listar Campañas
```http
GET /api/campanas-notificacion/
Authorization: Token {tu_token}
```

**Filtros disponibles:**
- `?estado=BORRADOR` - Filtrar por estado
- `?tipo_audiencia=TODOS` - Filtrar por tipo de audiencia
- `?search=promocion` - Buscar por nombre/título

**Respuesta:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "nombre": "Campaña Promocional Black Friday",
      "estado": "BORRADOR",
      "estado_display": "Borrador",
      "tipo_audiencia": "SEGMENTO",
      "titulo": "¡Black Friday! 50% descuento",
      "cuerpo": "Aprovecha nuestras ofertas exclusivas...",
      "total_destinatarios": 150,
      "puede_activarse": true,
      "puede_editarse": true,
      "preview_destinatarios": {
        "total": 150,
        "muestra": [
          {"id": 4, "nombre": "Luis Blanco", "email": "luis@prueba.com", "rol": "Cliente"}
        ]
      },
      "created_at": "2025-11-01T10:30:00Z"
    }
  ]
}
```

---

#### 2️⃣ Crear Campaña
```http
POST /api/campanas-notificacion/
Authorization: Token {token_admin}
Content-Type: application/json
```

**Body:**
```json
{
  "nombre": "Promoción Fin de Semana",
  "descripcion": "Campaña para usuarios con más de 5 viajes",
  "titulo": "🎉 Oferta Especial para Ti",
  "cuerpo": "Como cliente VIP, tienes 30% de descuento este fin de semana",
  "tipo_notificacion": "promocion",
  "tipo_audiencia": "SEGMENTO",
  "segmento_filtros": {
    "num_viajes__gte": 5,
    "rol__nombre": "Cliente"
  },
  "datos_extra": {
    "imagen_url": "https://ejemplo.com/promo.jpg",
    "deep_link": "/paquetes",
    "codigo_descuento": "VIP30"
  },
  "enviar_inmediatamente": false,
  "fecha_programada": "2025-11-05T10:00:00Z"
}
```

**Respuesta:**
```json
{
  "id": 5,
  "nombre": "Promoción Fin de Semana",
  "estado": "BORRADOR",
  "puede_activarse": true,
  "preview_destinatarios": {
    "total": 45,
    "muestra": [...]
  },
  ...
}
```

---

#### 3️⃣ Ver Preview de Campaña
```http
GET /api/campanas-notificacion/{id}/preview/
Authorization: Token {token_admin}
```

**Respuesta:**
```json
{
  "campana": {
    "id": 5,
    "nombre": "Promoción Fin de Semana",
    "estado": "BORRADOR"
  },
  "contenido": {
    "titulo": "🎉 Oferta Especial para Ti",
    "cuerpo": "Como cliente VIP, tienes 30% de descuento...",
    "tipo_notificacion": "promocion",
    "datos_extra": {
      "deep_link": "/paquetes",
      "codigo_descuento": "VIP30"
    }
  },
  "segmentacion": {
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
      "num_viajes__gte": 5,
      "rol__nombre": "Cliente"
    }
  },
  "estadisticas": {
    "total_destinatarios": 45,
    "distribucion_roles": [
      {"rol__nombre": "Cliente", "cantidad": 45}
    ]
  },
  "destinatarios": [
    {
      "id": 8,
      "nombre": "María García",
      "email": "maria@example.com",
      "rol": "Cliente",
      "num_viajes": 7
    },
    ...
  ]
}
```

---

#### 4️⃣ Enviar Prueba
```http
POST /api/campanas-notificacion/{id}/enviar_test/
Authorization: Token {token_admin}
Content-Type: application/json
```

**Body (opcional):**
```json
{
  "usuario_id": 4
}
```

Si no se proporciona `usuario_id`, se envía al usuario actual (admin).

**Respuesta:**
```json
{
  "success": true,
  "notificacion_id": 123,
  "mensaje": "Notificación de prueba enviada a Luis Blanco"
}
```

---

#### 5️⃣ Activar Campaña
```http
POST /api/campanas-notificacion/{id}/activar/
Authorization: Token {token_admin}
```

**Comportamiento:**
- Si `enviar_inmediatamente=true`: Envía ahora mismo
- Si tiene `fecha_programada`: Marca como PROGRAMADA (scheduler la ejecutará)

**Respuesta (envío inmediato):**
```json
{
  "mensaje": "Campaña ejecutada inmediatamente",
  "estado": "COMPLETADA",
  "resultado": {
    "success": true,
    "total_enviados": 45,
    "total_errores": 0,
    "total_destinatarios": 45
  }
}
```

**Respuesta (programada):**
```json
{
  "mensaje": "Campaña programada exitosamente",
  "estado": "PROGRAMADA",
  "fecha_programada": "2025-11-05T10:00:00Z",
  "total_destinatarios": 45
}
```

---

#### 6️⃣ Cancelar Campaña
```http
POST /api/campanas-notificacion/{id}/cancelar/
Authorization: Token {token_admin}
```

Solo funciona para campañas en estado BORRADOR o PROGRAMADA.

**Respuesta:**
```json
{
  "mensaje": "Campaña cancelada exitosamente",
  "estado": "CANCELADA"
}
```

---

#### 7️⃣ Actualizar Métricas
```http
POST /api/campanas-notificacion/{id}/actualizar_metricas/
Authorization: Token {token_admin}
```

Recalcula cuántas notificaciones fueron leídas.

**Respuesta:**
```json
{
  "success": true,
  "total_leidos": 32,
  "total_enviados": 45,
  "porcentaje_lectura": 71.11
}
```

---

## 📝 Ejemplos de Segmentación

### Todos los usuarios
```json
{
  "tipo_audiencia": "TODOS"
}
```

### Lista específica de usuarios
```json
{
  "tipo_audiencia": "USUARIOS",
  "usuarios_objetivo": [4, 8, 15, 16, 23, 42]
}
```

### Segmento por filtros
```json
{
  "tipo_audiencia": "SEGMENTO",
  "segmento_filtros": {
    "rol__nombre": "Cliente",
    "num_viajes__gte": 3,
    "pais": "Bolivia"
  }
}
```

### Filtros avanzados Django ORM
```json
{
  "tipo_audiencia": "SEGMENTO",
  "segmento_filtros": {
    "reservas__estado": "COMPLETADA",
    "reservas__created_at__year": 2025,
    "num_viajes__lt": 10
  }
}
```

---

## ⏰ Scheduler de Campañas Programadas

### Ejecutar manualmente
```bash
py manage.py ejecutar_campanas_programadas
```

### Modo simulación (dry-run)
```bash
py manage.py ejecutar_campanas_programadas --dry-run
```

### Forzar ejecución de una campaña
```bash
py manage.py ejecutar_campanas_programadas --force-id 5
```

### Configurar Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar cada 5 minutos)
*/5 * * * * cd /ruta/proyecto && /ruta/venv/bin/python manage.py ejecutar_campanas_programadas >> /var/log/campanas.log 2>&1
```

### Configurar Task Scheduler (Windows)
1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Desencadenador: Repetir cada 5 minutos
4. Acción: Iniciar programa
   - Programa: `C:\ruta\venv\Scripts\python.exe`
   - Argumentos: `manage.py ejecutar_campanas_programadas`
   - Directorio: `C:\ruta\proyecto`

---

## 🔐 Permisos

### Usuarios Administradores
- ✅ Crear campañas
- ✅ Editar campañas (solo BORRADOR/PROGRAMADA)
- ✅ Eliminar campañas (solo BORRADOR)
- ✅ Ver preview
- ✅ Enviar pruebas
- ✅ Activar campañas
- ✅ Cancelar campañas

### Usuarios Normales
- ✅ Listar campañas (solo lectura)
- ✅ Ver detalles de campaña
- ❌ Crear/editar/eliminar
- ❌ Activar/cancelar

---

## 📊 Estados de Campaña

| Estado | Descripción | Puede Editarse | Puede Activarse | Puede Cancelarse |
|--------|-------------|----------------|-----------------|------------------|
| **BORRADOR** | Recién creada | ✅ | ✅ | ✅ |
| **PROGRAMADA** | Esperando fecha | ✅ | ❌ | ✅ |
| **EN_CURSO** | Ejecutándose | ❌ | ❌ | ❌ |
| **COMPLETADA** | Finalizada | ❌ | ❌ | ❌ |
| **CANCELADA** | Cancelada | ❌ | ❌ | ❌ |

---

## 🧪 Testing con curl

### Crear campaña de prueba
```bash
curl -X POST http://localhost:8000/api/campanas-notificacion/ \
  -H "Authorization: Token TU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Campaña",
    "titulo": "Hola Test",
    "cuerpo": "Esta es una prueba",
    "tipo_notificacion": "sistema",
    "tipo_audiencia": "TODOS",
    "enviar_inmediatamente": true
  }'
```

### Ver preview
```bash
curl -X GET http://localhost:8000/api/campanas-notificacion/1/preview/ \
  -H "Authorization: Token TU_TOKEN_ADMIN"
```

### Activar campaña
```bash
curl -X POST http://localhost:8000/api/campanas-notificacion/1/activar/ \
  -H "Authorization: Token TU_TOKEN_ADMIN"
```

---

## 🐛 Troubleshooting

### "No se puede activar una campaña en estado X"
- Verificar que la campaña esté en estado BORRADOR
- Usar endpoint de cancelación si está PROGRAMADA y quieres reactivarla

### "La campaña no tiene destinatarios"
- Verificar filtros de segmentación
- Usar endpoint de preview para ver cuántos usuarios coinciden
- Revisar que haya usuarios activos en el sistema

### Campañas programadas no se ejecutan
- Verificar que el command `ejecutar_campanas_programadas` esté corriendo
- Revisar logs: `/var/log/campanas.log`
- Ejecutar manualmente: `py manage.py ejecutar_campanas_programadas`

### Error al enviar FCM
- Verificar que `RUTA_CUENTA_SERVICIO_FIREBASE` esté configurada
- Revisar que los usuarios tengan dispositivos FCM activos
- Verificar logs del servidor para detalles

---

## 📚 Integración con Sistema Existente

El sistema **NO modifica** el flujo existente de notificaciones reactivas (tickets, etc.).

### Flujo Original (sigue funcionando)
```
Ticket creado → Notificacion creada → Signal dispara FCM
```

### Nuevo Flujo (campañas administrativas)
```
Admin crea CampañaNotificacion → Admin activa → Crea Notificaciones → Signal dispara FCM
```

Ambos conviven sin conflicto. Las notificaciones de campañas incluyen en `datos`:
```json
{
  "campana_id": "5",
  "campana_nombre": "Promoción Fin de Semana",
  ...
}
```

---

## 🎓 Mejores Prácticas

1. **Siempre usar Preview** antes de activar
2. **Enviar Prueba** a tu dispositivo primero
3. **Programar campañas** en horarios óptimos (ej. 10 AM - 8 PM)
4. **Segmentar adecuadamente** para relevancia
5. **Monitorear métricas** después del envío
6. **Mantener datos_extra** consistentes para deep linking

---

## 📞 Soporte

Para dudas o issues:
- Revisar logs: `tail -f /var/log/campanas.log`
- Django admin: `/admin/condominio/campananotificacion/`
- Bitácora de acciones: `/api/bitacora/`

---

**Implementado por:** Sistema de Notificaciones v2.0  
**Fecha:** Noviembre 2025  
**Compatibilidad:** Django 5.2.7, DRF 3.x, Firebase Admin SDK 7.1.0
