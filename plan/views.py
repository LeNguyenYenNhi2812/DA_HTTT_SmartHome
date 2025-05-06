from django.shortcuts import render
from django.http import JsonResponse
from api import models
from django.db import transaction


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView 
from rest_framework import serializers
from .serializers import CreatePlanSerializer, PlanResponseSerializer
import json

from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from api.models import Room, Device, PlanDevice, PlanSensor, Plan, Sensor, House, User
from django.contrib.auth import authenticate # type: ignore
import logging

class get_room_plans(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, house_id):
        house = House.objects.filter(house_id=house_id, admin=request.user).exists()
        if not house:
            return Response(
                {"error": "You don't have permission to view plans for this house"},
                status=status.HTTP_403_FORBIDDEN
            )

        rooms = Room.objects.filter(house_id=house_id).prefetch_related(
            'device_set',  # Prefetch devices
            'device_set__plandevice_set',  # Prefetch plan devices
            'device_set__plandevice_set__plan',  # Prefetch plans
            'device_set__plandevice_set__plan__plansensor_set',  # Prefetch plan sensors
            'device_set__plandevice_set__plan__plansensor_set__sensor',  # Prefetch sensors
        )

        result = []
        seen_plan_ids = set()  

        for room in rooms:
            plans_data = []
            
            for device in room.device_set.all():
                for plan_device in device.plandevice_set.all():
                    plan = plan_device.plan
                    
                    if plan.plan_id in seen_plan_ids:
                        continue
                    seen_plan_ids.add(plan.plan_id)

                    plan_devices_data = [{
                        "device_id": pd.device.device_id,
                        "name": pd.device.name,
                        "type": pd.device.type,
                        "brand": pd.device.brand,
                        "value": pd.value,
                        "room": pd.device.room.name,
                        "on_off": pd.on_off,
                        "added_at": pd.added_at.strftime("%Y-%m-%d %H:%M:%S")
                    } for pd in plan.plandevice_set.all()]

                    plan_sensors_data = [{
                        "sensor_id": ps.sensor.sensor_id,
                        "name": ps.sensor.name,
                        "type": ps.sensor.type,
                        "value": ps.sensor.value,
                        "location": ps.sensor.location,
                        "sign": ps.sign,
                        "threshold": ps.threshold,
                        "added_at": ps.added_at.strftime("%Y-%m-%d %H:%M:%S")
                    } for ps in plan.plansensor_set.all()]

                    plans_data.append({
                        "plan_id": plan.plan_id,
                        "name": plan.name,
                        "and_or": plan.and_or,
                        "devices": plan_devices_data,
                        "sensors": plan_sensors_data
                    })

            result.append({
                "room_id": room.room_id,
                "room_name": room.name,
                "plans": plans_data
            })

        return JsonResponse(result, safe=False)
    
class create_plan(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePlanSerializer

    def post(self, request, house_id):
        try:
            if not House.objects.filter(house_id=house_id, admin=request.user).exists():
                return Response(
                    {"error": "You don't have permission to create plan for this house"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = CreatePlanSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data

            with transaction.atomic():
                plan = Plan.objects.create(
                    name=data['name'],
                    and_or=data['and_or']
                )

                if 'devices' in data and data['devices']:
                    device_ids = [d['device_id'] for d in data['devices']]
                    devices = {
                        d.device_id: d for d in Device.objects.filter(
                            device_id__in=device_ids,
                            room__house_id=house_id
                        )
                    }

                    plan_devices = [
                        PlanDevice(
                            plan=plan,
                            device=devices.get(d['device_id']),
                            value=d.get('value'),
                            on_off=d.get('on_off')
                        ) for d in data['devices'] if d['device_id'] in devices
                    ]
                    PlanDevice.objects.bulk_create(plan_devices)

                if 'sensors' in data and data['sensors']:
                    sensor_ids = [s['sensor_id'] for s in data['sensors']]
                    sensors = {
                        s.sensor_id: s for s in Sensor.objects.filter(
                            sensor_id__in=sensor_ids,
                            room__house_id=house_id
                        )
                    }

                    plan_sensors = [
                        PlanSensor(
                            plan=plan,
                            sensor=sensors.get(s['sensor_id']),
                            sign=s['sign'],
                            threshold=s['threshold']
                        ) for s in data['sensors'] if s['sensor_id'] in sensors
                    ]
                    PlanSensor.objects.bulk_create(plan_sensors)

            # response_serializer = PlanResponseSerializer(plan)
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class delete_plan(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, plan_id):
        try:
            plan = Plan.objects.get(plan_id=plan_id)
            devices = Device.objects.filter(plandevice__plan=plan, room__house__admin=request.user)
            sensors = Sensor.objects.filter(plansensor__plan=plan, room__house__admin=request.user)
            
            if not (devices.exists() or sensors.exists()):
                return Response(
                    {"error": "You don't have permission to delete this plan"},
                    status=status.HTTP_403_FORBIDDEN
                )
            plan.delete()
            return Response(
                {"message": "Plan deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Plan.DoesNotExist:
            return Response(
                {"error": f"Plan with id {plan_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class edit_plan(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePlanSerializer
    
    def put(self, request, plan_id):
        try:
            plan = Plan.objects.get(plan_id=plan_id)
            
            existing_devices = []
            existing_sensors = []
            
            serializer = CreatePlanSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = serializer.validated_data

            if 'devices' in data:
                for device_data in data['devices']:
                    try:
                        device = Device.objects.get(
                            device_id=device_data['device_id'],
                            room__house__admin=request.user
                        )
                        existing_devices.append(device)
                    except Device.DoesNotExist:
                        return Response(
                            {"error": f"Device with id {device_data['device_id']} not found"}, 
                            status=status.HTTP_404_NOT_FOUND
                        )

            if 'sensors' in data:
                for sensor_data in data['sensors']:
                    try:
                        sensor = Sensor.objects.get(
                            sensor_id=sensor_data['sensor_id'],
                            room__house__admin=request.user
                        )
                        existing_sensors.append(sensor)
                    except Sensor.DoesNotExist:
                        return Response(
                            {"error": f"Sensor with id {sensor_data['sensor_id']} not found"}, 
                            status=status.HTTP_404_NOT_FOUND
                        )

            plan.name = data['name']
            plan.and_or = data['and_or']
            plan.save()

            PlanDevice.objects.filter(plan=plan).delete()
            PlanSensor.objects.filter(plan=plan).delete()

            for i, device in enumerate(existing_devices):
                device_data = data['devices'][i]
                PlanDevice.objects.create(
                    plan=plan,
                    device=device,
                    value=device_data.get('value', None),
                    on_off=device_data.get('on_off', None)
                )

            for i, sensor in enumerate(existing_sensors):
                sensor_data = data['sensors'][i]
                PlanSensor.objects.create(
                    plan=plan,
                    sensor=sensor,
                    sign=sensor_data['sign'],
                    threshold=sensor_data['threshold']
                )

            return Response(status=status.HTTP_200_OK)

        except Plan.DoesNotExist:
            return Response(
                {"error": f"Plan with id {plan_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )