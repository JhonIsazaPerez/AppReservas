from django.urls import path
from . import views  # El punto (.) indica que views está en el mismo directorio

urlpatterns = [
    path('reservas/', views.reserva, name='reserva'),
]