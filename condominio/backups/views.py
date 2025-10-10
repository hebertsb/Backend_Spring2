import os
import shutil
from django.conf import settings
from django.http import JsonResponse, FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from datetime import datetime
import zipfile

BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

# Crear carpeta si no existe
os.makedirs(BACKUP_DIR, exist_ok=True)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def crear_backup(request):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.zip'
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Archivos de base de datos
    db_path = settings.DATABASES['default']['NAME']

    # Archivos del proyecto (opcional, excluir virtualenv y node_modules)
    project_root = settings.BASE_DIR
    exclude_dirs = ['venv', 'node_modules', 'backups']

    with zipfile.ZipFile(backup_path, 'w') as zipf:
        # Agregar base de datos
        zipf.write(db_path, os.path.basename(db_path))

        # Agregar archivos del proyecto
        for foldername, subfolders, filenames in os.walk(project_root):
            subfolders[:] = [f for f in subfolders if f not in exclude_dirs]
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                relpath = os.path.relpath(filepath, project_root)
                zipf.write(filepath, relpath)

    return JsonResponse({'message': 'Backup creado', 'backup_file': backup_name})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def listar_backups(request):
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
    return JsonResponse({'backups': backups})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def restaurar_backup(request):
    backup_file = request.data.get('backup_file')
    if not backup_file or not os.path.exists(os.path.join(BACKUP_DIR, backup_file)):
        return JsonResponse({'error': 'Backup no encontrado'}, status=400)

    backup_path = os.path.join(BACKUP_DIR, backup_file)

    # Extraer contenido
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        zipf.extractall(settings.BASE_DIR)

    return JsonResponse({'message': f'Backup {backup_file} restaurado correctamente'})
