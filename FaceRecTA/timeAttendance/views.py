from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from sqlite3 import Error
from django.contrib.auth.decorators import login_required
from timeAttendance.models import EmployeeAttendance, EmployeeDetail, StrangerDetails, TerminalDetails
from django.forms.models import model_to_dict
from datetime import date, datetime, timedelta
import os
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn
def home(request):

    return render(request, 'timeAttendance/home.html')
def get_terminal_information(ipAddress, username, passwrod):

    a = None

    #username = this.username
    #username = request.POST.get("username")
    #password = request.POST.get("password")

    #url = "http://192.168.0.33/action/GetSysParam"
    url = "http://"+ipAddress+"/action/GetSysParam"

    headers = {
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.16.3",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
        'Host': "192.168.0.33",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }

    #response = requests.request("POST", url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))

    response = requests.request("POST", url, headers=headers, auth=HTTPBasicAuth(username, password))

    json_data = response.text
    data = json.loads(json_data)
    a = data['info']
    response_data = {}
    response_data['info'] = a

@csrf_exempt
@login_required
def GetDeviceID(request):
    date2 = None
    date_tag = None
    if request.GET.get('date') and request.GET.get('date2'):
        message = 'You submitted: %r' % request.GET['date']
        date2 = datetime.strptime(request.GET['date'], "%Y-%m-%d" ).date()
        date_tag = {'date' : request.GET['date']}
        date_tag_to = {'date_to' : request.GET['date2']}
        date_to = datetime.strptime(request.GET['date2'], "%Y-%m-%d" ).date()
        #print()
        #print(request.GET['date'])
        #print(request.GET['date2'])
        #print()
    else:
        date_tag = {'date' : str(date.today())}
        date_tag_to = {'date_to' : str(date.today())}

        date2 = date.today()
        date_to = date.today()

    todays_employee = []
    data=[]
    emp=[]
    emp_grouped = [[None]]
    #emp_grouped[0] = [0,2]
    # Create a connectin to the database
    #conn = create_connection(r"C:\sqlite\db\pythonsqlite.db")
    #cur = conn.cursor()
    #cur.execute(r"SELECT * FROM attendence")
    #cur.execute(r"SELECT * FROM attendence WHERE date(enter_time) = date('now') and name like 'basyir'")
    #cur.execute(r"SELECT * FROM attendence WHERE date(enter_time) = date('now')")
    #rows = cur.fetchall()

    temp_data = EmployeeAttendance.objects.all()
    temp_data_list = []
    date_range = []
    #for temp_data2 in temp_data:
        #temp_data_list.append(model_to_dict(temp_data2))

    #print(type(temp_data))
    try:
        delta = date_to - date2

        for i in range(delta.days + 1):
            day = date2 + timedelta(days=i)
            print()
            print(day)
            print()
            date_range.append(day)

    except Exception as e:
        print(e)

    date_range_dict_list = []
    for date_temp in date_range:
        date_range_dict = {
            'date' : date_temp
            }
        date_range_dict_list.append(date_range_dict)

    employee_id_list_list = []
    
    for date_range_individual in date_range:
        
        #employee_id_list = EmployeeAttendance.objects.values('employee_id').filter(capture_time__contains = str(date2)).distinct()
        employee_id_list = EmployeeAttendance.objects.values('EmployeeDetail').filter(capture_time__contains = str(date_range_individual)).distinct()
        #employee_id_list_list.append(EmployeeAttendance.objects.values('employee_id').filter(capture_time__contains = str(date_range_individual)).distinct())


        for employee_id_dict in employee_id_list:
            try:
                #temp2 = EmployeeAttendance.objects.filter(employee_id = employee_id_dict['employee_id'], capture_time__contains = str(date2))
                temp2 = EmployeeAttendance.objects.filter(EmployeeDetail = employee_id_dict['EmployeeDetail'], capture_time__contains = str(date_range_individual))

                temp2_earliest = temp2.earliest('capture_time')
                temp2_latest = temp2.latest('capture_time')

                temp2_datetime_earliest = datetime.strptime(temp2_earliest.capture_time,"%Y-%m-%dT%H:%M:%S")
                temp2_datetime_latest = datetime.strptime(temp2_latest.capture_time,"%Y-%m-%dT%H:%M:%S")

                working_hours = temp2_datetime_latest - temp2_datetime_earliest

                temp3 = list(EmployeeAttendance.objects.values('temperature').filter(EmployeeDetail_id = temp2_earliest.EmployeeDetail.id, capture_time__contains = str(temp2_earliest.capture_time)[0:10]))

                temp4 = []
                temp4.clear()
                print("\n\n\n")
                print(str(temp2_earliest.capture_time)[0:10])
                print("\n\n\n")
                for tmp in temp3:
                    if (tmp['temperature'] == '') :
                        temp4.append(0)
                    else:
                        temp4.append(float(tmp['temperature']))

                temp4_max = temp4[0]
                temp4_min = temp4[-1]

                temp_employee_daily_info = { 'branch': temp2_earliest.EmployeeDetail.branch ,'department': temp2_earliest.EmployeeDetail.department,'employee_id': temp2_earliest.EmployeeDetail.id, 'name': temp2_earliest.EmployeeDetail.name, 'capture_time_earliest': temp2_earliest.capture_time, 'capture_location_earliest': temp2_earliest.capture_location.terminal_name, 'capture_time_latest': temp2_latest.capture_time, 'capture_location_latest':temp2_latest.capture_location.terminal_name, 'working_hours':str(working_hours), 'date':date_range_individual, 'temperature_max':temp4_max, 'temperature_min':temp4_min}

                temp_data_list.append(temp_employee_daily_info)
            except Exception as d:
                print("d Exception")
                print(d)
    all_employee_details = EmployeeDetail.objects.all()
    all_employee_details_dict = []
    for all_employee_detail in all_employee_details:
        all_employee_details_dict.append(model_to_dict(all_employee_detail))

    unique_department_list = EmployeeDetail.objects.order_by().values('department').distinct()
    unique_department_dict_list = []
    for unique_department in unique_department_list:
        unique_department_dict_list.append(unique_department)

    #MUST BE A LIST OF DICTIONARY
    context= {
        'data': temp_data_list,
        'all_emp': all_employee_details_dict,
        'department': unique_department_dict_list,
        'date_tag': date_tag,
        'date_tag2': date_tag_to,
        'date_range': date_range_dict_list
        }

    return render(request, 'timeAttendance/deviceDetails.html', context)
@csrf_exempt
@login_required
def Detailed_view(request):
    temp_data_list=[]
    if request.GET.get('employee_id') and request.GET.get('date'):
        employee_id = request.GET['employee_id']
        date = request.GET['date']

        query_set = list(EmployeeAttendance.objects.filter(EmployeeDetail_id = employee_id, capture_time__contains = str(date[0:10])))

        print("\n\n")
        for employee in query_set:
            temp_employee = {'name':str(employee.EmployeeDetail.name), 'id':str(employee.EmployeeDetail.id), 'capture_time':str(employee.capture_time), 'capture_location':str(employee.capture_location.terminal_name), 'temperature':str(employee.temperature)}
            temp_data_list.append(temp_employee)
            print(str(employee.EmployeeDetail.name) + "  " + str(employee.EmployeeDetail.id) + "  " + str(employee.capture_time) + "  " + str(employee.capture_location_id))
        print("\n\n")

    context= {
        'data': temp_data_list
        }

    return render(request, 'timeAttendance/detailedView.html', context)

"""
Im fucking lazy, I dont want to properly implement this method. I dont want to create a new database table just to hold strager's data.
The temperature information is just concatinated into the file name. This will not cause any problem for now, but will surely fuck up the
system once the amount of picture grows bigger over time. Please dont be mad. Oh and the name for the capture location is just a string
that i hard coded in the view file.
5/5/2020
FIXED :)
"""
@csrf_exempt
@login_required
def Stranger_view(request):
    stranger_list_dict = []
    terminal_name_list_dict = []


    distinct_teminals = StrangerDetails.objects.values('capture_location_id').distinct()
    for terminal in distinct_teminals:
        terminal_name = TerminalDetails.objects.filter(terminal_id = terminal['capture_location_id'])
        print(terminal_name[0].terminal_name)
        temp_terminal_name = {
                    "terminal_name": terminal_name[0].terminal_name,
        }

        print(temp_terminal_name)

        terminal_name_list_dict.append(temp_terminal_name)

    strangers = StrangerDetails.objects.all()
    for stranger in strangers:
        stranger_dict = {
                    "temperature": stranger.temperature,
                    "capture_time": stranger.capture_time,
                    "image_name": stranger.image_name,
                    "capture_location": stranger.capture_location.terminal_name
        }

        stranger_list_dict.append(stranger_dict)

    #MUST BE A LIST OF DICTIONARY
    try:
        reverse_list = reversed(stranger_list_dict)
        context= {
            'strangers': reverse_list,
            'terminal_names': terminal_name_list_dict
            }
    except Exception as e:
        print(e)

    return render(request, 'timeAttendance/strangerView.html', context)

@csrf_exempt
@login_required
def Print_view(request):

    context= {
            'table': request.POST["table_hidden"],
            'organization': request.POST["organization_hidden"],
            'department' : request.POST["department_hidden"],
            'date_start': request.POST["date_start_hidden"],
            'date_end':request.POST["date_end_hidden"],
            'shift_start': request.POST["shift_start_hidden"],
            'shift_end': request.POST["shift_end_hidden"],
            'hour_start': request.POST["hour_start_hidden"],
            'employee_name': request.POST["employee_name_hidden"],
            'temperature': request.POST["temperature_hidden"]
            }
    
    return render(request, 'timeAttendance/print.html', context)
    
