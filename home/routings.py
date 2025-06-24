from django.urls import re_path
from home.consumers import DashboardConsumer #稍後自行建立的consumers.py

websocket_urlpatterns =[
	re_path(r'live_dashboard/', DashboardConsumer.as_asgi()),
]