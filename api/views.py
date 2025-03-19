from django.shortcuts import render
import requests,json
from django.http import HttpResponse,JsonResponse
from dotenv import dotenv_values
import os
from . import models

from django.views.decorators.csrf import csrf_exempt
# Create your views here.
env_values = dotenv_values(".pas")  # Chỉ định đường dẫn file

# Lấy API key từ file
ADAFRUIT_IO_KEY = env_values.get("ADAFRUIT_IO_KEY")

print("API Key Loaded:", ADAFRUIT_IO_KEY)  # Kiểm tra xem API key có được load khôn
headers = {
            "Content-Type": "application/json",
            "X-AIO-Key": ADAFRUIT_IO_KEY,
        }
@csrf_exempt     
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
@csrf_exempt
def handleDataGET(request,url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        filteredData = [
            {i: x for i,x in item.items() if i not in ["created_epoch", "expiration"]}
            for item in data

        ]
        return JsonResponse(filteredData, safe=False)
    else:
        return JsonResponse("Error", safe=False)
    
@csrf_exempt
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
        return handleDataPOST(request, url)
    elif request.method == "GET":
        return handleDataGET(request, url)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
@csrf_exempt
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
        return handleDataPOST(request, url)
    elif request.method == "GET":
        return handleDataGET(request, url)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
    
def dbData(request):
    persons = models.Person.objects.all().values()  # Trả về QuerySet dạng dictionary
    return JsonResponse(list(persons), safe=False)


            