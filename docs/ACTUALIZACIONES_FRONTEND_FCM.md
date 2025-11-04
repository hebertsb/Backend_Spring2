# 🔄 Actualizaciones Frontend - Sistema de Notificaciones FCM

## 📋 Resumen de Cambios

Se ha creado un nuevo endpoint `/api/usuarios/con_fcm/` que **filtra automáticamente usuarios con tokens FCM activos**. Esto resuelve el problema de mostrar usuarios que no pueden recibir notificaciones.

---

## 🚨 Problema Anterior

**ANTES:** El frontend llamaba a `/api/usuarios/` y mostraba **TODOS** los usuarios del sistema, incluyendo aquellos que:
- ❌ No tienen la app instalada
- ❌ No tienen tokens FCM registrados
- ❌ No pueden recibir notificaciones push

**Resultado:** Administrador creaba campañas para usuarios que nunca recibirían las notificaciones.

---

## ✅ Solución Implementada

**AHORA:** Nuevo endpoint `/api/usuarios/con_fcm/` que retorna **solo usuarios con dispositivos FCM activos**.

---

## 📡 Nuevo Endpoint

### **URL Base**
```
GET https://backendspring2-production.up.railway.app/api/usuarios/con_fcm/
```

### **Autenticación**
Requiere token de autenticación:
```javascript
headers: {
    'Authorization': `Token ${tuTokenDeAutenticacion}`
}
```

### **Parámetros Query (Opcionales)**

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `rol` | string | Filtrar por rol | `?rol=Cliente` |
| `search` | string | Buscar por nombre | `?search=Luis` |

### **Ejemplos de Uso**

```javascript
// Todos los usuarios con FCM
GET /api/usuarios/con_fcm/

// Solo clientes con FCM
GET /api/usuarios/con_fcm/?rol=Cliente

// Solo proveedores con FCM
GET /api/usuarios/con_fcm/?rol=Proveedor

// Buscar usuario específico con FCM
GET /api/usuarios/con_fcm/?search=Luis

// Combinar filtros
GET /api/usuarios/con_fcm/?rol=Cliente&search=Maria
```

### **Respuesta del Servidor**

```json
{
  "count": 5,
  "usuarios": [
    {
      "id": 8,
      "nombre": "Luis Fernando Mamani",
      "email": "luis@example.com",
      "rol": "Cliente",
      "telefono": "+591 12345678",
      "num_viajes": 7,
      "total_dispositivos_fcm": 2
    },
    {
      "id": 12,
      "nombre": "María García López",
      "email": "maria@example.com",
      "rol": "Cliente",
      "telefono": "+591 87654321",
      "num_viajes": 3,
      "total_dispositivos_fcm": 1
    }
  ]
}
```

### **Campos de Respuesta**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | number | Total de usuarios con FCM activo |
| `usuarios` | array | Lista de usuarios |
| `usuarios[].id` | number | ID del usuario (usar para campañas) |
| `usuarios[].nombre` | string | Nombre completo |
| `usuarios[].email` | string | Email del usuario |
| `usuarios[].rol` | string | Rol: "Cliente", "Proveedor", etc. |
| `usuarios[].telefono` | string | Teléfono de contacto |
| `usuarios[].num_viajes` | number | Cantidad de viajes realizados |
| `usuarios[].total_dispositivos_fcm` | number | Cantidad de dispositivos activos |

---

## 🔧 Cambios Requeridos en el Frontend

### **1. Actualizar Fetch de Usuarios en Componente de Campañas**

#### **❌ CÓDIGO ANTERIOR (Eliminar/Comentar)**

```javascript
// archivo: components/CampanaForm.jsx (o similar)

const fetchUsuarios = async () => {
    try {
        const response = await axios.get(
            'https://backendspring2-production.up.railway.app/api/usuarios/',
            {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`
                }
            }
        );
        
        // ❌ PROBLEMA: Trae TODOS los usuarios
        setUsuariosDisponibles(response.data);
        
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
};
```

#### **✅ CÓDIGO ACTUALIZADO (Usar este)**

```javascript
// archivo: components/CampanaForm.jsx (o similar)

const fetchUsuariosConFCM = async () => {
    try {
        const response = await axios.get(
            'https://backendspring2-production.up.railway.app/api/usuarios/con_fcm/',
            {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`
                }
            }
        );
        
        // ✅ SOLUCIÓN: Solo usuarios con FCM activo
        // Nota: La respuesta ahora tiene estructura {count, usuarios}
        setUsuariosDisponibles(response.data.usuarios);
        
        // Opcional: Mostrar el total en UI
        console.log(`${response.data.count} usuarios disponibles para notificaciones`);
        
    } catch (error) {
        console.error('Error al cargar usuarios con FCM:', error);
        
        // Mostrar mensaje al usuario
        setError('No se pudieron cargar los usuarios. Intenta nuevamente.');
    }
};
```

---

### **2. Componente de Selección de Usuarios (React/Next.js)**

#### **Ejemplo Completo con Filtros**

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

const UsuarioSelectorFCM = ({ onSelectUsuarios, tipoAudiencia }) => {
    const [usuarios, setUsuarios] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedIds, setSelectedIds] = useState([]);
    const [filtroRol, setFiltroRol] = useState('');
    const [busqueda, setBusqueda] = useState('');
    const [error, setError] = useState(null);

    // Cargar usuarios con FCM activo
    const fetchUsuarios = async () => {
        setLoading(true);
        setError(null);
        
        try {
            // Construir URL con filtros
            let url = `${process.env.NEXT_PUBLIC_API_URL}/api/usuarios/con_fcm/`;
            const params = new URLSearchParams();
            
            if (filtroRol) params.append('rol', filtroRol);
            if (busqueda) params.append('search', busqueda);
            
            if (params.toString()) url += `?${params.toString()}`;
            
            const response = await axios.get(url, {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`
                }
            });
            
            setUsuarios(response.data.usuarios);
            
        } catch (error) {
            console.error('Error al cargar usuarios:', error);
            setError('No se pudieron cargar los usuarios con notificaciones activas');
        } finally {
            setLoading(false);
        }
    };

    // Cargar al montar y cuando cambien filtros
    useEffect(() => {
        if (tipoAudiencia === 'USUARIOS') {
            fetchUsuarios();
        }
    }, [tipoAudiencia, filtroRol, busqueda]);

    // Manejar selección de usuarios
    const toggleUsuario = (id) => {
        setSelectedIds(prev => {
            const newIds = prev.includes(id)
                ? prev.filter(i => i !== id)
                : [...prev, id];
            
            onSelectUsuarios(newIds);
            return newIds;
        });
    };

    // Seleccionar todos
    const seleccionarTodos = () => {
        const todosIds = usuarios.map(u => u.id);
        setSelectedIds(todosIds);
        onSelectUsuarios(todosIds);
    };

    // Limpiar selección
    const limpiarSeleccion = () => {
        setSelectedIds([]);
        onSelectUsuarios([]);
    };

    if (tipoAudiencia !== 'USUARIOS') return null;

    return (
        <div className="usuario-selector-fcm">
            <h3>Seleccionar Usuarios con Notificaciones Activas</h3>
            
            {/* Filtros */}
            <div className="filtros">
                <select 
                    value={filtroRol} 
                    onChange={(e) => setFiltroRol(e.target.value)}
                    className="filtro-rol"
                >
                    <option value="">Todos los roles</option>
                    <option value="Cliente">Solo Clientes</option>
                    <option value="Proveedor">Solo Proveedores</option>
                </select>
                
                <input
                    type="text"
                    placeholder="Buscar por nombre..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                    className="filtro-busqueda"
                />
            </div>

            {/* Mensaje de error */}
            {error && (
                <div className="alert alert-error">
                    ⚠️ {error}
                </div>
            )}

            {/* Loading state */}
            {loading && (
                <div className="loading">
                    Cargando usuarios con notificaciones activas...
                </div>
            )}

            {/* Lista de usuarios */}
            {!loading && usuarios.length > 0 && (
                <>
                    <div className="acciones">
                        <button onClick={seleccionarTodos} className="btn-secondary">
                            Seleccionar Todos ({usuarios.length})
                        </button>
                        <button onClick={limpiarSeleccion} className="btn-secondary">
                            Limpiar Selección
                        </button>
                        <span className="contador">
                            {selectedIds.length} seleccionado(s)
                        </span>
                    </div>

                    <div className="usuarios-lista">
                        {usuarios.map(usuario => (
                            <div 
                                key={usuario.id}
                                className={`usuario-card ${selectedIds.includes(usuario.id) ? 'selected' : ''}`}
                                onClick={() => toggleUsuario(usuario.id)}
                            >
                                <input
                                    type="checkbox"
                                    checked={selectedIds.includes(usuario.id)}
                                    onChange={() => {}}
                                    className="usuario-checkbox"
                                />
                                
                                <div className="usuario-info">
                                    <h4>{usuario.nombre}</h4>
                                    <p className="email">{usuario.email}</p>
                                    <div className="detalles">
                                        <span className="badge badge-rol">{usuario.rol}</span>
                                        <span className="badge badge-viajes">
                                            🧳 {usuario.num_viajes} viajes
                                        </span>
                                        <span className="badge badge-fcm">
                                            📱 {usuario.total_dispositivos_fcm} 
                                            {usuario.total_dispositivos_fcm === 1 ? ' dispositivo' : ' dispositivos'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}

            {/* Sin resultados */}
            {!loading && usuarios.length === 0 && (
                <div className="sin-resultados">
                    <p>📭 No hay usuarios con notificaciones activas que cumplan los filtros.</p>
                    <p className="ayuda">
                        Los usuarios deben tener la app instalada y haber registrado su dispositivo FCM.
                    </p>
                </div>
            )}
        </div>
    );
};

export default UsuarioSelectorFCM;
```

---

### **3. Estilos CSS Sugeridos**

```css
/* archivo: components/UsuarioSelectorFCM.css */

.usuario-selector-fcm {
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
}

.filtros {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

.filtro-rol,
.filtro-busqueda {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.filtro-busqueda {
    flex: 1;
}

.acciones {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
}

.contador {
    margin-left: auto;
    font-weight: 600;
    color: #2563eb;
}

.usuarios-lista {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;
}

.usuario-card {
    display: flex;
    gap: 12px;
    padding: 16px;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.usuario-card:hover {
    border-color: #60a5fa;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.usuario-card.selected {
    border-color: #2563eb;
    background: #eff6ff;
}

.usuario-checkbox {
    margin-top: 4px;
    cursor: pointer;
}

.usuario-info {
    flex: 1;
}

.usuario-info h4 {
    margin: 0 0 4px 0;
    font-size: 16px;
    color: #1f2937;
}

.email {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #6b7280;
}

.detalles {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.badge-rol {
    background: #dbeafe;
    color: #1e40af;
}

.badge-viajes {
    background: #fef3c7;
    color: #92400e;
}

.badge-fcm {
    background: #d1fae5;
    color: #065f46;
}

.alert-error {
    padding: 12px;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 6px;
    margin-bottom: 16px;
}

.loading,
.sin-resultados {
    text-align: center;
    padding: 40px;
    color: #6b7280;
}

.sin-resultados .ayuda {
    font-size: 14px;
    margin-top: 8px;
}
```

---

### **4. Integración en Formulario de Campaña**

```jsx
// archivo: pages/campanas/crear.jsx (o similar)

import { useState } from 'react';
import UsuarioSelectorFCM from '@/components/UsuarioSelectorFCM';

const CrearCampana = () => {
    const [formData, setFormData] = useState({
        nombre: '',
        descripcion: '',
        titulo: '',
        cuerpo: '',
        tipo_notificacion: 'promocion',
        tipo_audiencia: 'TODOS',
        usuarios_objetivo: [],
        segmento_filtros: {},
        enviar_inmediatamente: false,
        fecha_programada: null
    });

    const handleSelectUsuarios = (ids) => {
        setFormData(prev => ({
            ...prev,
            usuarios_objetivo: ids
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const response = await axios.post(
                `${process.env.NEXT_PUBLIC_API_URL}/api/campanas-notificacion/`,
                formData,
                {
                    headers: {
                        'Authorization': `Token ${localStorage.getItem('authToken')}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            console.log('Campaña creada:', response.data);
            // Redirigir o mostrar éxito
            
        } catch (error) {
            console.error('Error al crear campaña:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* Campos básicos */}
            <input
                type="text"
                placeholder="Nombre de la campaña"
                value={formData.nombre}
                onChange={(e) => setFormData({...formData, nombre: e.target.value})}
            />

            {/* Selector de tipo de audiencia */}
            <select
                value={formData.tipo_audiencia}
                onChange={(e) => setFormData({...formData, tipo_audiencia: e.target.value})}
            >
                <option value="TODOS">Todos los usuarios</option>
                <option value="USUARIOS">Usuarios específicos</option>
                <option value="SEGMENTO">Segmento personalizado</option>
            </select>

            {/* Componente de selección de usuarios */}
            <UsuarioSelectorFCM
                onSelectUsuarios={handleSelectUsuarios}
                tipoAudiencia={formData.tipo_audiencia}
            />

            {/* Botón submit */}
            <button type="submit">Crear Campaña</button>
        </form>
    );
};

export default CrearCampana;
```

---

## 🧪 Testing del Nuevo Endpoint

### **Test 1: Verificar que solo devuelve usuarios con FCM**

```javascript
// Test en consola del navegador o componente de test

const testEndpoint = async () => {
    try {
        const response = await fetch(
            'https://backendspring2-production.up.railway.app/api/usuarios/con_fcm/',
            {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('authToken')}`
                }
            }
        );
        
        const data = await response.json();
        
        console.log('✅ Total usuarios con FCM:', data.count);
        console.log('📱 Usuarios:', data.usuarios);
        
        // Verificar que todos tienen total_dispositivos_fcm > 0
        const todosConFCM = data.usuarios.every(u => u.total_dispositivos_fcm > 0);
        console.log('✅ Todos tienen FCM activo:', todosConFCM);
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
};

testEndpoint();
```

### **Test 2: Verificar filtros**

```javascript
// Test con filtro de rol
const testFiltroRol = async () => {
    const response = await fetch(
        'https://backendspring2-production.up.railway.app/api/usuarios/con_fcm/?rol=Cliente',
        {
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`
            }
        }
    );
    
    const data = await response.json();
    console.log('Clientes con FCM:', data.usuarios);
};

testFiltroRol();
```

---

## 📊 Comparación Antes vs Después

| Aspecto | ❌ Antes | ✅ Ahora |
|---------|----------|----------|
| **Endpoint** | `/api/usuarios/` | `/api/usuarios/con_fcm/` |
| **Usuarios mostrados** | Todos los usuarios | Solo con FCM activo |
| **Verificación FCM** | No | Sí (`dispositivos_fcm__activo=True`) |
| **Indicador de dispositivos** | No | Sí (`total_dispositivos_fcm`) |
| **Filtros disponibles** | Ninguno | `rol`, `search` |
| **Estructura respuesta** | Array directo | `{count, usuarios[]}` |
| **Garantía de entrega** | ❌ No | ✅ Sí |

---

## ⚠️ Consideraciones Importantes

### **1. Cambio de Estructura de Respuesta**

```javascript
// ❌ ANTES: Array directo
response.data  // [{id: 1, nombre: "..."}, ...]

// ✅ AHORA: Objeto con count y usuarios
response.data.usuarios  // [{id: 1, nombre: "..."}, ...]
response.data.count     // 5
```

**Acción requerida:** Actualizar `setUsuariosDisponibles(response.data)` a `setUsuariosDisponibles(response.data.usuarios)`

### **2. Usuarios sin FCM**

Si un usuario **no aparece** en la lista de `/con_fcm/`:
- ✅ Es correcto: Ese usuario no tiene la app instalada o no ha registrado su dispositivo
- ✅ No debe incluirse en campañas (no recibiría la notificación)
- 💡 Solución para el usuario: Instalar la app y abrir sesión para registrar su dispositivo FCM

### **3. Autenticación**

El endpoint requiere token de autenticación. Si obtienes `401 Unauthorized`:

```javascript
// Verificar que el token existe
const token = localStorage.getItem('authToken');
console.log('Token:', token ? 'Existe' : 'No existe');

// Verificar headers
headers: {
    'Authorization': `Token ${token}`,  // ← Nota el espacio después de "Token"
    'Content-Type': 'application/json'
}
```

---

## 🚀 Checklist de Implementación

### **Backend (Ya completado ✅)**
- [x] Endpoint `/api/usuarios/con_fcm/` creado
- [x] Filtros por rol y búsqueda implementados
- [x] Campo `total_dispositivos_fcm` agregado
- [x] Código desplegado en Railway (commit `1c13c10`)

### **Frontend (Por hacer 📝)**
- [ ] Cambiar endpoint de `/api/usuarios/` a `/api/usuarios/con_fcm/`
- [ ] Actualizar estructura de respuesta (`response.data` → `response.data.usuarios`)
- [ ] Implementar componente `UsuarioSelectorFCM` (opcional pero recomendado)
- [ ] Agregar filtros de rol y búsqueda (opcional)
- [ ] Mostrar indicador de `total_dispositivos_fcm` en UI (opcional)
- [ ] Testing de integración completa
- [ ] Deploy frontend a Netlify

---

## 📞 Soporte

Si tienes problemas:

1. **Verificar endpoint funciona:**
   ```bash
   curl -H "Authorization: Token TU_TOKEN" \
        https://backendspring2-production.up.railway.app/api/usuarios/con_fcm/
   ```

2. **Verificar logs del backend:**
   - Railway Dashboard → Tu Proyecto → Logs

3. **Verificar que usuarios tienen FCM:**
   ```bash
   curl -H "Authorization: Token TU_TOKEN" \
        https://backendspring2-production.up.railway.app/api/fcm-dispositivos/
   ```

---

## 🎯 Resultado Esperado

Después de implementar estos cambios:

✅ Frontend muestra **solo usuarios que pueden recibir notificaciones**
✅ Administrador ve cuántos dispositivos tiene cada usuario
✅ Campañas llegan a **100% de usuarios seleccionados**
✅ No más confusión sobre por qué algunos usuarios no reciben notificaciones

---

**Última actualización:** 2 de noviembre de 2025
**Commit relacionado:** `1c13c10` - "feat: Agregado endpoint para listar usuarios con tokens FCM activos"
