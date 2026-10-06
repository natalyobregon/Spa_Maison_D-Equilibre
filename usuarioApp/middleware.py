from django.contrib import messages

from .roles import obtener_rol, ADMINISTRADOR, TERAPEUTA, CLIENTE


class RestriccionPorRolMiddleware:
    """
    Restringe las áreas internas según el rol del usuario autenticado:
<<<<<<< HEAD
      /administrador/  -> solo Administrador
      /terapeuta/      -> Administrador y Terapeuta
=======
      /administrador/      -> solo Administrador
      /terapeuta/           -> Administrador y Terapeuta
      /usuario/reservas/    -> solo Cliente (agendar/ver/editar/cancelar citas)
      /usuario/perfil/      -> solo Cliente (perfil y resumen de cliente)
>>>>>>> 319e90c77a57cae8a1f0d1eafa3ec41119082ca8
    Las peticiones sin sesión las maneja @login_required de cada vista.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            rol = obtener_rol(user)
            ruta = request.path

            if ruta.startswith('/administrador/') and rol != ADMINISTRADOR:
                return self._denegar(request, user, rol)

            if ruta.startswith('/terapeuta/') and rol not in (ADMINISTRADOR, TERAPEUTA):
                return self._denegar(request, user, rol)

<<<<<<< HEAD
        return self.get_response(request)

    def _denegar(self, request, user, rol):
        # Import local para evitar importaciones circulares con views.py
        from usuarioApp.views import _redirect_by_role

        # El aviso solo se muestra al cliente, porque su panel sí muestra mensajes
        if rol == CLIENTE:
            messages.error(request, "No tienes permiso para acceder a esa sección.")
=======
            es_area_cliente = ruta.startswith('/usuario/reservas/') or ruta.startswith('/usuario/perfil/')
            if es_area_cliente and rol != CLIENTE:
                return self._denegar(request, user, rol)

        return self.get_response(request)

    def _denegar(self, request, user, rol):
        from usuarioApp.views import _redirect_by_role

        messages.error(request, "No tienes permiso para acceder a esa sección.")
>>>>>>> 319e90c77a57cae8a1f0d1eafa3ec41119082ca8

        return _redirect_by_role(user)