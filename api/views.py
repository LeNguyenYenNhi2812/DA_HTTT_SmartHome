from django.shortcuts import render
import requests,json
from django.http import HttpResponse,JsonResponse

from django.views.decorators.csrf import csrf_exempt
# Create your views here.


@csrf_exempt
def fanData(request):
    if request.method == "POST":
        url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-fan/data"
        headers = {
            "Content-Type": "application/json",
            "X-AIO-Key": "aio_oDCu724ANQdpqlNhi6rNarzFSLxb"
        }
        dataJson = json.loads(request.body)
        feedData = {
            "value": dataJson["value"],
            "feed_id": dataJson["feed_id"],
            "feed_key": dataJson["feed_key"]
        }
        print(feedData)
        # return JsonResponse(feedData, safe=False)
        response = requests.post(url, headers=headers, json=feedData)

        if response.status_code == 200 or response.status_code == 201:
            return JsonResponse({"message": "Success", "status": response.status_code}, safe=False)
        else:
            return JsonResponse({"message": "Error", "status": response.status_code, "response": response.text}, safe=False)




    elif request.method == "GET":
        url = "https://io.adafruit.com/api/v2/nhu_lephanbao/feeds/smarthome-fan/data"
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