from django.core.management.base import BaseCommand
from usuarios.views import crear_usuarios_desde_api


class Command(BaseCommand):
    help = "Sincroniza los usuarios desde la API de colaboradores y taxistas"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando sincronización de usuarios...")
        crear_usuarios_desde_api()
        self.stdout.write(self.style.SUCCESS("Sincronización completada con éxito"))
