from django.core.management.base import BaseCommand
from taxista.tasks import sync_conductores


class Command(BaseCommand):
    help = "Sincroniza los taxistas desde la API"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando sincronización de taxistas...")
        sync_conductores()
        self.stdout.write(self.style.SUCCESS("Sincronización de taxistas completada"))
