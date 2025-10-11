from django.urls import path
from .views import crear_backup, listar_backups, restaurar_backup, descargar_backup, eliminar_backup

urlpatterns = [
    path('crear/', crear_backup, name='crear_backup'),
    path('listar/', listar_backups, name='listar_backups'),
    path('restaurar/', restaurar_backup, name='restaurar_backup'),
     path('download/<str:filename>/', descargar_backup, name='descargar_backup'),
    path('delete/<str:filename>/', eliminar_backup, name='eliminar_backup'),
]
