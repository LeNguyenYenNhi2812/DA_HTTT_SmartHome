# from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
   # path('fan', views.fanData, name='fanData'),
   # path('humidity', views.humidityData, name='humidityData'),
   # path('device/<str:type>', views.deviceData, name='deviceData'),
   # path('sensor/<str:type>', views.sensorData, name='sensorData'),
   path('sensorData/<int:roomid>', views.getRoomSensorData, name='getRoomSensorData'),
   path('createDevice', views.createDevice, name='createDevice'),
   path('postDeviceData', views.postDeviceData, name='postDeviceData'),
   path('postSensorData', views.postSensorData, name='postSensorData'),
   path('runSensorLog', views.run_sensor_log, name='runSensorLog'),

]