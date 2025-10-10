# authz/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

from authz.models import Rol
from condominio.models import Usuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'
        read_only_fields = ['id', 'created_at']




class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer()  # Para mostrar detalles del rol

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'rubro', 'num_viajes', 'rol']