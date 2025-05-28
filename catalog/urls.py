from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('catalog/pdf/', views.descargar_productos_pdf, name='descargar_productos_pdf'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)