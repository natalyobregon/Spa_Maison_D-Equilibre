from django.urls import path
from apiApp import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
]