# from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
   # path('fan', views.fanData, name='fanData'),
   # path('humidity', views.humidityData, name='humidityData'),
   path('device/<str:type>', views.deviceData, name='deviceData'),
]