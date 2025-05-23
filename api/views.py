from django.shortcuts import render # type: ignore
import requests,json
from django.http import HttpResponse,JsonResponse # type: ignore
from dotenv import dotenv_values # type: ignore
from django.test import RequestFactory # type: ignore
from . import task
from datetime import datetime
import pytz
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
from . import models
import datetime
from django.db.models import Count
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule # type: ignore
import json
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.utils.dateparse import parse_datetime # type: ignore
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
env_values = dotenv_values(".pas")  # Chỉ định đường dẫn file

# Lấy API key từ file
ADAFRUIT_IO_KEY = env_values.get("ADAFRUIT_IO_KEY")



# print("API Key Loaded:", ADAFRUIT_IO_KEY)  # Kiểm tra xem API key có được load khôn
headers = {
            "Content-Type": "application/json",
            "X-AIO-Key": ADAFRUIT_IO_KEY,
        }  
# def handleDataPOST(request,url):
#     dataJson = json.loads(request.body)
#     feedData = {
#                 "value": dataJson["value"]
#                 # "feed_id": dataJson["feed_id"],
#                 # "feed_key": dataJson["feed_key"]
#             }
#     print("feedData",feedData)
#     response = requests.post(url, headers=headers, json=feedData)

#     if response.status_code == 200 or response.status_code == 201:
#         return JsonResponse({"message": "Success", "status": response.status_code}, safe=False)
#     else:
#         return JsonResponse({"message": "Error", "status": response.status_code, "response": response.text}, safe=False)
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
@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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
            "type": sensor.type,
            "location": sensor.location,
            "room_id": sensor.room_id,
            # Thêm các trường khác nếu cần
        })
    return JsonResponse(sensorData, safe=False)

@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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
                "time": log.time.astimezone(VN_TZ).isoformat(),
                "action": log.action,

                }
            )
        return JsonResponse(sensorData, safe=False)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON format"}, status=400)
    



from django_celery_beat.models import ClockedSchedule, PeriodicTask
import uuid

@csrf_exempt
def scheduleDeviceAction(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        name = data.get("name")
        time_str = data.get("time")
        user_id = data.get("user_id")
        device_id = data.get("device_id")
        on_off = data.get("on_off")
        value = data.get("value")

        if not all([name, time_str, user_id, device_id]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        scheduled_time = parse_datetime(time_str)
    

        if scheduled_time is None:
            return JsonResponse({"message": "Invalid datetime format"}, status=400)

        # Tạo bản ghi Schedule
        schedule_obj = models.Schedule.objects.create(
            name=name,
            time=scheduled_time,
            description=data.get("description"),
            user_id_id=user_id,
            action="Scheduled Device Update",
            on_off=on_off,
            value=value,
        )

        # Tạo ClockedSchedule cho thời gian cụ thể
        clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=scheduled_time)

        PeriodicTask.objects.create(
            name=f"schedule-{uuid.uuid4()}",
            task='api.task.execute_scheduled_device',
            clocked=clocked,
            one_off=True,
            args=json.dumps([device_id, on_off, value]),
        )

        return JsonResponse({"message": "Schedule created successfully", "schedule_id": schedule_obj.schedule_id})

    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)





# Create Device


@api_view(['POST'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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
    id = data.get("id")

    if not name or not type or not room_id:
        return JsonResponse({"message": "name, type, and room_id are required"}, status=400)

    try:
        room = models.Room.objects.get(room_id=room_id)  # Lấy instance của Room
    except models.Room.DoesNotExist:
        return JsonResponse({"message": "Room not found"}, status=404)

    user = None
    if id:
        try:
            user = models.User.objects.get(id=id)  # Lấy instance của User (nếu có)
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
        id=user,  
    )

    return JsonResponse({"message": "Device created successfully", "device_id": device.device_id}, status=201)
@api_view(['POST'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def postDeviceData(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    device_id = data.get("device_id")
    on_off = data.get("on_off")
    value = data.get("value")
      # Chuyển đổi về kiểu số nguyên nếu có giá trị
    
    pinned = data.get("pinned")
    id = data.get("id")

    if not on_off and not value:
        return JsonResponse({"message": "on_off or level is required"}, status=400)

    try:
        device = models.Device.objects.get(device_id=device_id)  # Lấy instance của Device
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)
    try:
        user = models.User.objects.get(id=id)  # Lấy instance của User (nếu có)
    except models.User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404)

    
    # Cập nhật trạng thái của thiết bị
    device.on_off = on_off 
    device.value = value
    device.pinned = pinned  
    device.save()
    device_map = {
        "fan": "smarthome-fan",
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
    # value = int(value)  
    # value= int(device_id)*1000+ value
    # value = str(value)
    # value = "0"+value
    id = value[0]+value[1]
    print("id",id)
    if (int(id) %2 ==0):
        newValue= "00"+value[2:]
    else:
        newValue= "01"+value[2:]

    print("newValue",newValue)
    feedData = {
                "value": newValue,
            }
    
    repondse=requests.post(url, headers=headers, json=feedData)
    if repondse.status_code == 200 or repondse.status_code == 201:
        print("Success")
    else:
        print("Error", repondse.text)

    return JsonResponse({"message": "Device updated successfully"}, status=200)




@api_view(['POST'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def postDeviceDataLED(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    device_id = data.get("device_id")
    on_off = data.get("on_off")
    value = data.get("value")
      # Chuyển đổi về kiểu số nguyên nếu có giá trị
    
    pinned = data.get("pinned")
    id = data.get("id")

    if not on_off and not value:
        return JsonResponse({"message": "on_off or level is required"}, status=400)

    try:
        device = models.Device.objects.get(device_id=device_id)  # Lấy instance của Device
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)
    try:
        user = models.User.objects.get(id=id)  # Lấy instance của User (nếu có)
    except models.User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404)

    
    # Cập nhật trạng thái của thiết bị
    device.on_off = on_off 
    device.value = value
    device.pinned = pinned  
    device.save()
    device_map = {
        "led": "smarthome-led",
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
    # value = int(value)  
    # value= int(device_id)*1000+ value
    # value = str(value)
    # value = "0"+value
    id = value[len(value)-2]+value[len(value)-1]
    print("id",id)
    if (int(id) %4 ==0):
        newValue = value[0:len(value)-2]+"00"
    elif (int(id) %4 ==1):
        newValue = value[0:len(value)-2]+"01"
    elif (int(id) %4 ==2):
        newValue = value[0:len(value)-2]+"02"
    elif (int(id) %4 ==3):
        newValue = value[0:len(value)-2]+"03"

    print("newValue",newValue)
    feedData = {
                "value": newValue,
            }
    
    repondse=requests.post(url, headers=headers, json=feedData)
    if repondse.status_code == 200 or repondse.status_code == 201:
        print("Success")
    else:
        print("Error", repondse.text)

    return JsonResponse({"message": "Device updated successfully"}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def renameDevice(request, deviceid):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    new_name = data.get("name")

    if not new_name:
        return JsonResponse({"message": "New name is required"}, status=400)

    try:
        device = models.Device.objects.get(device_id=deviceid)  # Lấy instance của Device
        device.name = new_name
        device.save()
        return JsonResponse({"message": "Device renamed successfully"}, status=200)
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)


@api_view(['DELETE'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def deleteDevice(request, deviceid):
    if request.method != "DELETE":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        device_id = deviceid
        if not device_id:
            return JsonResponse({"message": "device_id is required"}, status=400)

        # Xóa thiết bị
        device = models.Device.objects.get(device_id=device_id)
        device.delete()

        return JsonResponse({"message": "Device deleted successfully"}, status=200)
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)

@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def getCommonValue(request, deviceid):
    try:
        device = models.Device.objects.get(device_id=deviceid)
    except models.Device.DoesNotExist:
        return JsonResponse({"message": "Device not found"}, status=404)

    most_common = (
        models.LogDevice.objects
        .filter(device=device, value__isnull=False)
        .exclude(value='0')  
        .values('value')
        .annotate(count=Count('value'))
        .order_by('-count')
        .first()
    )

    if not most_common:
        return JsonResponse({"message": "No valid logged values found for this device"}, status=404)

    return JsonResponse({
        "device_id": deviceid,
        "most_frequent_value": most_common['value'],
        "count": most_common['count']
    })

@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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

    
@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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
@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
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
@api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def getLogDevice(request, deviceid):
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        device_id = deviceid

        if not device_id:
            return JsonResponse({"message": "device_id is required"}, status=400)

        # Lấy tất cả LogDevice thuộc Device
        logs = models.LogDevice.objects.filter(device_id=device_id).order_by('-time')
        log_data = [
            {
                "log_id": log.log_device_id,
                "time": log.time.astimezone(VN_TZ).isoformat(),
                "action": log.action,
                "on_off": log.on_off,
                "value": log.value,
            }
            for log in logs
        ]

        return JsonResponse(log_data, safe=False)
    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)

# thêm sénor

def createSensor(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)
    data = json.loads(request.body)
    name = data.get("name")
    type = data.get("type")
    location = data.get("location")
    value = 0
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
        every=1,
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



def postDataInLogSensor(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)
    data = json.loads(request.body)
    time = data.get("time")
    action = data.get("action")
    value = data.get("value")
    sensor_id = data.get("sensor_id")
    if not time or not action or not value or not sensor_id:
        return JsonResponse({"message": "time, action, value, and sensor_id are required"}, status=400)
    models.LogSensor.objects.create(
        time=time,
        action=action,
        value=value,
        sensor_id=sensor_id
    )
    return JsonResponse({"message": "Log created successfully"}, status=201)

#get Electricity
# @api_view(['GET'])  # hoặc GET/DELETE tùy API của bạn
# @permission_classes([IsAuthenticated])
# def getElectricity(request):
#     if request.method != "GET":
#         return JsonResponse({"message": "Invalid request method"}, status=405)

#     try:
#         body = json.loads(request.body)
#         device_ids = body.get("device_id", [])
#         start_time_str = body.get("start_time")
#         end_time_str = body.get("end_time")
        
#         if not device_ids or not start_time_str or not end_time_str:
#             return JsonResponse({"message": "Missing required parameters"}, status=400)
        
#         if not isinstance(device_ids, list):
#             device_ids = [device_ids]
        
        
    
#     except Exception as e:
#         return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
  
from django.utils.dateparse import parse_datetime
from datetime import timedelta
import pytz

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getElectricity(request):
    if request.method != "GET":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        body = json.loads(request.body)
        start_time_str = body.get("start_time")
        end_time_str = body.get("end_time")
        room_id = body.get("room_id")

        if not all([start_time_str, end_time_str, room_id]):
            return JsonResponse({"message": "Missing required parameters"}, status=400)

        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)

        if not (start_time and end_time):
            return JsonResponse({"message": "Invalid datetime format"}, status=400)

        # Ensure timezone-aware comparisons
        if timezone.is_naive(start_time) or timezone.is_naive(end_time):
            start_time = timezone.make_aware(start_time, timezone=pytz.UTC)
            end_time = timezone.make_aware(end_time, timezone=pytz.UTC)
        # print("start_time",start_time)
        # print("end_time",end_time)
        print(end_time-start_time)
        devices = models.Device.objects.filter(room_id=room_id)
        result = []

        for device in devices:
            logs = models.LogDevice.objects.filter(
                device=device,
                time__range=(start_time, end_time)
            ).order_by("time")
            # print("logs",logs)
            total_active_time = timedelta()
            prev_on = None

            for log in logs:
                # print("log",log.time)
                if log.on_off:
                    prev_on = log.time
                    # print("prev_on1",prev_on)
                elif not log.on_off and prev_on:
                    # print("prev_on",prev_on)
                    total_active_time += log.time - prev_on
                    # print("total_active_time",total_active_time)
                    prev_on = None

            # If device was still ON at the end of period
            prev_on = timezone.make_aware(prev_on, timezone=pytz.UTC) if prev_on else None
            if prev_on:
                total_active_time += end_time - prev_on
                print("total_active_time",total_active_time)
            result.append({
                "device_id": device.device_id,
                "time_consumed_seconds": int(total_active_time.total_seconds())
            })

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

  #house room
@api_view(['POST'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def createHouse(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    
    location = data.get("location")
    admin_id = data.get("id")

    if  not location or not admin_id:
        return JsonResponse({"message": "location and id are required"}, status=400)

    
    house = models.House.objects.create(
        location=location,
        admin_id=admin_id, 
    )

    return JsonResponse({"message": "House created successfully", "house_id": house.house_id}, status=201)
@api_view(['POST'])  # hoặc GET/DELETE tùy API của bạn
@permission_classes([IsAuthenticated])
def createRoom(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    
    name = data.get("name")
    house_id = data.get("house_id")
    # level = data.get("level")

    if not name or not house_id:
        return JsonResponse({"message": "name and house_id are required"}, status=400)

    
    room = models.Room.objects.create(
        name=name,
        house_id=house_id
        # level=level
    )

    return JsonResponse({"message": "Room created successfully", "room_id": room.room_id}, status=201)