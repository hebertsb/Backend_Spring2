import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from authz.models import Rol
from condominio.models import Usuario

# Crear rol y usuario
rol_c, _ = Rol.objects.get_or_create(nombre='Cliente')
u = User.objects.create_user(username='tmpcli', email='tmpcli@example.com', password='tmp')
perfil = Usuario.objects.create(user=u, nombre='Tmp', rol=rol_c)

client = APIClient()
client.force_authenticate(user=u)
resp = client.post('/api/tickets/', {'asunto':'a','descripcion':'d'}, format='json')
print('status', resp.status_code)
try:
    print('data', resp.json())
except Exception:
    print('content', resp.content)
