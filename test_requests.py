#!/usr/bin/env python
"""
Script para probar el endpoint mis_reservas con requests
"""
import requests

def test_endpoint():
    print("🔍 Probando endpoint con requests...")
    
    url = "http://localhost:8000/api/reservas/mis_reservas/"
    headers = {
        'Authorization': 'Token 3aee2ad1484245488cd436453d90410aa72fd311',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa:")
            print(response.json())
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está Django corriendo?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()