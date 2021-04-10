import time
import json
import sqlite3
from sqlite3 import Error
from datetime import datetime
import requests as requests_import
from requests.auth import HTTPBasicAuth

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_guest(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM guestmanagementapp_guestdetails")

    rows = cur.fetchall()

    return(rows)

def select_all_terminal(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM timeAttendance_terminaldetails")

    rows = cur.fetchall()

    return(rows)

def main():
    database = r"db.sqlite3"

    # create a database connection
    conn = create_connection(database)
    x=10
    while x<100:
        current_time = str(datetime.now().strftime('%H:%M'))
        with conn:

            try:
                print(select_all_terminal(conn)[1])
                print(select_all_guest(conn)[0])
                print("\n")
                print(current_time)
            except:
                print("no guest")

            if(str(datetime.now().strftime('%H:%M')) == '00:00'):
                terminals = select_all_terminal(conn)
                guests = select_all_guest(conn)
                for terminal in terminals:
                    if (terminal[0] != 0):
                        for guest in guests:
                            url = "http://"+terminal[1]+"/action/EditPerson"

                            headers = {
                                'Content-Type': "application/json",
                                'User-Agent': "PostmanRuntime/7.16.3",
                                'Accept': "*/*",
                                'Cache-Control': "no-cache",
                                'Postman-Token': "299fa413-9e09-4776-ab1d-5dae8c1ad2e7,95df307a-1643-4b35-b8fd-db3ed2e78a60",
                                'Host': terminal[1],
                                'Accept-Encoding': "gzip, deflate",
                                'Content-Length': "",
                                'Connection': "keep-alive",
                                'cache-control': "no-cache"
                                }

                            body = {
                                    "operator": "EditPerson",
                					"info": {
                					"DeviceID":terminal[0],
                					"IdType":0,
                					"CustomizeID":guest[7],
                					"PersonType": 1
                                    		}

                                    }

                            response = requests_import.request("POST", url, headers=headers, auth=HTTPBasicAuth("admin", "admin"), json=body)
                            json_data = response.text
                            data = json.loads(json_data)
                            print(data['info']['Result'])

                time.sleep(60)


            time.sleep(10)

if __name__ == '__main__':
    main()
