from rest_framework import serializers
from .models import (
    Categoria, Servicio, Usuario, Campania, Cupon, Reserva, Visitante,
    ReservaVisitante, CampaniaServicio, Pago, ReglaReprogramacion, Reprogramacion
)

# =====================================================
# 🏷️ CATEGORIA
# =====================================================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🧍 USUARIO
# =====================================================
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🎯 CAMPAÑA
# =====================================================
class CampaniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campania
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🎟️ CUPON
# =====================================================
class CuponSerializer(serializers.ModelSerializer):
    campania = CampaniaSerializer(read_only=True)
    campania_id = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(), source='campania', write_only=True
    )

    class Meta:
        model = Cupon
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🏞️ SERVICIO
# =====================================================
class ServicioSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    proveedor = UsuarioSerializer(read_only=True)
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source='proveedor', write_only=True
    )

    class Meta:
        model = Servicio
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🧾 RESERVA
# =====================================================
class ReservaSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source='cliente', write_only=True
    )
    cupon = CuponSerializer(read_only=True)
    cupon_id = serializers.PrimaryKeyRelatedField(
        queryset=Cupon.objects.all(), source='cupon', write_only=True, allow_null=True
    )

    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 👥 VISITANTE
# =====================================================
class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🔗 RESERVA_VISITANTE
# =====================================================
class ReservaVisitanteSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source='reserva', write_only=True
    )
    visitante = VisitanteSerializer(read_only=True)
    visitante_id = serializers.PrimaryKeyRelatedField(
        queryset=Visitante.objects.all(), source='visitante', write_only=True
    )

    class Meta:
        model = ReservaVisitante
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🔗 CAMPAÑA_SERVICIO
# =====================================================
class CampaniaServicioSerializer(serializers.ModelSerializer):
    servicio = ServicioSerializer(read_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.all(), source='servicio', write_only=True
    )
    campania = CampaniaSerializer(read_only=True)
    campania_id = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(), source='campania', write_only=True
    )

    class Meta:
        model = CampaniaServicio
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 💳 PAGO
# =====================================================
class PagoSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source='reserva', write_only=True
    )

    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🔁 REGLA_REPROGRAMACION
# =====================================================
class ReglaReprogramacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaReprogramacion
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# =====================================================
# 🔄 REPROGRAMACION
# =====================================================
class ReprogramacionSerializer(serializers.ModelSerializer):
    reserva = ReservaSerializer(read_only=True)
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source='reserva', write_only=True
    )

    class Meta:
        model = Reprogramacion
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
