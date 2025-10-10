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
