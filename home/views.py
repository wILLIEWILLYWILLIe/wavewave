from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.timezone import localtime
import math, json
from home.mqtt_client import init_mqtt
from home.models import DashboardData
import pytz
from asgiref.sync import sync_to_async

taipei_tz = pytz.timezone('Asia/Taipei')
mqtt_client = init_mqtt()

ANT_ARRAY = [0, 8, 1, 9, 2, 10 , 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

def index(request):
    return redirect('dashboard/')

# Dashboard
def dashboard(request):
    context = {
        'segment': 'dashboard',
        'ant_range': ANT_ARRAY,
        'app_name': 'Dashboard',
        'app_version': '1.0',
    }
    return render(request, 'pages/dashboard/dashboard.html', context=context)

# iSmartWave Dashboard
def ismartwave_dashboard(request):
    context = {
        'segment': 'ismartwave',
        'ant_range': ANT_ARRAY,
        'app_name': 'iSmartWave',
        'app_version': '2.0',
    }
    return render(request, 'pages/dashboard/dashboard.html', context=context)


@csrf_protect
def _dashboard_ws(request):
    return JsonResponse({'websocket_url': '/live_dashboard/'})

dashboard_ws = sync_to_async(_dashboard_ws, thread_sensitive=True)
