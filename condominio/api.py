from rest_framework import viewsets, permissions
from django.utils import timezone

# Helper to safely get perfil from user
def get_user_perfil(user):
    """Safely get perfil from user object"""
    if user and hasattr(user, 'perfil'):
        return getattr(user, 'perfil', None)
    return None

# Helper to log into Bitacora
def log_bitacora(request, accion, descripcion=None):
    """Create a Bitacora entry using request context (user perfil and IP).

    descripcion: optional free text describing the change; if callable, it will be called
    with the saved instance to produce a description.
    """
    try:
        Bitacora = __import__('condominio.models', fromlist=['Bitacora']).Bitacora
        # try to resolve perfil from request.user
        perfil = None
        user = getattr(request, 'user', None)
        perfil = get_user_perfil(user)

        # Determine IP
        ip = None
        # Common headers for real client IPs behind proxies
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            ip = xff.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        Bitacora.objects.create(usuario=perfil, accion=accion, descripcion=(descripcion or ''), ip_address=ip)
    except Exception:
        # Avoid failing the main operation if logging fails
        pass


# Audited base viewset: automatic Bitacora entries for CRUD
class AuditedModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet that writes Bitacora entries on create/update/destroy.

    Subclasses may override or call super() for custom behavior.
    """
    def _make_description(self, action, instance):
        # Default description: ModelName id=.. repr
        try:
            model_name = instance.__class__.__name__
            pk = getattr(instance, 'id', None)
            return f"{model_name} {action} id={pk}"
        except Exception:
            return f"{action}"

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            descripcion = self._make_description('creado', instance)
            log_bitacora(self.request, f'Crear {instance.__class__.__name__}', descripcion)
        except Exception:
            pass

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            descripcion = self._make_description('actualizado', instance)
            log_bitacora(self.request, f'Actualizar {instance.__class__.__name__}', descripcion)
        except Exception:
            pass

    def perform_destroy(self, instance):
        try:
            descripcion = self._make_description('eliminado', instance)
            log_bitacora(self.request, f'Eliminar {instance.__class__.__name__}', descripcion)
        except Exception:
            pass
        instance.delete()
from .models import (
    Categoria, Servicio, Usuario, Campania, Cupon, Reserva, Visitante,
    ReservaVisitante, CampaniaServicio, Pago, ReglaReprogramacion, 
    HistorialReprogramacion, ConfiguracionGlobalReprogramacion, Reprogramacion
)
from .serializer import (
    CategoriaSerializer, ServicioSerializer, UsuarioSerializer, CampaniaSerializer,
    CuponSerializer, ReservaSerializer, VisitanteSerializer, ReservaVisitanteSerializer,
    CampaniaServicioSerializer, PagoSerializer, ReglaReprogramacionSerializer,
    HistorialReprogramacionSerializer, ConfiguracionGlobalReprogramacionSerializer,
    ReprogramacionSerializer, PaqueteCompletoSerializer
)
from .serializer import TicketSerializer, TicketDetailSerializer, TicketMessageSerializer, NotificacionSerializer
from .serializer import BitacoraSerializer
from .models import Ticket, TicketMessage, Notificacion
from .utils import assign_agent_to_ticket
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


# =====================================================
# 🏷️ CATEGORIA
# =====================================================
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 🧍 USUARIO
# =====================================================
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        # Siempre devolver 200 para usuarios autenticados.
        # Si existe el perfil, devolverlo serializado; si no, devolver un fallback público mínimo.
        user = request.user
        perfil = get_user_perfil(user)

        if perfil:
            # Usar el serializador público consistente con login/register
            from authz.serializer import PublicUsuarioSerializer
            serializer = PublicUsuarioSerializer(perfil)
            return Response(serializer.data)

        # Perfil no existe: devolver información pública mínima del user
        fallback = {
            'id': None,
            'user': user.id,
            'nombre': None,
            'rubro': None,
            'num_viajes': 0,
            'rol': None,
        }
        return Response(fallback)


# =====================================================
# 🎯 CAMPAÑA
# =====================================================
class CampaniaViewSet(viewsets.ModelViewSet):
    queryset = Campania.objects.all()
    serializer_class = CampaniaSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 📦 PAQUETES COMPLETOS
# =====================================================
class PaqueteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para mostrar paquetes completos (campaña + servicios incluidos)
    Solo permite lectura (GET) - para crear/editar usar campanias y campania-servicios
    """
    queryset = Campania.objects.prefetch_related('servicios__servicio__categoria', 'cupones').all()
    serializer_class = PaqueteCompletoSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Filtros personalizados para paquetes"""
        queryset = super().get_queryset()
        
        # Filtrar solo campañas activas/vigentes si se solicita
        activo = self.request.query_params.get('activo', None)
        if activo and activo.lower() == 'true':
            from django.utils import timezone
            hoy = timezone.now().date()
            queryset = queryset.filter(fecha_fin__gte=hoy)
        
        # Filtrar por tipo de descuento
        tipo_descuento = self.request.query_params.get('tipo_descuento', None)
        if tipo_descuento:
            queryset = queryset.filter(tipo_descuento=tipo_descuento)
        
        # Filtrar por descuento mínimo
        descuento_min = self.request.query_params.get('descuento_min', None)
        if descuento_min:
            queryset = queryset.filter(monto__gte=descuento_min)
        
        return queryset


# =====================================================
# 🎟️ CUPON
# =====================================================
class CuponViewSet(viewsets.ModelViewSet):
    queryset = Cupon.objects.select_related('campania').all()
    serializer_class = CuponSerializer
    permission_classes = [permissions.AllowAny]




# =====================================================
# 🏞️ SERVICIO
# =====================================================
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.select_related('categoria', 'proveedor').all()
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]




# =====================================================
# 🧾 RESERVA
# =====================================================
class ReservaViewSet(AuditedModelViewSet):
    queryset = Reserva.objects.select_related('cliente', 'cupon').all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.AllowAny]

    # Auditing hooks: create bitacora entries on create/update/destroy
    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            # create a basic description with id and cliente
            descripcion = f"Reserva creada id={instance.id} cliente={getattr(instance.cliente, 'nombre', None)}"
            log_bitacora(self.request, 'Crear Reserva', descripcion)
        except Exception:
            pass

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            descripcion = f"Reserva actualizada id={instance.id} cliente={getattr(instance.cliente, 'nombre', None)}"
            log_bitacora(self.request, 'Actualizar Reserva', descripcion)
        except Exception:
            pass

    def perform_destroy(self, instance):
        try:
            descripcion = f"Reserva eliminada id={instance.id} cliente={getattr(instance.cliente, 'nombre', None)}"
            # we log before deletion so we can reference instance fields
            log_bitacora(self.request, 'Eliminar Reserva', descripcion)
        except Exception:
            pass
        instance.delete()


# =====================================================
# 👥 VISITANTE
# =====================================================
class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 🔗 RESERVA_VISITANTE
# =====================================================
class ReservaVisitanteViewSet(viewsets.ModelViewSet):
    queryset = ReservaVisitante.objects.select_related('reserva', 'visitante').all()
    serializer_class = ReservaVisitanteSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 🔗 CAMPAÑA_SERVICIO
# =====================================================
class CampaniaServicioViewSet(viewsets.ModelViewSet):
    queryset = CampaniaServicio.objects.select_related('servicio', 'campania').all()
    serializer_class = CampaniaServicioSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 💳 PAGO
# =====================================================
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('reserva').all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 🔁 REGLA_REPROGRAMACION
# =====================================================
class ReglaReprogramacionViewSet(viewsets.ModelViewSet):
    queryset = ReglaReprogramacion.objects.all()
    serializer_class = ReglaReprogramacionSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 🔄 REPROGRAMACION
# =====================================================
class ReprogramacionViewSet(viewsets.ModelViewSet):
    queryset = Reprogramacion.objects.select_related('reserva').all()
    serializer_class = ReprogramacionSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# 📋 HISTORIAL_REPROGRAMACION
# =====================================================
class HistorialReprogramacionViewSet(viewsets.ModelViewSet):
    queryset = HistorialReprogramacion.objects.select_related('reserva', 'reprogramado_por').all()
    serializer_class = HistorialReprogramacionSerializer
    permission_classes = [permissions.AllowAny]


# =====================================================
# ⚙️ CONFIGURACION_GLOBAL_REPROGRAMACION
# =====================================================
class ConfiguracionGlobalReprogramacionViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionGlobalReprogramacion.objects.all()
    serializer_class = ConfiguracionGlobalReprogramacionSerializer
    permission_classes = [permissions.AllowAny]


# ==========================
# Soporte (Tickets)
# ==========================
class TicketViewSet(AuditedModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TicketDetailSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        user = self.request.user
        try:
            perfil = getattr(user, "perfil", None)
        except Exception:
            perfil = None

        ticket = serializer.save(creador=perfil)
        assign_agent_to_ticket(ticket)

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = getattr(user, "perfil", None)
        except Exception:
            return Ticket.objects.none()

        if perfil and hasattr(perfil, 'rol') and perfil.rol and perfil.rol.nombre.lower() == 'soporte':
            return Ticket.objects.all()
        return Ticket.objects.filter(creador=perfil)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.estado = 'Cerrado'
        ticket.save()
        Notificacion.objects.create(usuario=ticket.creador, tipo='ticket_cerrado', datos={'ticket_id': ticket.id})
        return Response({'status': 'cerrado'})


class TicketMessageViewSet(viewsets.ModelViewSet):
    queryset = TicketMessage.objects.all()
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            perfil = getattr(user, "perfil", None)
        except Exception:
            perfil = None

        message = serializer.save(autor=perfil)
        ticket = message.ticket
        if perfil and perfil.rol and perfil.rol.nombre.lower() == 'soporte':
            ticket.estado = 'Respondido'
            ticket.save()
            Notificacion.objects.create(usuario=ticket.creador, tipo='ticket_respondido', datos={'ticket_id': ticket.id, 'message_id': message.id})


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = getattr(user, "perfil", None)
        except Exception:
            return Notificacion.objects.none()
        return Notificacion.objects.filter(usuario=perfil)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        noti = self.get_object()
        noti.leida = True
        noti.save()
        return Response({'status': 'leida'})


class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = __import__('condominio.models', fromlist=['Bitacora']).Bitacora.objects.all()
    serializer_class = BitacoraSerializer
    permission_classes = [permissions.IsAuthenticated]
