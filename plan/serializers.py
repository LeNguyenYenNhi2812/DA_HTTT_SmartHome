from rest_framework import serializers
from api.models import PlanDevice, PlanSensor, Device, Sensor

class SensorDataSerializer(serializers.Serializer):
    sensor_id = serializers.IntegerField()
    sign = serializers.CharField()
    threshold = serializers.FloatField()

class CreatePlanSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    and_or = serializers.ChoiceField(
        choices=[('AND', 'And'), ('OR', 'Or')],
        required=True
    )
    devices = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        error_messages={
            'required': 'At least one device must be provided',
            'min_length': 'At least one device must be provided'
        }
    )
    sensors = serializers.ListField(
        child=SensorDataSerializer(),
        required=True,
        min_length=1,
        error_messages={
            'required': 'At least one sensor must be provided',
            'min_length': 'At least one sensor must be provided'
        }
    )

class PlanDeviceSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()
    on_off = serializers.BooleanField(required=False)
    added_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

class PlanSensorSerializer(serializers.Serializer):
    sensor_id = serializers.IntegerField()
    sign = serializers.CharField(max_length=10)
    threshold = serializers.FloatField()
    added_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

class PlanResponseSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    name = serializers.CharField()
    and_or = serializers.CharField()
    devices = serializers.SerializerMethodField()
    sensors = serializers.SerializerMethodField()

    def get_devices(self, obj):
        plan_devices = PlanDevice.objects.filter(plan=obj)
        return [{
            "device_id": pd.device.device_id,
            "name": pd.device.name,
            "type": pd.device.type,
            "value": pd.device.value,
            "on_off": pd.device.on_off,
            "added_at": pd.added_at.strftime("%Y-%m-%d %H:%M:%S")
        } for pd in plan_devices]

    def get_sensors(self, obj):
        plan_sensors = PlanSensor.objects.filter(plan=obj)
        return [{
            "sensor_id": ps.sensor.sensor_id,
            "name": ps.sensor.name,
            "type": ps.sensor.type,
            "value": ps.sensor.value,
            "sign": ps.sign, 
            "threshold": ps.threshold,
            "added_at": ps.added_at.strftime("%Y-%m-%d %H:%M:%S")
        } for ps in plan_sensors]