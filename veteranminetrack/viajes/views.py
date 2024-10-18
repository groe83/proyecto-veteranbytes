from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Estado, Ruta, Viaje, RutaViaje, ViajeColaborador, Colaborador
from .serializers import (
    EstadoSerializer,
    RutaSerializer,
    ViajeSerializer,
    RutaViajeSerializer,
    ViajeColaboradorSerializer,
)
from rest_framework.permissions import IsAuthenticated
from colaboradores.models import Colaborador
from django.db.utils import IntegrityError
from datetime import datetime
from django.utils.timezone import make_aware


# Permiso personalizado que permite solo a Administradores y Logística crear, actualizar y eliminar.
class IsAdminOrLogistica(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name__in=["Administrador", "Logística"]).exists():
            return True
        if view.action in [
            "list",
            "retrieve",
        ]:  # Permitir a todos ver los viajes y rutas
            return True
        return False


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]


class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]


class ViajeViewSet(viewsets.ModelViewSet):
    queryset = Viaje.objects.all()
    serializer_class = ViajeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def info_viaje(self, request, pk=None):
        """
        Muestra la información detallada de un viaje, incluyendo colaboradores y detalles de la ruta.
        """
        try:
            viaje = self.get_object()

            # Filtrar los colaboradores asociados al viaje
            colaboradores = ViajeColaborador.objects.filter(id_viaje=viaje)

            # Obtener la ruta relacionada al viaje
            ruta = viaje.id_ruta  # Relación con la ruta principal
            ruta_data = RutaSerializer(ruta).data  # Serializar la ruta

            # Serializar colaboradores y viaje
            colaboradores_data = ViajeColaboradorSerializer(
                colaboradores, many=True
            ).data
            viaje_data = ViajeSerializer(viaje).data

            return Response(
                {
                    "viaje": viaje_data,
                    "colaboradores": colaboradores_data,
                    "ruta": ruta_data,  # Incluir los detalles de la ruta
                },
                status=status.HTTP_200_OK,
            )

        except Viaje.DoesNotExist:
            return Response(
                {"error": "Viaje no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        """Guarda el usuario creador al crear un viaje."""
        serializer.save(usuario_creador=self.request.user)

    def perform_update(self, serializer):
        """Guarda el usuario modificador al actualizar un viaje."""
        serializer.save(usuario_modificador=self.request.user)

    @action(
        detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated]
    )
    def cancelar(self, request, pk=None):
        """
        Cancela un viaje con un motivo específico.
        """
        viaje = self.get_object()
        motivo = request.data.get("motivo_cancelacion")

        if not motivo:
            return Response(
                {"error": "Motivo de cancelación requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Asignar el motivo y cambiar el estado del viaje
        viaje.motivo_cancelacion = motivo

        # Asignar un estado de 'Cancelado' (Asegúrate que este estado exista en la base de datos)
        try:
            estado_cancelado = Estado.objects.get(nombre_estado="Cancelado")
        except Estado.DoesNotExist:
            return Response(
                {"error": "Estado 'Cancelado' no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        viaje.id_estado = estado_cancelado
        viaje.save()

        return Response(
            {"status": "Viaje cancelado exitosamente."},
            status=status.HTTP_200_OK,
        )


class RutaViajeViewSet(viewsets.ModelViewSet):
    queryset = RutaViaje.objects.all()
    serializer_class = RutaViajeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]


class ViajeColaboradorViewSet(viewsets.ModelViewSet):
    queryset = ViajeColaborador.objects.all()
    serializer_class = ViajeColaboradorSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Indicamos que el campo de búsqueda es 'rut_colaborador'
    lookup_field = "rut_colaborador"

    # Sobrescribir el método destroy para desactivar el borrado
    def destroy(self, request, *args, **kwargs):
        """
        Desactiva el método destroy - Eliminar un colaborador de todos los viajes está deshabilitado.
        """
        return Response(
            {
                "message": "La eliminación de un colaborador de todos los viajes está deshabilitada."
            },
            status=status.HTTP_403_FORBIDDEN,  # Código de estado 403 para denegar acceso a esta funcionalidad
        )

    def retrieve(self, request, rut_colaborador=None, *args, **kwargs):
        """GET - Recupera todos los registros de un colaborador por `rut_colaborador`."""
        viajes_colaborador = self.get_queryset().filter(rut_colaborador=rut_colaborador)

        if not viajes_colaborador.exists():
            return Response(
                {"detail": "No se encontraron viajes para este colaborador."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(viajes_colaborador, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="viaje/(?P<id_viaje>[^/.]+)")
    def viaje(self, request, id_viaje=None):
        """
        GET - Devuelve los colaboradores asociados a un viaje específico.
        """
        colaboradores = self.get_queryset().filter(id_viaje=id_viaje)

        if not colaboradores.exists():
            return Response(
                {"detail": "No se encontraron colaboradores para este viaje."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(colaboradores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], url_path="disponibilidad/(?P<id_viaje>[^/.]+)"
    )
    def disponibilidad(self, request, id_viaje=None):
        """
        GET - Devuelve los colaboradores disponibles y no disponibles para un viaje.
        """
        try:
            viaje = Viaje.objects.get(pk=id_viaje)

            # Obtener los colaboradores asignados al viaje
            colaboradores_asignados = ViajeColaborador.objects.filter(
                id_viaje=viaje
            ).values_list("rut_colaborador", flat=True)

            # Obtener todos los colaboradores
            todos_colaboradores = Colaborador.objects.all()

            # Separar los colaboradores disponibles y no disponibles
            disponibles = [
                {"rut_colaborador": col.rut_colaborador, "nombre": col.nombres}
                for col in todos_colaboradores
                if col.rut_colaborador not in colaboradores_asignados
            ]

            no_disponibles = [
                {"rut_colaborador": col.rut_colaborador, "nombre": col.nombres}
                for col in todos_colaboradores
                if col.rut_colaborador in colaboradores_asignados
            ]

            return Response(
                {
                    "viaje_id": id_viaje,
                    "disponibles": disponibles,
                    "no_disponibles": no_disponibles,
                },
                status=status.HTTP_200_OK,
            )

        except Viaje.DoesNotExist:
            return Response(
                {"error": "Viaje no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def asignar(self, request):
        colaboradores_data = request.data
        errores = []
        asignados = []

        for colaborador_data in colaboradores_data:
            rut_colaborador = colaborador_data.get("rut_colaborador")
            viaje_id = colaborador_data.get("id_viaje")
            estado_id = colaborador_data.get("id_estado")
            hora_asignacion = colaborador_data.get("hora_asignacion")

            if not all([rut_colaborador, viaje_id, estado_id, hora_asignacion]):
                errores.append(
                    f"Todos los campos son requeridos para el colaborador {rut_colaborador}."
                )
                continue

            try:
                # Convertir hora de asignación a objeto de tiempo
                hora_asignacion = make_aware(
                    datetime.strptime(hora_asignacion, "%Y-%m-%dT%H:%M:%S")
                )
                colaborador = Colaborador.objects.get(rut_colaborador=rut_colaborador)
                viaje = Viaje.objects.get(pk=viaje_id)

                # Validaciones
                if ViajeColaborador.objects.filter(
                    rut_colaborador=rut_colaborador, id_viaje=viaje
                ).exists():
                    errores.append(
                        f"El colaborador {rut_colaborador} ya está asignado a este viaje."
                    )
                    continue

                # Verifica las rutas asignadas al colaborador el mismo día
                viajes_existentes = ViajeColaborador.objects.filter(
                    rut_colaborador=rut_colaborador,
                    id_viaje__fecha_salida=viaje.fecha_salida,
                ).select_related("id_viaje__id_ruta")

                for viaje_existente in viajes_existentes:
                    if viaje_existente.id_viaje.id_ruta == viaje.id_ruta:
                        errores.append(
                            f"El colaborador {rut_colaborador} ya está asignado a esta ruta el mismo día."
                        )
                        break

                    if (
                        viaje_existente.id_viaje.id_ruta.punto_final_latitud
                        == viaje.id_ruta.punto_final_latitud
                    ):
                        errores.append(
                            f"El colaborador {rut_colaborador} ya tiene una asignación con destino a {viaje.id_ruta.descripcion_ruta} el {viaje.fecha_salida}."
                        )
                        break

                if errores:
                    continue

                # Crear la asignación
                ViajeColaborador.objects.create(
                    rut_colaborador=rut_colaborador,
                    id_viaje=viaje,
                    hora_asignacion=hora_asignacion,
                    id_estado_id=estado_id,
                )

                # Actualizar el número de pasajeros en el viaje
                viaje.numero_pasajeros = ViajeColaborador.objects.filter(
                    id_viaje=viaje
                ).count()
                viaje.save()

                # Marcar al colaborador como no disponible
                colaborador.disponible = False
                colaborador.save()

                asignados.append(rut_colaborador)

            except Colaborador.DoesNotExist:
                errores.append(f"Colaborador con RUT {rut_colaborador} no encontrado.")
            except Viaje.DoesNotExist:
                errores.append(f"Viaje con ID {viaje_id} no encontrado.")

        if errores:
            return Response(
                {
                    "status": "Asignación parcial completada.",
                    "asignados": asignados,
                    "errores": errores,
                },
                status=status.HTTP_207_MULTI_STATUS,
            )

        return Response(
            {
                "status": "Todos los colaboradores asignados correctamente.",
                "asignados": asignados,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path="viaje/(?P<id_viaje>[^/.]+)")
    def delete_colaborador_viaje(self, request, rut_colaborador=None, id_viaje=None):
        """
        Elimina un colaborador específico de un viaje específico.
        """
        try:
            colaborador = Colaborador.objects.get(rut_colaborador=rut_colaborador)
            viaje = Viaje.objects.get(pk=id_viaje)
            asignacion = ViajeColaborador.objects.get(
                rut_colaborador=colaborador.rut_colaborador, id_viaje=viaje
            )
            asignacion.delete()

            # Actualizar el número de pasajeros en el viaje
            viaje.numero_pasajeros = ViajeColaborador.objects.filter(
                id_viaje=viaje
            ).count()
            viaje.save()

            return Response(
                {"status": "Colaborador eliminado correctamente del viaje."},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Colaborador.DoesNotExist:
            return Response(
                {"error": "Colaborador no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Viaje.DoesNotExist:
            return Response(
                {"error": "Viaje no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )
        except ViajeColaborador.DoesNotExist:
            return Response(
                {"error": "Asignación no encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
