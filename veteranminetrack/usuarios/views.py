import requests
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, viewsets
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,
    GroupSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    AdminPasswordChangeSerializer,
    GroupPermissionSerializer,
)

User = get_user_model()


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista personalizada para obtener el token JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


# Permiso personalizado para Administradores y Logística
class IsAdminOrLogistica(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a Administradores y Logística realizar ciertas acciones.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(
            name__in=["Administrador", "Logística"]
        ).exists()


# Vista para gestionar usuarios
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Aplica permisos personalizados solo en las acciones de creación, actualización o eliminación.
        """
        if self.action in ["create", "update", "destroy"]:
            return [IsAdminOrLogistica()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filtra el queryset según el grupo al que pertenece el usuario.
        Los usuarios de los grupos 'Colaborador', 'Campamentero' y 'Taxista' solo pueden ver sus propios datos.
        También se puede filtrar por el estado del usuario (activo/inactivo).
        """
        queryset = super().get_queryset()

        # Filtrar por estado activo/inactivo si se incluye en la solicitud
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        # Filtrar usuarios según el grupo
        if self.request.user.groups.filter(
            name__in=["Colaborador", "Campamentero", "Taxista"]
        ).exists():
            # Solo puede ver sus propios datos
            return queryset.filter(id=self.request.user.id)

        # Otros usuarios como Administradores o Logística pueden ver todos los usuarios
        return queryset


class GroupViewSet(viewsets.ModelViewSet):  # Cambiado a ModelViewSet
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]  # Permisos adecuados


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Verifica si se proporciona el id del usuario (para que admin/logística cambien la contraseña de otro usuario)
        user_id = request.data.get("user_id")

        # Si no se proporciona un user_id, se asume que el usuario autenticado está cambiando su propia contraseña
        if not user_id or request.user.id == int(user_id):
            # El propio usuario cambia su contraseña
            serializer = PasswordChangeSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"detail": "Contraseña actualizada correctamente."},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Para el administrador o logística que cambia la contraseña de otro usuario
        if request.user.groups.filter(name__in=["Administrador", "Logística"]).exists():
            try:
                user_to_change = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Usuario no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serializador especial para que admin/logística cambien la contraseña sin la antigua
            serializer = AdminPasswordChangeSerializer(
                user_to_change, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "detail": f"Contraseña actualizada correctamente para {user_to_change.email}."
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": "No tiene permiso para cambiar la contraseña de otros usuarios."
            },
            status=status.HTTP_403_FORBIDDEN,
        )


# Función para obtener el token de autenticación desde la API externa
def obtener_token():
    # Hacer la solicitud al endpoint de autenticación
    auth_data = {"username": settings.API_USERNAME, "password": settings.API_PASSWORD}
    response = requests.post(settings.API_AUTH_URL, data=auth_data)

    if response.status_code == 200:
        return response.json().get("access")  # Devolvemos solo el token de acceso
    else:
        raise Exception("Error al obtener el token de autenticación.")


# Función para consumir las APIs de colaboradores y taxistas y crear usuarios en el sistema
def crear_usuarios_desde_api():
    token = obtener_token()  # Obtenemos el token de acceso

    # Agregar el token a las cabeceras de la solicitud
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener colaboradores
    response_colaboradores = requests.get(
        settings.API_COLABORADORES_URL, headers=headers
    )
    if response_colaboradores.status_code == 200:
        colaboradores = response_colaboradores.json()
        for colaborador in colaboradores:
            crear_usuario_colaborador(colaborador)

    # Obtener taxistas
    response_taxistas = requests.get(settings.API_TAXISTAS_URL, headers=headers)
    if response_taxistas.status_code == 200:
        taxistas = response_taxistas.json()
        for taxista in taxistas:
            crear_usuario_taxista(taxista)


def crear_usuario_colaborador(colaborador_data):
    # Obtener los datos del colaborador
    rut = colaborador_data.get("rut_colaborador")
    nombres = colaborador_data.get("nombres")
    apellido_paterno = colaborador_data.get("apellido_paterno")
    apellido_materno = colaborador_data.get("apellido_materno")
    email = colaborador_data.get("email")
    password = rut  # Contraseña basada en el rut

    # Verificar si el usuario ya existe
    user = User.objects.filter(email=email).first()

    if user:
        print(f"El usuario con el email {email} ya existe. Omitiendo...")
        return

    # Asignar al grupo de Colaboradores
    group_colaborador = Group.objects.get(name="Colaborador")

    # Crear el usuario
    user = User.objects.create(
        rut=rut,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        email=email,
        password=password,  # Este se encriptará con el método set_password después
    )
    user.set_password(password)
    user.groups.add(group_colaborador)
    user.save()


def crear_usuario_taxista(taxista_data):
    # Obtener los datos del taxista
    rut = taxista_data.get("rut_conductor")
    nombres = taxista_data.get("nombres")
    apellido_paterno = taxista_data.get("apellido_paterno")
    apellido_materno = taxista_data.get("apellido_materno")
    email = taxista_data.get("email")
    password = rut  # Contraseña basada en el rut

    # Verificar si el usuario ya existe
    user = User.objects.filter(email=email).first()

    if user:
        print(f"El usuario con el email {email} ya existe. Omitiendo...")
        return

    # Asignar al grupo de Taxistas
    group_taxista = Group.objects.get(name="Taxista")

    # Crear el usuario
    user = User.objects.create(
        rut=rut,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        email=email,
        password=password,  # Este se encriptará con el método set_password después
    )
    user.set_password(password)
    user.groups.add(group_taxista)
    user.save()


class GroupPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupPermissionSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminOrLogistica,
    ]  # Solo Administradores o Logística
