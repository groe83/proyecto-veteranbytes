import re
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


def validar_fecha_nacimiento(value):
    if value > timezone.now().date():
        raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")


def validar_rut(value):
    rut_pattern = re.compile(r"^\d{7,8}-[0-9Kk]$")  # Ejemplo: 12345678-9 o 12345678-K
    if not rut_pattern.match(value):
        raise ValidationError(
            "El formato del RUT no es válido. Debe ser de la forma '11111111-K'."
        )

    # Validar el dígito verificador
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


def validar_telefono(value):
    if not re.match(r"^\+?1?\d{9,15}$", value):
        raise ValidationError(
            "El número de teléfono no es válido. Debe tener entre 9 y 15 dígitos."
        )


def validar_ano_titulacion(value):
    current_year = datetime.date.today().year
    if value > current_year:
        raise ValidationError(
            f"El año de titulación no puede ser mayor que {current_year}."
        )


def validar_sueldo(value):
    if value < 0:
        raise ValidationError("El sueldo no puede ser negativo.")


def validar_fecha_ingreso(value):
    if value > timezone.now().date():
        raise ValidationError(
            "La fecha de ingreso no puede ser mayor a la fecha actual."
        )


# Validador personalizado para nombres y apellidos
def validar_nombre_apellido(value):
    # Aceptamos solo letras y espacios
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", value):
        raise ValidationError(
            "El nombre o apellido solo puede contener letras y espacios."
        )
