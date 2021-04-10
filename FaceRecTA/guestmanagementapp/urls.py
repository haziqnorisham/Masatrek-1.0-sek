from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registerguest/', views.register_guest, name='register_guest'),
    path('guestlist/', views.guest_list, name='guest_list'),
    path('registerguest/register_guest_proc/', views.register_guest_proc, name='register_guest_proc'),
    path('register_guest_proc_home/', views.register_guest_proc_home, name='register_guest_proc_home'),
    path('guestlist/guest_list_proc/', views.guest_list_proc, name='guest_list_proc'),
    path('guestattendance', views.guest_attendance, name='guest_attendance'),
    path('guestattendance/print/', views.guest_print, name='guest_print'),
    path('terminal/', views.terminal, name='terminal'),
    path('ajax_check_new_stranger/', views.ajax_check_new_stranger, name='ajax_check_new_stranger'),

]
