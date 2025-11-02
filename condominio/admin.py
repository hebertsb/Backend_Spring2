from django.contrib import admin
from .models import (
    Usuario, Categoria, Campania, Cupon, Reserva, Visitante, ReservaVisitante,
    Servicio, Paquete, PaqueteServicio, CampaniaServicio, Pago, Reprogramacion,
    Ticket, TicketMessage, Notificacion, FCMDevice, Bitacora, ComprobantePago,
    Proveedor, Suscripcion, ReglaReprogramacion, HistorialReprogramacion,
    ConfiguracionGlobalReprogramacion, CampanaNotificacion
)

# =====================================================
# 📢 CAMPAÑA DE NOTIFICACIONES - Admin
# =====================================================
@admin.register(CampanaNotificacion)
class CampanaNotificacionAdmin(admin.ModelAdmin):
    """
    Administración de campañas de notificaciones en Django Admin.
    """
    list_display = [
        'id', 'nombre', 'estado', 'tipo_audiencia', 
        'total_destinatarios', 'total_enviados', 'total_errores',
        'fecha_programada', 'fecha_enviada', 'created_at'
    ]
    list_filter = ['estado', 'tipo_audiencia', 'tipo_notificacion', 'created_at']
    search_fields = ['nombre', 'titulo', 'descripcion']
    readonly_fields = [
        'estado', 'fecha_enviada', 'enviado_por', 
        'total_destinatarios', 'total_enviados', 'total_leidos', 'total_errores',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('nombre', 'descripcion', 'estado')
        }),
        ('Contenido de la Notificación', {
            'fields': ('titulo', 'cuerpo', 'tipo_notificacion', 'datos_extra')
        }),
        ('Audiencia y Segmentación', {
            'fields': ('tipo_audiencia', 'usuarios_objetivo', 'segmento_filtros')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'enviar_inmediatamente')
        }),
        ('Ejecución', {
            'fields': ('fecha_enviada', 'enviado_por'),
            'classes': ('collapse',)
        }),
        ('Métricas', {
            'fields': ('total_destinatarios', 'total_enviados', 'total_leidos', 'total_errores'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Solo permitir eliminar campañas en BORRADOR."""
        if obj and obj.estado != 'BORRADOR':
            return False
        return super().has_delete_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir editar campañas en BORRADOR o PROGRAMADA."""
        if obj and not obj.puede_editarse():
            return False
        return super().has_change_permission(request, obj)


# Registrar otros modelos (ejemplo básico)
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rol', 'num_viajes', 'created_at']
    search_fields = ['nombre', 'user__email']
    list_filter = ['rol', 'created_at']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'tipo', 'leida', 'created_at']
    list_filter = ['tipo', 'leida', 'created_at']
    search_fields = ['usuario__nombre']
    readonly_fields = ['created_at']


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'tipo_dispositivo', 'activo', 'ultima_vez']
    list_filter = ['tipo_dispositivo', 'activo', 'created_at']
    search_fields = ['usuario__nombre', 'registration_id']
    readonly_fields = ['ultima_vez', 'created_at']


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'accion', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['usuario__nombre', 'accion', 'descripcion']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
