from django.shortcuts import render
import requests,json
from django.http import HttpResponse,JsonResponse
from dotenv import dotenv_values
import os
from django.utils.timezone import now
from . import models

from django.views.decorators.csrf import csrf_exempt
# Create your views here.
env_values = dotenv_values(".pas")  # Chỉ định đường dẫn file

# Lấy API key từ file
ADAFRUIT_IO_KEY = env_values.get("ADAFRUIT_IO_KEY")

# print("API Key Loaded:", ADAFRUIT_IO_KEY)  # Kiểm tra xem API key có được load khôn
headers = {
            "Content-Type": "application/json",
            "X-AIO-Key": ADAFRUIT_IO_KEY,
        }  
def handleDataPOST(request,url):
    dataJson = json.loads(request.body)
    feedData = {
                "value": dataJson["value"]
                # "feed_id": dataJson["feed_id"],
                # "feed_key": dataJson["feed_key"]
            }
    response = requests.post(url, headers=headers, json=feedData)

    if response.status_code == 200 or response.status_code == 201:
        return JsonResponse({"message": "Success", "status": response.status_code}, safe=False)
    else:
        return JsonResponse({"message": "Error", "status": response.status_code, "response": response.text}, safe=False)
def handleDataGET(request,url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        filteredData = [
            {i: x for i,x in item.items() if True}
            for item in data

        ]
        return JsonResponse(filteredData, safe=False)
    else:
        return JsonResponse("Error", safe=False)
    
def deviceData(request, type):  #output
    device_map = {
        "fan": "smarthome-fan",
        "led": "smarthome-led",
        "waterpump": "smarthome-waterpump"
    }

    if type not in device_map:
        return JsonResponse({"message": "Invalid device type"}, status=400)

    url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{device_map[type]}/data"

    if request.method == "POST":
        respond=handleDataPOST(request, url)
        # if respond.status_code == 200 or respond.status_code == 201:
        #     # Tìm deviceid trong database
        #     try:
        #         deviceid = models.Device.objects.filter(type=type).latest('deviceid')
        #     except models.Device.DoesNotExist:
        #         return JsonResponse({"message": "Device not found in database"}, status=404)
        # models..objects.create(
        #         event_time=now(),
        #         value=json.loads(request.body).get("value"),
        #         action=f"Data posted to Adafruit for {type}"
        #     )
        return respond
    elif request.method == "GET":
        return handleDataGET(request, url)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
def sensorData(request, type): #input
    sensor_map = {
        "humidity": "smarthome-humidity",
        "light": "smarthome-light",
        "temp": "smarthome-temp",
        "soilhumidity": "smarthome-soilhumidity",
        "pir": "smarthome-pir"
    }

    if type not in sensor_map:
        return JsonResponse({"message": "Invalid device type"}, status=400)

    url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{sensor_map[type]}/data"

    if request.method == "POST":
        response = handleDataPOST(request, url)
        if response.status_code == 200 or response.status_code == 201:
            # Tìm sensorid trong database
            try:
                sensorid = models.Sensor.objects.filter(type=type).latest('sensorid')
            except models.Sensor.DoesNotExist:
                return JsonResponse({"message": "Sensor not found in database"}, status=404)

        models.Session.objects.create(
                event_time=now(),
                value=json.loads(request.body).get("value"),
                action=f"Data posted to Adafruit for {type}"
            )
        models.SensorSession.objects.create(sensorid=sensorid, sessionid=models.Session.objects.latest("sessionid"))
        return response
    elif request.method == "GET":
        return handleDataGET(request, url)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
    
def dbData(request):
    persons = models.Person.objects.all().values()  # Trả về QuerySet dạng dictionary
    return JsonResponse(list(persons), safe=False)
def room(request):

    if request.method == 'GET':
        rooms = models.Room.objects.all().values()  
        return JsonResponse(list(rooms), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        room = models.Room.objects.create(name=data['name'])
        return JsonResponse({"message":"Insert successfully"}, safe=False)
def sensorAdd(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sensor = models.Sensor.objects.create(name=data['name'], type=data['type'], location=data['location'], value=data['value'])
        return JsonResponse({"message":"Insert successfully"}, safe=False)
    else:
        return JsonResponse({"message":"Invalid request method"}, status=405)

def deviceAdd(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device = models.Device.objects.create(name=data['name'], type=data['type'], value=data['value'], brand = data['brand'], configuration = data['configuration'])
        room = models.Room.objects.get(name=data['room-name'])  # Lấy phòng theo tên
        roomid = room
        models.DeviceRoom.objects.create(deviceid=models.Device.objects.filter(type=data['type']).latest('deviceid'), roomid=roomid)
        return JsonResponse({"message":"Insert successfully"}, safe=False)
    else:
        return JsonResponse({"message":"Invalid request method"}, status=405)
            