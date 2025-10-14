#!/usr/bin/env python
"""
Script para probar el endpoint mis_reservas
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from condominio.models import Usuario, Reserva
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

def test_reservas_endpoint():
    print("🔍 Probando endpoint /api/reservas/mis_reservas/")
    
    # Buscar usuario con token 3aee2ad1484245488cd436453d90410aa72fd311
    try:
        token_obj = Token.objects.get(key='3aee2ad1484245488cd436453d90410aa72fd311')
        user = token_obj.user
        print(f"✅ Usuario encontrado: {user.email}")
        
        # Verificar si tiene perfil
        try:
            perfil = getattr(user, 'perfil', None)
            if perfil:
                print(f"✅ Perfil encontrado: {perfil.nombre} (ID: {perfil.id})")
                
                # Contar reservas
                reservas_count = Reserva.objects.filter(cliente=perfil).count()
                print(f"📊 Reservas en DB: {reservas_count}")
                
                if reservas_count > 0:
                    reserva = Reserva.objects.filter(cliente=perfil).first()
                    print(f"📅 Primera reserva: ID={reserva.id}, Estado={reserva.estado}")
                
            else:
                print("❌ Usuario no tiene perfil Usuario")
                
        except Exception as e:
            print(f"❌ Error accediendo al perfil: {e}")
    
    except Token.DoesNotExist:
        print("❌ Token no encontrado")
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reservas_endpoint()