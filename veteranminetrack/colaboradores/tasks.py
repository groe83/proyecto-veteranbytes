import requests
from .models import Colaborador, Direccion, Contrato
from django.conf import settings

API_BASE_URL = "https://ryq-apis-1bf8cd7fef45.herokuapp.com/api"


def obtener_token():
    """
    Solicita el token de autenticación a la API externa.
    """
    auth_url = f"{API_BASE_URL}/token/"
    auth_data = {
        "username": settings.API_USERNAME,  # Credenciales configuradas en settings
        "password": settings.API_PASSWORD,
    }
    response = requests.post(auth_url, data=auth_data)
    if response.status_code == 200:
        return response.json().get("access")
    else:
        raise Exception("No se pudo obtener el token de autenticación")


def sync_colaboradores():
    """
    Sincroniza los datos de colaboradores, direcciones y contratos desde la API externa.
    """
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener colaboradores desde la API externa
    response_colaboradores = requests.get(
        f"{API_BASE_URL}/colaborador/", headers=headers
    )
    if response_colaboradores.status_code == 200:
        colaboradores_data = response_colaboradores.json()

        for colaborador_data in colaboradores_data:
            # Truncar los campos que pueden exceder la longitud permitida
            telefono1 = colaborador_data.get("telefono1", "")[
                :15
            ]  # Máximo 15 caracteres
            telefono2 = colaborador_data.get("telefono2", "")[
                :15
            ]  # Máximo 15 caracteres

            # Crear o actualizar el colaborador
            colaborador, created = Colaborador.objects.update_or_create(
                rut_colaborador=colaborador_data["rut_colaborador"],
                defaults={
                    "nombres": colaborador_data["nombres"],
                    "apellido_paterno": colaborador_data["apellido_paterno"],
                    "apellido_materno": colaborador_data["apellido_materno"],
                    "fecha_nacimiento": colaborador_data["fecha_nacimiento"],
                    "email": colaborador_data.get("email", ""),
                    "ano_titulacion": colaborador_data.get("ano_titulacion", None),
                    "situacion_laboral": colaborador_data.get("situacion_laboral", ""),
                    "telefono1": telefono1,  # Aplicamos truncamiento
                    "telefono2": telefono2,  # Aplicamos truncamiento
                    "estado_civil": colaborador_data.get("estado_civil", ""),
                    "prevision": colaborador_data.get("prevision", ""),
                    "afp": colaborador_data.get("afp", ""),
                    "genero": colaborador_data.get("genero", ""),
                    "profesion": colaborador_data.get("profesion", ""),
                    "formacion": colaborador_data.get("formacion", ""),
                },
            )

            # Sincronizar las direcciones del colaborador
            direcciones_data = colaborador_data.get("direccion_set", [])
            for direccion_data in direcciones_data:
                Direccion.objects.update_or_create(
                    colaborador=colaborador,
                    direccion=direccion_data["direccion"],
                    defaults={
                        "comuna": direccion_data.get("comuna", ""),
                        "region": direccion_data.get("region", ""),
                        "es_principal": direccion_data.get("es_principal", False),
                        "alias": direccion_data.get("alias", "")[
                            :50
                        ],  # Truncar alias a 50 caracteres
                    },
                )

            # Sincronizar los contratos del colaborador
            contratos_data = colaborador_data.get("contrato_set", [])
            for contrato_data in contratos_data:
                Contrato.objects.update_or_create(
                    colaborador=colaborador,
                    defaults={
                        "area": contrato_data.get("area", ""),
                        "cargo": contrato_data.get("cargo", ""),
                        "tipo_contrato": contrato_data.get("tipo_contrato", ""),
                        "motivo_contrato": contrato_data.get("motivo_contrato", ""),
                        "sueldo_liquido": contrato_data.get("sueldo_liquido", 0),
                        "sueldo_bruto": contrato_data.get("sueldo_bruto", 0),
                        "no_imponibles": contrato_data.get("no_imponibles", 0),
                        "fecha_ingreso": contrato_data.get("fecha_ingreso", None),
                        "jornada_trabajo": contrato_data.get("jornada_trabajo", ""),
                        "horario": contrato_data.get("horario", ""),
                        "observaciones": contrato_data.get("observaciones", "")[
                            :255
                        ],  # Truncar observaciones a 255 caracteres
                        "turno": contrato_data.get("turno", ""),
                    },
                )
    else:
        raise Exception("Error al obtener los colaboradores de la API externa")
