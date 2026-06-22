from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import Record


class Command(BaseCommand):
    help = 'Crea cuentas demo para demostrar los roles Admin, Organizador y Residente.'

    @transaction.atomic
    def handle(self, *args, **options):
        usuarios = [
            {
                'username': 'admin_demo',
                'email': 'admin_demo@demo.local',
                'password': 'Admin12345',
                'first_name': 'Admin',
                'last_name': 'Demo',
                'phone': '3000000001',
                'Address': 'Direccion demo',
                'city': 'Bogota',
                'state': 'Cundinamarca',
                'zipcode': '110111',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'organizador_demo',
                'email': 'organizador_demo@demo.local',
                'password': 'Organizador12345',
                'first_name': 'Organizador',
                'last_name': 'Demo',
                'phone': '3000000002',
                'Address': 'Direccion demo',
                'city': 'Bogota',
                'state': 'Cundinamarca',
                'zipcode': '110111',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'residente_demo',
                'email': 'residente_demo@demo.local',
                'password': 'Residente12345',
                'first_name': 'Residente',
                'last_name': 'Demo',
                'phone': '3000000003',
                'Address': 'Direccion demo',
                'city': 'Bogota',
                'state': 'Cundinamarca',
                'zipcode': '110111',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        for datos in usuarios:
            user, created = User.objects.update_or_create(
                username=datos['username'],
                defaults={
                    'email': datos['email'],
                    'first_name': datos['first_name'],
                    'last_name': datos['last_name'],
                    'is_staff': datos['is_staff'],
                    'is_superuser': datos['is_superuser'],
                    'is_active': True,
                }
            )
            user = User.objects.get(username=datos['username'])
            user.set_password(datos['password'])
            user.save()

            Record.objects.update_or_create(
                user=user,
                defaults={
                    'first_name': datos['first_name'],
                    'last_name': datos['last_name'],
                    'email': datos['email'],
                    'phone': datos['phone'],
                    'Address': datos['Address'],
                    'city': datos['city'],
                    'state': datos['state'],
                    'zipcode': datos['zipcode'],
                }
            )

            estado = 'creada' if created else 'actualizada'
            self.stdout.write(self.style.SUCCESS(f'Cuenta {estado}: {datos["username"]} / {datos["password"]}'))

        self.stdout.write(self.style.SUCCESS('Listo. Ingrese con cualquiera de las cuentas demo para ver su rol.'))
