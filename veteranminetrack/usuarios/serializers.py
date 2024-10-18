from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate

User = get_user_model()


# Serializador para el login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Verificar credenciales
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError(
            "Las credenciales son incorrectas o el usuario no está activo."
        )


class UserSerializer(serializers.ModelSerializer):
    # Este campo será usado para GET y PUT/POST
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "rut",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "email",
            "is_active",
            "password",
            "groups",  # Manejo de los grupos (tanto para GET como PUT/POST)
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},  # Ocultar el password
            "email": {"required": True},
        }

    def get_groups(self, obj):
        """
        Retorna un array con la representación de los grupos en GET (id y nombre).
        """
        return [{"id": group.id, "name": group.name} for group in obj.groups.all()]

    def to_internal_value(self, data):
        """
        Modifica el comportamiento para aceptar solo los IDs en PUT/POST
        """
        groups_data = data.pop("groups", None)
        validated_data = super().to_internal_value(data)

        if groups_data:
            groups = Group.objects.filter(id__in=groups_data)
            validated_data["groups"] = groups

        return validated_data

    def create(self, validated_data):
        # Extraer la contraseña antes de la creación del usuario
        password = validated_data.pop("password", None)
        groups_data = validated_data.pop("groups", None)

        # Crear el usuario sin la contraseña (se encripta después)
        user = User.objects.create(**validated_data)

        # Generar una contraseña automática basada en el nombre si no se proporcionó una
        if password:
            user.set_password(password)
        else:
            user.set_password(
                validated_data["nombres"]
            )  # Contraseña basada en el nombre

        # Validar que se asigna al menos un grupo al usuario
        if groups_data is None or len(groups_data) == 0:
            raise serializers.ValidationError(
                "El usuario debe tener al menos un rol asignado."
            )

        # Asignar los grupos al usuario
        user.groups.set(groups_data)

        user.save()
        return user

    def update(self, instance, validated_data):
        # Sobrescribir update para manejar el cambio de contraseña si se incluye
        password = validated_data.pop("password", None)

        # Validar si se están actualizando los grupos (roles)
        groups_data = validated_data.pop("groups", None)

        # Actualizar los demás campos del usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Si se proporcionó una nueva contraseña, hashearla antes de guardarla
        if password:
            instance.set_password(password)

        # Si se envían roles (grupos), actualizarlos
        if groups_data is not None:
            if len(groups_data) == 0:
                raise serializers.ValidationError(
                    "El usuario debe tener al menos un rol asignado."
                )

            # Actualizar los grupos
            instance.groups.set(groups_data)

        instance.save()
        return instance


# Serializador para que el usuario cambie su propia contraseña
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña antigua no es correcta.")
        return value

    def validate_new_password(self, value):
        # Aquí puedes agregar validaciones adicionales para la nueva contraseña
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()


# Serializador para que el admin o logística cambien la contraseña de otro usuario
class AdminPasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_new_password(self, value):
        # Aquí puedes agregar validaciones adicionales para la nueva contraseña
        return value

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()


# Serializador del grupo
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name"]  # Muestra tanto el ID como el nombre del permiso


class GroupPermissionSerializer(serializers.ModelSerializer):
    # Utilizamos el PermissionSerializer para devolver el nombre del permiso en lugar del ID
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]

    def update(self, instance, validated_data):
        # Extraemos los permisos del grupo
        permissions = validated_data.pop("permissions", None)

        # Actualizamos los demás campos del grupo
        instance = super().update(instance, validated_data)

        if permissions is not None:
            # Si se incluyen permisos, actualizamos los permisos del grupo
            instance.permissions.set(permissions)

        return instance
