from django.contrib import admin
from .models import User, House, HouseMember, Room, Device, Sensor, LogDevice, LogSensor, Schedule, Plan, PlanDevice, PlanSensor

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Custom User admin
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

# Register all models
admin.site.register(User, UserAdmin)
admin.site.register(House)
admin.site.register(HouseMember)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(LogDevice)
admin.site.register(LogSensor)
admin.site.register(Schedule)
admin.site.register(Plan)
admin.site.register(PlanDevice)
admin.site.register(PlanSensor)
