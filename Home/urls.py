from django.urls import path
from Home.views import *

urlpatterns = [
    path("",Home.as_view(), name="home"),
]
