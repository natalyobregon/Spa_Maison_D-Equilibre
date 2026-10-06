import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def manejador_excepciones(exc, context):
    """Errores conocidos de DRF: respuesta estándar. Cualquier otro error: 500 genérico en JSON,
    sin exponer detalles internos; el detalle queda solo en el registro del servidor."""
    response = exception_handler(exc, context)
    if response is None:
        logger.exception('Error no controlado en la API', exc_info=exc)
        return Response(
            {'detail': 'Error interno del servidor. Inténtalo nuevamente más tarde.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response