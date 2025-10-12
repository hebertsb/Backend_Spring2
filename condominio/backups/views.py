import os
import shutil
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from datetime import datetime
import zipfile
from .utils import BACKUP_DIR
from condominio.backups.restore_backup import restore_backup
from condominio.backups.utils import BACKUP_DIR
from pathlib import Path
from .upload_dropbox import upload_to_dropbox, list_backups_dropbox, download_from_dropbox


#BACKUP_DIR = os.path.join(settings.BASE_DIR, 'condominio', 'backups')
# Crear carpeta si no existe
#os.makedirs(BACKUP_DIR, exist_ok=True)

@api_view(['POST'])
#@permission_classes([IsAdminUser])
def crear_backup(request):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.zip'
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Ruta de la base de datos
    db_path = settings.DATABASES['default']['NAME']

    # Directorio raíz del proyecto (donde está manage.py)
    project_root = settings.BASE_DIR

    # Carpetas que queremos incluir explícitamente
    include_dirs = ['condominio', 'core', 'authz', 'config', 'scripts']

    # Carpetas a excluir dentro del recorrido
    exclude_dirs = ['venv', 'node_modules', 'backups', '__pycache__']

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Agregar base de datos
        if os.path.exists(db_path):
            zipf.write(db_path, os.path.basename(db_path))

        # Agregar archivos de las carpetas del backend
        for include_dir in include_dirs:
            include_path = os.path.join(project_root, include_dir)
            if not os.path.exists(include_path):
                continue

            for foldername, subfolders, filenames in os.walk(include_path):
                # Excluir carpetas no deseadas
                subfolders[:] = [f for f in subfolders if f not in exclude_dirs]

                for filename in filenames:
                    # Evitar incluir backups dentro de backups
                    if any(ex in foldername for ex in exclude_dirs):
                        continue
                    filepath = os.path.join(foldername, filename)
                    relpath = os.path.relpath(filepath, project_root)
                    zipf.write(filepath, relpath)

        # Agregar archivos raíz (manage.py, requirements.txt, etc.)
        for filename in os.listdir(project_root):
            if filename in ['manage.py', 'requirements.txt', '.env']:
                filepath = os.path.join(project_root, filename)
                zipf.write(filepath, os.path.basename(filepath))

    return JsonResponse({'message': 'Backup creado', 'backup_file': backup_name})


@api_view(['GET'])
#@permission_classes([IsAdminUser])
def listar_backups(request):
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
    return JsonResponse({'backups': backups})

@api_view(['POST'])
#@permission_classes([IsAdminUser])
def restaurar_backup(request):
    backup_file = request.data.get('backup_file')
    if not backup_file or not os.path.exists(os.path.join(BACKUP_DIR, backup_file)):
        return JsonResponse({'error': 'Backup no encontrado'}, status=400)

    backup_path = os.path.join(BACKUP_DIR, backup_file)

    # Extraer contenido
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        zipf.extractall(settings.BASE_DIR)

    return JsonResponse({'message': f'Backup {backup_file} restaurado correctamente'})

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

    # Leer opciones de restauración (acepta bool o string)
    restore_code = parse_bool(request.data.get('restore_code', True))
    restore_db = parse_bool(request.data.get('restore_db', True))

    # Ejecutar restore
    result = restore_backup(
        backup_zip_path=backup_path,
        restore_code=restore_code,
        restore_db=restore_db
    )

    if 'error' in result:
        return JsonResponse(result, status=400)
    return JsonResponse(result)


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


##### para dropbox ###
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

        # Ejecutar restauración
        result = restore_backup(Path(local_path), restore_code=restore_code, restore_db=restore_db)

        return JsonResponse({
            'message': f"Backup '{filename}' restaurado como tipo '{restore_type}'",
            'result': result
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)