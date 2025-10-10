from django.urls import path
from .views import crear_backup, listar_backups, restaurar_backup

urlpatterns = [
    path('backup/crear/', crear_backup, name='crear_backup'),
    path('backup/listar/', listar_backups, name='listar_backups'),
    path('backup/restaurar/', restaurar_backup, name='restaurar_backup'),
]
