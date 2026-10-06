from rest_framework.permissions import BasePermission, SAFE_METHODS

from usuarioApp.roles import obtener_rol, ADMINISTRADOR, TERAPEUTA


class AdminEscribeTodosLeen(BasePermission):
    """Cualquier usuario autenticado puede consultar; solo el Administrador puede modificar."""
    message = 'Solo los administradores pueden crear, modificar o eliminar este recurso.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return obtener_rol(request.user) == ADMINISTRADOR


class PermisoReservas(BasePermission):
    """Administrador y Cliente operan reservas; el Terapeuta solo consulta."""
    message = 'Tu perfil solo tiene permiso de consulta sobre las reservas.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return obtener_rol(request.user) != TERAPEUTA