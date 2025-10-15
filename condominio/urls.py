from django.urls import path, include
from rest_framework import routers

from authz.api import RolViewSet
from .api import (
    CategoriaViewSet, ServicioViewSet, UsuarioViewSet, CampaniaViewSet, PaqueteViewSet,
    CuponViewSet, ReservaViewSet, VisitanteViewSet, ReservaVisitanteViewSet,
    CampaniaServicioViewSet, PagoViewSet, ReglaReprogramacionViewSet,
    HistorialReprogramacionViewSet, ConfiguracionGlobalReprogramacionViewSet,
    ReprogramacionViewSet, TicketViewSet, TicketMessageViewSet, NotificacionViewSet,
    PerfilUsuarioViewSet, SoportePanelViewSet
)
from .api import BitacoraViewSet
from core.views import crear_pago, crear_checkout_session  # asegúrate que está bien importado

router = routers.DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'campanias', CampaniaViewSet)
router.register(r'paquetes', PaqueteViewSet, basename='paquete')
router.register(r'cupones', CuponViewSet)
router.register(r'reservas', ReservaViewSet)
router.register(r'visitantes', VisitanteViewSet)
router.register(r'reserva-visitantes', ReservaVisitanteViewSet)
router.register(r'campania-servicios', CampaniaServicioViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'reglas-reprogramacion', ReglaReprogramacionViewSet)
router.register(r'reprogramaciones', ReprogramacionViewSet)
router.register(r'rol', RolViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'ticket-messages', TicketMessageViewSet)
router.register(r'notificaciones', NotificacionViewSet)
router.register(r'historial-reprogramacion', HistorialReprogramacionViewSet)
router.register(r'configuracion-global-reprogramacion', ConfiguracionGlobalReprogramacionViewSet)
router.register(r'bitacora', BitacoraViewSet)
# 👤 APIs para perfiles y soporte
router.register(r'perfil', PerfilUsuarioViewSet, basename='perfil')
router.register(r'soporte-panel', SoportePanelViewSet, basename='soporte-panel')

urlpatterns = router.urls + [
    path('crear-pago/', crear_pago, name='crear-pago'),
    path('crear-checkout-session/', crear_checkout_session, name='crear-checkout-session'),

     path('backups/', include('condominio.backups.urls')),
  
]
