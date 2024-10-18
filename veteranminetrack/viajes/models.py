from django.db import models
from django.conf import settings
from colaboradores.models import Colaborador  # Importar modelo de Colaborador
from taxista.models import (
    Vehiculo,
    Conductor,
)  # Importar modelo Vehiculo desde la app taxista
from .validators import (
    validar_latitud,
    validar_longitud,
    validar_fecha_salida,
    validar_valor_no_negativo,
    validar_numero_pasajeros,
    validar_orden,
    validar_fecha_asignacion,
)
from django.core.exceptions import ValidationError
from django.utils import timezone


# Modelo Estado
class Estado(models.Model):
    nombre_estado = models.CharField(max_length=255)
    descripcion_estado = models.TextField()  # Campo de descripción para el estado
    entidad = models.CharField(
        max_length=50
    )  # Campo para asociar la entidad del estado

    def __str__(self):
        return self.nombre_estado


# Modelo Ruta
class Ruta(models.Model):
    descripcion_ruta = models.CharField(max_length=255)
    punto_inicial_latitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_latitud]
    )
    punto_inicial_longitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_longitud]
    )
    punto_final_latitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_latitud]
    )
    punto_final_longitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_longitud]
    )

    def __str__(self):
        return self.descripcion_ruta


# Modelo Viaje
class Viaje(models.Model):
    codigo_viaje = models.CharField(max_length=50)  # Obligatorio
    fecha_salida = models.DateField(validators=[validar_fecha_salida])  # Obligatorio
    hora_salida = models.TimeField()  # Obligatorio
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viajes_creados",
    )  # Obligatorio
    usuario_modificador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="viajes_modificados",
    )
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE)  # Obligatorio
    id_ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)  # Obligatorio
    id_vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        db_column="id_vehiculo",
        null=True,
        blank=True,
    )
    id_conductor = models.ForeignKey(
        Conductor,  # Cambiado a Conductor
        on_delete=models.CASCADE,
        db_column="id_conductor",
        null=True,
        blank=True,
    )
    punto_partida = models.CharField(max_length=255, null=True, blank=True)
    punto_destino = models.CharField(max_length=255, null=True, blank=True)
    numero_pasajeros = models.IntegerField(
        validators=[validar_numero_pasajeros], null=True, blank=True
    )
    kilometros = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[validar_valor_no_negativo],
        null=True,
        blank=True,
    )
    valor_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_valor_no_negativo],
        null=True,
        blank=True,
    )
    estado_inicio_real = models.TimeField(null=True, blank=True)
    estado_fin_real = models.TimeField(null=True, blank=True)
    motivo_cancelacion = models.CharField(max_length=255, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    id_viaje_anterior = models.BigIntegerField(null=True, blank=True)
    tarifa_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_valor_no_negativo],
        null=True,
        blank=True,
    )
    peajes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_valor_no_negativo],
        null=True,
        blank=True,
    )
    tarifa_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_valor_no_negativo],
        null=True,
        blank=True,
    )
    codigo_qr = models.CharField(max_length=255, null=True, blank=True)
    confirmado_por_conductor = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        usuario_modificador = kwargs.pop("usuario_modificador", None)
        if usuario_modificador:
            print(f"Guardando usuario modificador con ID: {usuario_modificador.id}")
            self.usuario_modificador = usuario_modificador  # Asignación directa
        else:
            print("No se proporcionó usuario modificador.")
        super(Viaje, self).save(*args, **kwargs)

    def __str__(self):
        return self.codigo_viaje

    def clean(self):
        # Validar que la hora de salida no sea en el pasado si la fecha es hoy
        if (
            self.fecha_salida == timezone.now().date()
            and self.hora_salida < timezone.now().time()
        ):
            raise ValidationError(
                "La hora de salida no puede ser en el pasado si el viaje es hoy."
            )

        # Validar que la hora de fin real sea después de la hora de inicio real
        if (
            self.estado_fin_real
            and self.estado_inicio_real
            and self.estado_fin_real < self.estado_inicio_real
        ):
            raise ValidationError(
                "La hora de fin debe ser posterior a la hora de inicio."
            )


# Modelo RutaViaje
class RutaViaje(models.Model):
    id_viaje = models.ForeignKey(
        Viaje, on_delete=models.CASCADE, related_name="ruta_viaje"
    )
    latitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_latitud]
    )
    longitud = models.DecimalField(
        max_digits=25, decimal_places=15, validators=[validar_longitud]
    )
    orden = models.IntegerField(validators=[validar_orden])

    def __str__(self):
        return f"Punto {self.orden} del viaje {self.id_viaje.codigo_viaje}"

    def clean(self):
        super().clean()
        # Validar que las coordenadas no sean ambas 0
        if self.latitud == 0 and self.longitud == 0:
            raise ValidationError(
                "La latitud y la longitud no pueden ser ambas 0, ya que no representan una ubicación válida."
            )


class ViajeColaborador(models.Model):
    rut_colaborador = models.CharField(max_length=255)
    id_viaje = models.ForeignKey(
        "Viaje", on_delete=models.CASCADE, db_column="id_viaje"
    )
    hora_asignacion = models.DateTimeField()
    id_estado = models.ForeignKey(
        "Estado", on_delete=models.CASCADE, db_column="id_estado"
    )

    class Meta:
        unique_together = (("rut_colaborador", "id_viaje"),)
