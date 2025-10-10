from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserSerializer
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
            return Response(
                {
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
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

        user = User.objects.create_user(
             email=email, password=password
        )

        nombre = request.data.get("nombre")
        rubro = request.data.get("rubro")
        carnet = request.data.get("carnet")
        fecha_nacimiento = request.data.get("fecha_nacimiento")

        Usuario.objects.create(
            user=user,
            nombre=nombre,
            rubro=rubro,
            carnet=carnet,
            fecha_nacimiento=fecha_nacimiento,
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def perfil(request):
    return Response({"message": "perfil successful"})
