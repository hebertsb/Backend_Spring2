from django.urls import path
from .views import crear_backup, listar_backups, restaurar_backup, descargar_backup, eliminar_backup, listar_backups_dropbox, restaurar_desde_dropbox, descargar_desde_dropbox

urlpatterns = [
    path('crear/', crear_backup, name='crear_backup'),
    path('listar/', listar_backups, name='listar_backups'),
    path('restaurar/', restaurar_backup, name='restaurar_backup'),
     path('download/<str:filename>/', descargar_backup, name='descargar_backup'),
    path('delete/<str:filename>/', eliminar_backup, name='eliminar_backup'),
  
      # 🆕 Endpoints para Dropbox
    path('dropbox/listar/', listar_backups_dropbox, name='listar_backups_dropbox'),
    path('dropbox/restaurar/', restaurar_desde_dropbox, name='restaurar_desde_dropbox'),
    path('dropbox/descargar/<str:filename>/', descargar_desde_dropbox, name='descargar_desde_dropbox'),
    
]



