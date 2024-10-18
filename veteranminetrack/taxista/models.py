from django.db import models
from .validators import (
    validar_rut,
    validar_fecha_nacimiento,
    validar_telefono,
    validar_fecha_vencimiento_licencia,
    validar_fecha_fin,
    validar_nombres_apellidos,
    validar_email,
    validar_capacidad_ocupantes,
    validar_fecha_asignacion,
)


class Conductor(models.Model):
    rut_conductor = models.CharField(
        max_length=12, unique=True, validators=[validar_rut]
    )
    nombres = models.CharField(max_length=100, validators=[validar_nombres_apellidos])
    apellido_paterno = models.CharField(
        max_length=100, validators=[validar_nombres_apellidos]
    )
    apellido_materno = models.CharField(
        max_length=100, validators=[validar_nombres_apellidos]
    )
    fecha_nacimiento = models.DateField(validators=[validar_fecha_nacimiento])
    telefono = models.CharField(max_length=15, validators=[validar_telefono])
    email = models.EmailField(max_length=100, validators=[validar_email])
    licencia_conducir = models.CharField(max_length=20)
    categoria_licencia = models.CharField(max_length=10)
    fecha_vencimiento_licencia = models.DateField(
        validators=[validar_fecha_vencimiento_licencia]
    )
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"


class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    ano = models.IntegerField()
    tipo_vehiculo = models.CharField(max_length=100)
    capacidad_ocupantes = models.IntegerField(
        validators=[validar_capacidad_ocupantes]
    )  # Capacidad máxima de 15 ocupantes
    numero_chasis = models.CharField(max_length=50)
    numero_motor = models.CharField(max_length=50)
    tipo_combustible = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo} ({self.ano})"


class AsignacionVehiculoConductor(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="asignaciones",
        db_column="id_vehiculo",
    )
    conductor = models.ForeignKey(
        Conductor,
        on_delete=models.CASCADE,
        related_name="asignaciones",
        db_column="id_conductor",
    )
    fecha_asignacion = models.DateField(
        validators=[validar_fecha_asignacion]
    )  # Permite fechas futuras para asignación
    hora_asignacion = models.TimeField()  # Obligatoria
    fecha_fin = models.DateField(validators=[validar_fecha_fin])
    hora_fin = models.TimeField()  # Obligatoria

    def __str__(self):
        return f"Asignación de {self.conductor} al vehículo {self.vehiculo}"
