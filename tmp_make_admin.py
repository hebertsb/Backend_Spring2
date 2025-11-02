"""
Script para hacer administrador a Luis Fernando
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

user = User.objects.get(email='luis@prueba.com')
print(f"Usuario: {user.username}")
print(f"Antes: is_staff={user.is_staff}")

user.is_staff = True
user.save()

print(f"Después: is_staff={user.is_staff}")
print("✅ Ahora Luis Fernando puede crear campañas")
