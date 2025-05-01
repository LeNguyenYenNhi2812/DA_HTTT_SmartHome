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
from api.models import Room, Device, PlanDevice, PlanSensor, Plan, Sensor
from django.contrib.auth import authenticate # type: ignore
import logging



class get_room_plans(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, house_id):
        
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
                            "value": pd.device.value,
                            "on_off": pd.device.on_off,
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
                            "added_at": ps.added_at.strftime("%Y-%m-%d %H:%M:%S")
                        })

                    plan_exists = any(p["plan_id"] == plan.plan_id for p in plans_data)
                    if not plan_exists:
                        plans_data.append({
                            "plan_id": plan.plan_id,
                            "name": plan.name,
                            "and_or": plan.and_or,
                            "sign": plan.sign,
                            "threshold": plan.threshold,
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
                for device_id in data['devices']:
                    try:
                        device = Device.objects.get(device_id=device_id)
                        PlanDevice.objects.create(
                            plan=plan,
                            device=device
                        )
                    except Device.DoesNotExist:
                        plan.delete()
                        return Response(
                            {"error": f"Device with id {device_id} not found"}, 
                            status=status.HTTP_404_NOT_FOUND
                        )

            if 'sensors' in data and data['sensors']:
                for sensor_data in data['sensors']:
                    try:
                        sensor = Sensor.objects.get(sensor_id=sensor_data['sensor_id'])
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
                        
            response_serializer = PlanResponseSerializer(plan)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
