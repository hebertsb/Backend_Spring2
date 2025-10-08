from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status

# Create your views here.


@api_view(["POST"])
def login(request):
    return Response({"message": "Login successful"})


@api_view(["POST"]) 
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        email = serializer.validated_data.get("email")
        password = serializer.validated_data["password"]

        # Crear usuario con contraseña encriptada
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def perfil(request):
    return Response({"message": "perfil successful"})


@api_view(["POST"])
def logout(request):
    return Response({"message": "Logout successful"})
