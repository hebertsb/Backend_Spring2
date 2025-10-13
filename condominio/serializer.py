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
    HistorialReprogramacion,
    ConfiguracionGlobalReprogramacion,
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
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        fecha_inicio = data.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fecha_fin = data.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        monto = data.get("monto", getattr(self.instance, "monto", None))

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if monto is not None and monto <= 0:
            raise serializers.ValidationError("El monto de descuento debe ser mayor que cero.")
        return data


# =====================================================
# 📦 PAQUETE COMPLETO (Campaña + Servicios)
# =====================================================
class PaqueteCompletoSerializer(serializers.ModelSerializer):
    """Serializer para mostrar paquetes completos con servicios incluidos"""
    servicios_incluidos = serializers.SerializerMethodField()
    cupones_disponibles = serializers.SerializerMethodField()
    precio_total_servicios = serializers.SerializerMethodField()
    
    class Meta:
        model = Campania
        fields = "__all__" 
        read_only_fields = ["id", "created_at"]
    
    def get_servicios_incluidos(self, obj):
        """Obtiene todos los servicios incluidos en esta campaña/paquete"""
        from .models import CampaniaServicio
        campania_servicios = CampaniaServicio.objects.filter(campania=obj).select_related('servicio__categoria')
        return [
            {
                'id': cs.servicio.pk,
                'titulo': cs.servicio.titulo,
                'descripcion': cs.servicio.descripcion,
                'duracion': cs.servicio.duracion,
                'capacidad_max': cs.servicio.capacidad_max,
                'punto_encuentro': cs.servicio.punto_encuentro,
                'precio_usd': float(cs.servicio.precio_usd),
                'categoria': cs.servicio.categoria.nombre if cs.servicio.categoria else None,
                'imagen_url': cs.servicio.imagen_url,
                'estado': cs.servicio.estado,
                'servicios_incluidos': cs.servicio.servicios_incluidos
            }
            for cs in campania_servicios
        ]
    
    def get_cupones_disponibles(self, obj):
        """Obtiene cupones disponibles para esta campaña"""
        from django.db import models
        cupones = obj.cupones.filter(nro_usos__lt=models.F('cantidad_max'))
        return [
            {
                'id': cupon.pk,
                'usos_restantes': cupon.cantidad_max - cupon.nro_usos,
                'cantidad_max': cupon.cantidad_max,
                'nro_usos': cupon.nro_usos
            }
            for cupon in cupones
        ]
    
    def get_precio_total_servicios(self, obj):
        """Calcula precio total de servicios incluidos en USD"""
        from .models import CampaniaServicio
        campania_servicios = CampaniaServicio.objects.filter(campania=obj).select_related('servicio')
        total_usd = sum(cs.servicio.precio_usd for cs in campania_servicios)
        return {
            'total_usd': float(total_usd),
            'cantidad_servicios': len(campania_servicios)
        }


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
    reprogramado_por_nombre = serializers.CharField(source='reprogramado_por.nombre', read_only=True)

    class Meta:
        model = Reserva
        fields = "__all__"
        read_only_fields = ["id", "codigo", "reprogramado_por_nombre", "numero_reprogramaciones", "fecha_reprogramacion", "created_at", "updated_at"]


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
        queryset=Servicio.objects.all(),
        source="servicio",
        write_only=True
    )
    campania = CampaniaSerializer(read_only=True)
    campania_id = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(),
        source="campania",
        write_only=True
    )

    class Meta:
        model = CampaniaServicio
        fields = [
            "id",
            "created_at",
            "updated_at",
            "servicio",
            "servicio_id",
            "campania",
            "campania_id",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        servicio = data.get("servicio")
        campania = data.get("campania")
        if CampaniaServicio.objects.filter(servicio=servicio, campania=campania).exists():
            raise serializers.ValidationError("Esta relación de servicio y campaña ya existe.")
        return data


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
        read_only_fields = ["id", "created_at", "updated_at"]


# =====================================================
# � HISTORIAL_REPROGRAMACION
# =====================================================
class HistorialReprogramacionSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(source='reserva.codigo', read_only=True)
    reprogramado_por_nombre = serializers.CharField(source='reprogramado_por.nombre', read_only=True)
    
    class Meta:
        model = HistorialReprogramacion
        fields = "__all__"
        read_only_fields = ["id", "reserva_codigo", "reprogramado_por_nombre", "created_at", "updated_at"]


# =====================================================
# ⚙️ CONFIGURACION_GLOBAL_REPROGRAMACION
# =====================================================
class ConfiguracionGlobalReprogramacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionGlobalReprogramacion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


# =====================================================
#  REPROGRAMACION
# =====================================================
class ReprogramacionSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(source='reserva.codigo', read_only=True)
    solicitado_por_nombre = serializers.CharField(source='solicitado_por.nombre', read_only=True)
    aprobado_por_nombre = serializers.CharField(source='aprobado_por.nombre', read_only=True)
    
    class Meta:
        model = Reprogramacion
        fields = "__all__"
        read_only_fields = ["id", "reserva_codigo", "solicitado_por_nombre", "aprobado_por_nombre", "created_at", "updated_at"]


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
