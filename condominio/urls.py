from django.urls import path, include
from rest_framework import routers

from authz.api import RolViewSet
from .api import (
    CategoriaViewSet, ServicioViewSet, UsuarioViewSet, CampaniaViewSet, PaqueteViewSet,
    CuponViewSet, ReservaViewSet, VisitanteViewSet, ReservaVisitanteViewSet,
    CampaniaServicioViewSet, PagoViewSet, ReglaReprogramacionViewSet,
    HistorialReprogramacionViewSet, ConfiguracionGlobalReprogramacionViewSet,
    ReprogramacionViewSet, TicketViewSet, TicketMessageViewSet, NotificacionViewSet,
    PerfilUsuarioViewSet, SoportePanelViewSet,
    # Endpoints de reportes
    reporte_ventas_general, reporte_clientes, reporte_productos, 
    reporte_por_voz, estadisticas_dashboard
)
from .api import BitacoraViewSet

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
router.register(r'perfil', PerfilUsuarioViewSet, basename='perfil')
router.register(r'soporte-panel', SoportePanelViewSet, basename='soporte-panel')

urlpatterns = router.urls + [
    path('backups/', include('condominio.backups.urls')),
    path('reservas-multiservicio/',
        __import__('condominio.api').api.ReservaConServiciosCreateView.as_view(),
        name='reservas-multiservicio'),
    path('confirmar-pago-multiservicio/',
        __import__('condominio.api').api.ConfirmarPagoReservaMultiservicioView.as_view(),
        name='confirmar-pago-multiservicio'),
    
    # =====================================================
    # 📊 REPORTES AVANZADOS (CU19)
    # =====================================================
    path('reportes/ventas/', reporte_ventas_general, name='reporte-ventas'),
    path('reportes/clientes/', reporte_clientes, name='reporte-clientes'),
    path('reportes/productos/', reporte_productos, name='reporte-productos'),
    path('reportes/voz/', reporte_por_voz, name='reporte-voz'),
    path('reportes/dashboard/', estadisticas_dashboard, name='dashboard'),
]
