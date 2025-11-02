# 📢 GUÍA COMPLETA: Sistema de Notificaciones Push FCM

## 📋 **Índice**
1. [Archivos Modificados/Creados](#archivos-modificadoscreados)
2. [Dependencias y Requirements](#dependencias-y-requirements)
3. [Modelos Django](#modelos-django)
4. [Serializers](#serializers)
5. [ViewSets y API Endpoints](#viewsets-y-api-endpoints)
6. [Signals (Automáticos)](#signals-automáticos)
7. [Tasks (Lógica de Negocio)](#tasks-lógica-de-negocio)
8. [Firebase Initialization](#firebase-initialization)
9. [Configuración Settings](#configuración-settings)
10. [URLs](#urls)
11. [Migraciones](#migraciones)
12. [Variables de Entorno Railway](#variables-de-entorno-railway)
13. [Scheduler de Campañas](#scheduler-de-campañas)
14. [Testing](#testing)

---

## 1️⃣ **Archivos Modificados/Creados**

### **Archivos NUEVOS a crear:**
```
Backend_Spring2/
├── condominio/
│   ├── models.py                    # ✏️ MODIFICAR (agregar modelos FCM)
│   ├── serializer.py                # ✏️ MODIFICAR (agregar serializers FCM)
│   ├── api.py                       # ✏️ MODIFICAR (agregar ViewSets FCM)
│   ├── urls.py                      # ✏️ MODIFICAR (agregar rutas FCM)
│   ├── tasks.py                     # 🆕 CREAR NUEVO
│   ├── signals.py                   # ✏️ MODIFICAR
│   ├── signals_fcm.py               # 🆕 CREAR NUEVO
│   └── scheduler_campanas.py        # 🆕 CREAR NUEVO
├── core/
│   ├── firebase.py                  # 🆕 CREAR NUEVO
│   └── notifications.py             # 🆕 CREAR NUEVO
├── requirements.txt                 # ✏️ MODIFICAR
├── start.sh                         # ✏️ MODIFICAR
└── Procfile                         # ✏️ MODIFICAR
```

---

## 2️⃣ **Dependencias y Requirements**

### **Agregar a `requirements.txt`:**
```txt
# Firebase Admin SDK para notificaciones push
firebase-admin==7.1.0

# Scheduling
schedule==1.2.0
```

### **Instalar localmente:**
```bash
pip install firebase-admin==7.1.0 schedule==1.2.0
pip freeze > requirements.txt
```

---

## 3️⃣ **Modelos Django**

### **Agregar a `condominio/models.py`:**

```python
# ============================================
# 📱 DISPOSITIVOS FCM (Firebase Cloud Messaging)
# ============================================
class FCMDevice(models.Model):
    """
    Dispositivos móviles registrados para recibir notificaciones push.
    Cada usuario puede tener múltiples dispositivos (ej: teléfono + tablet).
    """
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='dispositivos_fcm',
        help_text='Usuario propietario del dispositivo'
    )
    registration_id = models.TextField(
        unique=True,
        help_text='Token FCM único del dispositivo'
    )
    tipo_dispositivo = models.CharField(
        max_length=20, 
        choices=[
            ('android', 'Android'),
            ('ios', 'iOS'),
            ('web', 'Web')
        ],
        default='android',
        help_text='Tipo de dispositivo'
    )
    nombre = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Nombre descriptivo (ej: "Celular de Juan")'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Si está activo para recibir notificaciones'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ultima_vez = models.DateTimeField(
        auto_now=True,
        help_text='Última vez que se actualizó el token'
    )

    class Meta:
        verbose_name = 'Dispositivo FCM'
        verbose_name_plural = 'Dispositivos FCM'
        ordering = ['-ultima_vez']

    def __str__(self):
        return f"{self.usuario.nombre} - {self.tipo_dispositivo} ({self.id})"


# ============================================
# 📢 CAMPAÑAS DE NOTIFICACIONES
# ============================================
class CampanaNotificacion(models.Model):
    """
    Campañas de notificaciones push masivas o segmentadas.
    Permite envío inmediato o programado.
    """
    
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PROGRAMADA', 'Programada'),
        ('EN_CURSO', 'En Curso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('ERROR', 'Error'),
    ]
    
    TIPOS_AUDIENCIA = [
        ('TODOS', 'Todos los usuarios'),
        ('USUARIOS', 'Usuarios específicos'),
        ('SEGMENTO', 'Segmento por filtros'),
        ('ROL', 'Por rol'),
    ]
    
    TIPOS_NOTIFICACION = [
        ('informativa', 'Informativa'),
        ('promocional', 'Promocional'),
        ('urgente', 'Urgente'),
        ('campana_marketing', 'Campaña Marketing'),
        ('actualizacion_sistema', 'Actualización Sistema'),
    ]
    
    # Información básica
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre interno de la campaña'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción interna (no se envía)'
    )
    
    # Contenido de la notificación
    titulo = models.CharField(
        max_length=100,
        help_text='Título que verá el usuario (máx 100 caracteres)'
    )
    cuerpo = models.TextField(
        max_length=500,
        help_text='Mensaje que verá el usuario (máx 500 caracteres)'
    )
    
    # Datos adicionales (JSON)
    datos_extra = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales para la app (acción, URL, etc.)'
    )
    
    # Clasificación
    tipo_notificacion = models.CharField(
        max_length=50,
        choices=TIPOS_NOTIFICACION,
        default='informativa'
    )
    
    # Segmentación
    tipo_audiencia = models.CharField(
        max_length=20,
        choices=TIPOS_AUDIENCIA,
        default='TODOS'
    )
    usuarios_objetivo = models.ManyToManyField(
        Usuario,
        blank=True,
        related_name='campanas_notificacion',
        help_text='Usuarios específicos (si tipo_audiencia=USUARIOS)'
    )
    segmento_filtros = models.JSONField(
        default=dict,
        blank=True,
        help_text='Filtros de segmentación (rol, num_viajes, etc.)'
    )
    
    # Programación
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='BORRADOR'
    )
    enviar_inmediatamente = models.BooleanField(
        default=True,
        help_text='Si es True, se envía al activar. Si es False, usar fecha_programada'
    )
    fecha_programada = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora de envío programado'
    )
    fecha_enviada = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora en que se completó el envío'
    )
    
    # Resultados
    total_destinatarios = models.IntegerField(
        default=0,
        help_text='Número de destinatarios objetivo'
    )
    total_enviados = models.IntegerField(
        default=0,
        help_text='Notificaciones enviadas exitosamente'
    )
    total_errores = models.IntegerField(
        default=0,
        help_text='Notificaciones con error'
    )
    resultado = models.JSONField(
        default=dict,
        blank=True,
        help_text='Detalles completos del envío'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Campaña de Notificación'
        verbose_name_plural = 'Campañas de Notificación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    def puede_activarse(self):
        """Verifica si la campaña puede ser activada."""
        return self.estado in ['BORRADOR', 'PROGRAMADA']
    
    def puede_cancelarse(self):
        """Verifica si la campaña puede ser cancelada."""
        return self.estado in ['BORRADOR', 'PROGRAMADA']
    
    def calcular_destinatarios(self):
        """Calcula el número de destinatarios según la segmentación."""
        usuarios = self.obtener_usuarios_objetivo()
        self.total_destinatarios = usuarios.count()
        self.save(update_fields=['total_destinatarios'])
        return self.total_destinatarios
    
    def obtener_usuarios_objetivo(self):
        """Retorna QuerySet de usuarios que recibirán la notificación."""
        if self.tipo_audiencia == 'TODOS':
            return Usuario.objects.filter(user__is_active=True)
        
        elif self.tipo_audiencia == 'USUARIOS':
            return self.usuarios_objetivo.filter(user__is_active=True)
        
        elif self.tipo_audiencia == 'SEGMENTO':
            usuarios = Usuario.objects.filter(user__is_active=True)
            
            # Aplicar filtros del segmento
            if 'rol' in self.segmento_filtros:
                usuarios = usuarios.filter(rol__nombre=self.segmento_filtros['rol'])
            
            if 'min_viajes' in self.segmento_filtros:
                usuarios = usuarios.filter(num_viajes__gte=self.segmento_filtros['min_viajes'])
            
            return usuarios
        
        elif self.tipo_audiencia == 'ROL':
            rol_nombre = self.segmento_filtros.get('rol')
            if rol_nombre:
                return Usuario.objects.filter(user__is_active=True, rol__nombre=rol_nombre)
        
        return Usuario.objects.none()
```

---

## 4️⃣ **Serializers**

### **Agregar a `condominio/serializer.py`:**

```python
# ============================================
# 📱 SERIALIZERS FCM
# ============================================
class FCMDeviceSerializer(serializers.ModelSerializer):
    """Serializer para dispositivos FCM."""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    
    class Meta:
        model = FCMDevice
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'registration_id',
            'tipo_dispositivo',
            'nombre',
            'activo',
            'created_at',
            'ultima_vez'
        ]
        read_only_fields = ['id', 'created_at', 'ultima_vez', 'usuario_nombre']


class CampanaNotificacionSerializer(serializers.ModelSerializer):
    """Serializer completo para campañas de notificación."""
    
    usuarios_objetivo_detalle = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_audiencia_display = serializers.CharField(source='get_tipo_audiencia_display', read_only=True)
    
    class Meta:
        model = CampanaNotificacion
        fields = [
            'id',
            'nombre',
            'descripcion',
            'titulo',
            'cuerpo',
            'datos_extra',
            'tipo_notificacion',
            'tipo_audiencia',
            'tipo_audiencia_display',
            'usuarios_objetivo',
            'usuarios_objetivo_detalle',
            'segmento_filtros',
            'estado',
            'estado_display',
            'enviar_inmediatamente',
            'fecha_programada',
            'fecha_enviada',
            'total_destinatarios',
            'total_enviados',
            'total_errores',
            'resultado',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'estado_display',
            'tipo_audiencia_display',
            'fecha_enviada',
            'total_destinatarios',
            'total_enviados',
            'total_errores',
            'resultado',
            'created_at',
            'updated_at'
        ]
    
    def get_usuarios_objetivo_detalle(self, obj):
        """Retorna información básica de usuarios objetivo (solo primeros 10)."""
        if obj.tipo_audiencia == 'USUARIOS':
            usuarios = obj.usuarios_objetivo.all()[:10]
            return [
                {
                    'id': u.id,
                    'nombre': u.nombre,
                    'email': u.user.email if hasattr(u, 'user') else None
                }
                for u in usuarios
            ]
        return []
    
    def validate(self, data):
        """Validaciones personalizadas."""
        # Si es programada, debe tener fecha
        if not data.get('enviar_inmediatamente') and not data.get('fecha_programada'):
            raise serializers.ValidationError(
                'Debe especificar fecha_programada si no es envío inmediato'
            )
        
        # Si es USUARIOS, debe tener usuarios
        if data.get('tipo_audiencia') == 'USUARIOS':
            usuarios = data.get('usuarios_objetivo', [])
            if not usuarios:
                raise serializers.ValidationError(
                    'Debe seleccionar al menos un usuario para tipo_audiencia=USUARIOS'
                )
        
        return data
```

---

## 5️⃣ **ViewSets y API Endpoints**

### **Agregar a `condominio/api.py`:**

```python
# ============================================
# 📱 DISPOSITIVOS FCM
# ============================================
from .models import FCMDevice, CampanaNotificacion
from .serializer import FCMDeviceSerializer, CampanaNotificacionSerializer

class FCMDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de dispositivos FCM.
    Permite registro y actualización de tokens desde la app móvil.
    """
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    
    def get_permissions(self):
        """
        - Registrar dispositivo: Permite sin autenticación (AllowAny)
        - Otras acciones: Requiere autenticación
        """
        if self.action == 'registrar':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Usuarios normales solo ven sus propios dispositivos."""
        user = self.request.user
        if user.is_staff or (hasattr(user, 'perfil') and user.perfil.rol and user.perfil.rol.nombre.lower() in ['admin', 'administrador', 'soporte']):
            return FCMDevice.objects.all()
        
        if hasattr(user, 'perfil') and user.perfil:
            return FCMDevice.objects.filter(usuario=user.perfil)
        
        return FCMDevice.objects.none()
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def registrar(self, request):
        """
        Registra o actualiza un dispositivo FCM.
        
        POST /api/fcm-dispositivos/registrar/
        Body:
        {
            "registration_id": "token_fcm_del_dispositivo",
            "tipo_dispositivo": "android",  # opcional
            "nombre": "Mi Celular"  # opcional
        }
        
        Retorna:
        - 201: Dispositivo creado
        - 200: Dispositivo actualizado
        """
        registration_id = request.data.get('registration_id')
        
        if not registration_id:
            return Response(
                {'error': 'registration_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener usuario autenticado (si existe)
        perfil = None
        if request.user.is_authenticated:
            perfil = getattr(request.user, 'perfil', None)
        
        if not perfil:
            return Response(
                {'error': 'Usuario no autenticado o sin perfil'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Buscar o crear dispositivo
        dispositivo, created = FCMDevice.objects.update_or_create(
            registration_id=registration_id,
            defaults={
                'usuario': perfil,
                'tipo_dispositivo': request.data.get('tipo_dispositivo', 'android'),
                'nombre': request.data.get('nombre', ''),
                'activo': True
            }
        )
        
        serializer = FCMDeviceSerializer(dispositivo)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return Response({
            'mensaje': 'Dispositivo registrado exitosamente' if created else 'Dispositivo actualizado',
            'dispositivo': serializer.data
        }, status=status_code)
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactiva un dispositivo (dejar de recibir notificaciones).
        
        POST /api/fcm-dispositivos/{id}/desactivar/
        """
        dispositivo = self.get_object()
        dispositivo.activo = False
        dispositivo.save(update_fields=['activo'])
        
        return Response({
            'mensaje': 'Dispositivo desactivado',
            'dispositivo_id': dispositivo.id
        })
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activa un dispositivo.
        
        POST /api/fcm-dispositivos/{id}/activar/
        """
        dispositivo = self.get_object()
        dispositivo.activo = True
        dispositivo.save(update_fields=['activo'])
        
        return Response({
            'mensaje': 'Dispositivo activado',
            'dispositivo_id': dispositivo.id
        })


# ============================================
# 📢 CAMPAÑAS DE NOTIFICACIONES
# ============================================
class CampanaNotificacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión administrativa de campañas de notificaciones push.
    Solo administradores pueden crear, modificar o ejecutar campañas.
    """
    queryset = CampanaNotificacion.objects.all()
    serializer_class = CampanaNotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'tipo_audiencia', 'tipo_notificacion']
    search_fields = ['nombre', 'titulo', 'descripcion']
    ordering_fields = ['created_at', 'fecha_programada', 'fecha_enviada']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Solo administradores pueden crear, modificar o ejecutar acciones sobre campañas."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 
                          'preview', 'enviar_test', 'activar', 'cancelar']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Vista previa de la campaña sin enviar.
        
        GET /api/campanas-notificacion/{id}/preview/
        """
        campana = self.get_object()
        
        usuarios = campana.obtener_usuarios_objetivo()
        total = usuarios.count()
        muestra = usuarios[:50]
        
        destinatarios_preview = [
            {
                'id': u.id,
                'nombre': u.nombre,
                'email': u.user.email if hasattr(u, 'user') and u.user else None,
                'rol': u.rol.nombre if u.rol else None,
            }
            for u in muestra
        ]
        
        return Response({
            'campana': {
                'id': campana.id,
                'nombre': campana.nombre,
                'estado': campana.estado,
            },
            'contenido': {
                'titulo': campana.titulo,
                'cuerpo': campana.cuerpo,
                'tipo_notificacion': campana.tipo_notificacion,
            },
            'segmentacion': {
                'tipo_audiencia': campana.tipo_audiencia,
                'total_destinatarios': total,
            },
            'destinatarios_preview': destinatarios_preview,
        })
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activa la campaña para envío inmediato o programado.
        
        POST /api/campanas-notificacion/{id}/activar/
        """
        from .tasks import ejecutar_campana_notificacion
        
        campana = self.get_object()
        
        if not campana.puede_activarse():
            return Response(
                {'error': f'No se puede activar una campaña en estado {campana.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total_destinatarios = campana.calcular_destinatarios()
        
        if total_destinatarios == 0:
            return Response(
                {'error': 'La campaña no tiene destinatarios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        perfil = getattr(request.user, 'perfil', None)
        ejecutor_id = perfil.id if perfil else None
        
        if campana.enviar_inmediatamente or not campana.fecha_programada:
            # Envío inmediato
            resultado = ejecutar_campana_notificacion(campana.id, ejecutor_id)
            
            if resultado['success']:
                return Response({
                    'mensaje': 'Campaña ejecutada inmediatamente',
                    'estado': 'COMPLETADA',
                    'resultado': resultado
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Error al ejecutar la campaña',
                    'resultado': resultado
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Programar
            campana.estado = 'PROGRAMADA'
            campana.save(update_fields=['estado'])
            
            return Response({
                'mensaje': 'Campaña programada exitosamente',
                'estado': 'PROGRAMADA',
                'fecha_programada': campana.fecha_programada,
                'total_destinatarios': total_destinatarios
            }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela una campaña en estado BORRADOR o PROGRAMADA.
        
        POST /api/campanas-notificacion/{id}/cancelar/
        """
        campana = self.get_object()
        
        if not campana.puede_cancelarse():
            return Response(
                {'error': f'No se puede cancelar una campaña en estado {campana.get_estado_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campana.estado = 'CANCELADA'
        campana.save(update_fields=['estado'])
        
        return Response({
            'mensaje': 'Campaña cancelada exitosamente',
            'estado': 'CANCELADA'
        }, status=status.HTTP_200_OK)
```

---

## 6️⃣ **Signals (Automáticos)**

### **Modificar `condominio/signals.py`:**

```python
import os

# Verificar si las señales FCM deben activarse
HABILITAR_SEÑAL_FCM = os.getenv('HABILITAR_SEÑAL_FCM', '').strip().strip('"').strip("'")

print(f"🔍 Verificando HABILITAR_SEÑAL_FCM: valor=\"{HABILITAR_SEÑAL_FCM}\" (original: \"{os.getenv('HABILITAR_SEÑAL_FCM')}\")")

if HABILITAR_SEÑAL_FCM and HABILITAR_SEÑAL_FCM.lower() in ('1', 'true', 'si', 'yes'):
    print("⚙️ Señales FCM activadas (HABILITAR_SEÑAL_FCM=true)")
    from . import signals_fcm  # Importar señales FCM
else:
    print("⚠️ Señales FCM desactivadas (HABILITAR_SEÑAL_FCM no está configurado)")
```

### **Crear `condominio/signals_fcm.py`:**

```python
"""
Signals para envío automático de notificaciones FCM.
Se activa cuando se crea una Notificacion.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notificacion
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notificacion)
def enviar_notificacion_fcm(sender, instance, created, **kwargs):
    """
    Signal que se dispara al crear una Notificacion.
    Envía push notification automáticamente al usuario.
    """
    if not created:
        return
    
    try:
        from core.notifications import enviar_tokens_push
        
        # Obtener dispositivos FCM del usuario
        dispositivos = instance.usuario.dispositivos_fcm.filter(activo=True)
        
        if not dispositivos.exists():
            logger.info(f"⚠️ Usuario {instance.usuario.nombre} no tiene dispositivos FCM activos")
            return
        
        tokens = [d.registration_id for d in dispositivos]
        
        # Extraer título de los datos
        titulo = instance.datos.get('titulo', 'Nueva Notificación')
        
        # Enviar notificación
        resultado = enviar_tokens_push(
            tokens=tokens,
            titulo=titulo,
            mensaje=instance.datos.get('mensaje', ''),
            datos={'notificacion_id': instance.id, 'tipo': instance.tipo}
        )
        
        logger.info(f"✅ FCM enviado para Notificacion {instance.id} (Usuario: {instance.usuario.nombre})")
        
    except Exception as e:
        logger.error(f"❌ Error enviando FCM para Notificacion {instance.id}: {e}")
```

---

## 7️⃣ **Tasks (Lógica de Negocio)**

### **Crear `condominio/tasks.py`:**

```python
"""
Tasks para ejecución de campañas de notificaciones.
"""
from django.utils import timezone
from .models import CampanaNotificacion, Notificacion, FCMDevice
from core.notifications import enviar_tokens_push
import logging

logger = logging.getLogger(__name__)


def ejecutar_campana_notificacion(campana_id, ejecutor_id=None):
    """
    Ejecuta una campaña de notificaciones.
    
    Args:
        campana_id: ID de la campaña
        ejecutor_id: ID del usuario que ejecuta (opcional)
    
    Returns:
        dict con resultado de la ejecución
    """
    try:
        campana = CampanaNotificacion.objects.get(id=campana_id)
        
        # Cambiar estado
        campana.estado = 'EN_CURSO'
        campana.save(update_fields=['estado'])
        
        # Obtener destinatarios
        usuarios = campana.obtener_usuarios_objetivo()
        
        total_enviados = 0
        total_errores = 0
        detalles = []
        
        # Enviar a cada usuario
        for usuario in usuarios:
            try:
                # Obtener dispositivos FCM activos
                dispositivos = FCMDevice.objects.filter(usuario=usuario, activo=True)
                
                if not dispositivos.exists():
                    detalles.append({
                        'usuario_id': usuario.id,
                        'status': 'sin_dispositivos',
                        'error': 'No tiene dispositivos FCM activos'
                    })
                    continue
                
                tokens = [d.registration_id for d in dispositivos]
                
                # Enviar notificación
                resultado = enviar_tokens_push(
                    tokens=tokens,
                    titulo=campana.titulo,
                    mensaje=campana.cuerpo,
                    datos={'campana_id': campana.id, 'tipo': campana.tipo_notificacion}
                )
                
                # Crear registro en Notificacion
                Notificacion.objects.create(
                    usuario=usuario,
                    tipo=campana.tipo_notificacion,
                    datos={
                        'titulo': campana.titulo,
                        'mensaje': campana.cuerpo,
                        'campana_id': campana.id
                    }
                )
                
                if resultado.get('success'):
                    total_enviados += 1
                    detalles.append({
                        'usuario_id': usuario.id,
                        'status': 'success',
                        'dispositivos': len(tokens)
                    })
                else:
                    total_errores += 1
                    detalles.append({
                        'usuario_id': usuario.id,
                        'status': 'error',
                        'error': resultado.get('error')
                    })
                    
            except Exception as e:
                total_errores += 1
                detalles.append({
                    'usuario_id': usuario.id,
                    'status': 'error',
                    'error': str(e)
                })
                logger.error(f"Error enviando a usuario {usuario.id}: {e}")
        
        # Actualizar campaña
        campana.estado = 'COMPLETADA'
        campana.fecha_enviada = timezone.now()
        campana.total_enviados = total_enviados
        campana.total_errores = total_errores
        campana.resultado = {
            'total_enviados': total_enviados,
            'total_errores': total_errores,
            'detalles': detalles[:100]  # Limitar detalles
        }
        campana.save()
        
        logger.info(f"✅ Campaña {campana.id} completada: {total_enviados} enviados, {total_errores} errores")
        
        return {
            'success': True,
            'total_enviados': total_enviados,
            'total_errores': total_errores
        }
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando campaña {campana_id}: {e}")
        
        try:
            campana = CampanaNotificacion.objects.get(id=campana_id)
            campana.estado = 'ERROR'
            campana.resultado = {'error': str(e)}
            campana.save()
        except:
            pass
        
        return {
            'success': False,
            'error': str(e)
        }


def enviar_notificacion_test(campana_id, usuario_id):
    """Envía notificación de prueba a un usuario específico."""
    try:
        from .models import Usuario
        
        campana = CampanaNotificacion.objects.get(id=campana_id)
        usuario = Usuario.objects.get(id=usuario_id)
        
        dispositivos = FCMDevice.objects.filter(usuario=usuario, activo=True)
        
        if not dispositivos.exists():
            return {
                'success': False,
                'error': 'Usuario no tiene dispositivos FCM activos'
            }
        
        tokens = [d.registration_id for d in dispositivos]
        
        resultado = enviar_tokens_push(
            tokens=tokens,
            titulo=f"[TEST] {campana.titulo}",
            mensaje=f"{campana.cuerpo}",
            datos={'campana_id': campana.id, 'test': True}
        )
        
        if resultado.get('success'):
            return {
                'success': True,
                'mensaje': f'Notificación de prueba enviada a {len(tokens)} dispositivo(s)',
                'usuario': usuario.nombre
            }
        else:
            return {
                'success': False,
                'error': resultado.get('error')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def calcular_metricas_campana(campana_id):
    """Recalcula métricas de lectura de una campaña."""
    try:
        campana = CampanaNotificacion.objects.get(id=campana_id)
        
        # Contar notificaciones leídas
        notificaciones = Notificacion.objects.filter(
            datos__campana_id=campana.id
        )
        
        total_notificaciones = notificaciones.count()
        total_leidas = notificaciones.filter(leida=True).count()
        tasa_lectura = (total_leidas / total_notificaciones * 100) if total_notificaciones > 0 else 0
        
        # Actualizar resultado
        resultado = campana.resultado or {}
        resultado['metricas'] = {
            'total_notificaciones': total_notificaciones,
            'total_leidas': total_leidas,
            'tasa_lectura': round(tasa_lectura, 2)
        }
        campana.resultado = resultado
        campana.save(update_fields=['resultado'])
        
        return {
            'success': True,
            'metricas': resultado['metricas']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 8️⃣ **Firebase Initialization**

### **Crear `core/firebase.py`:**

```python
"""
Inicialización de Firebase Admin SDK.
"""
import firebase_admin
from firebase_admin import credentials
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)


def iniciar_firebase():
    """
    Inicializa Firebase Admin SDK si no está inicializado.
    
    Soporta 3 métodos de configuración:
    1. FIREBASE_CREDENTIALS_BASE64 (producción Railway)
    2. FIREBASE_CREDENTIALS_JSON (JSON como string)
    3. FIREBASE_CREDENTIALS_PATH (ruta a archivo .json)
    """
    # Si ya está inicializado, retornar la app existente
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass  # No está inicializado, continuar
    
    cred = None
    
    # Método 1: Base64 (preferido para Railway)
    base64_cred = os.getenv('FIREBASE_CREDENTIALS_BASE64')
    if base64_cred:
        try:
            json_string = base64.b64decode(base64_cred).decode('utf-8')
            cred_dict = json.loads(json_string)
            cred = credentials.Certificate(cred_dict)
            logger.info("✅ Firebase credentials cargadas desde Base64")
        except Exception as e:
            logger.error(f"❌ Error decodificando Base64: {e}")
    
    # Método 2: JSON como string
    if not cred:
        json_string = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if json_string:
            try:
                cred_dict = json.loads(json_string)
                cred = credentials.Certificate(cred_dict)
                logger.info("✅ Firebase credentials cargadas desde JSON string")
            except Exception as e:
                logger.error(f"❌ Error parseando JSON string: {e}")
    
    # Método 3: Ruta a archivo
    if not cred:
        json_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-service-account.json')
        if os.path.exists(json_path):
            try:
                cred = credentials.Certificate(json_path)
                logger.info(f"✅ Firebase credentials cargadas desde archivo: {json_path}")
            except Exception as e:
                logger.error(f"❌ Error cargando archivo: {e}")
    
    if not cred:
        raise ValueError(
            "No se encontraron credenciales de Firebase. "
            "Configure FIREBASE_CREDENTIALS_BASE64, FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH"
        )
    
    # Inicializar Firebase
    app = firebase_admin.initialize_app(cred)
    logger.info(f"✅ Firebase Admin inicializado correctamente: {app.name}")
    
    return app
```

### **Crear `core/notifications.py`:**

```python
"""
Utilidades para envío de notificaciones push con Firebase.
"""
from firebase_admin import messaging
from .firebase import iniciar_firebase
import logging

logger = logging.getLogger(__name__)


def enviar_tokens_push(tokens, titulo, mensaje, datos=None):
    """
    Envía notificación push a uno o más tokens FCM.
    
    Args:
        tokens (list): Lista de tokens FCM
        titulo (str): Título de la notificación
        mensaje (str): Cuerpo de la notificación
        datos (dict): Datos adicionales (opcional)
    
    Returns:
        dict: Resultado del envío
    """
    if not tokens:
        return {'success': False, 'error': 'No hay tokens'}
    
    if isinstance(tokens, str):
        tokens = [tokens]
    
    try:
        # Asegurar que Firebase esté inicializado
        iniciar_firebase()
        
        # Construir mensaje
        mensajes = []
        for token in tokens:
            mensaje_fcm = messaging.Message(
                notification=messaging.Notification(
                    title=titulo,
                    body=mensaje
                ),
                data=datos or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            mensajes.append(mensaje_fcm)
        
        # Enviar (uno por uno para mejor control de errores)
        resultados = []
        for i, msg in enumerate(mensajes):
            try:
                response = messaging.send(msg)
                resultados.append({'token': tokens[i][:20], 'success': True, 'response': response})
                logger.info(f"✅ Notificación enviada: {response}")
            except messaging.UnregisteredError:
                resultados.append({'token': tokens[i][:20], 'success': False, 'error': 'Token no registrado'})
                logger.warning(f"⚠️ Token no registrado: {tokens[i][:20]}")
            except Exception as e:
                resultados.append({'token': tokens[i][:20], 'success': False, 'error': str(e)})
                logger.error(f"❌ Error enviando a token {tokens[i][:20]}: {e}")
        
        exitosos = sum(1 for r in resultados if r['success'])
        
        return {
            'success': exitosos > 0,
            'total_enviados': exitosos,
            'total_errores': len(resultados) - exitosos,
            'detalles': resultados
        }
        
    except Exception as e:
        logger.error(f"❌ Error al enviar mensajes FCM: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 9️⃣ **Configuración Settings**

### **Agregar a `config/settings.py`:**

```python
# ============================================
# FIREBASE CLOUD MESSAGING (FCM)
# ============================================

# Las credenciales se cargan desde variables de entorno
# Ver core/firebase.py para detalles de configuración

# Habilitar señales FCM automáticas
HABILITAR_SEÑAL_FCM = os.getenv('HABILITAR_SEÑAL_FCM', 'false')
```

---

## 🔟 **URLs**

### **Agregar a `condominio/urls.py`:**

```python
from .api import FCMDeviceViewSet, CampanaNotificacionViewSet

router.register(r'fcm-dispositivos', FCMDeviceViewSet, basename='fcm-dispositivos')
router.register(r'campanas-notificacion', CampanaNotificacionViewSet, basename='campanas-notificacion')
```

---

## 1️⃣1️⃣ **Migraciones**

### **Crear migración:**

```bash
python manage.py makemigrations condominio
python manage.py migrate
```

---

## 1️⃣2️⃣ **Variables de Entorno Railway**

### **Agregar en Railway:**

```bash
FIREBASE_CREDENTIALS_BASE64=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6Im5vdGlndWlhd...
HABILITAR_SEÑAL_FCM=true
```

### **Generar Base64 desde JSON:**

```python
import json
import base64

# Leer tu archivo firebase-service-account.json
with open('firebase-service-account.json', 'r') as f:
    cred_dict = json.load(f)

# Convertir a string JSON
json_string = json.dumps(cred_dict)

# Codificar en Base64
base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

print("FIREBASE_CREDENTIALS_BASE64:")
print(base64_encoded)
```

---

## 1️⃣3️⃣ **Scheduler de Campañas**

### **Crear `condominio/scheduler_campanas.py`:**

```python
"""
Scheduler para ejecutar campañas programadas automáticamente.
"""
import schedule
import time
from django.utils import timezone
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


def ejecutar_campanas_programadas():
    """
    Busca y ejecuta campañas programadas cuya fecha ya llegó.
    """
    from condominio.models import CampanaNotificacion
    from condominio.tasks import ejecutar_campana_notificacion
    
    ahora = timezone.now()
    
    logger.info(f"=== Verificando campañas programadas ({ahora}) ===")
    
    # Buscar campañas PROGRAMADAS cuya fecha ya pasó
    campanas = CampanaNotificacion.objects.filter(
        estado='PROGRAMADA',
        fecha_programada__lte=ahora
    )
    
    if not campanas.exists():
        logger.info("No hay campañas programadas pendientes de ejecutar.")
        return
    
    logger.info(f"Encontradas {campanas.count()} campañas para ejecutar:")
    
    for campana in campanas:
        try:
            tiempo_transcurrido = (ahora - campana.fecha_programada).total_seconds() / 60
            
            logger.info(f"📢 Campaña #{campana.id}: {campana.nombre}")
            logger.info(f"   Programada: {campana.fecha_programada}")
            logger.info(f"   Atraso: {tiempo_transcurrido:.1f} minutos")
            logger.info(f"   Destinatarios: {campana.total_destinatarios}")
            logger.info(f"   Ejecutando...")
            
            resultado = ejecutar_campana_notificacion(campana.id)
            
            if resultado['success']:
                logger.info(f"   ✓ Completada: {resultado['total_enviados']} enviados, {resultado['total_errores']} errores")
            else:
                logger.error(f"   ✗ Error: {resultado.get('error')}")
                
        except Exception as e:
            logger.error(f"   ✗ Excepción ejecutando campaña {campana.id}: {e}")
    
    logger.info("=== Resumen ===")
    logger.info(f"✓ Ejecutadas exitosamente: {sum(1 for c in campanas if c.estado == 'COMPLETADA')}")
    logger.info(f"✗ Con errores: {sum(1 for c in campanas if c.estado == 'ERROR')}")
    logger.info(f"Total procesadas: {campanas.count()}")


class Command(BaseCommand):
    help = 'Ejecuta el scheduler de campañas programadas'
    
    def handle(self, *args, **options):
        logger.info("="*60)
        logger.info("🤖 [SCHEDULER CMD] Iniciando scheduler de campañas")
        logger.info("="*60)
        
        # Programar tarea cada 1 minuto
        schedule.every(1).minutes.do(ejecutar_campanas_programadas)
        
        logger.info("✅ Job programado: cada 1 minuto")
        logger.info("🔄 Iniciando loop infinito...")
        
        # Loop infinito
        while True:
            schedule.run_pending()
            time.sleep(1)
```

### **Modificar `start.sh`:**

```bash
#!/bin/bash

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar scheduler en background
echo "🤖 Iniciando scheduler de campañas en background..."
python manage.py runscript scheduler_campanas &
SCHEDULER_PID=$!
echo "✅ Scheduler iniciado con PID: $SCHEDULER_PID"

# Iniciar servidor Gunicorn
echo "🚀 Iniciando servidor Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8080
```

### **Modificar `Procfile`:**

```
web: bash start.sh
```

---

## 1️⃣4️⃣ **Testing**

### **Script de prueba local:**

```python
# test_fcm_local.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from condominio.models import Usuario, FCMDevice, CampanaNotificacion
from django.utils import timezone
from datetime import timedelta

# 1. Verificar usuario
usuario = Usuario.objects.first()
print(f"✅ Usuario: {usuario.nombre} (ID: {usuario.id})")

# 2. Crear dispositivo FCM de prueba
dispositivo, created = FCMDevice.objects.get_or_create(
    usuario=usuario,
    registration_id="TOKEN_PRUEBA_123",
    defaults={'tipo_dispositivo': 'android', 'activo': True}
)
print(f"✅ Dispositivo: {dispositivo.id} ({'creado' if created else 'existente'})")

# 3. Crear campaña de prueba
campana = CampanaNotificacion.objects.create(
    nombre="Test Campaña Local",
    titulo="🎉 Test Notificación",
    cuerpo="Esta es una notificación de prueba desde el sistema local.",
    tipo_notificacion='informativa',
    tipo_audiencia='USUARIOS',
    enviar_inmediatamente=True,
    estado='BORRADOR'
)
campana.usuarios_objetivo.add(usuario)
campana.calcular_destinatarios()

print(f"✅ Campaña creada: {campana.id}")
print(f"   Total destinatarios: {campana.total_destinatarios}")
print()
print("✅ Todo listo para probar!")
print(f"   Ejecuta: python -c 'from condominio.tasks import ejecutar_campana_notificacion; ejecutar_campana_notificacion({campana.id})'")
```

---

## 📝 **RESUMEN DE PASOS PARA TU COLABORADOR**

1. ✅ **Instalar dependencias:**
   ```bash
   pip install firebase-admin==7.1.0 schedule==1.2.0
   ```

2. ✅ **Copiar/crear archivos:**
   - `core/firebase.py`
   - `core/notifications.py`
   - `condominio/tasks.py`
   - `condominio/signals_fcm.py`
   - `condominio/scheduler_campanas.py`

3. ✅ **Modificar archivos existentes:**
   - `condominio/models.py` (agregar modelos FCMDevice y CampanaNotificacion)
   - `condominio/serializer.py` (agregar serializers)
   - `condominio/api.py` (agregar ViewSets)
   - `condominio/urls.py` (registrar rutas)
   - `condominio/signals.py` (activación condicional)
   - `requirements.txt` (dependencias)
   - `start.sh` (scheduler)
   - `Procfile` (si usa Railway)

4. ✅ **Generar migraciones:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. ✅ **Configurar variables de entorno Railway:**
   ```
   FIREBASE_CREDENTIALS_BASE64=...
   HABILITAR_SEÑAL_FCM=true
   ```

6. ✅ **Deploy a Railway:**
   ```bash
   git add .
   git commit -m "feat: Sistema completo de notificaciones FCM"
   git push origin main
   ```

---

## ⚠️ **NOTAS IMPORTANTES**

1. **Firebase Credentials:** Nunca commitear el archivo JSON al repositorio
2. **Base64:** Usar el método de Base64 para Railway (más confiable)
3. **Scheduler:** Se ejecuta automáticamente en `start.sh`
4. **Signals:** Solo se activan si `HABILITAR_SEÑAL_FCM=true`
5. **Testing:** Probar primero localmente antes de desplegar

---

**✅ Con esta guía tu colaborador tiene TODO lo necesario para implementar el sistema FCM desde cero.**
