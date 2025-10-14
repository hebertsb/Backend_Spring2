#!/usr/bin/env python
"""
Test del endpoint usando Django shell
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from condominio.api import ReservaViewSet

def test_mis_reservas():
    print("🔍 Testing mis_reservas endpoint...")
    
    try:
        # Obtener el token y usuario
        token_obj = Token.objects.get(key='3aee2ad1484245488cd436453d90410aa72fd311')
        user = token_obj.user
        print(f"✅ User: {user.email}")
        
        # Crear una request simulada
        factory = RequestFactory()
        request = factory.get('/api/reservas/mis_reservas/')
        request.user = user
        
        # Crear instancia del ViewSet
        viewset = ReservaViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        
        # Llamar al método mis_reservas
        response = viewset.mis_reservas(request)
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mis_reservas()