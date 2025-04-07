from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReservationListView.as_view(), name='reservation_list'),
    path('new/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('<int:pk>/', views.ReservationDetailView.as_view(), name='reservation_detail'),
    path('<int:pk>/edit/', views.ReservationUpdateView.as_view(), name='reservation_update'),
    path('<int:pk>/confirm/', views.confirm_reservation, name='reservation_confirm'),
    path('<int:pk>/finish/', views.finish_reservation, name='reservation_finish'),
    path('<int:pk>/cancel/', views.cancel_reservation, name='reservation_cancel'),
    path('api/<int:pk>/change-state/', views.api_change_state, name='api_change_state'),
]

