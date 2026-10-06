from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    return Response({
        'mensaje': "API de Spa Maison D'Equilibre",
        'version': '1.0',
    })