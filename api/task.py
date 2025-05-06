from celery import shared_task
import requests
from api import models
from dotenv import dotenv_values
env_values = dotenv_values(".pas")  # Chỉ định đường dẫn file

# Lấy API key từ file
ADAFRUIT_IO_KEY = env_values.get("ADAFRUIT_IO_KEY")
@shared_task
def fetch_sensor_data():
    sensor_map = {
        "humidity": "smarthome-humidity",
        "light": "smarthome-light",
        "temp": "smarthome-temp",
        "soilhumidity": "smarthome-soilhumidity",
        "pir": "smarthome-pir"
    }
    sensor_id = 10
    for sensor_id in range(10,15):
        try:
            sensor = models.Sensor.objects.get(sensor_id=sensor_id)
        except models.Sensor.DoesNotExist:
            continue

        # Ép kiểu sensor.type về chữ thường để khớp với sensor_map
        sensor_type_key = sensor.type.lower()
        if sensor_type_key not in sensor_map:
            continue

        url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{sensor_map[sensor_type_key]}/data?limit=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            first_item = data[0] if data and isinstance(data, list) else None
            if first_item:
                new_value = first_item.get("value")
                # Cập nhật value của sensor và lưu thủ công vào DB
                sensor.value = new_value
                sensor.save()
                sensor.refresh_from_db()
                # print("Sau khi lưu, sensor.value:", sensor.value)
                models.LogSensor.objects.create(
                    time=first_item.get("created_at"),
                    action=f"Sensor data fetched for {sensor.type} in room {sensor.location}",
                    value=new_value,
                    sensor=sensor,  # Hoặc sensor_id=sensor.sensor_id
                )

@shared_task
def execute_scheduled_device(device_id, on_off, value):
    try:
        device = models.Device.objects.get(device_id=device_id)
        device.on_off = on_off
        device.value = value
        device.save()

        # Log again if needed
        models.LogDevice.objects.create(
            device=device,
            action="Executed scheduled update",
            on_off=on_off,
            value=value,
        )

        # Post to Adafruit
        device_map = {
            "fan": "smarthome-fan",
            "led": "smarthome-led",
            "waterpump": "smarthome-waterpump"
        }

        if device.type not in device_map:
            return

        url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{device_map[device.type]}/data"
        headers = {
            "Content-Type": "application/json",
            "X-AIO-Key": dotenv_values(".pas").get("ADAFRUIT_IO_KEY"),
        }

        # Format value similar to your postDeviceData
        feed_data = {"value": value}
        requests.post(url, headers=headers, json=feed_data)

    except models.Device.DoesNotExist:
        pass

    # try:
    #     sensor = models.Sensor.objects.get(sensor_id=sensor_id)
    # except models.Sensor.DoesNotExist:
    #     return

    # # Ép kiểu sensor.type về chữ thường để khớp với sensor_map
    # sensor_type_key = sensor.type.lower()
    # if sensor_type_key not in sensor_map:
    #     return

    # url = f"https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/{sensor_map[sensor_type_key]}/data?limit=1"
    # response = requests.get(url)

    # if response.status_code == 200:
    #     data = response.json()
    #     first_item = data[0] if data and isinstance(data, list) else None
    #     if first_item:
    #         new_value = first_item.get("value")
    #         # Cập nhật value của sensor và lưu thủ công vào DB
    #         sensor.value = new_value
    #         sensor.save()
    #         sensor.refresh_from_db()
    #         print("Sau khi lưu, sensor.value:", sensor.value)
    #         # log_message = f"Sensor data fetched for {sensor.type} in room {sensor.location}"
    #         # Đồng thời tạo log cho sensor
    #         models.LogSensor.objects.create(
    #             time=first_item.get("created_at"),
    #             action=f"Sensor data fetched for {sensor.type} in room {sensor.location}",
    #             value=new_value,
    #             sensor=sensor,  # Hoặc sensor_id=sensor.sensor_id
    #         )
