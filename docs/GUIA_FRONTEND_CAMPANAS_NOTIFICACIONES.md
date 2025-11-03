# 📱 Guía Frontend - Sistema de Campañas de Notificaciones

## 📋 Índice
1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [Endpoints Disponibles](#endpoints-disponibles)
4. [Flujo de Usuario](#flujo-de-usuario)
5. [Componentes Sugeridos](#componentes-sugeridos)
6. [Ejemplos de Requests](#ejemplos-de-requests)
7. [Validaciones del Frontend](#validaciones-del-frontend)
8. [Estados y Transiciones](#estados-y-transiciones)
9. [Diseño UI/UX Sugerido](#diseño-uiux-sugerido)
10. [Casos de Uso Completos](#casos-de-uso-completos)

---

## 🎯 Introducción

El sistema de campañas permite a los administradores crear, gestionar y enviar notificaciones push de manera controlada a usuarios específicos o grupos segmentados.

### Características Principales:
- ✅ Creación de campañas con vista previa
- ✅ Segmentación de audiencia (todos, roles, usuarios específicos)
- ✅ Envío de notificaciones de prueba
- ✅ Programación de envíos futuros
- ✅ Métricas en tiempo real
- ✅ Historial y bitácora

### Requisitos Previos:
- Usuario debe ser **Administrador** (`is_staff: true`)
- Token de autenticación válido
- Conexión con Firebase Cloud Messaging configurada

---

## 🔐 Autenticación

### 1. Login

**Endpoint:** `POST /api/login/`

**Request:**
```json
{
    "email": "admin@sistema.com",
    "password": "admin12345"
}
```

**Response (200 OK):**
```json
{
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "user": {
        "id": 5,
        "email": "admin@sistema.com",
        "nombre": "Admin Sistema",
        "rol": "Administrador",
        "is_staff": true
    }
}
```

**Guardar en localStorage/sessionStorage:**
```javascript
localStorage.setItem('authToken', response.token);
localStorage.setItem('userId', response.user.id);
localStorage.setItem('userName', response.user.nombre);
```

**Uso en requests posteriores:**
```javascript
headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`,
    'Content-Type': 'application/json'
}
```

---

## 📡 Endpoints Disponibles

### Base URL
```
http://127.0.0.1:8000/api/campanas-notificacion/
```

### Listado de Endpoints

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/campanas-notificacion/` | Listar todas las campañas | Admin |
| POST | `/api/campanas-notificacion/` | Crear nueva campaña | Admin |
| GET | `/api/campanas-notificacion/{id}/` | Ver detalle de campaña | Admin |
| PUT/PATCH | `/api/campanas-notificacion/{id}/` | Actualizar campaña | Admin |
| DELETE | `/api/campanas-notificacion/{id}/` | Eliminar campaña (solo BORRADOR) | Admin |
| GET | `/api/campanas-notificacion/{id}/preview/` | Vista previa de destinatarios | Admin |
| POST | `/api/campanas-notificacion/{id}/enviar_test/` | Enviar notificación de prueba | Admin |
| POST | `/api/campanas-notificacion/{id}/activar/` | Activar/ejecutar campaña | Admin |
| POST | `/api/campanas-notificacion/{id}/cancelar/` | Cancelar campaña programada | Admin |
| POST | `/api/campanas-notificacion/{id}/actualizar_metricas/` | Recalcular métricas | Admin |

---

## 🎨 Flujo de Usuario

### Flujo Principal de Creación

```
┌─────────────────┐
│ 1. Dashboard    │
│ Campañas        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Botón:       │
│ "Nueva Campaña" │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ 3. Formulario Creación  │
│ - Nombre                │
│ - Título notificación   │
│ - Cuerpo notificación   │
│ - Tipo audiencia        │
│ - Segmentación (si aplica)│
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. Guardar      │
│ (Estado: BORRADOR)│
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ 5. Ver Preview      │
│ - Lista destinatarios│
│ - Estadísticas      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 6. Enviar Prueba    │
│ (a mi dispositivo)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│ 7. ¿Aprobar?    │
│ Sí → Activar    │
│ No → Editar     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 8. Activar      │
│ (Envío masivo)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 9. Ver Métricas │
│ - Enviados      │
│ - Leídos        │
│ - Errores       │
└─────────────────┘
```

---

## 🧩 Componentes Sugeridos

### 1. **CampanasList.jsx/vue** (Dashboard)

**Funcionalidades:**
- Tabla/cards con todas las campañas
- Filtros: estado, audiencia, búsqueda
- Badges de estado con colores
- Botón "Nueva Campaña"
- Acciones rápidas: Ver, Editar, Eliminar

**Columnas sugeridas:**
- Nombre
- Estado (badge con color)
- Tipo audiencia
- Total destinatarios
- Enviados / Errores
- Fecha creación
- Fecha envío
- Acciones

**Request:**
```javascript
// Listar todas
GET /api/campanas-notificacion/

// Con filtros
GET /api/campanas-notificacion/?estado=BORRADOR&search=Bienvenida

// Ordenar
GET /api/campanas-notificacion/?ordering=-created_at
```

---

### 2. **CampanaForm.jsx/vue** (Crear/Editar)

**Campos del formulario:**

```javascript
const formData = {
    // Básicos (requeridos)
    nombre: '',                    // string, max 200 chars
    titulo: '',                    // string, max 100 chars
    cuerpo: '',                    // string, max 500 chars
    tipo_notificacion: '',         // select (ver opciones abajo)
    tipo_audiencia: '',            // select: TODOS, USUARIOS, SEGMENTO
    
    // Opcionales
    descripcion: '',               // textarea
    enviar_inmediatamente: false,  // boolean
    fecha_programada: null,        // datetime (si no es inmediato)
    
    // Condicionales según tipo_audiencia
    usuarios_objetivo: [],         // array de IDs (si USUARIOS)
    segmento_filtros: {}          // object (si SEGMENTO)
}
```

**Opciones de `tipo_notificacion`:**
```javascript
const tiposNotificacion = [
    { value: 'campana_marketing', label: '📢 Campaña Marketing' },
    { value: 'promocion', label: '🎁 Promoción' },
    { value: 'recordatorio', label: '⏰ Recordatorio' },
    { value: 'sistema', label: '⚙️ Sistema' }
];
```

**Opciones de `tipo_audiencia`:**
```javascript
const tiposAudiencia = [
    { 
        value: 'TODOS', 
        label: 'Todos los usuarios',
        description: 'Enviar a todos los usuarios activos del sistema'
    },
    { 
        value: 'USUARIOS', 
        label: 'Usuarios específicos',
        description: 'Seleccionar usuarios manualmente'
    },
    { 
        value: 'SEGMENTO', 
        label: 'Segmento personalizado',
        description: 'Filtrar por rol, país, viajes, etc.'
    }
];
```

**Componente según audiencia:**

```jsx
// Si tipo_audiencia === 'USUARIOS'
<UsuarioSelector
    multiple={true}
    selected={formData.usuarios_objetivo}
    onChange={(ids) => setFormData({...formData, usuarios_objetivo: ids})}
/>

// Si tipo_audiencia === 'SEGMENTO'
<SegmentacionForm
    filters={formData.segmento_filtros}
    onChange={(filters) => setFormData({...formData, segmento_filtros: filters})}
/>
```

---

### 3. **SegmentacionForm.jsx/vue** (Filtros avanzados)

**Filtros disponibles:**

```javascript
const filtrosDisponibles = {
    // Por rol
    rol__nombre: {
        type: 'select',
        label: 'Rol de usuario',
        options: ['Cliente', 'Proveedor', 'Administrador']
    },
    
    // Por viajes
    num_viajes__gte: {
        type: 'number',
        label: 'Número de viajes mayor o igual a',
        min: 0
    },
    num_viajes__lte: {
        type: 'number',
        label: 'Número de viajes menor o igual a',
        min: 0
    },
    
    // Por ubicación
    pais: {
        type: 'select',
        label: 'País',
        options: ['Bolivia', 'Perú', 'Argentina', 'Chile']
    },
    
    // Por género
    genero: {
        type: 'select',
        label: 'Género',
        options: [
            { value: 'M', label: 'Masculino' },
            { value: 'F', label: 'Femenino' }
        ]
    }
};
```

**Ejemplo de segmento_filtros:**
```javascript
// Clientes que han viajado más de 3 veces
{
    "rol__nombre": "Cliente",
    "num_viajes__gte": 3
}

// Usuarios de Bolivia
{
    "pais": "Bolivia"
}

// Proveedores hombres
{
    "rol__nombre": "Proveedor",
    "genero": "M"
}
```

---

### 4. **CampanaPreview.jsx/vue** (Vista previa)

**Request:**
```javascript
GET /api/campanas-notificacion/{id}/preview/
```

**Response:**
```json
{
    "campana": {
        "id": 1,
        "nombre": "Bienvenida Nuevos Usuarios",
        "estado": "BORRADOR"
    },
    "contenido": {
        "titulo": "¡Bienvenido! 🎉",
        "cuerpo": "Explora nuestros servicios",
        "tipo_notificacion": "campana_marketing"
    },
    "destinatarios": [
        {
            "id": 4,
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "rol": "Cliente",
            "tiene_dispositivo_fcm": true
        },
        {
            "id": 5,
            "nombre": "María García",
            "email": "maria@example.com",
            "rol": "Cliente",
            "tiene_dispositivo_fcm": false
        }
    ],
    "estadisticas": {
        "total_destinatarios": 15,
        "con_dispositivo_fcm": 12,
        "sin_dispositivo_fcm": 3,
        "distribucion_roles": {
            "Cliente": 10,
            "Proveedor": 3,
            "Administrador": 2
        }
    },
    "nota": "Mostrando primeros 50 destinatarios"
}
```

**UI Sugerido:**
- Card con el contenido de la notificación (preview móvil)
- Lista de destinatarios (con paginación si >50)
- Gráfico de distribución por roles
- Alertas si hay usuarios sin dispositivo FCM
- Botones: "Enviar Prueba", "Activar", "Editar"

---

### 5. **CampanaDetail.jsx/vue** (Ver detalle)

**Request:**
```javascript
GET /api/campanas-notificacion/{id}/
```

**Response:**
```json
{
    "id": 1,
    "nombre": "Bienvenida Nuevos Usuarios",
    "descripcion": "Campaña de bienvenida para nuevos registros",
    "titulo": "¡Bienvenido! 🎉",
    "cuerpo": "Explora nuestros servicios y encuentra las mejores ofertas",
    "tipo_notificacion": "campana_marketing",
    "tipo_audiencia": "TODOS",
    "estado": "COMPLETADA",
    "enviar_inmediatamente": false,
    "fecha_programada": null,
    "fecha_enviada": "2025-11-01T21:30:00Z",
    "total_destinatarios": 15,
    "total_enviados": 13,
    "total_errores": 2,
    "total_leidos": 8,
    "usuarios_objetivo": [],
    "segmento_filtros": {},
    "created_at": "2025-11-01T20:00:00Z",
    "updated_at": "2025-11-01T21:30:00Z",
    "puede_editarse": false,
    "puede_activarse": false,
    "puede_cancelarse": false
}
```

**Mostrar:**
- Información general (nombre, descripción, tipo)
- Estado actual con badge
- Contenido de la notificación
- Métricas (gráfico de torta o barras)
- Audiencia configurada
- Timeline de acciones
- Botones según estado

---

## 📝 Ejemplos de Requests Completos

### Ejemplo 1: Crear Campaña para Todos

```javascript
const crearCampanaTodos = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/campanas-notificacion/', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nombre: "Bienvenida Nuevos Usuarios",
            descripcion: "Campaña de bienvenida automatizada",
            titulo: "¡Bienvenido a nuestro sistema! 🎉",
            cuerpo: "Explora nuestros servicios y encuentra las mejores ofertas de turismo.",
            tipo_notificacion: "campana_marketing",
            tipo_audiencia: "TODOS",
            enviar_inmediatamente: false
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log('Campaña creada:', data);
        // Redirigir a preview
        router.push(`/campanas/${data.id}/preview`);
    } else {
        console.error('Errores:', data);
        // Mostrar errores en el formulario
    }
};
```

---

### Ejemplo 2: Crear Campaña Segmentada (Solo Clientes)

```javascript
const crearCampanaClientes = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/campanas-notificacion/', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nombre: "Black Friday - Solo Clientes",
            descripcion: "Promoción exclusiva para clientes",
            titulo: "🔥 Black Friday: 50% OFF",
            cuerpo: "Solo para ti: descuentos increíbles en todos los paquetes turísticos",
            tipo_notificacion: "promocion",
            tipo_audiencia: "SEGMENTO",
            segmento_filtros: {
                rol__nombre: "Cliente"
            },
            enviar_inmediatamente: false
        })
    });
    
    return await response.json();
};
```

---

### Ejemplo 3: Crear Campaña con Usuarios Específicos

```javascript
const crearCampanaEspecifica = async (usuariosSeleccionados) => {
    const response = await fetch('http://127.0.0.1:8000/api/campanas-notificacion/', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nombre: "Invitación Programa Beta",
            titulo: "📢 Invitación exclusiva",
            cuerpo: "Has sido seleccionado para nuestro programa beta de nuevas funcionalidades",
            tipo_notificacion: "sistema",
            tipo_audiencia: "USUARIOS",
            usuarios_objetivo: usuariosSeleccionados, // [4, 5, 8, 12]
            enviar_inmediatamente: false
        })
    });
    
    return await response.json();
};
```

---

### Ejemplo 4: Enviar Notificación de Prueba

```javascript
const enviarPrueba = async (campanaId) => {
    const response = await fetch(
        `http://127.0.0.1:8000/api/campanas-notificacion/${campanaId}/enviar_test/`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                // Opcional: enviar a usuario específico
                // usuario_id: 5
                // Si no se especifica, se envía al usuario actual
            })
        }
    );
    
    const data = await response.json();
    
    if (response.ok) {
        alert('✅ Notificación de prueba enviada. Revisa tu dispositivo.');
    }
    
    return data;
};
```

---

### Ejemplo 5: Activar Campaña

```javascript
const activarCampana = async (campanaId) => {
    // Confirmación importante
    const confirmar = confirm(
        '⚠️ ¿Estás seguro de activar esta campaña?\n\n' +
        'Esta acción enviará notificaciones a TODOS los destinatarios y no se puede deshacer.'
    );
    
    if (!confirmar) return;
    
    const response = await fetch(
        `http://127.0.0.1:8000/api/campanas-notificacion/${campanaId}/activar/`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }
    );
    
    const data = await response.json();
    
    if (response.ok) {
        alert(`✅ Campaña activada exitosamente!\n\n` +
              `Enviados: ${data.campana.total_enviados}\n` +
              `Errores: ${data.campana.total_errores}`);
    }
    
    return data;
};
```

---

### Ejemplo 6: Cancelar Campaña

```javascript
const cancelarCampana = async (campanaId) => {
    const response = await fetch(
        `http://127.0.0.1:8000/api/campanas-notificacion/${campanaId}/cancelar/`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }
    );
    
    return await response.json();
};
```

---

## ✅ Validaciones del Frontend

### Validaciones de Formulario

```javascript
const validarFormulario = (formData) => {
    const errores = {};
    
    // Nombre (requerido, max 200 caracteres)
    if (!formData.nombre || formData.nombre.trim() === '') {
        errores.nombre = 'El nombre es requerido';
    } else if (formData.nombre.length > 200) {
        errores.nombre = 'El nombre no puede exceder 200 caracteres';
    }
    
    // Título (requerido, max 100 caracteres)
    if (!formData.titulo || formData.titulo.trim() === '') {
        errores.titulo = 'El título es requerido';
    } else if (formData.titulo.length > 100) {
        errores.titulo = 'El título no puede exceder 100 caracteres';
    }
    
    // Cuerpo (requerido, max 500 caracteres)
    if (!formData.cuerpo || formData.cuerpo.trim() === '') {
        errores.cuerpo = 'El cuerpo es requerido';
    } else if (formData.cuerpo.length > 500) {
        errores.cuerpo = 'El cuerpo no puede exceder 500 caracteres';
    }
    
    // Tipo notificación (requerido)
    if (!formData.tipo_notificacion) {
        errores.tipo_notificacion = 'Selecciona un tipo de notificación';
    }
    
    // Tipo audiencia (requerido)
    if (!formData.tipo_audiencia) {
        errores.tipo_audiencia = 'Selecciona un tipo de audiencia';
    }
    
    // Validaciones condicionales según audiencia
    if (formData.tipo_audiencia === 'USUARIOS') {
        if (!formData.usuarios_objetivo || formData.usuarios_objetivo.length === 0) {
            errores.usuarios_objetivo = 'Debes seleccionar al menos un usuario';
        }
    }
    
    if (formData.tipo_audiencia === 'SEGMENTO') {
        if (!formData.segmento_filtros || Object.keys(formData.segmento_filtros).length === 0) {
            errores.segmento_filtros = 'Debes configurar al menos un filtro';
        }
    }
    
    // Fecha programada
    if (!formData.enviar_inmediatamente && !formData.fecha_programada) {
        errores.fecha_programada = 'Debes especificar una fecha o marcar envío inmediato';
    }
    
    if (formData.fecha_programada) {
        const fechaSeleccionada = new Date(formData.fecha_programada);
        const ahora = new Date();
        
        if (fechaSeleccionada <= ahora) {
            errores.fecha_programada = 'La fecha debe ser en el futuro';
        }
    }
    
    return {
        esValido: Object.keys(errores).length === 0,
        errores
    };
};
```

---

## 📊 Estados y Transiciones

### Estados de Campaña

```javascript
const ESTADOS_CAMPANA = {
    BORRADOR: {
        label: 'Borrador',
        color: 'gray',
        icon: '📝',
        descripcion: 'Campaña en edición',
        acciones: ['editar', 'eliminar', 'preview', 'enviar_test', 'activar']
    },
    PROGRAMADA: {
        label: 'Programada',
        color: 'blue',
        icon: '📅',
        descripcion: 'Esperando fecha de envío',
        acciones: ['ver', 'cancelar']
    },
    EN_CURSO: {
        label: 'En Curso',
        color: 'yellow',
        icon: '⏳',
        descripcion: 'Enviando notificaciones',
        acciones: ['ver']
    },
    COMPLETADA: {
        label: 'Completada',
        color: 'green',
        icon: '✅',
        descripcion: 'Campaña enviada exitosamente',
        acciones: ['ver', 'duplicar', 'actualizar_metricas']
    },
    CANCELADA: {
        label: 'Cancelada',
        color: 'red',
        icon: '❌',
        descripcion: 'Campaña cancelada',
        acciones: ['ver']
    }
};
```

### Componente Badge de Estado

```jsx
const EstadoBadge = ({ estado }) => {
    const config = ESTADOS_CAMPANA[estado];
    
    return (
        <span className={`badge badge-${config.color}`}>
            {config.icon} {config.label}
        </span>
    );
};
```

### Diagrama de Transiciones

```
BORRADOR
  ├─→ PROGRAMADA (si tiene fecha_programada)
  ├─→ COMPLETADA (si enviar_inmediatamente)
  └─→ CANCELADA (acción manual)

PROGRAMADA
  ├─→ EN_CURSO (cuando llega la fecha)
  ├─→ COMPLETADA (después de enviar)
  └─→ CANCELADA (acción manual)

EN_CURSO
  └─→ COMPLETADA (automático)

COMPLETADA
  └─→ (estado final)

CANCELADA
  └─→ (estado final)
```

---

## 🎨 Diseño UI/UX Sugerido

### Página: Dashboard de Campañas

```
┌────────────────────────────────────────────────────┐
│  📢 Campañas de Notificaciones                     │
│                                   [+ Nueva Campaña]│
├────────────────────────────────────────────────────┤
│                                                     │
│  Filtros:  [Estado ▼] [Audiencia ▼] [🔍 Buscar]   │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 📝 Bienvenida Nuevos Usuarios                │  │
│  │ Estado: Borrador | Audiencia: Todos          │  │
│  │ Creada: 01/11/2025                           │  │
│  │ [👁 Ver] [✏️ Editar] [🗑️ Eliminar]           │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ ✅ Black Friday - Solo Clientes              │  │
│  │ Estado: Completada | Audiencia: Segmento     │  │
│  │ Enviados: 45/50 | Leídos: 30                 │  │
│  │ [👁 Ver Métricas] [📋 Duplicar]              │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

### Página: Crear/Editar Campaña

```
┌────────────────────────────────────────────────────┐
│  ← Volver    Nueva Campaña de Notificación         │
├────────────────────────────────────────────────────┤
│                                                     │
│  📋 Información Básica                             │
│  ┌──────────────────────────────────────────────┐  │
│  │ Nombre*:                                      │  │
│  │ [                                           ] │  │
│  │                                               │  │
│  │ Descripción (opcional):                       │  │
│  │ [                                           ] │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  📱 Contenido de la Notificación                   │
│  ┌──────────────────────────────────────────────┐  │
│  │ Título* (max 100 caracteres):                 │  │
│  │ [                                           ] │  │
│  │ Caracteres: 0/100                             │  │
│  │                                               │  │
│  │ Cuerpo* (max 500 caracteres):                 │  │
│  │ [                                           ] │  │
│  │ [                                           ] │  │
│  │ Caracteres: 0/500                             │  │
│  │                                               │  │
│  │ Tipo de notificación*:                        │  │
│  │ ○ 📢 Campaña Marketing                        │  │
│  │ ○ 🎁 Promoción                                │  │
│  │ ○ ⏰ Recordatorio                             │  │
│  │ ○ ⚙️ Sistema                                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  👥 Audiencia                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │ ¿A quién enviar?*                             │  │
│  │ ○ Todos los usuarios                          │  │
│  │ ○ Usuarios específicos                        │  │
│  │ ○ Segmento personalizado                      │  │
│  │                                               │  │
│  │ [Configurar audiencia →]                      │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ⏰ Programación                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │ ☑ No enviar ahora, programar para después    │  │
│  │                                               │  │
│  │ Fecha y hora:                                 │  │
│  │ [02/11/2025] [10:00]                          │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  [Cancelar]                    [Guardar Borrador]  │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

### Página: Vista Previa

```
┌────────────────────────────────────────────────────┐
│  ← Volver    Vista Previa: Bienvenida Nuevos Usuarios│
├────────────────────────────────────────────────────┤
│                                                     │
│  📱 Preview de Notificación         📊 Estadísticas│
│  ┌─────────────────────┐  ┌────────────────────┐  │
│  │                     │  │ Total: 15          │  │
│  │  🎉                 │  │ Con FCM: 12 (80%)  │  │
│  │  ¡Bienvenido!       │  │ Sin FCM: 3 (20%)   │  │
│  │                     │  │                    │  │
│  │  Explora nuestros   │  │ Por Rol:           │  │
│  │  servicios y...     │  │ • Clientes: 10     │  │
│  │                     │  │ • Proveedores: 3   │  │
│  │     [Ver más]       │  │ • Admins: 2        │  │
│  │                     │  │                    │  │
│  └─────────────────────┘  └────────────────────┘  │
│                                                     │
│  👥 Destinatarios (mostrando primeros 50)          │
│  ┌──────────────────────────────────────────────┐  │
│  │ ✅ Luis Blanco (luis@prueba.com) - Cliente   │  │
│  │ ⚠️ Ana García (ana@example.com) - Admin      │  │
│  │    Sin dispositivo FCM                        │  │
│  │ ✅ Carlos Méndez (carlos@example.com) - Prov │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ⚠️ 3 usuarios no tienen dispositivos registrados  │
│                                                     │
│  [✏️ Editar]  [📧 Enviar Prueba]  [🚀 Activar]    │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## 💼 Casos de Uso Completos

### Caso 1: Campaña de Bienvenida

**Objetivo:** Enviar notificación a todos los nuevos usuarios

**Flujo:**
1. Clic en "Nueva Campaña"
2. Llenar formulario:
   - Nombre: "Bienvenida Nuevos Usuarios"
   - Título: "¡Bienvenido! 🎉"
   - Cuerpo: "Explora nuestros servicios"
   - Tipo: Campaña Marketing
   - Audiencia: Todos
   - No programar (enviar después de aprobar)
3. Guardar borrador
4. Ver preview → verificar destinatarios
5. Enviar prueba → verificar en dispositivo
6. Activar → envío masivo

**JSON para crear:**
```json
{
    "nombre": "Bienvenida Nuevos Usuarios",
    "titulo": "¡Bienvenido! 🎉",
    "cuerpo": "Explora nuestros servicios y encuentra las mejores ofertas",
    "tipo_notificacion": "campana_marketing",
    "tipo_audiencia": "TODOS",
    "enviar_inmediatamente": false
}
```

---

### Caso 2: Promoción Black Friday (Solo Clientes)

**Objetivo:** Enviar descuento exclusivo a clientes

**Flujo:**
1. Nueva campaña
2. Configurar segmentación:
   - Tipo audiencia: Segmento
   - Filtro: rol__nombre = "Cliente"
3. Contenido:
   - Título: "🔥 Black Friday: 50% OFF"
   - Tipo: Promoción
4. Preview → validar que solo clientes aparezcan
5. Activar

**JSON:**
```json
{
    "nombre": "Black Friday - Solo Clientes",
    "titulo": "🔥 Black Friday: 50% de descuento",
    "cuerpo": "Solo para ti: descuentos exclusivos en todos los paquetes",
    "tipo_notificacion": "promocion",
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente"
    },
    "enviar_inmediatamente": false
}
```

---

### Caso 3: Programa VIP (Viajeros Frecuentes)

**Objetivo:** Notificar a clientes con más de 5 viajes

**JSON:**
```json
{
    "nombre": "Programa VIP - Viajeros Frecuentes",
    "titulo": "✈️ ¡Eres VIP!",
    "cuerpo": "Gracias por ser un cliente frecuente. Disfruta beneficios exclusivos",
    "tipo_notificacion": "recordatorio",
    "tipo_audiencia": "SEGMENTO",
    "segmento_filtros": {
        "rol__nombre": "Cliente",
        "num_viajes__gte": 5
    },
    "enviar_inmediatamente": false
}
```

---

### Caso 4: Notificación a Usuarios Beta

**Objetivo:** Invitar a 5 usuarios específicos

**Flujo:**
1. Nueva campaña
2. Audiencia: Usuarios específicos
3. Abrir selector de usuarios
4. Buscar y seleccionar: IDs [4, 5, 8, 12, 15]
5. Activar

**JSON:**
```json
{
    "nombre": "Invitación Programa Beta",
    "titulo": "📢 Invitación exclusiva",
    "cuerpo": "Has sido seleccionado para probar nuestras nuevas funcionalidades",
    "tipo_notificacion": "sistema",
    "tipo_audiencia": "USUARIOS",
    "usuarios_objetivo": [4, 5, 8, 12, 15],
    "enviar_inmediatamente": false
}
```

---

### Caso 5: Recordatorio Semanal (Programado)

**Objetivo:** Enviar recordatorio cada lunes a las 10 AM

**JSON:**
```json
{
    "nombre": "Recordatorio Semanal - Ofertas",
    "titulo": "📅 Nuevas ofertas esta semana",
    "cuerpo": "Revisa las nuevas ofertas para tus destinos favoritos",
    "tipo_notificacion": "recordatorio",
    "tipo_audiencia": "TODOS",
    "enviar_inmediatamente": false,
    "fecha_programada": "2025-11-04T10:00:00Z"
}
```

**Nota:** Para envíos recurrentes, crear múltiples campañas o implementar lógica adicional.

---

## 🚨 Manejo de Errores

### Errores Comunes del Backend

```javascript
const manejarErrores = (response, data) => {
    if (response.status === 401) {
        // Token inválido o expirado
        alert('Tu sesión ha expirado. Por favor inicia sesión nuevamente.');
        localStorage.removeItem('authToken');
        router.push('/login');
        return;
    }
    
    if (response.status === 403) {
        // Sin permisos de admin
        alert('No tienes permisos para realizar esta acción. Debes ser administrador.');
        return;
    }
    
    if (response.status === 400) {
        // Errores de validación
        const errores = [];
        
        for (const [campo, mensajes] of Object.entries(data)) {
            if (Array.isArray(mensajes)) {
                errores.push(`${campo}: ${mensajes.join(', ')}`);
            } else {
                errores.push(`${campo}: ${mensajes}`);
            }
        }
        
        alert('Errores en el formulario:\n\n' + errores.join('\n'));
        return errores;
    }
    
    if (response.status === 404) {
        alert('Campaña no encontrada');
        return;
    }
    
    if (response.status >= 500) {
        alert('Error del servidor. Por favor intenta más tarde.');
        return;
    }
};
```

### Ejemplos de Respuestas de Error

**Error 400 - Validación:**
```json
{
    "titulo": ["Este campo es requerido."],
    "fecha_programada": ["Debe especificar fecha_programada o marcar enviar_inmediatamente"]
}
```

**Error 400 - Campaña sin destinatarios:**
```json
{
    "non_field_errors": ["La campaña no tiene destinatarios válidos"]
}
```

**Error 403 - Sin permisos:**
```json
{
    "detail": "No tiene permiso para realizar esta acción."
}
```

---

## 📊 Componente de Métricas

### Métricas Disponibles

```javascript
const MetricasCampana = ({ campana }) => {
    const calcularTasas = () => {
        const tasaExito = (campana.total_enviados / campana.total_destinatarios * 100).toFixed(1);
        const tasaApertura = (campana.total_leidos / campana.total_enviados * 100).toFixed(1);
        const tasaError = (campana.total_errores / campana.total_destinatarios * 100).toFixed(1);
        
        return { tasaExito, tasaApertura, tasaError };
    };
    
    const { tasaExito, tasaApertura, tasaError } = calcularTasas();
    
    return (
        <div className="metricas-campana">
            <h3>📊 Métricas</h3>
            
            <div className="metrica">
                <span>Total Destinatarios:</span>
                <strong>{campana.total_destinatarios}</strong>
            </div>
            
            <div className="metrica success">
                <span>✅ Enviados:</span>
                <strong>{campana.total_enviados} ({tasaExito}%)</strong>
            </div>
            
            <div className="metrica info">
                <span>👁️ Leídos:</span>
                <strong>{campana.total_leidos} ({tasaApertura}%)</strong>
            </div>
            
            <div className="metrica error">
                <span>❌ Errores:</span>
                <strong>{campana.total_errores} ({tasaError}%)</strong>
            </div>
            
            <button onClick={() => actualizarMetricas(campana.id)}>
                🔄 Actualizar Métricas
            </button>
        </div>
    );
};
```

---

## 🔔 Integración con Notificaciones en Tiempo Real

### Escuchar Actualizaciones (WebSocket o Polling)

```javascript
// Opción 1: Polling cada 10 segundos
const iniciarPolling = (campanaId) => {
    const intervalo = setInterval(async () => {
        const response = await fetch(
            `http://127.0.0.1:8000/api/campanas-notificacion/${campanaId}/`,
            {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`
                }
            }
        );
        
        const data = await response.json();
        
        // Actualizar estado en el componente
        setCampana(data);
        
        // Si la campaña está completada, detener polling
        if (data.estado === 'COMPLETADA') {
            clearInterval(intervalo);
        }
    }, 10000); // cada 10 segundos
    
    return intervalo;
};

// Opción 2: WebSocket (si está implementado)
const conectarWebSocket = (campanaId) => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/campanas/${campanaId}/`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Actualización de campaña:', data);
        setCampana(data);
    };
    
    return ws;
};
```

---

## 🧪 Testing y Debugging

### Consola de Debug

```javascript
// Agregar en desarrollo
if (process.env.NODE_ENV === 'development') {
    window.debugCampanas = {
        // Ver token actual
        verToken: () => {
            console.log('Token:', localStorage.getItem('authToken'));
        },
        
        // Simular creación de campaña
        crearTest: async () => {
            const response = await fetch('http://127.0.0.1:8000/api/campanas-notificacion/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre: "Test " + new Date().getTime(),
                    titulo: "Test",
                    cuerpo: "Test",
                    tipo_notificacion: "sistema",
                    tipo_audiencia: "TODOS",
                    enviar_inmediatamente: false
                })
            });
            console.log('Response:', await response.json());
        }
    };
}
```

### Checklist de Testing

- [ ] Login y obtención de token
- [ ] Listar campañas (vacío y con datos)
- [ ] Crear campaña - Todos los usuarios
- [ ] Crear campaña - Usuarios específicos
- [ ] Crear campaña - Segmento personalizado
- [ ] Ver preview de campaña
- [ ] Enviar notificación de prueba
- [ ] Activar campaña
- [ ] Cancelar campaña programada
- [ ] Ver métricas
- [ ] Editar campaña en borrador
- [ ] Eliminar campaña en borrador
- [ ] Validaciones de formulario
- [ ] Manejo de errores 401, 403, 400, 500
- [ ] Responsive design
- [ ] Loading states
- [ ] Confirmaciones antes de acciones críticas

---

## 📚 Recursos Adicionales

### Archivos de Referencia

- `docs/CAMPANAS_NOTIFICACIONES_GUIA.md` - Documentación técnica completa
- `docs/GUIA_RAPIDA_CAMPANAS_POSTMAN.md` - Guía rápida de testing
- `postman/Campanas_Notificaciones.postman_collection.json` - Colección Postman

### Endpoints de Soporte

```javascript
// Ver usuarios disponibles
GET /api/usuarios/

// Ver roles
GET /api/rol/

// Ver dispositivos FCM
GET /api/fcm-dispositivos/

// Ver notificaciones enviadas
GET /api/notificaciones/?tipo=campana_marketing

// Ver bitácora de acciones
GET /api/bitacora/?accion__icontains=campaña
```

---

## 🎯 Resumen para el Desarrollador Frontend

### 1. **Primeros Pasos**
- Implementar sistema de autenticación con Token
- Crear servicio/API client para requests
- Implementar manejo de errores global

### 2. **Componentes Críticos**
- `CampanasList` - Dashboard principal
- `CampanaForm` - Crear/Editar
- `CampanaPreview` - Vista previa
- `SegmentacionForm` - Filtros de audiencia
- `CampanaDetail` - Ver métricas

### 3. **Flujo Mínimo Viable (MVP)**
```
Login → Dashboard → Nueva Campaña → 
Formulario Simple (Todos) → 
Preview → Activar → Ver Métricas
```

### 4. **Mejoras Incrementales**
- Fase 1: CRUD básico con audiencia "TODOS"
- Fase 2: Selector de usuarios específicos
- Fase 3: Segmentación avanzada con filtros
- Fase 4: Programación de envíos
- Fase 5: Dashboard con gráficos y estadísticas

### 5. **Consideraciones UX**
- ✅ Confirmación antes de activar (acción irreversible)
- ✅ Loading states en todas las acciones async
- ✅ Mensajes de éxito/error claros
- ✅ Contador de caracteres en título/cuerpo
- ✅ Preview móvil de la notificación
- ✅ Badges de estado con colores intuitivos

---

## 🚀 ¡Listo para Implementar!

Esta guía contiene todo lo necesario para implementar el sistema completo de campañas de notificaciones.

**¿Dudas o necesitas más ejemplos?** Consulta:
- La colección de Postman (23 requests listos)
- Los scripts de testing en `scripts/`
- La documentación técnica en `docs/`

¡Éxito con la implementación! 🎉
