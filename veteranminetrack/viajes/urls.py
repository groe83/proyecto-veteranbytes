from rest_framework.routers import DefaultRouter
from .views import (
    EstadoViewSet,
    RutaViewSet,
    ViajeViewSet,
    RutaViajeViewSet,
    ViajeColaboradorViewSet,
)

router = DefaultRouter()
router.register(r"estados", EstadoViewSet, basename="estados")
router.register(r"rutas", RutaViewSet, basename="rutas")
router.register(r"viajes", ViajeViewSet, basename="viajes")
router.register(r"rutas-viajes", RutaViajeViewSet, basename="rutas-viajes")
router.register(
    r"viajes-colaboradores", ViajeColaboradorViewSet, basename="viajes-colaboradores"
)

urlpatterns = router.urls
