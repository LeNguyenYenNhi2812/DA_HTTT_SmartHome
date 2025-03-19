from django.shortcuts import render
import requests,json
from django.http import HttpResponse,JsonResponse
from dotenv import dotenv_values
import os

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
# def deviceData(request,type): 
#     dataJson = json.loads(request.body)  
#     deviceType = dataJson["type"]
#     if deviceType == "humidity":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-humidity/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "fan":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-fan/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "light":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-light/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "temp":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-temp/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "soilhumidity":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-soilhumidity/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "pir":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-pir/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "led":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-led/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     elif deviceType == "waterpump":
#         url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-waterpump/data"
#         if request.method == "POST":
#             return handleDataPOST(request,url)
#         elif request.method == "GET":
#             return handleDataGET(request,url)
#     else:
#         return JsonResponse("Error", safe=False)
    
def deviceData(request, type):  
    device_map = {
        "humidity": "smarthome-humidity",
        "fan": "smarthome-fan",
        "light": "smarthome-light",
        "temp": "smarthome-temp",
        "soilhumidity": "smarthome-soilhumidity",
        "pir": "smarthome-pir",
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
    


            