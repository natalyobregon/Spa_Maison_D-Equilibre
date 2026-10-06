from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView,
)

from apiApp import views

router = DefaultRouter()
router.register('terapias', views.TerapiaViewSet, basename='terapia')
router.register('terapeutas', views.TerapeutaViewSet, basename='terapeuta')
router.register('reservas', views.ReservaViewSet, basename='reserva')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
] + router.urls + [
    path('<path:ruta>', views.recurso_no_encontrado),
]