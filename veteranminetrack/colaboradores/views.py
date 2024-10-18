from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Colaborador, Direccion, Contrato
from .serializers import ColaboradorSerializer, DireccionSerializer, ContratoSerializer
from .permissions import IsAdminOrLogistica


class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]
    lookup_field = "rut_colaborador"  # Usamos rut_colaborador en lugar de id


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]

    def get_queryset(self):
        """
        Filtramos las direcciones basadas en el rut del colaborador.
        """
        rut_colaborador = self.kwargs.get("rut_colaborador")
        if rut_colaborador:
            return Direccion.objects.filter(
                colaborador__rut_colaborador=rut_colaborador
            )
        return (
            Direccion.objects.all()
        )  # Retorna todas las direcciones si no se pasa rut_colaborador

    lookup_field = (
        "id"  # Usamos el ID de la dirección para recuperar, actualizar o eliminar
    )


class ContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLogistica]

    def get_queryset(self):
        """
        Filtramos los contratos basados en el rut del colaborador.
        """
        rut_colaborador = self.kwargs.get("rut_colaborador")
        if rut_colaborador:
            return Contrato.objects.filter(colaborador__rut_colaborador=rut_colaborador)
        return (
            Contrato.objects.all()
        )  # Retorna todos los contratos si no se pasa rut_colaborador

    lookup_field = (
        "id"  # Usamos el ID del contrato para recuperar, actualizar o eliminar
    )
