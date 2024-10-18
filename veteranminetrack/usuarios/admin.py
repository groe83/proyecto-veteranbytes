from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.contrib.auth.models import Group


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Campos a mostrar en la lista de usuarios
    list_display = [
        "email",
        "rut",
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "is_staff",
    ]

    # Campos que estarán disponibles en el formulario de edición
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Información Personal",
            {"fields": ("rut", "nombres", "apellido_paterno", "apellido_materno")},
        ),
        (
            "Permisos",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups")},
        ),  # Asegúrate de incluir 'groups'
    )

    # Campos a utilizar al crear un nuevo usuario
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "rut",
                    "nombres",
                    "apellido_paterno",
                    "apellido_materno",
                    "password1",
                    "password2",
                    "is_staff",
                    "groups",
                ),
            },
        ),
    )

    # Configuración para el orden de los campos
    ordering = ("email",)

    # Filtrar por grupos en la lista de usuarios
    list_filter = ["is_staff", "groups"]

    # Campos a buscar en el administrador de usuarios
    search_fields = ["email", "nombres", "apellido_paterno", "apellido_materno", "rut"]
