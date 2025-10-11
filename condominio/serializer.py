from rest_framework import serializers
from authz.serializer import RolSerializer
from .models import (
    Categoria,
    Servicio,
    Usuario,
    Campania,
    Cupon,
    Reserva,
    Visitante,
    ReservaVisitante,
    CampaniaServicio,
    Pago,
    ReglaReprogramacion,
    Reprogramacion,
)


# =====================================================
# 🏷️ CATEGORIA
# =====================================================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🧍 USUARIO
# =====================================================
class UsuarioSerializer(serializers.ModelSerializer):
    # anidar el rol como objeto para que sea consistente con el login
    rol = RolSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🎯 CAMPAÑA
# =====================================================
class CampaniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campania
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🎟️ CUPON
# =====================================================
class CuponSerializer(serializers.ModelSerializer):
    campania = CampaniaSerializer(read_only=True)
    campania_id = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(), source="campania", write_only=True
    )

    class Meta:
        model = Cupon
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🏞️ SERVICIO
# =====================================================
class ServicioSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source="categoria", write_only=True
    )
    proveedor = UsuarioSerializer(read_only=True)
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source="proveedor", write_only=True
    )

    class Meta:
        model = Servicio
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🧾 RESERVA
# =====================================================
class ReservaSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source="cliente", write_only=True
    )
    cupon = CuponSerializer(read_only=True)
    cupon_id = serializers.PrimaryKeyRelatedField(
        queryset=Cupon.objects.all(),
        source="cupon",
        write_only=True,
        required=False, 
        allow_null=True, 
    )

    class Meta:
        model = Reserva
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 👥 VISITANTE
# =====================================================
class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🔗 RESERVA_VISITANTE
# =====================================================
class ReservaVisitanteSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source="reserva", write_only=True
    )
    visitante = VisitanteSerializer(read_only=True)
    visitante_id = serializers.PrimaryKeyRelatedField(
        queryset=Visitante.objects.all(), source="visitante", write_only=True
    )

    class Meta:
        model = ReservaVisitante
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🔗 CAMPAÑA_SERVICIO
# =====================================================
class CampaniaServicioSerializer(serializers.ModelSerializer):
    servicio = ServicioSerializer(read_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.all(), source="servicio", write_only=True
    )
    campania = CampaniaSerializer(read_only=True)
    campania_id = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(), source="campania", write_only=True
    )

    class Meta:
        model = CampaniaServicio
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 💳 PAGO
# =====================================================
class PagoSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source="reserva", write_only=True
    )

    class Meta:
        model = Pago
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🔁 REGLA_REPROGRAMACION
# =====================================================
class ReglaReprogramacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaReprogramacion
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 🔄 REPROGRAMACION
# =====================================================
class ReprogramacionSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source="reserva", write_only=True
    )

    class Meta:
        model = Reprogramacion
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# ==========================
# Soporte (Tickets)
# ==========================
class TicketMessageSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source="autor.nombre", read_only=True)

    class Meta:
        model = __import__(
            "condominio.models", fromlist=["TicketMessage"]
        ).TicketMessage
        fields = ["id", "ticket", "autor", "autor_nombre", "texto", "created_at"]
        read_only_fields = ["id", "created_at", "autor_nombre", "autor"]


class TicketSerializer(serializers.ModelSerializer):
    creador_nombre = serializers.CharField(source="creador.nombre", read_only=True)
    agente_nombre = serializers.CharField(source="agente.nombre", read_only=True)

    class Meta:
        model = __import__("condominio.models", fromlist=["Ticket"]).Ticket
        fields = [
            "id",
            "creador",
            "creador_nombre",
            "asunto",
            "descripcion",
            "estado",
            "agente",
            "agente_nombre",
            "prioridad",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "creador",
            "creador_nombre",
            "estado",
            "agente",
            "agente_nombre",
            "created_at",
            "updated_at",
        ]


class TicketDetailSerializer(TicketSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ["messages"]


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = __import__('condominio.models', fromlist=['Notificacion']).Notificacion
        fields = ['id', 'usuario', 'tipo', 'datos', 'leida', 'created_at']
        read_only_fields = ['id', 'created_at']


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    actor_email = serializers.SerializerMethodField()
    created_at_local = serializers.SerializerMethodField()

    class Meta:
        model = __import__('condominio.models', fromlist=['Bitacora']).Bitacora
        # include computed fields actor_email and created_at_local in the public fields
        fields = ['id', 'usuario', 'usuario_nombre', 'actor_email', 'accion', 'descripcion', 'ip_address', 'created_at', 'created_at_local']
        read_only_fields = ['id', 'created_at', 'usuario_nombre', 'created_at_local', 'actor_email']

    def get_actor_email(self, obj):
        try:
            return obj.usuario.user.email if obj.usuario and getattr(obj.usuario,'user',None) else None
        except Exception:
            return None

    def get_created_at_local(self, obj):
        # Convert UTC time (stored) to America/La_Paz
        try:
            from django.utils import timezone
            from zoneinfo import ZoneInfo
            utc_dt = obj.created_at
            if utc_dt is None:
                return None
            if timezone.is_naive(utc_dt):
                # assume stored as UTC
                utc_dt = utc_dt.replace(tzinfo=ZoneInfo('UTC'))
            local_dt = utc_dt.astimezone(ZoneInfo('America/La_Paz'))
            return local_dt.isoformat()
        except Exception:
            return str(obj.created_at)
