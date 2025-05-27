from django.urls import path
from . import views
from .views import coupon_list, apply_coupon

urlpatterns = [
    path('', views.ReservationListView.as_view(), name='reservation_list'),
    
    # Rutas para el proceso de creación en 3 pasos
    path('new/step1/', views.ReservationCreateStep1View.as_view(), name='reservation_create_step1'),
    path('new/step2/', views.ReservationCreateStep2View.as_view(), name='reservation_create_step2'),
    path('new/step2/time/', views.ReservationCreateStep2TimeView.as_view(), name='reservation_create_step2_time'),
    path('new/step3/', views.ReservationCreateStep3View.as_view(), name='reservation_create_step3'),
    path('coupons/', coupon_list, name='coupon_list'),
    path('apply_coupon/<int:coupon_id>/', apply_coupon, name='apply_coupon'),
    
    # Redirigir la ruta original de new/ al paso 1
    path('new/', views.ReservationCreateStep1View.as_view(), name='reservation_create'),
    
    # Rutas para el proceso de edición en 3 pasos
    path('<int:pk>/edit/step1/', views.ReservationUpdateStep1View.as_view(), name='reservation_update_step1'),
    path('<int:pk>/edit/step2/', views.ReservationUpdateStep2View.as_view(), name='reservation_update_step2'),
    path('<int:pk>/edit/step2/time/', views.ReservationUpdateStep2TimeView.as_view(), name='reservation_update_step2_time'),
    path('<int:pk>/edit/step3/', views.ReservationUpdateStep3View.as_view(), name='reservation_update_step3'),
    
    # Redirigir la ruta original de edit/ al paso 1
    path('<int:pk>/edit/', views.ReservationUpdateStep1View.as_view(), name='reservation_update'),
    
    # Rutas para ver detalles y cambiar estado (mantener como estaban)
    path('<int:pk>/', views.ReservationDetailView.as_view(), name='reservation_detail'),
    path('<int:pk>/confirm/', views.confirm_reservation, name='reservation_confirm'),
    path('<int:pk>/finish/', views.finish_reservation, name='reservation_finish'),
    path('<int:pk>/cancel/', views.cancel_reservation, name='reservation_cancel'),
    #path('api/<int:pk>/change-state/', views.api_change_state, name='api_change_state'),
]

