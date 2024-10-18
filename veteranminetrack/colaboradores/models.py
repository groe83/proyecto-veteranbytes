from django.db import models
from .validators import (
    validar_rut,
    validar_fecha_nacimiento,
    validar_telefono,
    validar_ano_titulacion,
    validar_sueldo,
    validar_fecha_ingreso,
    validar_nombre_apellido,
)


class Colaborador(models.Model):
    rut_colaborador = models.CharField(
        max_length=12, primary_key=True, validators=[validar_rut]
    )
    nombres = models.CharField(max_length=100, validators=[validar_nombre_apellido])
    apellido_paterno = models.CharField(
        max_length=100, validators=[validar_nombre_apellido]
    )
    apellido_materno = models.CharField(
        max_length=100, validators=[validar_nombre_apellido]
    )
    fecha_nacimiento = models.DateField(validators=[validar_fecha_nacimiento])
    email = models.EmailField()
    ano_titulacion = models.IntegerField(validators=[validar_ano_titulacion], null=True)
    situacion_laboral = models.CharField(
        max_length=255, null=True, blank=True, default="Activo"
    )

    telefono1 = models.CharField(max_length=15, validators=[validar_telefono])
    telefono2 = models.CharField(max_length=15, validators=[validar_telefono])
    estado_civil = models.CharField(max_length=50)
    prevision = models.CharField(max_length=50)
    afp = models.CharField(max_length=50)
    genero = models.CharField(max_length=50)
    profesion = models.CharField(max_length=100)
    formacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"


class Direccion(models.Model):
    direccion = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.CASCADE, related_name="direcciones"
    )
    es_principal = models.BooleanField(default=False)
    alias = models.CharField(max_length=50)

    def __str__(self):
        return self.direccion


class Contrato(models.Model):
    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.CASCADE, related_name="contratos"
    )
    area = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=100)
    motivo_contrato = models.CharField(max_length=100)
    sueldo_liquido = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_sueldo]
    )
    sueldo_bruto = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_sueldo]
    )
    no_imponibles = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_sueldo]
    )
    fecha_ingreso = models.DateField(validators=[validar_fecha_ingreso])
    jornada_trabajo = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)
    observaciones = models.TextField(null=True, blank=True)
    turno = models.CharField(
        max_length=20,  # Cambiado a 20
        null=True,
        blank=True,
        choices=[
            ("7x7", "Turno 7x7"),
            ("10x10", "Turno 10x10"),
            ("4x4", "Turno 4x4"),
            ("5x2", "Turno 5x2"),
            ("N/A", "Sin turno"),
        ],  # Opciones agregadas
    )

    def __str__(self):
        return f"Contrato de {self.colaborador}"
