from django.core.exceptions import ValidationError
from django.utils import timezone


def validar_latitud(value):
    if value < -90 or value > 90:
        raise ValidationError("La latitud debe estar entre -90 y 90 grados.")


def validar_longitud(value):
    if value < -180 or value > 180:
        raise ValidationError("La longitud debe estar entre -180 y 180 grados.")


# Validar que la fecha de salida no esté en el pasado
def validar_fecha_salida(value):
    if value < timezone.now().date():
        raise ValidationError("La fecha de salida no puede ser en el pasado.")


# Validar que los valores monetarios no sean negativos
def validar_valor_no_negativo(value):
    if value < 0:
        raise ValidationError("Este valor no puede ser negativo.")


# Validar que el número de pasajeros no sea mayor de 15
def validar_numero_pasajeros(value):
    if value > 15:
        raise ValidationError("El número de pasajeros no puede ser mayor de 15.")
    if value < 1:
        raise ValidationError("El número de pasajeros debe ser al menos 1.")


# Validar que el orden sea un número positivo
def validar_orden(value):
    if value <= 0:
        raise ValidationError("El orden debe ser un número positivo.")


def validar_fecha_asignacion(fecha):
    if fecha < timezone.now():
        raise ValidationError("La fecha de asignación no puede ser en el pasado.")
