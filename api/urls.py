# from django.contrib import admin
from django.urls import path, include # type: ignore
from . import views
urlpatterns = [
   # path('fan', views.fanData, name='fanData'),
   # path('humidity', views.humidityData, name='humidityData'),
   # path('device/<str:type>', views.deviceData, name='deviceData'),
   # path('sensor/<str:type>', views.sensorData, name='sensorData'),
   path('getRoomSensorData/<int:roomid>', views.getRoomSensorData, name='getRoomSensorData'),
   path('sensorDataTime/<int:roomid>', views.getRoomSensorDataTime, name='getRoomSensorDataTime'),
   path('createDevice', views.createDevice, name='createDevice'),
   path('postDeviceData', views.postDeviceData, name='postDeviceData'),
   path('postDeviceDataLED', views.postDeviceDataLED, name='postDeviceDataLED'),

   
   path('deleteDevice/<int:deviceid>', views.deleteDevice, name='deleteDevice'),
   path('getCommonValue/<int:deviceid>', views.getCommonValue, name='getCommonValue'),
   path('createSensor', views.createSensor, name='postSensorData'),
   path('runSensorLog', views.run_sensor_log, name='runSensorLog'),
   path('getNumberOfDevices/<int:houseid>', views.getNumberOfDevices, name='getNumberOfDevices'),
   path("getAllDevices/<int:houseid>", views.getAllDevices, name="getAllDevices"),
   path('getNumberDevicesInRoom/<int:roomid>', views.getNumberDevicesInRoom, name='getNumberDevicesInRoom'),
   path('getElectricity', views.getElectricity, name='getElectricity'),
   path('createHouse', views.createHouse, name='createHouse'),
   path('createRoom', views.createRoom, name='createRoom'),
   path('postDataInLogSensor', views.postDataInLogSensor, name='postDataInLogSensor'),
   path('getLogDevice/<int:deviceid>', views.getLogDevice, name='getLogDevice'),
   path('renameDevice/<int:deviceid>', views.renameDevice, name='renameDevice'),
]