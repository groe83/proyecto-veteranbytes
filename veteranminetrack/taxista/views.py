from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conductor, Vehiculo, AsignacionVehiculoConductor
from .serializers import (
    ConductorSerializer,
    VehiculoSerializer,
    AsignacionVehiculoConductorSerializer,
)


# Vista para el modelo Conductor
class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    lookup_field = (
        "rut_conductor"  # Usamos el rut en lugar del id para buscar conductores
    )

    @action(detail=True, methods=["get"])
    def asignaciones(self, request, rut_conductor=None):
        """
        Endpoint personalizado para obtener las asignaciones de un conductor.
        """
        conductor = self.get_object()
        asignaciones = AsignacionVehiculoConductor.objects.filter(conductor=conductor)
        serializer = AsignacionVehiculoConductorSerializer(asignaciones, many=True)
        return Response(serializer.data)


# Vista para el modelo Vehiculo
# Vista para el modelo Vehiculo
class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    lookup_field = "id"  # Se manejarán por ID, no rut

    @action(detail=True, methods=["get"])
    def conductores(self, request, id=None):
        """
        Endpoint personalizado para obtener los conductores asignados a un vehículo.
        """
        vehiculo = self.get_object()
        asignaciones = AsignacionVehiculoConductor.objects.filter(vehiculo=vehiculo)
        conductores = [asignacion.conductor for asignacion in asignaciones]
        serializer = ConductorSerializer(conductores, many=True)
        return Response(serializer.data)


# Vista para el modelo AsignacionVehiculoConductor
class AsignacionVehiculoConductorViewSet(viewsets.ModelViewSet):
    queryset = AsignacionVehiculoConductor.objects.all()
    serializer_class = AsignacionVehiculoConductorSerializer
