import os
import json
import base64
import requests as requests_import
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from requests.auth import HTTPBasicAuth
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required, user_passes_test
from timeAttendance.models import EmployeeDetail, TerminalDetails, EmployeeAttendance, StrangerDetails, Departments
from guestmanagementapp.models import GuestDetails, GuestAttendance
from django.shortcuts import redirect
from django.contrib.auth.models import User

def exist_in_any_terminal(employee_id):
    terminal_details_object_list = TerminalDetails.objects.all()
    for terminal_details_object in terminal_details_object_list:
        if( terminal_details_object.terminal_id != 0 ):
            url = "http://"+terminal_details_object.terminal_ip+"/action/SearchPerson"

            headers = {
                'Content-Type': "application/json",
                'User-Agent': "PostmanRuntime/7.16.3",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                'Host': terminal_details_object.terminal_ip,
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }

            body = {
                    "operator": "SearchPerson",
                    "info": {
                        "DeviceID":terminal_details_object.terminal_id,
                        "SearchType":0,
                        "SearchID":employee_id,
                        "Picture":0
                        }
                    }

            response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"), json=body)
            json_data = response.text
            data = json.loads(json_data)
            if ("Result" not in data["info"].keys()):
                return True

def check_all_terminal_connection():

    terminal_details_object_list = TerminalDetails.objects.all()

    for terminal_details_object in terminal_details_object_list:
        if( terminal_details_object.terminal_id != 0 ):

            url = "http://"+terminal_details_object.terminal_ip+"/action/GetSysParam"

            headers = {
                        'Authorization': 'Basic YWRtaW46YWRtaW4='
                        }

            response = requests_import.request("POST", url, headers=headers)

            json_data = response.text
            data = json.loads(json_data)
            if ( data['info']['DeviceID'] == terminal_details_object.terminal_id ):
                print("TERMINAL CONNECTED AND VALIDATED TO BE CORRECT")
            else:
                raise Exception("TERMINAL DATA MISSMATCH")

def get_all_employee_id():

    id_list = []
    terminal_details_list = TerminalDetails.objects.values_list('terminal_id', 'terminal_ip')

    for terminal_detail in terminal_details_list:

        if(terminal_detail[1] != "0.0.0.0"):

            url = "http://"+terminal_detail[1]+"/action/SearchPersonList"

            body = {
                    "operator": "SearchPersonList",
                    "info": {
                        "DeviceID": int(terminal_detail[0]),
                        "BeginTime":"2010-06-01T00:00:00",
                        "EndTime":"2050-06-19T23:59:59",
                        "RequestCount":1000,
                        "Gender":2,
                        "Age":"0-100",
                        "MjCardNo":0,
                        "Name":"",
                        "BeginNO":0,
                        "Picture": 0
                    }
                }

            headers = {
                        'Content-Type': "application/json",
                        'Authorization': "Basic YWRtaW46YWRtaW4=",
                        'User-Agent': "PostmanRuntime/7.17.1",
                        'Accept': "*/*",
                        'Cache-Control': "no-cache",
                        'Postman-Token': "246f59d4-ccb8-4bec-a3cd-3018a46a685e,1e6fcb78-072c-405c-936a-85c58d4d6960",
                        'Host': terminal_detail[1],
                        'Accept-Encoding': "gzip, deflate",
                        'Content-Length': "169",
                        'Connection': "keep-alive",
                        'cache-control': "no-cache"
                        }

            response = requests_import.request("POST", url, json=body, headers=headers)

            json_data = response.text
            data = json.loads(json_data)
            a = data['info']['List']
            for entry in a:
                #print (entry['IdCard'])
                id_list.append(entry['IdCard'])

    return id_list

@login_required
def home(requests):

    terminal_dict_list = []


    terminal_obj_list = TerminalDetails.objects.all()
    for index,terminal_obj in enumerate(terminal_obj_list):
        temp_model = model_to_dict(terminal_obj)
        temp_model["counter"] = index
        terminal_dict_list.append(temp_model)


    context= {
        "terminal_dict_list" : terminal_dict_list
        }

    return render(requests, "administrator/administrator_home.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def registration(requests):

    registered = {"registered" : False}
    if requests.method == 'POST':

        data = requests.POST.copy()

        print("username = " + data.get('username'))
        print("email = " + data.get('email'))
        print("passsword = " + data.get('password'))

        user = User.objects.create_user(data.get('username'), password=data.get('password'))
        user.is_staff=True
        user.email = data.get('email')

        if(data.get('is_superuser') == "on"):
            print("admin : True")
            user.is_superuser=True
        else:
            print("admin : False")
            user.is_superuser=False

        user.save()
        registered["registered"] = True
        messages.success(requests, 'User Registered')

    context = {"registered" : registered}

    return render(requests, "administrator/registration.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync(requests):

    ip_address_list = []
    ip_address_list2 = []
    deviceID_list = []

    if requests.method == 'GET':
        data = requests.GET.copy()
        if "sync" in requests.GET.keys():
            try:
                #ip_address_list = data.get("ip_list").splitlines()
                print(requests.GET.keys())

                for key in requests.GET.keys():

                    print(str(data.get(key)) == "sync")
                    if (str(data.get(key)) == "sync"):
                        t=None
                    else:
                        print(data.get(key))
                        ip_address_list.append(data.get(key))

                for ip_address in ip_address_list:
                    a2 = None

                    #username = this.username
                    #username = request.POST.get("username")
                    #password = request.POST.get("password")

                    #url = "http://192.168.0.33/action/GetSysParam"
                    url = "http://"+ip_address+"/action/GetSysParam"

                    headers = {
                        'Content-Type': "application/json",
                        'User-Agent': "PostmanRuntime/7.16.3",
                        'Accept': "*/*",
                        'Cache-Control': "no-cache",
                        'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                        'Host': ip_address,
                        'Accept-Encoding': "gzip, deflate",
                        'Content-Length': "",
                        'Connection': "keep-alive",
                        'cache-control': "no-cache"
                        }

                    #response = requests.request("POST", url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))

                    response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"))

                    json_data = response.text
                    data = json.loads(json_data)
                    a2 = data['info']
                    response_data = {}
                    response_data['info'] = a2
                    print(a2["DeviceID"])
                    deviceID_list.append(a2["DeviceID"])

                    encoded_string = None
                    all_employee = EmployeeDetail.objects.all()
                    for employee in all_employee:
                        #print(employee)

                        image_name = employee.image_name
                        with open("static/"+image_name, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                            #print(type(encoded_string))
                        picjson = "data:image/jpeg;base64,"+encoded_string.decode("utf-8")
                        a = None

                        #username = this.username
                        #username = request.POST.get("username")
                        #password = request.POST.get("password")

                        #url = "http://192.168.0.33/action/GetSysParam"
                        url = "http://"+ip_address+"/action/AddPerson"

                        headers = {
                            'Content-Type': "application/json",
                            'User-Agent': "PostmanRuntime/7.16.3",
                            'Accept': "*/*",
                            'Cache-Control': "no-cache",
                            'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                            'Host': ip_address,
                            'Accept-Encoding': "gzip, deflate",
                            'Content-Length': "",
                            'Connection': "keep-alive",
                            'cache-control': "no-cache"
                            }

                        body = {
                                "operator": "AddPerson",
                                "info": {
                                    "DeviceID":int(a2["DeviceID"]),
                                    "IdType":0,
                                    "PersonType": 0,
                                    "Name":str(employee.name),
                                    "Gender":employee.gender,
                                    "CardType":0,
                                    "IdCard":str(employee.id),
                                    "CustomizeID":employee.id,
                                    "Native": "",
                                    "Tempvalid": 0,
                                    " ChannelAuthority0":"1",
                                    " ChannelAuthority1":"1",
                                    " ChannelAuthority2":"1",
                                    " ChannelAuthority3":"1"
                                  },
                                	"picinfo": picjson
                                }

                        #response = requests.request("POST", url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))

                        response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"), json=body)

                        json_data = response.text
                        data = json.loads(json_data)
                        a = data['info']
                        response_data = {}
                        response_data['info'] = a
            except:
                return HttpResponse("ERROR Synching")

        else:
            print(requests.GET.keys())

            for key in requests.GET.keys():
                #print(data.get(key))
                ip_address_list2.append(data.get(key))

            for ip_address in ip_address_list2:
                try:
                    print(ip_address)
                    TerminalDetails.objects.get(terminal_ip=ip_address).delete()
                except:
                    pass


    #return HttpResponse("<h1>Synching Done</h1>")
    return render(requests, "administrator/sync.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def employee_add(requests):

    department_dict_list = []
    department_list = Departments.objects.all()

    for department in department_list:
        temp_dict = {
            'id': department.id,
            'name': department.name
        }
        department_dict_list.append(temp_dict)

    registered = {"registered" : False}
    get_img_name = ''
    if requests.method == 'GET' and 'img_name' in requests.GET:
        get_img_name = requests.GET['img_name']

    temp_list = []

    files = os.listdir("static")
    for file in files:
        temp_list.append({"name" : str(file)})

    temp_list.reverse()

    context= {
        'image': temp_list,
        'registered' : registered,
        'image_name': get_img_name,
        'department_list': department_dict_list
        }

    return render(requests, "administrator/employee_add.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def employee_add_process(requests):

    if requests.method == 'POST':

        #Check connection to all available terminal
        #Check if the user has been previously registered into any one of the terminals
        #Abort operation if user has been previosly registered into any one of the terminals
        try:
            check_all_terminal_connection()
            data = requests.POST.copy()

            if(exist_in_any_terminal(data.get("Employee_ID"))):
                messages.error(requests, 'User has previosly been registered in one or more of the terminals')
                raise Exception('User has previosly been registered in one or more of the terminals')

            #Ensure that all the input data is valid and does not cause an Exception
            #Throw error message is Exception occurs
            try:

                emp = EmployeeDetail()
                emp.name = data.get("Name")
                emp.id = data.get("Employee_ID")

                #this actually the gender checking 0 for male 1 for female
                if (data.get("Employee") == "0"):
                    emp.gender = 0
                else:
                    emp.gender = 1

                emp.image_name = data.get("img_name")
                emp.department = Departments.objects.get(id = data.get("Department"))
                emp.branch = data.get("Branch")
                #status should always be set to zero and only zero, should be changed, stupid decision from previous design
                emp.status = 0

            except Exception as e:
                print(e)
                messages.error(requests, 'Error reading entered data, make sure data is correct')

            #Ensure that employee data is saved cleanly to masatrek's database
            #Throw error message is Exception occurs
            else:
                try:

                    terminal_details_object_list = TerminalDetails.objects.all()

                    has_error = 0
                    for terminal_details_object in terminal_details_object_list:
                        if( terminal_details_object.terminal_id != 0 ):

                            image_name = emp.image_name
                            with open("static/"+image_name, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())

                            picjson = "data:image/jpeg;base64,"+encoded_string.decode("utf-8")


                            url = "http://"+terminal_details_object.terminal_ip+"/action/AddPerson"

                            headers = {
                                'Content-Type': "application/json",
                                'User-Agent': "PostmanRuntime/7.16.3",
                                'Accept': "*/*",
                                'Cache-Control': "no-cache",
                                'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                                'Host': terminal_details_object.terminal_ip,
                                'Accept-Encoding': "gzip, deflate",
                                'Content-Length': "",
                                'Connection': "keep-alive",
                                'cache-control': "no-cache"
                                }

                            body = {
                                    "operator": "AddPerson",
                                    "info": {
                                        "DeviceID":int(terminal_details_object.terminal_id),
                                        "IdType":2,
                                        "PersonType": 0,
                                        "Name":str(emp.name),
                                        "Gender":emp.gender,                                                                                                                      
                                        "PersonUUID":emp.id, 
                                        "Native": "",
                                        "Tempvalid": 0,
                                        " ChannelAuthority0":"1",
                                        " ChannelAuthority1":"1",
                                        " ChannelAuthority2":"1",
                                        " ChannelAuthority3":"1"
                                      },
                                        "picinfo": picjson
                                    }

                            response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"), json=body)
                            json_data = response.text
                            data = json.loads(json_data)
                            print(data['info']['Result'])
                            if(data['info']['Result'] == "Fail"):
                                print("entered Exception")
                                messages.error(requests, "From Terminal : " + str(terminal_details_object.terminal_name) + " Message : " +data['info']['Detail'])
                                has_error = 1


                    if(has_error == 1):
                        raise Exception(data['info']['Detail'])

                    emp.save()
                    messages.success(requests, 'Employee succesfull registered and synced to ALL terminal')

                    try:
                        stranger = StrangerDetails.objects.get(image_name = emp.image_name)
                        employee_attendance = EmployeeAttendance()
                        employee_attendance.capture_time = stranger.capture_time
                        employee_attendance.capture_location_id = stranger.capture_location_id
                        employee_attendance.EmployeeDetail_id = emp.id
                        employee_attendance.temperature = stranger.temperature
                        employee_attendance.save()
                        messages.success(requests, 'Succesfully created employee attendance!')
                    except Exception as e:
                        print(e)
                        messages.error(requests, 'Error creating and saving employee time attendance based on newly registered guest.!')
                except Exception as e:
                    print(e)
                    messages.error(requests, 'Error saving data to the database and syncing to ALL terminal, make sure data is correct')

        except Exception as e:
            print(e)
            messages.error(requests, "ONE or MORE terminal is disconnected! Please ensure ALL terminal is connected befor registering a new employee!")

        #registered["registered"] = True
    response = redirect('/administrator/employee_add/')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_device(requests):

    if requests.method == 'POST':
        data = requests.POST.copy()
        terminal_obj = TerminalDetails()
        terminal_obj.terminal_ip = data.get("ip_address")
        terminal_obj.terminal_name = data.get("device_name")

        ip_address = data.get("ip_address")

        try:
            a = None
            url = "http://"+ip_address+"/action/GetSysParam"
            server_url = "http://"+str(data.get("server_ip_address"))+":80"
            print(server_url)

            headers = {
                'Content-Type': "application/json",
                'User-Agent': "PostmanRuntime/7.16.3",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                'Host': ip_address,
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }

            response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"))

            json_data = response.text
            data = json.loads(json_data)
            a = data['info']
            response_data = {}
            response_data['info'] = a
            print(a["DeviceID"])
            terminal_obj.terminal_id = int(a["DeviceID"])



            body2 = {
                    "operator": "Subscribe",
                    "info": {
                        "DeviceID": int(a["DeviceID"]),
                        "Num": 2,
                        "Topics":["Snap", "Verify"],
                        "SubscribeAddr":server_url,
                        "SubscribeUrl":{"Snap":"/Subscribe/Snap", "Verify":"/Subscribe/Verify", "HeartBeat":"/Subscribe/heartbeat"},
                        "Auth":"Basic",
                        "User": "admin",
                        "Pwd": "admin"
                        }
                    }

            headers2 = {
                'Content-Type': "application/json",
                'Authorization': "Basic YWRtaW46YWRtaW4=",
                'User-Agent': "PostmanRuntime/7.16.3",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Postman-Token': "60ee7fb9-57cd-48c0-9d83-388d78ce51ea,4e2240de-573c-49d0-a6e1-26b8fdc47c15",
                'Host': ip_address,
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "392",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }

            url2 = "http://"+ip_address+"/action/Subscribe"
            requests_import.request("POST", url2, json=body2, headers=headers2)
            terminal_obj.save()
            messages.success(requests, 'Successfully Added Device')
            response = redirect('/administrator/sync_to_all/')
            return response
        except:
            messages.error(requests, 'Failed Adding Device')
    
    return render(requests, "administrator/add_device.html")

@login_required
def employee_list(requests):

    department_dict_list = []
    department_list = Departments.objects.all()

    for department in department_list:
        temp_dict = {
            'id': department.id,
            'name': department.name
        }
        department_dict_list.append(temp_dict)

    employee_dict_list = []
    temp = "Female"

    employee_list = EmployeeDetail.objects.all()
    for employee in employee_list:



        if(employee.gender == 0):
            temp = "Male"
        else:
            temp = "Female"

        employee_dict = {
                    "name": employee.name,
                    "employee_id": employee.id,
                    "gender": temp,
                    "img_name": employee.image_name,
                    "branch": employee.branch,
                    "department": employee.department.name
        }

        if(employee.status == 0):
            employee_dict_list.append(employee_dict)


    context={
        "employee_list": employee_dict_list,
        "department_list": department_dict_list
    }
    return render(requests, "administrator/employee_list.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def employee_delete_process(requests):

    if requests.method == 'POST':
        #Check connection to all terminal
        try:
            check_all_terminal_connection()

            #get POST data and makes sure Employee to delete is present in masatrek database.
            try:

                data = requests.POST.copy()
                print(data.get("employee_id"))

                temp_emp = EmployeeDetail.objects.get(id = data.get("employee_id"))



                terminal_details_list = TerminalDetails.objects.all()

                has_error = 0
                for terminal_detail in terminal_details_list:

                    if(terminal_detail.terminal_id != 0):
                        url = "http://"+terminal_detail.terminal_ip+"/action/DeletePerson"

                        body = {
                                "operator": "DeletePerson",
                                "info": {
                                    "DeviceID": int(terminal_detail.terminal_id),
                                    "TotalNum": 1,
                                    "IdType": 2,
                                    "PersonUUID": [temp_emp.id]
                                    }
                                }

                        headers = {
                                    'Content-Type': "application/json",
                                    'Authorization': "Basic YWRtaW46YWRtaW4=",
                                    'User-Agent': "PostmanRuntime/7.17.1",
                                    'Accept': "*/*",
                                    'Cache-Control': "no-cache",
                                    'Postman-Token': "246f59d4-ccb8-4bec-a3cd-3018a46a685e,1e6fcb78-072c-405c-936a-85c58d4d6960",
                                    'Host': terminal_detail.terminal_ip,
                                    'Accept-Encoding': "gzip, deflate",
                                    'Content-Length': "169",
                                    'Connection': "keep-alive",
                                    'cache-control': "no-cache"
                                    }

                        response = requests_import.request("POST", url, json=body, headers=headers)
                        json_data = response.text
                        data = json.loads(json_data)
                        print(data['info']['Result'])
                        if(data['info']['Result'] == "Fail"):
                            print("entered Exception")
                            messages.error(requests, "From Terminal : " + str(terminal_detail.terminal_name) + " Message : " +data['info']['Detail'])
                            has_error = 1

                if(has_error == 1):
                        raise Exception(data['info']['Detail'])

                temp_emp.delete()
                messages.success(requests, "Succesfully deleted employee from ALL connected terminal!")

            except Exception as e:
                print(e)
                messages.error(requests, "Make sure EMPLOYEE is REGISTERED in MASATREK and sync to ALL terminal before DELETING!")
        except Exception as e:
            messages.error(requests, "ONE or MORE terminal is disconnected! Please ensure ALL terminal is connected befor DELETING an employee!")
            print(e)

    response = redirect('/administrator/employee_list/')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def full_reset(requests):

    EmployeeDetail.objects.all().delete()
    EmployeeAttendance.objects.all().delete()
    StrangerDetails.objects.all().delete()
    GuestDetails.objects.all().delete()
    GuestAttendance.objects.all().delete()


    terminal_details_list = TerminalDetails.objects.values_list('terminal_id', 'terminal_ip')
    for terminal_detail in terminal_details_list:

        print()
        print(terminal_detail[1])
        print(terminal_detail[0])
        print()

        if(terminal_detail[1] != "0.0.0.0"):
            for emp_num in get_all_employee_id():
                url = "http://"+terminal_detail[1]+"/action/DeletePerson"

                body = {
                        "operator": "DeletePerson",
                        "info": {
                            "DeviceID": int(terminal_detail[0]),
                            "TotalNum": 1,
                            "IdType": 0,
                            "CustomizeID": [emp_num]
                            }
                        }

                headers = {
                            'Content-Type': "application/json",
                            'Authorization': "Basic YWRtaW46YWRtaW4=",
                            'User-Agent': "PostmanRuntime/7.17.1",
                            'Accept': "*/*",
                            'Cache-Control': "no-cache",
                            'Postman-Token': "246f59d4-ccb8-4bec-a3cd-3018a46a685e,1e6fcb78-072c-405c-936a-85c58d4d6960",
                            'Host': terminal_detail[1],
                            'Accept-Encoding': "gzip, deflate",
                            'Content-Length': "169",
                            'Connection': "keep-alive",
                            'cache-control': "no-cache"
                            }

                response = requests_import.request("POST", url, json=body, headers=headers)

    TerminalDetails.objects.all().delete()
    temp_term = TerminalDetails()
    temp_term.terminal_id = 0
    temp_term.terminal_ip = "0.0.0.0"
    temp_term.terminal_name = "Terminal Unavailable"
    temp_term.save()

    return render(requests, "administrator/full_reset.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def bld(requests):
    return HttpResponse("<h1>08-05-2020")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ajax_edit_employee(requests):
    try:
        id_from_dom = requests.GET["employee_id"]
        employee = EmployeeDetail.objects.get(id=id_from_dom)
        employee = model_to_dict(employee)
        return JsonResponse(employee)
    except Exception as e:
        print(e)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_employee(requests):

    if requests.method == 'POST':
        try:
            id = requests.POST["modal_id"]
            name = requests.POST["modal_name"]
            gender = requests.POST["modal_gender"]
            department = requests.POST["modal_department"]

            try:

                employee = EmployeeDetail.objects.get(id = id)
                employee.name = name
                employee.gender = int(gender)
                employee.department = Departments.objects.get(id = department)
                try:
                    employee.save()
                    messages.success(requests, "Succesfully updated empoyee data!")
                except Exception as e:
                    print(e)
                    messages.error(requests, "Unable to save form value to Masatrek database, please ensure intpu is valid !")

            except Exception as e:
                print(e)
                messages.error(requests, "Unable to assign form value to Employee objects, please ensure intpu is valid !")

        except Exception as e:
            print(e)
            messages.error(requests, "Unable to read form date, please ensure input is valid !")

    response = redirect('/administrator/employee_list/')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync_to_all(requests):
    #check for all terminal Connection

    try:
        check_all_terminal_connection()
        try:
            all_terminal = TerminalDetails.objects.all()
            all_employee = EmployeeDetail.objects.all()
            try:
                for terminal in all_terminal:
                    if( terminal.terminal_id != 0 ):
                        for employee in all_employee:
                            image_name = employee.image_name
                            with open("static/"+image_name, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())

                            picjson = "data:image/jpeg;base64,"+encoded_string.decode("utf-8")


                            url = "http://"+terminal.terminal_ip+"/action/AddPerson"

                            headers = {
                                'Content-Type': "application/json",
                                'User-Agent': "PostmanRuntime/7.16.3",
                                'Accept': "*/*",
                                'Cache-Control': "no-cache",
                                'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                                'Host': terminal.terminal_ip,
                                'Accept-Encoding': "gzip, deflate",
                                'Content-Length': "",
                                'Connection': "keep-alive",
                                'cache-control': "no-cache"
                                }

                            body = {
                                    "operator": "AddPerson",
                                    "info": {
                                        "DeviceID":int(terminal.terminal_id),
                                        "IdType":2,
                                        "PersonType": 0,
                                        "Name":str(employee.name),
                                        "Gender":employee.gender,
                                        "PersonUUID":employee.id,
                                        "Native": "",
                                        "Tempvalid": 0,
                                        " ChannelAuthority0":"1",
                                        " ChannelAuthority1":"1",
                                        " ChannelAuthority2":"1",
                                        " ChannelAuthority3":"1"
                                      },
                                        "picinfo": picjson
                                    }

                            response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"), json=body)
                            json_data = response.text
                            data = json.loads(json_data)
                            print(data['info']['Result'])
                            if(data['info']['Result'] == "Fail"):
                                print("entered Exception")
                                messages.error(requests, "From Terminal : " + str(terminal.terminal_name) + " Message : " +data['info']['Detail'])
                                has_error = 1
                messages.success(requests, "Done Syncing All")
            except Exception as e:
                print(e)
                messages.error(requests, "Error synching to terminals! || " + str(e))
        except Exception as e:
            print(e)
            messages.error(requests, "Cant get all employee or terminal! || " + str(e))
    except Exception as e:
        print(e)
        messages.error(requests, "some terminal not connected! || " + str(e))
    response = redirect('/administrator/')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def login_list(requests):
    
    if requests.method == 'POST':   
        try:     
            id = requests.POST["user_id"]  
            User.objects.get(id=id).delete()      
        except Exception as e:
            print(e)
    usr_dict_list = []
    users = User.objects.all()
    
    for usr in users:
        usr = model_to_dict(usr)
        usr_dict_list.append(usr)
        print(usr["id"])

    context= {
        'users_login': usr_dict_list
        }

    return render(requests, "administrator/login_list.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_departments(requests):

    # To-Do : Error message when no department found.
    department_list = Departments.objects.all()
    department_dict_list = []

    if len(department_list) > 0:
        for department in department_list:

            department_dict = {
                        "id": department.id,
                        "name": department.name
            }

            department_dict_list.append(department_dict)

        context={
            "department_list": department_dict_list
        }

        return render(requests, "administrator/manage_departments.html", context)
    else:
        messages.error(requests, "No departments found")
        return render(requests, "administrator/manage_departments.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_department_process(requests):

    # To-Do : Check for duplicate department names.

    if requests.method == 'POST':  
      
        data = requests.POST.copy()        

        department = Departments()
        department.name = str(data.get("Department_Name"))
        department.save()
        messages.success(requests, 'New department saved.')

    else:
        i=None
        # To-Do : redirect with erorr message
    
    response = redirect('/administrator/manage_departments')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_department_process(requests):

    if requests.method == 'POST':  
      
        data = requests.POST.copy()        

        department = Departments.objects.get(id = data.get("Delete_Department_Id"))
        department.delete()
        messages.success(requests, 'Department deleted.')

    else:
        i=None
        # To-Do : redirect with erorr message
    
    response = redirect('/administrator/manage_departments')
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_department_process(requests):

    if requests.method == 'POST':  
      
        data = requests.POST.copy()        

        department = Departments.objects.get(id = data.get("Edit_Department_Id"))
        department.name = str(data.get("Department_Name"))
        department.save()
        messages.success(requests, 'Department Edited.')

    else:
        i=None
        # To-Do : redirect with erorr message
    
    response = redirect('/administrator/manage_departments')
    return response
