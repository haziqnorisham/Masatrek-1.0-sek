from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='administrator_home'),
    path('registration/', views.registration, name='registration'),
    path('Sync/', views.sync, name='Sync'),
    path('employee_add/', views.employee_add, name='employee_add'),
    path('update_employee/', views.update_employee, name='update_employee'),
    path('employee_add_process/', views.employee_add_process, name='employee_add_process'),
    path('employee_delete_process/', views.employee_delete_process, name='employee_delete_process'),
    path('ajax_edit_employee/', views.ajax_edit_employee, name='ajax_edit_employee'),
    path('add_device/', views.add_device, name='add_device'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('full_reset/', views.full_reset, name='full_reset'),
    path('bld1234567890/', views.bld, name='bld'),
    path('sync_to_all/', views.sync_to_all, name='sync_to_all'),
    path('login_list/', views.login_list, name='login_list'),

]
