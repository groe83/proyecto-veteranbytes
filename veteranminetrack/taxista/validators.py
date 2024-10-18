import re
from django.core.exceptions import ValidationError
from django.utils import timezone


# Validador para RUT
def validar_rut(value):
    rut_pattern = re.compile(r"^\d{7,8}-[0-9Kk]$")
    if not rut_pattern.match(value):
        raise ValidationError(
            "El formato del RUT no es válido. Debe ser de la forma '11111111-K'."
        )

    rut, dv = value.split("-")
    rut = int(rut)
    dv = dv.upper()

    suma = 0
    multiplicador = 2
    for digit in reversed(str(rut)):
        suma += int(digit) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2

    expected_dv = 11 - (suma % 11)
    if expected_dv == 11:
        expected_dv = "0"
    elif expected_dv == 10:
        expected_dv = "K"
    else:
        expected_dv = str(expected_dv)

    if dv != expected_dv:
        raise ValidationError("El dígito verificador del RUT es incorrecto.")


# Validador para fechas de nacimiento
def validar_fecha_nacimiento(value):
    if value > timezone.now().date():
        raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")


# Validador para teléfonos
def validar_telefono(value):
    if not re.match(r"^\+?1?\d{9,15}$", value):
        raise ValidationError(
            "El número de teléfono no es válido. Debe tener entre 9 y 15 dígitos."
        )


# Validador para la fecha de vencimiento de la licencia de conducir
def validar_fecha_vencimiento_licencia(value):
    if value < timezone.now().date():
        raise ValidationError("La licencia de conducir no puede estar vencida.")


# Validador para la fecha de fin de asignación
def validar_fecha_fin(value):
    if value < timezone.now().date():
        raise ValidationError("La fecha de fin no puede ser anterior a hoy.")


# Validador para nombres y apellidos (solo letras y espacios)
def validar_nombres_apellidos(value):
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", value):
        raise ValidationError(
            "El nombre o apellido solo puede contener letras y espacios."
        )


# Validador para el correo electrónico
def validar_email(value):
    if not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$", value):
        raise ValidationError("El formato del correo electrónico es inválido.")


# Validador para la capacidad de ocupantes (máximo 15)
def validar_capacidad_ocupantes(value):
    if value > 15:
        raise ValidationError("La capacidad máxima de ocupantes es 15.")


def validar_fecha_asignacion(value):
    if value < timezone.now().date():
        raise ValidationError(
            "La fecha de asignación no puede ser anterior a la fecha actual."
        )
