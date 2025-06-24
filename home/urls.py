from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ismartwave/', views.ismartwave_dashboard, name='ismartwave'),
    path('api/get_dashboard_ws/', views.dashboard_ws, name='get_dashboard_ws'),
    
    # 新增的路由名稱，避免衝突
    path('radar-monitor/', views.dashboard, name='radar_monitor'),
    path('wave-dashboard/', views.dashboard, name='wave_dashboard'),
    path('smart-radar/', views.ismartwave_dashboard, name='smart_radar'),
]
