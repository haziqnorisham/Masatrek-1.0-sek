from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('btnAction/', views.GetDeviceID, name='tapage'),
    path('btnAction/detailed/', views.Detailed_view, name='Detailed_view'),
    path('btnAction/print/', views.Print_view, name='Print_view'),
    path('stranger/', views.Stranger_view, name='Stranger_view'),
]
