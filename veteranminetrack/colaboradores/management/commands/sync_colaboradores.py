from django.core.management.base import BaseCommand
from colaboradores.tasks import sync_colaboradores


class Command(BaseCommand):
    help = "Sincroniza los colaboradores desde la API"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando sincronización de colaboradores...")
        sync_colaboradores()
        self.stdout.write(
            self.style.SUCCESS("Sincronización de colaboradores completada")
        )
