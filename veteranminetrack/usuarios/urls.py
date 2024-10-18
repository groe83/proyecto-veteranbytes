from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserViewSet,
    GroupViewSet,
    LoginView,
    PasswordChangeView,
    GroupPermissionViewSet,  # Importar la vista de permisos
)
from rest_framework.routers import DefaultRouter

# Crear el router para las vistas del CRUD de usuarios y los grupos
router = DefaultRouter()
router.register(r"usuarios", UserViewSet)
router.register(r"groups", GroupViewSet, basename="groups")
router.register(
    r"roles-permisos", GroupPermissionViewSet, basename="roles-permisos"
)  # Nueva ruta

# URLs para JWT, CRUD de usuarios y grupos
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),  # Sin 'api/'
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "cambio_contrasena/", PasswordChangeView.as_view(), name="cambio_contrasena"
    ),  # Nueva ruta para el cambio de contraseña
    path("", include(router.urls)),
]
