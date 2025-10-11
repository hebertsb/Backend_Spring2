from rest_framework import viewsets, permissions
from .models import (
    Categoria, Servicio, Usuario, Campania, Cupon, Reserva, Visitante,
    ReservaVisitante, CampaniaServicio, Pago, ReglaReprogramacion, Reprogramacion
)
from .serializer import (
    CategoriaSerializer, ServicioSerializer, UsuarioSerializer, CampaniaSerializer,
    CuponSerializer, ReservaSerializer, VisitanteSerializer, ReservaVisitanteSerializer,
    CampaniaServicioSerializer, PagoSerializer, ReglaReprogramacionSerializer,
    ReprogramacionSerializer
)
from .serializer import TicketSerializer, TicketDetailSerializer, TicketMessageSerializer, NotificacionSerializer
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
        try:
            perfil = user.perfil
        except Exception:
            perfil = None

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
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('cliente', 'cupon').all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.AllowAny]


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


# ==========================
# Soporte (Tickets)
# ==========================
class TicketViewSet(viewsets.ModelViewSet):
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
            perfil = user.perfil
        except Exception:
            perfil = None

        ticket = serializer.save(creador=perfil)
        assign_agent_to_ticket(ticket)

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = user.perfil
        except Exception:
            return Ticket.objects.none()

        if perfil.rol and perfil.rol.nombre.lower() == 'soporte':
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
            perfil = user.perfil
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
            perfil = user.perfil
        except Exception:
            return Notificacion.objects.none()
        return Notificacion.objects.filter(usuario=perfil)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        noti = self.get_object()
        noti.leida = True
        noti.save()
        return Response({'status': 'leida'})
