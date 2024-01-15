#!/usr/bin/python3

import datetime
import getopt
import sys
import time
import importlib

import socketio
import requests

import blackjack
import bank

sio = socketio.Client()
session = requests.Session()

Users = {}
my_id = ""
anon_name = "Spy"

plugins = ["blackjack", "bank"]

def main():
    server = "play.gikopoi.com"
    area = "for"
    room = "bar"
    character = "naito_npc"
    name = "giko.py"
    password = ""
    
    logon(server, area, room, character, name, password)

    while True:
        val = input()
        sio.emit("user-msg", val)
        pass
    
    return

def logon(server, area, room, character, name,  password):
    url = "https://" + server
    wss = "ws://" + server + ":8085/socket.io/"
    print("[+] Connect")
    connect_value = {"userName": name,
                     "characterId": character,
                     "areaId": area,
                     "roomId": room,
                     "password": password}
    connect_response = session.post(f"{url}/login", connect_value)
    connect_json = connect_response.json()
    print(connect_json)
    if not connect_json['isLoginSuccessful'] is True:
        print("Not able to login")
        return

    print("[+] Connected")
    user_id = str(connect_json['userId'])
    p_uid = str(connect_json['privateUserId'])
    version = str(connect_json["appVersion"])
    
    t_form = "%a %b %d %Y %H:%M:%S %Z (%z)"
    timestamp = datetime.datetime.now().strftime(t_form)
    send = " ".join([timestamp, user_id,
                     "window.EXPECTED_SERVER_VERSION:", version,
                     "loginMessage.appVersion:", version,
                     "DIFFERENT: false"])
    ret = session.post(f"{url}/client-log",
                       data = send,
                       headers = {"Content-Type": "text/plain"})
    print(ret.text)
    
    global my_id
    my_id = user_id
    print(f"id: {user_id}")
    sio.connect(wss, headers={"private-user-id": p_uid})

    get_users(session, url, area, room)
    print([Users[k] for k in Users])
    return

def get_users(s:requests.Session, server, area, room):
    print("[+] Get Rooms Users")
    val = s.get(f'{server}/areas/{area}/rooms/{room}')
    if(val.status_code == 200):
        users = val.json()['connectedUsers'];
        print("[+] found {}".format(str(len(users))))
        for user in users:
            Users[user['id']] = user['name']

def get_username(userid):
    try:
        return Users[userid]
    except:
        return "Anonymous"

def send_message(msg):
    sio.emit("user-msg", msg)
    sio.emit("user-msg", "")
    
@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('server-user-joined-room')
def user_join(data):
    try:
        user = [data['id'], data['name']]
        Users[user[0]] = user[1]
        print("{} joined".format(user[1]))
        time.sleep(1)
        
    except Exception as ex:
        print(ex)
        pass

@sio.on('server-msg')
def server_msg(event,namespace):
    author = get_username(event)
    output = []

    if author == "":
        author = anon_name
    if event == my_id:
        return
    if len(namespace) == 0:
        return
    
    print('< {} > {}'.format(author, namespace))
    
    for i in plugins:
        cmd = getattr(eval(i), "cmd")
        output.append(cmd(author, namespace))
    output = [i for i in output if i]
    if len(output):
        if isinstance(output[0], list):
            output = [o for oo in output for o in oo]
                            
        if len(output):
            for o in output:
                send_message(o)
                time.sleep(1)


if __name__ == "__main__":
    main()
