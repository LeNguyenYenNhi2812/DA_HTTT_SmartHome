# smart_home/models.py
from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    name = models.CharField(max_length=100)  # e.g., Lamp, Sprinkler
    type = models.CharField(max_length=50)   # e.g., Light, Irrigation
    status = models.BooleanField(default=False)  # On/Off
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.type})"

class Schedule(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()  # Time to turn on
    end_time = models.TimeField()    # Time to turn off
    days = models.CharField(max_length=50)  # e.g., "Mon,Tue,Wed"
    action = models.CharField(max_length=20, choices=[('ON', 'Turn On'), ('OFF', 'Turn Off')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule for {self.device.name} at {self.start_time}"

# smart_home/serializers.py
from rest_framework import serializers
from .models import Device, Schedule

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'type', 'status']

class ScheduleSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    device_id = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(), source='device', write_only=True
    )

    class Meta:
        model = Schedule
        fields = ['id', 'device', 'device_id', 'start_time', 'end_time', 'days', 'action']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data

# smart_home/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Device, Schedule
from .serializers import DeviceSerializer, ScheduleSerializer
from datetime import datetime, time
import pytz

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def schedule_form(request):
    devices = Device.objects.filter(user=request.user)
    if request.method == 'POST':
        device_id = request.POST.get('device')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        days = ','.join(request.POST.getlist('days'))
        action = request.POST.get('action')
        
        try:
            device = Device.objects.get(id=device_id, user=request.user)
            Schedule.objects.create(
                user=request.user,
                device=device,
                start_time=start_time,
                end_time=end_time,
                days=days,
                action=action
            )
            return redirect('schedule_form')
        except Device.DoesNotExist:
            return render(request, 'smart_home/schedule_form.html', {
                'devices': devices,
                'error': 'Invalid device selected.'
            })
        except Exception as e:
            return render(request, 'smart_home/schedule_form.html', {
                'devices': devices,
                'error': str(e)
            })
    
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, 'smart_home/schedule_form.html', {
        'devices': devices,
        'schedules': schedules
    })

# smart_home/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'schedules', views.ScheduleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('schedule/', views.schedule_form, name='schedule_form'),
]

# smart_home/tasks.py (Simulated schedule execution)
from django.utils import timezone
from .models import Schedule, Device
import logging

logger = logging.getLogger(__name__)

def execute_schedules():
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%a')

    schedules = Schedule.objects.filter(days__contains=current_day)
    for schedule in schedules:
        try:
            if schedule.start_time <= current_time <= schedule.end_time:
                device = schedule.device
                device.status = (schedule.action == 'ON')
                device.save()
                logger.info(f"Executed schedule {schedule.id} for {device.name}: {schedule.action}")
        except Exception as e:
            logger.error(f"Error executing schedule {schedule.id}: {str(e)}")