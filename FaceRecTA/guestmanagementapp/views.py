import os
import json
import base64
from datetime import date, datetime, timedelta
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth
import requests as requests_import
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from timeAttendance.models import TerminalDetails, StrangerDetails
from guestmanagementapp.models import GuestDetails, GuestAttendance, GuestBlacklist
from django.contrib.auth.decorators import login_required

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

@login_required
def home(requests):
    terminal_details_list_dict = []

    terminal_details_model = TerminalDetails.objects.all()
    try:
        sranger_list_3_dict = []
        stranger_list_3 = StrangerDetails.objects.all().order_by("-id")
        for strng in stranger_list_3:
            sranger_list_3_dict.append(model_to_dict(strng))



        latest_stranger_id = StrangerDetails.objects.all().order_by("-id")[0]
        latest_stranger_id = model_to_dict(latest_stranger_id)
        print(latest_stranger_id)

        for i, terminal_detail_model in enumerate(terminal_details_model):
            if model_to_dict(terminal_detail_model)["terminal_id"] != 0:
                terminal_details_list_dict.append(model_to_dict(terminal_detail_model))



        context= {
            "latest_strangers" : sranger_list_3_dict,
            "terminal_details" : terminal_details_list_dict,
            "latest_stranger_id" : latest_stranger_id
            }
        return render(requests, "guestmanagementapp/home.html", context)
    except Exception as e:
        return render(requests, "guestmanagementapp/home.html")
        print(e)



@login_required
def register_guest(requests):

    try:
        temp_list = []
        if requests.method == 'GET' and 'img_name' in requests.GET:
            messages.info(requests, 'Image selected, please enter guest details.')
            image_requested = {'image_requested' : requests.GET['img_name'] }
            temp_list.append(image_requested)
        else:
            image_requested = {'image_requested' : 'select image' }
            temp_list.append(image_requested)
    except Exception as e:
        print(e)
    image_list = []
    files = os.listdir("static")
    for file in files:
        image_list.append({"name" : str(file)})

    context= {
        'image_names': image_list,
        'image_requested': temp_list
        }

    return render(requests, "guestmanagementapp/register_guest.html", context)

@login_required
def register_guest_proc(requests):
    if requests.method == 'POST':

        if (requests.POST["image_name"] == ""):
            messages.error(requests, 'No image selected, guest not registered')
        else:
            guest = GuestDetails()
            try:#Try connecting to all terminal.
                #Ensure all terminal can be reached to avoid mismatch database of masatrek and device's database.
                try:
                    check_all_terminal_connection()
                except Exception as e:
                    raise SystemError('One or more terminal failed connect, Please ensure all terminal is connected!')

                try:
                    guest.id               = int(requests.POST["nric"])
                    guest.name             = requests.POST["name"]
                    guest.image_name       = requests.POST["image_name"]
                    guest.phone_number     = int(requests.POST["phone"])
                    guest.nric             = int(requests.POST["nric"])
                    guest.comment          = requests.POST["comment"]
                    guest.status           = 0
                except:
                    raise ValueError('Please ensure all the input is corect!')

                try:#try registering into terminal
                    terminal_details_object_list = TerminalDetails.objects.all()

                    has_error = 0
                    for terminal_details_object in terminal_details_object_list:
                        if( terminal_details_object.terminal_id != 0 ):

                            image_name = guest.image_name
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
                                        "IdType":0,
                                        "PersonType": 0,
                                        "Name":str(guest.name),
                                        "Gender":0,
                                        "CardType":0,
                                        "IdCard":str(guest.nric),
                                        "CustomizeID":guest.nric,
                                        "Native": "",
                                        #"Tempvalid": 1,
                                        "Tempvalid": 0,
                                        #"ValidEnd ": expired_date_time.strftime('%Y-%m-%dT%H:%M:%S'),
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
                except Exception as e:
                    raise SystemError('Failed registering the guest into the terminal. Contact administrator!')

                try:
                    guest.save()
                    messages.success(requests, 'Guest succesfully registered')
                except:
                    raise SystemError('Failed to save the guest to masatrek database. Contact administrotor!')

            except Exception as e:
                print(e)
                messages.error(requests, str(type(e)) +"    "+ str(e))


    response = redirect('/guestmanagement/registerguest/')
    return response

@login_required
def guest_list(requests):

    guest_list_dict = []
    try:
        guests = GuestDetails.objects.all()

        for guest in guests:
            guest_dict = {
                        "name": guest.name,
                        "id": guest.id,
                        "image_name": guest.image_name,
                        "phone_number": guest.phone_number,
                        "nric": guest.nric,
                        "comment": guest.comment
            }
            if(guest.status == 0):
                guest_list_dict.append(guest_dict)
    except Exception as e:
        messages.info(requests, e)

    context={
        "guest_list": guest_list_dict
    }

    return render(requests, "guestmanagementapp/guest_list.html", context)

@login_required
def guest_list_proc(requests):
    if requests.method == 'POST':
        try:#check all terminal is connected
            check_all_terminal_connection()
            try:#check if guest is present in database
                guest = GuestDetails.objects.get(id=int(requests.POST["guest_id"]))
                guest.status = 0
                guest.save()
            except Exception as e:
                print(e)
                messages.error(requests, "User does not exist in database. contact administrator!")

            GuestAttendance.objects.filter(GuestDetails_id = int(requests.POST["guest_id"])).delete
            terminal_objects = TerminalDetails.objects.all()
            for terminal in terminal_objects:
                if(terminal.terminal_ip != "0.0.0.0"):
                    url = "http://"+terminal.terminal_ip+"/action/DeletePerson"

                    body = {
                            "operator": "DeletePerson",
                            "info": {
                                "DeviceID": int(terminal.terminal_id),
                                "TotalNum": 1,
                                "IdType": 0,
                                "CustomizeID": [int(guest.nric)],
                                }
                            }

                    headers = {
                                'Content-Type': "application/json",
                                'Authorization': "Basic YWRtaW46YWRtaW4=",
                                'User-Agent': "PostmanRuntime/7.17.1",
                                'Accept': "*/*",
                                'Cache-Control': "no-cache",
                                'Postman-Token': "246f59d4-ccb8-4bec-a3cd-3018a46a685e,1e6fcb78-072c-405c-936a-85c58d4d6960",
                                'Host': str(terminal.terminal_id),
                                'Accept-Encoding': "gzip, deflate",
                                'Content-Length': "169",
                                'Connection': "keep-alive",
                                'cache-control': "no-cache"
                                }
                    try:
                        response = requests_import.request("POST", url, json=body, headers=headers)
                        messages.success(requests, "Succesfully removed guest from terminal " + str(terminal.terminal_name))
                        guest.delete()
                    except Exception as e:
                        print(e)
                        messages.error(requests, e)
            try:
                guest.delete()
            except Exception as e:
                print(e)
                messages.error(requests, "Unable to delete guest from database, contact administrator!")

        except Exception as e:
            print(e)
            messages.error(requests, "One or more terminal cannot be reached. Please ensure all terminal is connected!")

    response = redirect('/guestmanagement/guestlist/')
    return response

@login_required
def guest_attendance(requests):

    guest_attendance_list_dict = []
    date_dict = []
    if "date_selector" in requests.GET and requests.GET["date_selector"] != '':
        id_for_today = GuestAttendance.objects.filter(capture_time__contains = requests.GET["date_selector"]).values('GuestDetails_id').distinct()
        date_dict.append({"date": requests.GET["date_selector"]})
        print(id_for_today)
    else:
        id_for_today = GuestAttendance.objects.filter(capture_time__contains = str(datetime.today().strftime('%Y-%m-%d'))).values('GuestDetails_id').distinct()
        date_dict.append({"date": str(datetime.today().strftime('%Y-%m-%d'))})
        print(id_for_today)
    for guest_id in id_for_today:
        try:
            guest_attendance_for_today = GuestAttendance.objects.filter(GuestDetails_id = guest_id['GuestDetails_id'] ,capture_time__contains = str(date_dict[0]['date']))

            earliest_capture = guest_attendance_for_today.earliest('capture_time')
            latest_capture = guest_attendance_for_today.latest('capture_time')

        except Exception as e:
            print(e)

        try:
            guest_dict = {
                        "name": earliest_capture.GuestDetails.name,
                        "nric": earliest_capture.GuestDetails.nric,
                        "img_name": earliest_capture.GuestDetails.image_name,
                        "enter_time": earliest_capture.capture_time,
                        "enter_location": earliest_capture.capture_location.terminal_name,
                        "enter_temperature": earliest_capture.temperature,
                        "exit_time": latest_capture.capture_time,
                        "exit_location": latest_capture.capture_location.terminal_name,
                        "exit_temperature": latest_capture.temperature
            }
            guest_attendance_list_dict.append(guest_dict)
        except Exception as e:
            print(e)
    context={
        "guest_attendance_list": guest_attendance_list_dict,
        "selected_date" : date_dict
    }

    return render(requests, "guestmanagementapp/guest_attendance.html", context)

@login_required
def terminal(requests):
    test_val = 0
    if ((requests.method == 'POST') and (requests.POST["button"] == "sync")):
        print(requests.POST["button"])
        if 'terminal_ip' not in requests.POST:
            messages.error(requests, "Please selected terminal to sync")
        else:
            ip_address_list = requests.POST.getlist("terminal_ip")
            guest_objects = GuestDetails.objects.filter(status=0)

            for ip_address in ip_address_list:
                for guest in guest_objects:

                    try:
                        picjson = None
                        image_name = guest.image_name
                        with open("static/"+image_name, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        picjson = "data:image/jpeg;base64,"+encoded_string.decode("utf-8")
                    except Exception as e:
                        print(e)
                    try:
                        terminal_object = TerminalDetails.objects.get(terminal_ip = ip_address)
                        print(terminal_object.terminal_id)
                    except Exception as e:
                        messages.error(requests, "Unable to connect to selected terminal")

                    try:
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
                                    "DeviceID":int(terminal_object.terminal_id),
                                    "IdType":0,
                                    "PersonType": 0,
                                    "Name":str(guest.name),
                                    "Gender":0,
                                    "CardType":0,
                                    "IdCard":guest.nric,
                                    "CustomizeID":guest.nric,
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
                        messages.success(requests, "Successfully sync to terminal " + terminal_object.terminal_name)
                    except Exception as e:
                        messages.error(requests, e)
                        print(e)
                        break

    if ((requests.method == 'POST') and (requests.POST["button"] == "del")):
        if 'terminal_ip' not in requests.POST:
            messages.error(requests, "Please selected terminal delete")
        else:
            try:
                ip_address_list = requests.POST.getlist("terminal_ip")
                for ip_address in ip_address_list:
                    terminal_object = TerminalDetails.objects.get(terminal_ip = ip_address)
                    body2 = {
                            "operator": "Subscribe",
                            "info": {
                                "DeviceID": int(terminal_object.terminal_id),
                                "Num": 2,
                                "Topics":["Snap", "Verify"],
                                "SubscribeAddr":"http://"+"0.0.0.0"+":80",
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
                        'Host': terminal_object.terminal_ip,
                        'Accept-Encoding': "gzip, deflate",
                        'Content-Length': "392",
                        'Connection': "keep-alive",
                        'cache-control': "no-cache"
                        }

                    url2 = "http://"+ip_address+"/action/Subscribe"
                    requests_import.request("POST", url2, json=body2, headers=headers2)
                    terminal_object.delete()
                    messages.success(requests, "Succesfully deleted the terminal")
            except Except as e:
                print(e)
                messages.error(requests, e)


    response = redirect('/guestmanagement/')
    return response

def ajax_check_new_stranger(requests):
    try:
        id_from_dom = requests.GET["current_stranger_id"]
        latest_stranger = StrangerDetails.objects.all().order_by("-id")[0]
        latest_blacklist = GuestBlacklist.objects.all().order_by("-id")[0]


        latest_stranger_datetime = datetime.strptime(latest_stranger.capture_time, '%Y-%m-%dT%H:%M:%S')
        latest_blacklist_datetime = datetime.strptime(latest_blacklist.capture_time, '%Y-%m-%dT%H:%M:%S')

        if(latest_blacklist_datetime > latest_stranger_datetime):
            if(int(latest_blacklist.id) != int(id_from_dom)):
                data = {
                    'type' : 0,
                    'new_user' : 1,
                    'user_id' : int(latest_blacklist.id),
                    'user_name' : latest_blacklist.GuestDetails.name,
                    'user_nric' : latest_blacklist.GuestDetails.nric,
                    'user_phone': latest_blacklist.GuestDetails.phone_number,
                    'capture_time' : latest_blacklist.capture_time,
                    'temperature' : latest_blacklist.temperature,
                    'image_name' : latest_blacklist.GuestDetails.image_name,
                    'capture_location_id' : latest_blacklist.capture_location.terminal_id,
                    'capture_location_name' : latest_blacklist.capture_location.terminal_name,
                }
            else:
                data = {
                    'new_user' : 0,
                    'user_id' : int(latest_stranger.id)
                }
        else:
            if(int(latest_stranger.id) != int(id_from_dom)):
                data = {
                    'type' : 1,
                    'new_user' : 1,
                    'user_id' : int(latest_stranger.id),
                    'capture_time' : latest_stranger.capture_time,
                    'temperature' : latest_stranger.temperature,
                    'image_name' : latest_stranger.image_name,
                    'capture_location_id' : latest_stranger.capture_location.terminal_id,
                    'capture_location_name' : latest_stranger.capture_location.terminal_name,
                }
            else:
                data = {
                    'new_user' : 0,
                    'user_id' : int(latest_stranger.id)
                }
        return JsonResponse(data)
    except Exception as e:
        if(int(latest_stranger.id) != int(id_from_dom)):
            data = {
                'type' : 1,
                'new_user' : 1,
                'user_id' : int(latest_stranger.id),
                'capture_time' : latest_stranger.capture_time,
                'temperature' : latest_stranger.temperature,
                'image_name' : latest_stranger.image_name,
                'capture_location_id' : latest_stranger.capture_location.terminal_id,
                'capture_location_name' : latest_stranger.capture_location.terminal_name,
            }
        else:
            data = {
                'new_user' : 0,
                'user_id' : int(latest_stranger.id)
            }
        print(e)
        return JsonResponse(data)



def register_guest_proc_home(requests):

    if requests.method == 'POST':
        try:#check all terminal is online
            check_all_terminal_connection()

            try:#check all post data is valid
                image_name          = requests.POST["modal_image"]
                name                = requests.POST["modal_name"]
                nric                = requests.POST["modal_nric"]
                phone               = requests.POST["modal_phone"]
                duration            = requests.POST["modal_duration"]
                comment             = requests.POST["modal_comment"]

                temperature         = requests.POST["modal_temperature"]
                capture_time        = requests.POST["modal_capture_time"]
                capture_location_id = requests.POST["modal_terminal_id"]

                try:#check post data can be assigned to object & calculate validity date
                    guest = GuestDetails()
                    guest.id            = int(nric)
                    guest.name          = name
                    guest.image_name    = image_name
                    guest.phone_number  = phone
                    guest.nric          = int(nric)
                    guest.comment       = comment
                    guest.status        = 0

                    #assign capture_time to datetime object
                    capture_date_time = datetime.strptime(capture_time, '%Y-%m-%dT%H:%M:%S')
                    #add the n hours to the time stamp of the image
                    expired_date_time = capture_date_time + timedelta(hours=int(duration))
                    '''
                    #sanity check for time conversion
                    print("\n\n")
                    print(capture_date_time.strftime('%Y-%m-%dT%H:%M:%S'))
                    print(expired_date_time.strftime('%Y-%m-%dT%H:%M:%S'))
                    print("\n\n")
                    '''
                    guest.valid_until   = expired_date_time.strftime('%Y-%m-%dT%H:%M:%S')

                    try:#try registering into terminal
                        terminal_details_object_list = TerminalDetails.objects.all()

                        has_error = 0
                        for terminal_details_object in terminal_details_object_list:
                            if( terminal_details_object.terminal_id != 0 ):

                                image_name = guest.image_name
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
                                            "IdType":0,
                                            "PersonType": 0,
                                            "Name":str(guest.name),
                                            "Gender":0,
                                            "CardType":0,
                                            "IdCard":str(guest.nric),
                                            "CustomizeID":guest.nric,
                                            "Native": "",
                                            #"Tempvalid": 1,
                                            "Tempvalid": 0,
                                            #"ValidEnd ": expired_date_time.strftime('%Y-%m-%dT%H:%M:%S'),
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
                    except Exception as e:
                        raise e

                    try:#Check that object can be cleanly saved
                        guest.save()
                        messages.success(requests, 'Succesfully registered guest, The guest visit will expire on : ' + expired_date_time.strftime('%d-%m-%Y  %I:%M %p'))
                        try:#check that attendance can be generated based on image snapshpo
                            guest2 = GuestDetails.objects.get(nric = int(nric))
                            #print("\n\n")
                            #print(model_to_dict(guest2))
                            #print(nric)
                            #print("\n\n")
                            attendance = GuestAttendance()
                            attendance.temperature = temperature
                            attendance.capture_time = capture_date_time.strftime('%Y-%m-%dT%H:%M:%S')
                            attendance.capture_location_id = int(capture_location_id)
                            attendance.GuestDetails_id = guest2.id
                            attendance.save()
                            messages.success(requests, 'Succesfully created attendance for registered guest')
                        except Exception as e:
                            print(e)
                            messages.error(requests, 'Error creating attendance for registered guest!')
                    except Exception as e:
                        print(e)
                        messages.error(requests, 'Unable to save guest object to the database, please ensure that all field information is valid!')

                except Exception as e:
                    print(e)
                    messages.error(requests, 'Cant assign field value to GuestDetails object, please ensure that all field information is valid!')

            except Exception as e:
                print(e)
                messages.error(requests, 'Input field issues, please ensure that all field information is valid!')

        except Exception as e:
            print(e)
            messages.error(requests, 'One or more terminal disconnected, please ensure that all termianl is connected!')
    response = redirect('/guestmanagement/')
    return response

@login_required
def guest_print(request):

    context= {
            'table': request.POST["table_hidden"],
            'name': request.POST["name_hidden"],
            'nric' : request.POST["nric_hidden"],
            'temperature': request.POST["temperature_hidden"],
            'date':request.POST["date_hidden"]
            }
    
    return render(request, 'guestmanagementapp/print.html', context)