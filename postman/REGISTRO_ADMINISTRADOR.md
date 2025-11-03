# 📝 Registrar Usuario Administrador en Postman

## 🎯 Endpoint de Registro

**URL:** `http://127.0.0.1:8000/api/register/`  
**Método:** `POST`  
**Content-Type:** `application/json`  
**Autenticación:** No requerida

---

## 📋 Roles Disponibles en el Sistema

| ID | Nombre       | Descripción                    |
|----|--------------|--------------------------------|
| 1  | Administrador| Control total del sistema      |
| 2  | Cliente      | Usuarios finales del servicio  |
| 3  | Proveedor    | Proveedores de servicios       |
| 4  | Soporte      | Personal de soporte técnico    |

---

## 🔐 Registrar Administrador

### Body JSON para Postman:

```json
{
    "nombres": "Admin",
    "apellidos": "Sistema",
    "email": "admin@sistema.com",
    "password": "admin12345",
    "password_confirm": "admin12345",
    "rol": 1,
    "telefono": "+59170000000",
    "fecha_nacimiento": "1990-01-01",
    "genero": "M",
    "documento_identidad": "12345678",
    "pais": "Bolivia"
}
```

### Campos Requeridos ⚠️

- ✅ **nombres** (string): Nombre(s) del usuario
- ✅ **email** (string): Email único en el sistema
- ✅ **password** (string): Mínimo 8 caracteres
- ✅ **password_confirm** (string): Debe coincidir con password
- ✅ **rol** (integer): ID del rol (1 para Administrador)

### Campos Opcionales 📝

- apellidos (string): Apellidos del usuario
- telefono (string): Número de teléfono
- fecha_nacimiento (date): Formato YYYY-MM-DD
- genero (string): "M" o "F"
- documento_identidad (string): CI/DNI/Pasaporte
- pais (string): País de residencia
- rubro (string): Solo para proveedores

---

## 📦 Ejemplos de Registro

### 1️⃣ Administrador Completo

```json
{
    "nombres": "Juan Carlos",
    "apellidos": "Pérez López",
    "email": "juan.perez@admin.com",
    "password": "AdminPass2024!",
    "password_confirm": "AdminPass2024!",
    "rol": 1,
    "telefono": "+59171234567",
    "fecha_nacimiento": "1985-05-15",
    "genero": "M",
    "documento_identidad": "9876543",
    "pais": "Bolivia"
}
```

### 2️⃣ Administrador Mínimo (solo campos requeridos)

```json
{
    "nombres": "Admin",
    "email": "admin@test.com",
    "password": "password123",
    "password_confirm": "password123",
    "rol": 1
}
```

### 3️⃣ Registrar Cliente

```json
{
    "nombres": "María",
    "apellidos": "González",
    "email": "maria.gonzalez@cliente.com",
    "password": "cliente123",
    "password_confirm": "cliente123",
    "rol": 2,
    "telefono": "+59177777777",
    "pais": "Bolivia"
}
```

### 4️⃣ Registrar Proveedor

```json
{
    "nombres": "Carlos",
    "apellidos": "Mendoza",
    "email": "carlos.mendoza@proveedor.com",
    "password": "proveedor123",
    "password_confirm": "proveedor123",
    "rol": 3,
    "rubro": "Turismo de Aventura",
    "telefono": "+59172345678",
    "pais": "Bolivia"
}
```

---

## ✅ Respuesta Exitosa (201 Created)

```json
{
    "id": 5,
    "nombre": "Juan Carlos Pérez López",
    "user": {
        "id": 6,
        "username": "juan.perez@admin.com",
        "email": "juan.perez@admin.com",
        "first_name": "Juan Carlos",
        "last_name": "Pérez López",
        "is_staff": true,
        "is_active": true
    },
    "rol": {
        "id": 1,
        "nombre": "Administrador",
        "slug": null
    },
    "rubro": "",
    "telefono": "+59171234567",
    "fecha_nacimiento": "1985-05-15",
    "genero": "M",
    "documento_identidad": "9876543",
    "pais": "Bolivia"
}
```

**Notas importantes:**
- `is_staff: true` - El usuario puede acceder a endpoints administrativos
- Se crea automáticamente el usuario Django (`User`) y el perfil (`Usuario`)
- El `username` es igual al `email`

---

## ❌ Errores Comunes

### Email ya registrado
```json
{
    "email": [
        "Este correo electrónico ya está registrado."
    ]
}
```

### Contraseña muy corta
```json
{
    "password": [
        "La contraseña debe tener al menos 8 caracteres."
    ]
}
```

### Contraseñas no coinciden
```json
{
    "password_confirm": [
        "Las contraseñas no coinciden."
    ]
}
```

### Rol no existe
```json
{
    "rol": [
        "Invalid pk \"99\" - object does not exist."
    ]
}
```

### Campos requeridos faltantes
```json
{
    "nombres": [
        "This field is required."
    ],
    "email": [
        "This field is required."
    ],
    "password": [
        "This field is required."
    ],
    "rol": [
        "This field is required."
    ]
}
```

---

## 🚀 Pasos en Postman

### PASO 1: Crear Request
1. Clic en **New → HTTP Request**
2. Cambiar método a **POST**
3. URL: `http://127.0.0.1:8000/api/register/`

### PASO 2: Configurar Headers
```
Content-Type: application/json
```

### PASO 3: Configurar Body
1. Selecciona la pestaña **Body**
2. Marca **raw**
3. Selecciona **JSON** en el dropdown
4. Pega el JSON de registro

### PASO 4: Enviar Request
1. Clic en **Send**
2. Verifica que la respuesta sea **201 Created**
3. Guarda el `id` y `email` del usuario creado

---

## 🔐 Siguiente Paso: Login

Después de registrar el administrador, inicia sesión:

**URL:** `http://127.0.0.1:8000/api/login/`  
**Método:** `POST`

**Body:**
```json
{
    "email": "admin@sistema.com",
    "password": "admin12345"
}
```

**Respuesta:**
```json
{
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "user": {
        "id": 5,
        "email": "admin@sistema.com",
        "nombre": "Admin Sistema",
        "rol": "Administrador"
    }
}
```

**⚠️ Guarda el token!** Lo necesitarás para todas las requests de campañas:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## 📊 Verificar Usuario Creado

**URL:** `http://127.0.0.1:8000/api/usuarios/`  
**Método:** `GET`  
**Headers:**
```
Authorization: Token {tu_token_aquí}
```

Busca tu usuario en la lista y verifica que tenga el rol "Administrador".

---

## 🎯 Request Completo para Importar a Postman

```json
{
    "name": "Registrar Administrador",
    "request": {
        "method": "POST",
        "header": [
            {
                "key": "Content-Type",
                "value": "application/json"
            }
        ],
        "body": {
            "mode": "raw",
            "raw": "{\n    \"nombres\": \"Admin\",\n    \"apellidos\": \"Sistema\",\n    \"email\": \"admin@sistema.com\",\n    \"password\": \"admin12345\",\n    \"password_confirm\": \"admin12345\",\n    \"rol\": 1,\n    \"telefono\": \"+59170000000\",\n    \"fecha_nacimiento\": \"1990-01-01\",\n    \"genero\": \"M\",\n    \"documento_identidad\": \"12345678\",\n    \"pais\": \"Bolivia\"\n}"
        },
        "url": {
            "raw": "http://127.0.0.1:8000/api/register/",
            "protocol": "http",
            "host": ["127", "0", "0", "1"],
            "port": "8000",
            "path": ["api", "register", ""]
        }
    }
}
```

---

## 🎉 ¡Listo!

Ahora puedes:
1. ✅ Registrar administradores
2. ✅ Hacer login y obtener token
3. ✅ Crear campañas de notificaciones
4. ✅ Gestionar usuarios del sistema

**Siguiente:** Importa la colección `Campanas_Notificaciones.postman_collection.json` y comienza a probar las campañas! 🚀
