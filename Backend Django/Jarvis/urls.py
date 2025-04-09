from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("getModelInfo/", views.get_model_info, name="get_model_info"),
]
