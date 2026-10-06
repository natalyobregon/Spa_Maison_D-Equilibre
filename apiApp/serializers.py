from django.utils import timezone
from rest_framework import serializers

from adminApp.models import Terapia
from terapeutaApp.models import Terapeuta
from usuarioApp.models import Reserva
from usuarioApp.forms import HORAS_DISPONIBLES


# ---------- Mantenedor 1: Terapia ----------
class TerapiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terapia
        fields = ['id', 'nombre', 'precio', 'duracion', 'descripcion', 'imagen', 'creado']
        read_only_fields = ['id', 'creado']

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value


# ---------- Mantenedor 2: Terapeuta ----------
class TerapeutaPublicoSerializer(serializers.ModelSerializer):
    """Versión para el perfil Usuario: solo campos públicos (sin correo ni certificado)."""
    terapias = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Terapeuta
        fields = ['id', 'nombre', 'profesion', 'foto', 'terapias']
        read_only_fields = fields


class TerapeutaAdminSerializer(serializers.ModelSerializer):
    """Versión para el perfil Administrador: todos los campos, incluida información sensible."""

    class Meta:
        model = Terapeuta
        fields = ['id', 'nombre', 'profesion', 'correo', 'foto', 'certificado', 'terapias']
        read_only_fields = ['id']

    def validate_correo(self, value):
        return value.strip().lower()


# ---------- Transacción: Reserva ----------
class ReservaSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    terapia_nombre = serializers.CharField(source='terapia.nombre', read_only=True)
    terapeuta_nombre = serializers.CharField(source='terapeuta.nombre', read_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'usuario', 'terapia', 'terapia_nombre', 'terapeuta',
                  'terapeuta_nombre', 'fecha', 'hora', 'estado', 'observaciones', 'creado']
        read_only_fields = ['id', 'usuario', 'estado', 'creado']

    def validate_fecha(self, value):
        cambia = self.instance is None or value != self.instance.fecha
        if cambia and value < timezone.localdate():
            raise serializers.ValidationError('No puedes agendar una cita en una fecha que ya pasó.')
        return value

    def validate(self, attrs):
        inst = self.instance
        fecha = attrs.get('fecha', inst.fecha if inst else None)
        hora = attrs.get('hora', inst.hora if inst else None)
        terapia = attrs.get('terapia', inst.terapia if inst else None)
        terapeuta = attrs.get('terapeuta', inst.terapeuta if inst else None)
        usuario = inst.usuario if inst else self.context['request'].user
        errores = {}

        if hora and hora.strftime('%H:%M') not in HORAS_DISPONIBLES:
            errores['hora'] = 'Elige una hora dentro del horario de atención (9:00 a 17:00).'

        if terapeuta and terapia and not terapeuta.terapias.filter(pk=terapia.pk).exists():
            errores['terapeuta'] = f'{terapeuta.nombre} no realiza "{terapia.nombre}".'

        if fecha and hora and 'hora' not in errores:
            ahora = timezone.localtime()
            cambia = inst is None or fecha != inst.fecha or hora != inst.hora
            if cambia and fecha == ahora.date() and hora <= ahora.time():
                errores['hora'] = 'Esa hora ya pasó. Elige una hora posterior a la actual.'
            else:
                ocupadas = Reserva.objects.filter(fecha=fecha, hora=hora).exclude(estado='CANCELADA')
                if inst:
                    ocupadas = ocupadas.exclude(pk=inst.pk)
                if terapeuta and ocupadas.filter(terapeuta=terapeuta).exists():
                    errores['hora'] = f'{terapeuta.nombre} ya tiene una cita en ese horario.'
                elif ocupadas.filter(usuario=usuario).exists():
                    errores['hora'] = 'Ya existe otra cita agendada en ese mismo horario.'

        if errores:
            raise serializers.ValidationError(errores)
        return attrs