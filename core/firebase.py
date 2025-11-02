import os
import json
import firebase_admin
from firebase_admin import credentials


def iniciar_firebase():
    """Inicializa y devuelve la app firebase_admin.

    Soporta dos modos:
    1. Local (desarrollo): Usa RUTA_CUENTA_SERVICIO_FIREBASE con ruta al archivo JSON
    2. Producción (Railway): Usa FIREBASE_CREDENTIALS_JSON con el contenido del JSON como string
    """
    # Evitar reinicializar si ya está inicializada
    if firebase_admin._apps:
        return firebase_admin.get_app()

    # Modo 1: Variable con contenido JSON (PRODUCCIÓN - Railway, Heroku, etc.)
    json_content = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if json_content:
        try:
            cred_dict = json.loads(json_content)
            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred)
            return app
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Error al parsear FIREBASE_CREDENTIALS_JSON: {e}')
    
    # Modo 2: Variable con ruta a archivo (DESARROLLO LOCAL)
    ruta = os.getenv('RUTA_CUENTA_SERVICIO_FIREBASE') or os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if ruta:
        if not os.path.exists(ruta):
            raise RuntimeError(f'El archivo de credenciales no existe: {ruta}')
        cred = credentials.Certificate(ruta)
        app = firebase_admin.initialize_app(cred)
        return app
    
    # Si no hay ninguna configuración
    raise RuntimeError(
        'No se encontró configuración de Firebase. Configura una de estas variables:\n'
        '  - FIREBASE_CREDENTIALS_JSON (recomendado para producción)\n'
        '  - RUTA_CUENTA_SERVICIO_FIREBASE (para desarrollo local)'
    )
