import os
import shutil
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from rest_framework.decorators import api_view
from datetime import datetime
import zipfile
from pathlib import Path
import traceback

# Importaciones de módulos internos
from .utils import BACKUP_DIR
from condominio.backups.restore_backup import restore_backup
from condominio.backups.upload_dropbox import (
    upload_to_dropbox,
    list_backups_dropbox,
    download_from_dropbox,
    get_dropbox_share_link
)
from condominio.backups.backup_full import run_backup


# ============================================================
# 🚀 CREAR BACKUP COMPLETO (POSTGRES + BACKEND + FIXTURES)
# ============================================================

@api_view(['POST'])
def crear_backup(request):
    """
    Crea un backup completo del sistema:
    - Incluye la base de datos PostgreSQL (usando DATABASE_URL)
    - Incluye el código backend (condominio, core, authz, config)
    - Incluye fixtures JSON
    - Sube el ZIP resultante a Dropbox y devuelve el enlace directo.
    """
    try:
        print("🚀 Iniciando creación de backup completo desde API...")

        # Parámetros opcionales
        include_backend = request.data.get('include_backend', True)
        include_db = request.data.get('include_db', True)
        db_type = request.data.get('db_type', 'postgres')

        # Ejecutar el proceso completo de backup
        run_backup(
            include_backend=include_backend,
            include_db=include_db,
            db_type=db_type
        )

        # Buscar el archivo ZIP más reciente
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith("full_backup_") and f.endswith(".zip")],
            key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)),
            reverse=True
        )

        if not backups:
            return JsonResponse({"error": "No se generó ningún archivo de backup."}, status=500)

        latest_backup = backups[0]
        dropbox_path = f"/backups/{latest_backup}"

        # Intentar generar enlace de Dropbox
        link = get_dropbox_share_link(latest_backup)

        print(f"✅ Backup generado: {latest_backup}")
        print(f"🔗 Enlace Dropbox: {link}")

        return JsonResponse({
            "message": "Backup completo generado y subido correctamente.",
            "backup_file": latest_backup,
            "dropbox_path": dropbox_path,
            "dropbox_link": link or "No disponible"
        })

    except Exception as e:
        print("❌ Error al crear backup:", e)
        traceback.print_exc()
        return JsonResponse({
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


# ============================================================
# 📋 LISTAR BACKUPS LOCALES
# ============================================================

@api_view(['GET'])
def listar_backups(request):
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
    return JsonResponse({'backups': backups})


# ============================================================
# ♻️ RESTAURAR BACKUP LOCAL
# ============================================================

def parse_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return default


@api_view(['POST'])
def restaurar_backup(request):
    backup_file = request.data.get('backup_file')
    if not backup_file:
        return JsonResponse({'error': 'Debe especificar backup_file'}, status=400)

    backup_path = Path(BACKUP_DIR) / backup_file
    if not backup_path.exists():
        return JsonResponse({'error': 'Backup no encontrado'}, status=400)

    restore_code = parse_bool(request.data.get('restore_code', True))
    restore_db = parse_bool(request.data.get('restore_db', True))

    result = restore_backup(
        backup_zip_path=backup_path,
        restore_code=restore_code,
        restore_db=restore_db
    )

    if 'error' in result:
        return JsonResponse(result, status=400)
    return JsonResponse(result)


# ============================================================
# ⬇️ DESCARGAR BACKUP LOCAL
# ============================================================

@api_view(['GET'])
def descargar_backup(request, filename):
    """
    Descarga un archivo de backup por nombre.
    Ejemplo: /api/backups/download/full_backup_20251011_095500.zip
    """
    file_path = Path(BACKUP_DIR) / filename
    if not file_path.exists() or not file_path.is_file():
        raise Http404("Backup no encontrado")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
    return response


# ============================================================
# 🗑️ ELIMINAR BACKUP LOCAL
# ============================================================

@api_view(['DELETE'])
def eliminar_backup(request, filename):
    """
    Elimina un archivo de backup por nombre.
    Ejemplo: /api/backups/delete/full_backup_20251011_095500.zip
    """
    file_path = Path(BACKUP_DIR) / filename
    if not file_path.exists() or not file_path.is_file():
        return JsonResponse({'error': 'Backup no encontrado'}, status=404)

    try:
        os.remove(file_path)
        return JsonResponse({'message': f'Backup {filename} eliminado correctamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# ☁️ FUNCIONES DE DROPBOX
# ============================================================

@api_view(['GET'])
def listar_backups_dropbox(request):
    """Lista los backups almacenados en Dropbox."""
    try:
        files = list_backups_dropbox()
        return JsonResponse({'backups': files})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def restaurar_desde_dropbox(request):
    """
    Restaura un backup alojado en Dropbox.
    Espera un JSON con:
    {
        "filename": "full_backup_20251011_180130.zip",
        "type": "total" | "base" | "backend" | "frontend"
    }
    """
    filename = request.data.get('filename')
    restore_type = request.data.get('type', 'total').lower()

    if not filename:
        return JsonResponse({'error': 'Debe especificar el nombre del backup (filename)'}, status=400)

    try:
        # Descargar desde Dropbox al directorio local
        local_path = download_from_dropbox(filename, BACKUP_DIR)

        # Determinar qué restaurar
        restore_code = restore_type in ('total', 'backend', 'frontend')
        restore_db = restore_type in ('total', 'base')

        result = restore_backup(Path(local_path), restore_code=restore_code, restore_db=restore_db)

        return JsonResponse({
            'message': f"Backup '{filename}' restaurado como tipo '{restore_type}'",
            'result': result
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
