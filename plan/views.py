from django.shortcuts import render
from django.http import JsonResponse
from api import models


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
        house = House.objects.filter(house_id=house_id, admin=request.user).first()
        if not house:
            return Response(
                {"error": "You don't have permission to view plans for this house"},
                status=status.HTTP_403_FORBIDDEN
            )

        rooms = Room.objects.filter(house_id = house_id)
        result = []

        for room in rooms:
            devices = Device.objects.filter(room=room)
            
            plans_data = []
            for device in devices:
                plan_devices = PlanDevice.objects.filter(device=device)
                for plan_device in plan_devices:
                    plan = plan_device.plan
                    
                    plan_devices_data = []
                    for pd in PlanDevice.objects.filter(plan=plan):
                        plan_devices_data.append({
                            "device_id": pd.device.device_id,
                            "name": pd.device.name,
                            "type": pd.device.type,
                            "brand": pd.device.brand,
                            "value": pd.value,
                            "room": pd.device.room.name,
                            "on_off": pd.on_off,  
                            "added_at": pd.added_at.strftime("%Y-%m-%d %H:%M:%S")
                        })

                    plan_sensors_data = []
                    for ps in PlanSensor.objects.filter(plan=plan):
                        plan_sensors_data.append({
                            "sensor_id": ps.sensor.sensor_id,
                            "name": ps.sensor.name,
                            "type": ps.sensor.type,
                            "value": ps.sensor.value,
                            "location": ps.sensor.location,
                            "sign": ps.sign, 
                            "threshold": ps.threshold,  
                            "added_at": ps.added_at.strftime("%Y-%m-%d %H:%M:%S")
                        })

                    plan_exists = any(p["plan_id"] == plan.plan_id for p in plans_data)
                    if not plan_exists:
                        plans_data.append({
                            "plan_id": plan.plan_id,
                            "name": plan.name,
                            "and_or": plan.and_or,
                            "devices": plan_devices_data,
                            "sensors": plan_sensors_data
                        })

            room_data = {
                "room_id": room.room_id,
                "room_name": room.name,
                "plans": plans_data
            }
            result.append(room_data)

        return JsonResponse(result, safe=False)
    

class create_plan(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePlanSerializer

    def post(self, request, house_id):
        try:
            house = House.objects.filter(house_id=house_id, admin=request.user).first()
            if not house:
                return Response(
                    {"error": "You don't have permission to create plan for this house"},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = CreatePlanSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = serializer.validated_data
                    
            plan = Plan.objects.create(
                name=data['name'],
                and_or=data['and_or']
            )

            if 'devices' in data and data['devices']:
                for device_data in data['devices']:
                    try:
                        device = Device.objects.get(
                            device_id=device_data['device_id'],
                            room__house_id=house_id
                        )
                        PlanDevice.objects.create(
                            plan=plan,
                            device=device,
                            value=device_data.get('value', None),
                            on_off=device_data.get('on_off', None)
                        )
                    except Device.DoesNotExist:
                        plan.delete()
                        return Response(
                            {"error": f"Device with id {device_data['device_id']} not found"}, 
                            status=status.HTTP_404_NOT_FOUND
                        )

            if 'sensors' in data and data['sensors']:
                for sensor_data in data['sensors']:
                    try:
                        sensor = Sensor.objects.get(
                            sensor_id=sensor_data['sensor_id'],
                            room__house_id=house_id
                        )
                        PlanSensor.objects.create(
                            plan=plan,
                            sensor=sensor,
                            sign=sensor_data['sign'],
                            threshold=sensor_data['threshold']
                        )
                    except Sensor.DoesNotExist:
                        plan.delete()
                        return Response(
                            {"error": f"Sensor with id {sensor_data['sensor_id']} not found"}, 
                            status=status.HTTP_404_NOT_FOUND
                        )
                        
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