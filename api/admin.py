from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Plan, PlanDevice, PlanSensor, Device, House, Room, Sensor, LogDevice, LogSensor, Schedule

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'name', 'and_or')
    search_fields = ('name',)

@admin.register(PlanDevice)
class PlanDeviceAdmin(admin.ModelAdmin):
    list_display = ('plan', 'device', 'added_at')
    list_filter = ('plan',)

@admin.register(PlanSensor)
class PlanSensorAdmin(admin.ModelAdmin):
    list_display = ('plan', 'sensor', 'sign', 'threshold', 'added_at')
    list_filter = ('plan',)
    
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'type', 'room', 'on_off', 'pinned', 'date_created')
    list_filter = ('room', 'type', 'on_off', 'pinned')

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'name', 'type', 'location', 'value', 'room')
    list_filter = ('room', 'type')
    
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display =  ('house_id', 'location', 'admin')
    list_filter = ('house_id',)
    

