# 🌍 Configuración de Zona Horaria - Bolivia (UTC-4)

## ✅ Cambios Aplicados

Se ha configurado el backend Django para usar la zona horaria de Bolivia:

```python
# config/settings.py

LANGUAGE_CODE = 'es-bo'  # Español de Bolivia
TIME_ZONE = 'America/La_Paz'  # Bolivia (UTC-4)
USE_TZ = True  # Django maneja timezones automáticamente
```

---

## 🔄 Próximos Pasos

### 1. Reiniciar el Servidor Django

```bash
# Detén el servidor actual (Ctrl+C)
# Luego reinicia:
py manage.py runserver 0.0.0.0:8000
```

### 2. Probar Creación de Campaña

Ahora puedes enviar fechas desde tu frontend sin conversión:

```typescript
// Antes (causaba error):
fecha_programada: "2025-11-01T22:15"  // ❌ Se interpretaba como UTC

// Ahora (funcionará):
fecha_programada: "2025-11-01T22:15"  // ✅ Se interpreta como America/La_Paz
```

---

## 🧪 Verificar que Funciona

### Desde Python Shell:

```bash
py manage.py shell
```

```python
from django.utils import timezone
import pytz

# Ver zona horaria configurada
print("Zona horaria de Django:", timezone.get_current_timezone())
# Debería mostrar: America/La_Paz

# Ver hora actual en Bolivia
print("Hora actual (Bolivia):", timezone.now())
# Debería mostrar la hora local de Bolivia

# Verificar offset
tz = pytz.timezone('America/La_Paz')
print("Offset UTC:", timezone.now().astimezone(tz).strftime('%z'))
# Debería mostrar: -0400
```

---

## 📝 Ejemplo de Request que Ahora Funcionará

### Frontend (sin cambios):

```typescript
const payload = {
    nombre: "Dia de Muertos",
    titulo: "¡Bienvenido! 🎉",
    cuerpo: "Celebremos juntos",
    tipo_notificacion: "campana_marketing",
    tipo_audiencia: "USUARIOS",
    usuarios_objetivo: [4],
    enviar_inmediatamente: false,
    fecha_programada: "2025-11-02T10:00"  // ✅ Ahora se interpreta correctamente
};
```

### Backend (ahora interpretará):
- Fecha recibida: `2025-11-02T10:00`
- Se interpreta como: `2025-11-02 10:00:00 America/La_Paz (UTC-4)`
- Equivalente en UTC: `2025-11-02 14:00:00 UTC`
- Validación: ✅ Es futura si estamos antes de las 10 AM del 2 de nov en Bolivia

---

## ⚠️ Consideraciones

### Para Desarrollo Local:
✅ **PERFECTO** - Usar `TIME_ZONE = 'America/La_Paz'` evita confusiones

### Para Producción:
- Si tu servidor está en la nube (AWS, Railway, etc.), considera:
  - **Opción A:** Mantener `TIME_ZONE = 'America/La_Paz'` si todos tus usuarios son de Bolivia
  - **Opción B:** Usar `TIME_ZONE = 'UTC'` y hacer conversiones en el frontend para usuarios de múltiples zonas horarias

---

## 🔍 Debugging

### Ver logs del servidor:

Cuando crees una campaña, verás:

```
[02/Nov/2025 10:00:00] "POST /api/campanas-notificacion/ HTTP/1.1" 201 887
```

La hora mostrada será la hora de Bolivia, no UTC.

---

## 🎯 Testing Rápido

### 1. Reinicia el servidor
### 2. Intenta crear tu campaña de nuevo desde el frontend
### 3. La validación de fecha ahora usará la zona horaria de Bolivia

Si antes tenías este error:
```json
{
  "fecha_programada": ["La fecha programada debe ser futura"]
}
```

Ahora debería funcionar si la fecha está en el futuro según la hora de Bolivia.

---

## 💡 Alternativa: Ajustar Validación sin Cambiar Settings

Si prefieres mantener UTC en el servidor, puedes modificar la validación:

```python
# condominio/serializer.py

def validate(self, attrs):
    # ...
    fecha_programada = attrs.get('fecha_programada')
    
    if fecha_programada:
        # Agregar margen de tolerancia (5 minutos)
        from datetime import timedelta
        limite = timezone.now() - timedelta(minutes=5)
        
        if fecha_programada <= limite:
            raise serializers.ValidationError({
                'fecha_programada': 'La fecha programada debe ser futura'
            })
```

Pero la solución del TIME_ZONE es más limpia para desarrollo local.
