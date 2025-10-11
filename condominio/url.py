from rest_framework import routers

from authz.api import RolViewSet
from .api import (
    CategoriaViewSet, ServicioViewSet, UsuarioViewSet, CampaniaViewSet,
    CuponViewSet, ReservaViewSet, VisitanteViewSet, ReservaVisitanteViewSet,
    CampaniaServicioViewSet, PagoViewSet, ReglaReprogramacionViewSet,
    ReprogramacionViewSet
)
from .api import TicketViewSet, TicketMessageViewSet, NotificacionViewSet
from .api import BitacoraViewSet

router = routers.DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'campanias', CampaniaViewSet)
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
router.register(r'bitacora', BitacoraViewSet)

urlpatterns = router.urls
