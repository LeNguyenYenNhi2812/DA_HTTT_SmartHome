from django.db import models # type: ignore
from django.contrib.auth.models import AbstractUser # type: ignore

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    ssn = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20, unique=True)
    
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ], default=' MEMBER')
    def __str__(self):
        return self.username

    

class House(models.Model):
    house_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

class HouseMember(models.Model):
    house_member_id = models.AutoField(primary_key=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, choices=[
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member')
    ])

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    level = models.IntegerField(null=True, blank=True) #note: ch bik

    def __str__(self):
        return f"Room {self.room_id}: {self.name} (House: {self.house_id})"

class Device(models.Model):
    device_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    brand = models.CharField(max_length=50, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    on_off = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)  # Thêm trường pinned vào model Device
    date_created = models.DateTimeField(auto_now_add=True)  # Thêm trường date_created vào model Device
    id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    
    def __str__(self):
        return f"Device {self.device_id}: {self.name} ({self.type}) in Room {self.room.name}"
class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    location = models.CharField(max_length=100, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class LogDevice(models.Model):
    log_device_id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    on_off = models.BooleanField(null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)

class LogSensor(models.Model):
    log_sensor_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    value = models.IntegerField(null=True, blank=True)

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    time = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    on_off = models.BooleanField(null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)

class PlanDevice(models.Model):
    plan_device_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    on_off = models.BooleanField(null=True, blank=True)

class PlanSensor(models.Model):
    plan_sensor_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    sign = models.CharField(max_length=10, null=True, blank=True)
    threshold = models.FloatField(null=True, blank=True)
    
class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    and_or = models.CharField(max_length=10, choices=[('AND', 'And'), ('OR', 'Or')])
    devices = models.ManyToManyField(Device, through='PlanDevice')
    sensors = models.ManyToManyField(Sensor, through='PlanSensor')
    