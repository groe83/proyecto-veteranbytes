from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="VeteranMineTrack API",
        default_version="v1",
        description="Documentación de la API del proyecto VeteranMineTrack",
        contact=openapi.Contact(email="contacto@veteranminetrack.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # Cambia a True si quieres que Swagger sea público
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/", include("usuarios.urls")),  # Incluir las URLs de la app de usuarios
    path("api/viajes/", include("viajes.urls")),  # Incluir las URLs de la app de viajes
    path(
        "api/colaboradores/", include("colaboradores.urls")
    ),  # Incluir las URLs de la app de colaboradores
    path("api/taxista/", include("taxista.urls")),  # Incluir las URLs de la app taxista
    path("", RedirectView.as_view(url="/swagger/", permanent=True)),
]
