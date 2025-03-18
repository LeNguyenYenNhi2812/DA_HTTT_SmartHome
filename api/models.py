from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
# class Person(AbstractUser):
#     SSN = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=255)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     role = models.CharField(max_length=10, choices=[("Admin", "Admin"), ("User", "User")])
#     address = models.TextField()
#     mail = models.EmailField()
#     phone = models.CharField(max_length=15)
#     date_of_birth = models.DateField(null=True, blank=True)

# # Room Model
# class Room(models.Model):
#     name = models.CharField(max_length=255)


# Device Model
# class Device(models.Model):
#     name = models.CharField(max_length=255)
#     type = models.CharField(max_length=100)
#     status = models.CharField(max_length=50)
#     brand = models.CharField(max_length=100)
    # room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="devices")

# # Sensor Model
# class Sensor(models.Model):
#     name = models.CharField(max_length=255)
#     type = models.CharField(max_length=100)
#     location = models.CharField(max_length=255)
#     status = models.CharField(max_length=50)
    
#     device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="sensors")
#     # ch thêm foreign key cho room

# # Session Model (for sensor activity logging)
# class Session(models.Model):
#     sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="sessions")
#     event_time = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50)
#     action = models.TextField()
#     type = models.CharField(max_length=100)

# # Schedule Model
# class Schedule(models.Model):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="schedules")
#     activation_time = models.DateTimeField()
#     deactivation_time = models.DateTimeField()
#     name = models.CharField(max_length=255)
#     description = models.TextField()
