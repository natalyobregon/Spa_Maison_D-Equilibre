from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from adminApp.models import Terapia
from terapeutaApp.models import Terapeuta
from usuarioApp.models import Reserva

# Las claves (primer valor) son internas y sin acentos: sirven para cruzar las listas
# entre sí. Puedes cambiar nombres, precios y descripciones; si agregas o quitas una terapia,
# usa su clave en las listas de TERAPEUTAS y RESERVAS.
# (clave, nombre, precio, duración, descripción)
TERAPIAS = [
    ('masaje', 'Masaje', 35000, '60 minutos', 'Masaje corporal de relajación profunda.'),
    ('circuitos', 'Circuitos de agua', 28000, '45 minutos', 'Estimulación de puntos de presión.'),
    ('aroma', 'Aromaterapia', 30000, '50 minutos', 'Sesión con aceites esenciales para reducir el estrés.'),
    ('facial', 'Masaje facial', 32000, '60 minutos', 'Limpieza e hidratación facial.'),
    ('piedras', 'Piedras calientes', 45000, '75 minutos', 'Masaje con piedras volcánicas calientes.'),
]

# (clave, nombre, apellido, profesión, correo, claves de las terapias que realiza)
TERAPEUTAS = [
    ('nataly', 'Nataly', 'Obregón', 'Masoterapeuta', 'nataly.obregon@demo.spa.cl',
     ['masaje', 'piedras', 'aroma']),
    ('benjamin', 'Benjamín', 'Tabilo', 'Kinesiólogo', 'benjamin.tabilo@demo.spa.cl',
     ['masaje', 'circuitos']),
    ('visnupriya', 'Visnupriya', 'Amstein', 'Esteticista', 'visnupriya.amstein@demo.spa.cl',
     ['facial', 'aroma']),
]

# (usuario, nombre, apellido)
CLIENTES = [
    ('cliente.demo1', 'Ana', 'Pérez'),
    ('cliente.demo2', 'Luis', 'Vera'),
    ('cliente.demo3', 'Carla', 'Núñez'),
]

# (índice cliente, clave terapia, clave terapeuta, días desde hoy, hora, estado, observaciones)
RESERVAS = [
    (0, 'masaje', 'nataly', 3, '10:00', 'PENDIENTE', 'Dolor lumbar leve'),
    (0, 'aroma', 'visnupriya', 5, '15:00', 'CONFIRMADA', ''),
    (1, 'circuitos', 'benjamin', 2, '09:00', 'CONFIRMADA', ''),
    (1, 'piedras', 'nataly', 7, '11:00', 'PENDIENTE', ''),
    (2, 'facial', 'visnupriya', 4, '12:00', 'PENDIENTE', 'Piel sensible'),
    (2, 'masaje', 'benjamin', 1, '16:00', 'CANCELADA', ''),
    (0, 'circuitos', 'benjamin', 9, '14:00', 'CANCELADA', ''),
]


class Command(BaseCommand):
    help = ('Carga datos de demostración (terapias, terapeutas, clientes y reservas). '
            'Se puede ejecutar varias veces sin duplicar registros.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--password', required=True,
            help='Contraseña que tendrán las cuentas de demostración (terapeutas y clientes).',
        )

    def handle(self, *args, **options):
        password = options['password']
        try:
            validate_password(password)
        except ValidationError as e:
            raise CommandError('Contraseña no válida: ' + ' '.join(e.messages))

        with transaction.atomic():
            call_command('crear_roles', verbosity=0)
            grupo_terapeuta = Group.objects.get(name='Terapeuta')
            grupo_cliente = Group.objects.get(name='Cliente')

            terapias = {}
            for clave, nombre, precio, duracion, descripcion in TERAPIAS:
                terapia, _ = Terapia.objects.get_or_create(
                    nombre=nombre,
                    defaults={'precio': precio, 'duracion': duracion, 'descripcion': descripcion},
                )
                terapias[clave] = terapia

            terapeutas = {}
            for clave, nombre, apellido, profesion, correo, claves_terapias in TERAPEUTAS:
                ficha, _ = Terapeuta.objects.get_or_create(
                    correo=correo,
                    defaults={'nombre': f'{nombre} {apellido}', 'profesion': profesion},
                )
                ficha.terapias.add(*[terapias[c] for c in claves_terapias])
                usuario, creado = User.objects.get_or_create(
                    username=correo,
                    defaults={'email': correo, 'first_name': nombre, 'last_name': apellido},
                )
                if creado:
                    usuario.set_password(password)
                    usuario.save()
                usuario.groups.add(grupo_terapeuta)
                terapeutas[clave] = ficha

            clientes = []
            for username, nombre, apellido in CLIENTES:
                usuario, creado = User.objects.get_or_create(
                    username=username,
                    defaults={'email': f'{username}@demo.spa.cl',
                              'first_name': nombre, 'last_name': apellido},
                )
                if creado:
                    usuario.set_password(password)
                    usuario.save()
                usuario.groups.add(grupo_cliente)
                clientes.append(usuario)

            if Reserva.objects.filter(usuario__in=clientes).exists():
                self.stdout.write('Las reservas de demostración ya existen; no se vuelven a crear.')
            else:
                hoy = timezone.localdate()
                for idx, c_terapia, c_terapeuta, dias, hora, estado, obs in RESERVAS:
                    Reserva.objects.create(
                        usuario=clientes[idx], terapia=terapias[c_terapia],
                        terapeuta=terapeutas[c_terapeuta], fecha=hoy + timedelta(days=dias),
                        hora=hora, estado=estado, observaciones=obs,
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Datos de demostración listos: {Terapia.objects.count()} terapias, '
            f'{Terapeuta.objects.count()} terapeutas, {User.objects.count()} usuarios, '
            f'{Reserva.objects.count()} reservas.'))