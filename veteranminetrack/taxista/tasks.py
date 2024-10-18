import requests
from .models import Conductor, Vehiculo, AsignacionVehiculoConductor
from django.conf import settings

API_BASE_URL = "https://ryq-apis-1bf8cd7fef45.herokuapp.com/api"


def obtener_token():
    """
    Solicita el token de autenticación a la API externa.
    """
    auth_url = f"{API_BASE_URL}/token/"
    auth_data = {
        "username": settings.API_USERNAME,  # Configura esto en tus variables de entorno
        "password": settings.API_PASSWORD,
    }
    response = requests.post(auth_url, data=auth_data)
    if response.status_code == 200:
        return response.json().get("access")
    else:
        raise Exception("No se pudo obtener el token de autenticación")


def sync_conductores():
    """
    Sincroniza conductores, vehículos y asignaciones de la API externa.
    """
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Sincronizar Conductores
    response_conductores = requests.get(f"{API_BASE_URL}/conductor/", headers=headers)
    if response_conductores.status_code == 200:
        conductores_data = response_conductores.json()
        for conductor_data in conductores_data:
            Conductor.objects.update_or_create(
                rut_conductor=conductor_data["rut_conductor"],
                defaults={
                    "nombres": conductor_data["nombres"],
                    "apellido_paterno": conductor_data["apellido_paterno"],
                    "apellido_materno": conductor_data["apellido_materno"],
                    "fecha_nacimiento": conductor_data["fecha_nacimiento"],
                    "telefono": conductor_data.get("telefono", ""),
                    "email": conductor_data.get("email", ""),
                    "licencia_conducir": conductor_data["licencia_conducir"],
                    "categoria_licencia": conductor_data.get("categoria_licencia", ""),
                    "fecha_vencimiento_licencia": conductor_data.get(
                        "fecha_vencimiento_licencia", None
                    ),
                    "direccion": conductor_data.get("direccion", ""),
                },
            )

    # Sincronizar Vehículos
    response_vehiculos = requests.get(
        f"{API_BASE_URL}/conductor/vehiculo/", headers=headers
    )
    if response_vehiculos.status_code == 200:
        vehiculos_data = response_vehiculos.json()
        for vehiculo_data in vehiculos_data:
            Vehiculo.objects.update_or_create(
                patente=vehiculo_data["patente"],
                defaults={
                    "marca": vehiculo_data["marca"]["nombre"],
                    "modelo": vehiculo_data["modelo"]["nombre"],
                    "color": vehiculo_data["color"]["nombre"],
                    "ano": vehiculo_data["ano"],
                    "tipo_vehiculo": vehiculo_data["tipo_vehiculo"]["tipo"],
                    "capacidad_ocupantes": vehiculo_data["tipo_vehiculo"][
                        "capacidad_ocupantes"
                    ],
                    "numero_chasis": vehiculo_data.get("numero_chasis", ""),
                    "numero_motor": vehiculo_data.get("numero_motor", ""),
                    "tipo_combustible": vehiculo_data.get("tipo_combustible", ""),
                },
            )

    # Sincronizar Asignaciones de Vehículos
    response_asignaciones = requests.get(
        f"{API_BASE_URL}/conductor/asignacion/", headers=headers
    )
    if response_asignaciones.status_code == 200:
        asignaciones_data = response_asignaciones.json()
        for asignacion_data in asignaciones_data:
            vehiculo = Vehiculo.objects.get(
                patente=asignacion_data["vehiculo"]["patente"]
            )
            conductor = Conductor.objects.get(
                rut_conductor=asignacion_data["conductor"]["rut_conductor"]
            )

            AsignacionVehiculoConductor.objects.update_or_create(
                vehiculo=vehiculo,
                conductor=conductor,
                defaults={
                    "fecha_asignacion": asignacion_data["fecha_asignacion"],
                    "hora_asignacion": asignacion_data.get("hora_asignacion", None),
                    "fecha_fin": asignacion_data["fecha_fin"],
                    "hora_fin": asignacion_data.get("hora_fin", None),
                },
            )
