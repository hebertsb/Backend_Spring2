"""
Script para verificar si el usuario actual es administrador
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from condominio.models import Usuario

# Token que estás usando según logs anteriores
# ed6199f2bf23b19a853e3ec0da5a2fe3b584e056...

# Buscar por el token
from rest_framework.authtoken.models import Token

print("=" * 70)
print("🔍 VERIFICANDO PERMISOS DE USUARIO")
print("=" * 70)

# Intentar con tokens recientes
tokens = Token.objects.all().order_by('-created')[:5]

for token in tokens:
    user = token.user
    print(f"\n👤 Usuario: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_active: {user.is_active}")
    print(f"   Token: {token.key[:20]}...")
    
    # Verificar si tiene perfil
    try:
        usuario = Usuario.objects.get(user=user)
        print(f"   Perfil: {usuario.nombre}")
        print(f"   Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
    except Usuario.DoesNotExist:
        print(f"   ⚠️  No tiene perfil de Usuario")
    
    # Determinar si puede crear campañas
    puede_crear = user.is_staff or user.is_superuser
    print(f"   {'✅' if puede_crear else '❌'} Puede crear campañas: {puede_crear}")

print("\n" + "=" * 70)
print("\n💡 Para crear campañas necesitas is_staff=True o is_superuser=True")
print("=" * 70)
