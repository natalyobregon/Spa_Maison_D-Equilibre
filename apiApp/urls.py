from rest_framework.routers import DefaultRouter

from apiApp import views

router = DefaultRouter()
router.register('terapias', views.TerapiaViewSet, basename='terapia')
router.register('terapeutas', views.TerapeutaViewSet, basename='terapeuta')
router.register('reservas', views.ReservaViewSet, basename='reserva')

urlpatterns = router.urls