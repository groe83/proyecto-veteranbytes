from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConductorViewSet, VehiculoViewSet, AsignacionVehiculoConductorViewSet

router = DefaultRouter()
router.register(r"conductores", ConductorViewSet, basename="conductores")
router.register(r"vehiculos", VehiculoViewSet, basename="vehiculos")
router.register(
    r"asignaciones", AsignacionVehiculoConductorViewSet, basename="asignaciones"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "conductores/<rut_conductor>/asignaciones/",
        ConductorViewSet.as_view({"get": "asignaciones"}),
        name="conductor-asignaciones",
    ),
]
