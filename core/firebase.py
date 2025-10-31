import os
import firebase_admin
from firebase_admin import credentials


def iniciar_firebase():
    """Inicializa y devuelve la app firebase_admin.

    Busca la variable de entorno en español `RUTA_CUENTA_SERVICIO_FIREBASE` y
    como fallback `FIREBASE_SERVICE_ACCOUNT` para compatibilidad.
    """
    # Evitar reinicializar si ya está inicializada
    if firebase_admin._apps:
        return firebase_admin.get_app()

    ruta = os.getenv('RUTA_CUENTA_SERVICIO_FIREBASE') or os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if not ruta:
        raise RuntimeError('La variable de entorno RUTA_CUENTA_SERVICIO_FIREBASE o FIREBASE_SERVICE_ACCOUNT no está configurada')

    cred = credentials.Certificate(ruta)
    app = firebase_admin.initialize_app(cred)
    return app
