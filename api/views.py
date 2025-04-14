from django.shortcuts import render # type: ignore
import requests,json
from django.http import HttpResponse,JsonResponse # type: ignore
from dotenv import dotenv_values # type: ignore
from django.test import RequestFactory # type: ignore
from . import task
from django.utils.timezone import now # type: ignore
from . import models

from django_celery_beat.models import PeriodicTask, IntervalSchedule # type: ignore
import json
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.utils.dateparse import parse_datetime # type: ignore
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
# def handleDataGET(request,url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()

#         filteredData = [
#             {i: x for i,x in item.items() if True}
#             for item in data

#         ]
#         return JsonResponse(filteredData, safe=False)
#     else:
#         return JsonResponse("Error", safe=False)
    


#Sensors Endpoints  
def getRoomSensorData(request,roomid):
    # return JsonResponse({"message": "Invalid request method"}, status=405)
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    room_id=roomid
    if not room_id:
        return JsonResponse({"message": "room_id is required"}, status=400)

    # Lấy danh sách cảm biến của room
    sensors = models.Sensor.objects.filter(room_id=room_id)
    sensorData = []
    for sensor in sensors:
        sensorData.append({
            "sensor_id": sensor.sensor_id,
            "name": sensor.name,
            "value": sensor.value,
            # Thêm các trường khác nếu cần
        })
    return JsonResponse(sensorData, safe=False)

def getRoomSensorDataTime(request,roomid):
    # return JsonResponse({"message": "Invalid request method"}, status=405)
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        room_id = data.get("room_id")
        start_time = parse_datetime(data.get("start_time"))
        end_time = parse_datetime(data.get("end_time"))
        if not all([room_id, start_time, end_time]):
            return JsonResponse({"message": "room_id, start_time, and end_time are required"}, status=400)
        
        sensors = models.Sensor.objects.filter(room_id=room_id)
        sensor_ids=sensors.values_list("sensor_id", flat=True)

        logs = models.LogSensor.objects.filter(sensor_id__in=sensor_ids, time__range=(start_time, end_time)).select_related("sensor")
        # print("logs",logs)
        sensorData=[]
        for log in logs:
            sensorData.append(
                {
                "sensor_id": log.sensor.sensor_id,
                "sensor_name": log.sensor.name,
                "type": log.sensor.type,
                "value": log.value,
                "time": log.time,
                "action": log.action,

                }
            )
        return JsonResponse(sensorData, safe=False)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON format"}, status=400)
# Create Device
def createDevice(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    name = data.get("name")
    type = data.get("type")
    brand = data.get("brand")
    value = data.get("value")
    room_id = data.get("room_id")
    on_off = data.get("on_off")
    pinned = data.get("pinned", False)  # Thêm trường pinned
    user_id = data.get("user_id")

    if not name or not type or not room_id:
        return JsonResponse({"message": "name, type, and room_id are required"}, status=400)

    try:
        room = models.Room.objects.get(room_id=room_id)  # Lấy instance của Room
    except models.Room.DoesNotExist:
        return JsonResponse({"message": "Room not found"}, status=404)

    user = None
    if user_id:
        try:
            user = models.User.objects.get(user_id=user_id)  # Lấy instance của User (nếu có)
        except models.User.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)

    device = models.Device.objects.create(
        name=name,
        type=type,
        brand=brand,
        value=value,
        room_id=room_id,
        on_off=on_off,
        pinned=pinned,  # Thêm trường pinned
        user_id=user,  # Thêm trường user_id
    )

    return JsonResponse({"message": "Device created successfully", "device_id": device.device_id}, status=201)
def postDeviceData(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    device_id = data.get("device_id")
    on_off = data.get("on_off")
    value = data.get("value")
    value = int(value)  # Chuyển đổi về kiểu số nguyên nếu có giá trị
    value= device_id*1000+ value
    pinned = data.get("pinned")
    user_id = data.get("user_id")

    if not on_off and not value:
        return JsonResponse({"message": "on_off or level is required"}, status=400)

    try:
        device = models.Device.objects.get(device_id=device_id)  # Lấy instance của Device
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)
    try:
        user = models.User.objects.get(user_id=user_id)  # Lấy instance của User (nếu có)
    except models.User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404)

    
    # Cập nhật trạng thái của thiết bị
    device.on_off = on_off 
    device.value = value
    device.pinned = pinned  
    device.save()
    device_map = {
        "fan": "smarthome-fan",
        "led": "smarthome-led",
        "waterpump": "smarthome-waterpump"
    }

    if device.type not in device_map:
        return JsonResponse({"message": "Invalid device type for Adafruit"}, status=400)

    url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{device_map[device.type]}/data"


    
    models.LogDevice.objects.create(
        device=device,
        action="Device state updated",
        on_off=on_off,
        value=value,  # Giả sử level là giá trị của thiết bị
    )  

    #Gửi dữ liệu lên Adafruit IO
    fake_request = request
    value = str(value)
    value = "0"+value
    fake_request._body = json.dumps({"value": value}).encode()
    adafruit_response = handleDataPOST(fake_request, url)

  

    return JsonResponse({"message": "Device updated successfully"}, status=200)

def getNumberOfDevices(request,houseid):
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        
        house_id = houseid

        if not house_id:
            return JsonResponse({"message": "house_id is required"}, status=400)

        # Lấy tất cả Room thuộc House
        rooms = models.Room.objects.filter(house_id=house_id)
        room_ids = rooms.values_list("room_id", flat=True)

        # Đếm số lượng Device thuộc các Room đó
        device_count = models.Device.objects.filter(room_id__in=room_ids).count()

        return JsonResponse({"device_count": device_count}, status=200)
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)

    
    
def getAllDevices(request, houseid):
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        if not houseid:
            return JsonResponse({"message": "house_id is required"}, status=400)

        rooms = models.Room.objects.filter(house_id=houseid)
        result = []

        for room in rooms:
            devices = models.Device.objects.filter(room=room)
            devices_data = [
                {
                    "device_id": device.device_id,
                    "name": device.name,
                    "type": device.type,
                    "brand": device.brand,
                    "value": device.value,
                    "on_off": device.on_off,
                    "pinned": device.pinned,
                    "date_created": device.date_created,
                }
                for device in devices
            ]

            result.append({
                "room_id": room.room_id,
                "room_title": room.name,
                "devices": devices_data
            })

        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)

def getNumberDevicesInRoom(request, roomid):
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        room_id = roomid

        if not room_id:
            return JsonResponse({"message": "room_id is required"}, status=400)

        # Lấy tất cả Device thuộc Room
        devices = models.Device.objects.filter(room_id=room_id)
        device_count = devices.count()

        return JsonResponse({"device_count": device_count}, status=200)
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)


# thêm sénor
def postSensorData(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)
    data = json.loads(request.body)
    name = data.get("name")
    type = data.get("type")
    location = data.get("location")
    value = data.get("value")
    room_id = data.get("room_id")
    sensor = models.Sensor.objects.create(
        name=name,
        type=type,
        location=location,
        value=value,
        room_id=room_id
    )
    return JsonResponse({"message": "Sensor created successfully", "sensor_id": sensor.sensor_id}, status=201)


def run_sensor_log(request):
    # Tạo khoảng lặp 1 phút (nếu chưa có)
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.MINUTES,
    )

    # Tạo task định kỳ nếu chưa có
    if not PeriodicTask.objects.filter(name="Fetch Sensor Data Periodically").exists():
        PeriodicTask.objects.create(
            interval=schedule,
            name="Fetch Sensor Data Periodically",
            task="api.task.fetch_sensor_data",
            args=json.dumps([]),
        )
 

    return JsonResponse({"message": "Task scheduled to run every 1 minute"})
