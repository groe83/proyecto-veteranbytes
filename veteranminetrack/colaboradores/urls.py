from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColaboradorViewSet, DireccionViewSet, ContratoViewSet

router = DefaultRouter()
router.register(r"", ColaboradorViewSet, basename="colaboradores")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<rut_colaborador>/direcciones/",
        DireccionViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="colaborador-direcciones-list-create",
    ),
    path(
        "<rut_colaborador>/direcciones/<int:id>/",
        DireccionViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="colaborador-direccion-detail",
    ),
    path(
        "<rut_colaborador>/contratos/",
        ContratoViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="colaborador-contratos-list-create",
    ),
    path(
        "<rut_colaborador>/contratos/<int:id>/",
        ContratoViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="colaborador-contrato-detail",
    ),
]
