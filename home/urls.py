from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard_ismartwave/', views.dashboard, name='dashboard_ismartwave'),
    path('api/get_dashboard_ws/', views.dashboard_ws, name='get_dashboard_ws'),
]
