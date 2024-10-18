from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model  # Importa get_user_model
from .models import Estado, Ruta, Viaje, RutaViaje, ViajeColaborador
from taxista.models import Vehiculo, Conductor


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = "__all__"


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = "__all__"


class ViajeSerializer(serializers.ModelSerializer):
    # Campos ForeignKey para realizar GET y POST correctamente
    id_estado = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all())
    id_ruta = serializers.PrimaryKeyRelatedField(queryset=Ruta.objects.all())
    id_vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(), required=False, allow_null=True
    )
    id_conductor = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Viaje
        fields = [
            "id",
            "codigo_viaje",
            "fecha_salida",
            "hora_salida",
            "fecha_creacion",
            "fecha_modificacion",
            "punto_partida",
            "punto_destino",
            "numero_pasajeros",
            "kilometros",
            "valor_estimado",
            "estado_inicio_real",
            "estado_fin_real",
            "motivo_cancelacion",
            "observaciones",
            "id_viaje_anterior",
            "tarifa_base",
            "peajes",
            "tarifa_total",
            "codigo_qr",
            "confirmado_por_conductor",
            "usuario_creador",  # Este mostrará el email en el GET
            "usuario_modificador",  # Este mostrará el email o 'Sin modificaciones'
            "id_estado",
            "id_ruta",
            "id_vehiculo",
            "id_conductor",
        ]

    def to_representation(self, instance):
        """
        Personaliza la representación de los datos en el GET.
        """
        representation = super().to_representation(instance)

        # Formatear fechas y horas sin microsegundos
        if instance.fecha_creacion:
            representation["fecha_creacion"] = instance.fecha_creacion.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        if instance.fecha_modificacion:
            representation["fecha_modificacion"] = instance.fecha_modificacion.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        if instance.hora_salida:
            representation["hora_salida"] = instance.hora_salida.strftime("%H:%M:%S")

        # Cambiar las claves en la representación del GET
        representation["estado"] = (
            instance.id_estado.nombre_estado if instance.id_estado else None
        )
        representation["ruta"] = (
            {"id": instance.id_ruta.id, "nombre": instance.id_ruta.descripcion_ruta}
            if instance.id_ruta
            else None
        )
        representation["vehiculo"] = (
            instance.id_vehiculo.modelo if instance.id_vehiculo else None
        )

        # Cambiar el campo conductor para mostrar nombre completo en lugar del correo
        if instance.id_conductor:
            representation["conductor"] = str(
                instance.id_conductor
            )  # Usar el método __str__ del modelo Conductor
        else:
            representation["conductor"] = None

        representation["viaje_anterior"] = (
            instance.id_viaje_anterior.codigo_viaje
            if instance.id_viaje_anterior
            else None
        )

        # Reemplazar usuario_creador y usuario_modificador por emails
        representation["usuario_creador"] = (
            instance.usuario_creador.email if instance.usuario_creador else None
        )
        representation["usuario_modificador"] = (
            instance.usuario_modificador.email
            if instance.usuario_modificador
            else "Sin modificaciones"
        )

        # Eliminar los campos de ID innecesarios para el GET
        del representation["id_estado"]
        del representation["id_ruta"]
        del representation["id_vehiculo"]
        del representation["id_conductor"]
        del representation["id_viaje_anterior"]

        return representation


class RutaViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RutaViaje
        fields = "__all__"


class ViajeColaboradorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViajeColaborador
        fields = ["rut_colaborador", "id_viaje", "hora_asignacion", "id_estado"]

    def to_representation(self, instance):
        """
        Personaliza la salida para que en vez del ID del estado se devuelva el nombre.
        """
        representation = super().to_representation(instance)
        representation["estado"] = instance.id_estado.nombre_estado
        del representation["id_estado"]  # Eliminamos el ID del estado para el GET

        # Formatear hora_asignacion sin microsegundos
        if instance.hora_asignacion:
            representation["hora_asignacion"] = instance.hora_asignacion.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        return representation

    def validate_rut_colaborador(self, value):
        """
        Validar que el rut_colaborador exista en la base de datos.
        """
        if not Colaborador.objects.filter(rut_colaborador=value).exists():
            raise serializers.ValidationError("El rut_colaborador no existe.")
        return value
