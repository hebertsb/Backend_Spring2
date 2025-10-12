# authz/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

from authz.models import Rol
from condominio.models import Usuario
from authz.models import UserRole
from django.contrib.auth.models import User

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
        fields = ['id', 'slug', 'nombre', 'descripcion', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(source='rol', queryset=Rol.objects.all(), write_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'rol', 'role_id', 'assigned_at', 'assigned_by']
        read_only_fields = ['id', 'rol', 'assigned_at', 'assigned_by']


class UserWithRolesSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'roles']

    def get_roles(self, obj):
        return list(obj.user_roles.values_list('rol__slug', flat=True))

    def get_full_name(self, obj):
        # Prefer User.first_name/last_name; si no existen, usar perfil.nombre (Usuario.nombre)
        first = obj.first_name or ''
        last = obj.last_name or ''
        if first or last:
            return f"{first} {last}".strip()
        # fallback to perfil.nombre if available
        perfil = getattr(obj, 'perfil', None)
        if perfil and getattr(perfil, 'nombre', None):
            return perfil.nombre
        return ''




class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer()  # Para mostrar detalles del rol

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'rubro', 'num_viajes', 'rol']


class PublicUsuarioSerializer(serializers.ModelSerializer):
    """Serializador público utilizado en respuestas de login/register/me.
    Devuelve el perfil unido con email/username del User y el rol como objeto.
    """
    rol = RolSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    telefono = serializers.CharField(read_only=True, allow_null=True)
    fecha_nacimiento = serializers.DateField(read_only=True, allow_null=True)
    genero = serializers.CharField(read_only=True, allow_null=True)
    documento_identidad = serializers.CharField(read_only=True, allow_null=True)
    pais = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombre', 'rol', 'num_viajes', 'telefono', 'fecha_nacimiento', 'genero', 'documento_identidad', 'pais']


class RegisterSerializer(serializers.Serializer):
    # Campos que el frontend envía según la guía (aceptamos variantes y las mapeamos)
    nombres = serializers.CharField(required=True, allow_blank=False)
    apellidos = serializers.CharField(required=False, allow_blank=True)
    # Aceptar alias que el frontend pueda enviar
    lastname = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    genero = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    documento_identidad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pais = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # campos específicos del backend existente (mantenemos compatibilidad)
    rol = serializers.IntegerField(required=True)
    rubro = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    # Nota: se elimina la validación de edad (fecha_nacimiento) por petición del frontend

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': ["Las contraseñas no coinciden."]
            })
        return attrs

    def create(self, validated_data):
        # Mapear campos del frontend al modelo existente sin tocar models.py
        nombres = validated_data.get('nombres')
        apellidos = validated_data.get('apellidos') or validated_data.get('lastname') or validated_data.get('last_name') or ''
        email = validated_data.get('email')
        password = validated_data.get('password')
        rol_id = validated_data.get('rol')
        rubro = validated_data.get('rubro', '')

        # Crear User
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombres
        user.last_name = apellidos
        user.save()

        # Buscar rol (el frontend debe proveer rol)
        try:
            rol = Rol.objects.get(pk=rol_id)
        except Rol.DoesNotExist:
            raise serializers.ValidationError({'rol': ["El rol especificado no existe."]})

        # Crear perfil Usuario
        nombre_completo = f"{nombres} {apellidos}".strip()
        perfil = Usuario.objects.create(
            user=user,
            nombre=nombre_completo,
            rubro=rubro,
            rol=rol,
            telefono=validated_data.get('telefono') or None,
            fecha_nacimiento=validated_data.get('fecha_nacimiento') or None,
            genero=validated_data.get('genero') or None,
            documento_identidad=validated_data.get('documento_identidad') or None,
            pais=validated_data.get('pais') or None,
        )

        # Nota: campos opcionales (telefono, fecha_nacimiento, genero, etc.) no se guardan
        # porque el modelo actual no los define. Si se necesitan, debemos extender el modelo
        # y crear migraciones.
        return perfil