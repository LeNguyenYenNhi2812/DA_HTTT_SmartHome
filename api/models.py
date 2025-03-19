# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove ` ` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    adminid = models.OneToOneField('Person', models.DO_NOTHING, db_column='adminid', primary_key=True)
    user_management = models.BooleanField(blank=True, null=True)
    permission_control = models.BooleanField(blank=True, null=True)

    class Meta:
         
        db_table = 'admin'


class Device(models.Model):
    deviceid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    value = models.CharField(max_length=20, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    configuration = models.JSONField(blank=True, null=True)

    class Meta:
         
        db_table = 'device'


class DeviceRoom(models.Model):
    deviceid = models.OneToOneField(Device, models.DO_NOTHING, db_column='deviceid', primary_key=True)  # The composite primary key (deviceid, roomid) found, that is not supported. The first column is selected.
    roomid = models.ForeignKey('Room', models.DO_NOTHING, db_column='roomid')

    class Meta:
         
        db_table = 'device_room'
        unique_together = (('deviceid', 'roomid'),)


class Person(models.Model):
    personid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    ssn = models.CharField(unique=True, max_length=20)
    username = models.CharField(unique=True, max_length=50)
    password = models.TextField()
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
         
        db_table = 'person'


class Room(models.Model):
    roomid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
         
        db_table = 'room'


class Schedule(models.Model):
    scheduleid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    activation_time = models.DateTimeField()
    deactivation_time = models.DateTimeField()
    personid = models.ForeignKey(Person, models.DO_NOTHING, db_column='personid', blank=True, null=True)

    class Meta:
         
        db_table = 'schedule'


class Sensor(models.Model):
    sensorid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True, null=True)
    value = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
         
        db_table = 'sensor'


class SensorDevice(models.Model):
    sensorid = models.OneToOneField(Sensor, models.DO_NOTHING, db_column='sensorid', primary_key=True)  # The composite primary key (sensorid, deviceid) found, that is not supported. The first column is selected.
    deviceid = models.ForeignKey(Device, models.DO_NOTHING, db_column='deviceid')

    class Meta:
         
        db_table = 'sensor_device'
        unique_together = (('sensorid', 'deviceid'),)


class SensorSession(models.Model):
    sensorid = models.OneToOneField(Sensor, models.DO_NOTHING, db_column='sensorid', primary_key=True)  # The composite primary key (sensorid, sessionid) found, that is not supported. The first column is selected.
    sessionid = models.ForeignKey('Session', models.DO_NOTHING, db_column='sessionid')

    class Meta:
         
        db_table = 'sensor_session'
        unique_together = (('sensorid', 'sessionid'),)


class Session(models.Model):
    sessionid = models.AutoField(primary_key=True)
    event_time = models.DateTimeField(blank=True, null=True)
    value = models.CharField(max_length=20, blank=True, null=True)
    action = models.TextField(blank=True, null=True)

    class Meta:
         
        db_table = 'session'


class Users(models.Model):
    userid = models.OneToOneField(Person, models.DO_NOTHING, db_column='userid', primary_key=True)
    sensor_access = models.BooleanField(blank=True, null=True)

    class Meta:
         
        db_table = 'users'
