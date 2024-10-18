from rest_framework import permissions


class IsAdminOrLogistica(permissions.BasePermission):
    """
    Permiso personalizado que permite el acceso solo a los usuarios que son
    administradores o pertenecen al grupo 'Logística'.
    """

    def has_permission(self, request, view):
        # Solo permitir el acceso a administradores o usuarios en el grupo 'Logística'
        return bool(
            request.user
            and (
                request.user.is_staff
                or request.user.groups.filter(name="Logística").exists()
            )
        )
