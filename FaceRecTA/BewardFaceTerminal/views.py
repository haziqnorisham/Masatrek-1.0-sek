from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import uuid
import os
from django.template import Context, loader

import sqlite3
from sqlite3 import Error
from io import StringIO
from PIL import Image
import cv2
import numpy as np
from timeAttendance.models import StrangerDetails
from guestmanagementapp.models import GuestDetails, GuestAttendance, GuestBlacklist

sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS attendence (
                                        id integer,
                                        name text NOT NULL,
                                        enter_time text
                                    ); """

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_entry(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO attendence(id,name,enter_time)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute('insert into timeAttendance_employeeattendance(capture_time,capture_location_id,EmployeeDetail_id, temperature) VALUES (?,?,?,?)', project)
    return cur.lastrowid

@csrf_exempt
def index(request):

    print("ENTERED SNAP REQUEST")

    json_data = request.read()
    data = json.loads(json_data)
    a = data['SanpPic']
    response_data = {}
    response_data['SanpPic'] = a

    stranger = StrangerDetails()
    stranger.capture_time = str(data['info']['CreateTime'])




    try:
        response_data['temperature'] = data['info']['Temperature']
        stranger.temperature = data['info']['Temperature']
    except:
        response_data['temperature'] = "00.0"
        stranger.temperature = "00.0"
    print("type = " + str(data['info']['DeviceID']))

    #print("\n\n\n")
    #print("TEMPERATURE : " + str(response_data['temperature']))
    #print("\n\n\n")

    new_string = str(a[22:])
    try:
        imgdata = base64.b64decode(new_string)
        id = str(uuid.uuid1())
        #filename = 'C:/Users/Haziq/Desktop'+id+'.jpg'  # I assume you have a way of picking unique filenames
        filename = 'static/img' + str(data['info']['CreateTime']).replace(":","-") +'.jpg'  # I assume you have a way of picking unique filenames
        stranger.capture_location_id = int(data['info']['DeviceID'])
        stranger.image_name = 'img' + str(data['info']['CreateTime']).replace(":","-") +'.jpg'
        stranger.save()
        with open(filename, 'wb') as f:
            f.write(imgdata)
    except Exception as e:
        print(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def index2(request):

    json_data = request.read()
    data = json.loads(json_data)
    a = data['info']
    response_data = {}
    response_data['info'] = a
    print(response_data['info'])
    print()
    print('PERSON ID = ' + str(response_data['info']['PersonID']))
    print('IdCard = ' + str(response_data['info']['PersonUUID']))
    print('CUSTOMIZE ID = ' + str(response_data['info']['CustomizeID']))
    print('IdCard = ' + str(response_data['info']['IdCard']))
    print('DEVICE ID = ' + str(response_data['info']['DeviceID']))
    print('NAME = ' + str(response_data['info']['Name']))
    print('ENTER TIME = ' + str(response_data['info']['CreateTime']))
    try:
        print('TEMPERATURE = ' + str(response_data['info']['Temperature']))
    except:
        response_data['info']['Temperature'] = 0.00
    print()
    try:
        if(response_data['info']['VerifyStatus'] == 2):
            guest = GuestDetails.objects.get(nric=int(response_data['info']['IdCard']))
            guest_attendance = GuestBlacklist()
            guest_attendance.capture_time           = str(response_data['info']['CreateTime'])
            guest_attendance.capture_location_id    = int(response_data['info']['DeviceID'])
            guest_attendance.GuestDetails_id        = int(response_data['info']['IdCard'])
            guest_attendance.temperature            = str(response_data['info']['Temperature'])
            guest_attendance.save()
            print("guest_saved")
        else:
            guest = GuestDetails.objects.get(nric=int(response_data['info']['IdCard']))
            guest_attendance = GuestAttendance()
            guest_attendance.capture_time           = str(response_data['info']['CreateTime'])
            guest_attendance.capture_location_id    = int(response_data['info']['DeviceID'])
            guest_attendance.GuestDetails_id        = int(response_data['info']['IdCard'])
            guest_attendance.temperature            = str(response_data['info']['Temperature'])
            guest_attendance.save()
            print("guest_saved")
    except Exception as e:
        print(e)
        conn = create_connection(r"db.sqlite3")
        with conn:
            if conn is not None:
                # create projects table
                p=None
                #create_table(conn, sql_create_projects_table)
            else:
                print("Error! cannot create the database connection.")

            project = [str(response_data['info']['CreateTime']), str(response_data['info']['DeviceID']), str(response_data['info']['PersonUUID']), str(response_data['info']['Temperature'])]
            project_id = insert_entry(conn, project)

    print(project_id)

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def index3(request):
    json_data = request.read()
    data = json.loads(json_data)
    a = data['info']
    response_data = {}
    response_data['info'] = a
    #print(type(a))
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def home(request):
    #json_data = request.read()
    #data = json.loads(json_data)
    #a = data['info']
    #response_data = {}
    #response_data['info'] = a
    #print(type(a))
    template = loader.get_template("mysite/page/home.html")
    return HttpResponse(template.render)

@csrf_exempt
def homePage(request):
    return render(request, 'home.html')

@csrf_exempt
def dev_page(request):
    return render(request, 'dev_page.html')
