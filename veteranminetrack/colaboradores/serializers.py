from rest_framework import serializers
from .models import Colaborador, Direccion, Contrato


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ["id", "direccion", "comuna", "region", "es_principal", "alias"]


class ContratoSerializer(serializers.ModelSerializer):
    colaborador = serializers.CharField(source="colaborador.rut_colaborador")

    class Meta:
        model = Contrato
        fields = [
            "id",
            "colaborador",  # Incluye el campo del colaborador
            "area",
            "cargo",
            "tipo_contrato",
            "motivo_contrato",
            "sueldo_liquido",
            "sueldo_bruto",
            "no_imponibles",
            "fecha_ingreso",
            "jornada_trabajo",
            "horario",
            "observaciones",
            "turno",
        ]


class ColaboradorSerializer(serializers.ModelSerializer):
    direcciones = DireccionSerializer(many=True, required=False)
    contratos = ContratoSerializer(many=True, required=False)

    class Meta:
        model = Colaborador
        fields = [
            "rut_colaborador",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "email",
            "ano_titulacion",
            "situacion_laboral",
            "telefono1",
            "telefono2",
            "estado_civil",
            "prevision",
            "afp",
            "genero",
            "profesion",
            "formacion",
            "direcciones",
            "contratos",
        ]

    def create(self, validated_data):
        # Extraer datos anidados de direcciones y contratos
        direcciones_data = validated_data.pop("direcciones", [])
        contratos_data = validated_data.pop("contratos", [])

        # Crear el colaborador
        colaborador = Colaborador.objects.create(**validated_data)

        # Crear las direcciones asociadas
        for direccion in direcciones_data:
            Direccion.objects.create(colaborador=colaborador, **direccion)

        # Crear los contratos asociados
        for contrato in contratos_data:
            Contrato.objects.create(colaborador=colaborador, **contrato)

        return colaborador

    def update(self, instance, validated_data):
        # Actualización de direcciones y contratos anidados
        direcciones_data = validated_data.pop("direcciones", [])
        contratos_data = validated_data.pop("contratos", [])

        # Actualizar los datos básicos del colaborador
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Actualizar las direcciones asociadas
        for direccion in direcciones_data:
            Direccion.objects.update_or_create(colaborador=instance, defaults=direccion)

        # Actualizar los contratos asociados
        for contrato in contratos_data:
            Contrato.objects.update_or_create(colaborador=instance, defaults=contrato)

        return instance
