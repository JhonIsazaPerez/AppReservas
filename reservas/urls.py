from django.urls import path
from . import views  

urlpatterns = [
    path('guardarDatos/', views.guardarDatos, name='guardar_datos'),  # Ruta para guardar datos
    path('reserva/', views.reserva, name='reserva'),
    path('calendario/', views.calendario, name='calendario'),
    path('hora/', views.hora, name='hora'),
    path('infoUser/', views.infoUser, name='infoUser'),
    
]
