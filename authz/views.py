from rest_framework.decorators import api_view
from rest_framework.response import Response

from authz.models import Rol
from .serializer import UserSerializer, UsuarioSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from condominio.models import Usuario  # importa tu modelo personalizado

# Create your views here.


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)

            try:
                perfil = user.perfil  # relación OneToOne con Usuario
                perfil_serializado = UsuarioSerializer(perfil).data
            except Usuario.DoesNotExist:
                perfil_serializado = None

            return Response(
                {
                    "token": token.key,
                    "user": perfil_serializado
                }
            )
        else:
            return Response(
                {"error": "Credenciales inválidas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except User.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )



@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        password = serializer.validated_data["password"]

        nombre = request.data.get("nombre")
        rubro = request.data.get("rubro")
        rol_id = request.data.get("rol")

        if not nombre or not rubro or not rol_id:
            return Response(
                {"error": "Los campos 'nombre', 'rubro' y 'rol' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        try:
            rol = Rol.objects.get(pk=rol_id)
        except Rol.DoesNotExist:
            return Response({"error": "El rol especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)

        perfil = Usuario.objects.create(
            user=user,
            nombre=nombre,
            rubro=rubro,
            rol=rol,
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UsuarioSerializer(perfil).data
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
def perfil(request):
    return Response({"message": "perfil successful"})


@api_view(["POST"])
def logout(request):
    # Invalida/elimina el token del usuario actual (si existe)
    token_key = None
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Token '):
        token_key = auth_header.split(' ', 1)[1]

    if token_key:
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)
