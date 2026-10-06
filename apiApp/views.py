from django.db.models import RestrictedError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from adminApp.models import Terapia
from terapeutaApp.models import Terapeuta
from usuarioApp.models import Reserva
from usuarioApp.roles import obtener_rol, ADMINISTRADOR, TERAPEUTA

from apiApp.permissions import AdminEscribeTodosLeen, PermisoReservas
from apiApp.serializers import (
    TerapiaSerializer, TerapeutaPublicoSerializer,
    TerapeutaAdminSerializer, ReservaSerializer,
)


class EliminacionProtegidaMixin:
    """Si el registro tiene reservas (on_delete=RESTRICT), responde 409 en vez de un error 500."""

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            self.perform_destroy(obj)
        except RestrictedError:
            return Response(
                {'detail': f'No se puede eliminar "{obj}" porque tiene reservas asociadas. '
                           'Cancela o reasigna esas reservas antes de eliminarlo.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TerapiaViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Terapia.objects.all().order_by('id')
    serializer_class = TerapiaSerializer
    permission_classes = [AdminEscribeTodosLeen]


class TerapeutaViewSet(EliminacionProtegidaMixin, viewsets.ModelViewSet):
    queryset = Terapeuta.objects.prefetch_related('terapias').order_by('id')
    permission_classes = [AdminEscribeTodosLeen]

    def get_serializer_class(self):
        # El administrador ve todos los campos; el resto, solo los públicos
        if obtener_rol(self.request.user) == ADMINISTRADOR:
            return TerapeutaAdminSerializer
        return TerapeutaPublicoSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [PermisoReservas]

    def get_queryset(self):
        user = self.request.user
        reservas = Reserva.objects.select_related('usuario', 'terapia', 'terapeuta')
        rol = obtener_rol(user)

        if rol == ADMINISTRADOR:
            return reservas
        if rol == TERAPEUTA:
            ficha = Terapeuta.objects.filter(correo__iexact=user.email).first() if user.email else None
            return reservas.filter(terapeuta=ficha) if ficha else reservas.none()
        return reservas.filter(usuario=user)  # Cliente: solo las suyas

    def perform_create(self, serializer):
        # El dueño de la reserva siempre es quien hace la petición
        serializer.save(usuario=self.request.user)

    def destroy(self, request, *args, **kwargs):
        reserva = self.get_object()
        if reserva.estado != 'CANCELADA':
            return Response(
                {'detail': 'Solo se pueden eliminar reservas ya canceladas. Cancela la cita primero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        reserva.estado = 'CANCELADA'
        reserva.save()
        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        reserva.estado = 'CANCELADA'
        reserva.save()
        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=['post'], url_path='estado')
    def cambiar_estado(self, request, pk=None):
        if obtener_rol(request.user) != ADMINISTRADOR:
            raise PermissionDenied('Solo los administradores pueden cambiar el estado de una reserva.')
        reserva = self.get_object()
        nuevo = request.data.get('estado')
        validos = [codigo for codigo, _ in Reserva.ESTADOS]
        if nuevo not in validos:
            return Response(
                {'estado': f'Estado inválido. Opciones: {", ".join(validos)}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reserva.estado = nuevo
        reserva.save()
        return Response(self.get_serializer(reserva).data)