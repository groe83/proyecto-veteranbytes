from rest_framework import serializers
from .models import Conductor, Vehiculo, AsignacionVehiculoConductor


# Serializador de Vehiculo
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "patente",
            "modelo",  # Esto incluye el nombre del modelo
            "marca",  # Campo de la marca directamente en el vehículo
            "color",  # Esto incluye el nombre del color
            "ano",
            "tipo_vehiculo",  # Esto incluye el tipo de vehículo como "Van", "Bus", etc.
            "capacidad_ocupantes",  # Capacidad de ocupantes del vehículo
            "numero_chasis",
            "numero_motor",
            "tipo_combustible",
        ]


# Serializador de Conductor
class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = [
            "id",
            "rut_conductor",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "telefono",
            "email",
            "licencia_conducir",
            "categoria_licencia",
            "fecha_vencimiento_licencia",
            "direccion",
        ]


# Serializador de AsignacionVehiculoConductor
class AsignacionVehiculoConductorSerializer(serializers.ModelSerializer):
    vehiculo = VehiculoSerializer(
        read_only=True
    )  # Relaciona con el serializador del vehículo
    id_vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(), source="vehiculo"
    )  # Para poder asignar el id del vehículo al crear la asignación
    conductor = ConductorSerializer(
        read_only=True
    )  # Relaciona con el serializador del conductor
    id_conductor = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(), source="conductor"
    )  # Para poder asignar el id del conductor al crear la asignación

    class Meta:
        model = AsignacionVehiculoConductor
        fields = [
            "id",
            "vehiculo",
            "id_vehiculo",
            "conductor",
            "id_conductor",
            "fecha_asignacion",
            "hora_asignacion",
            "fecha_fin",
            "hora_fin",
        ]
