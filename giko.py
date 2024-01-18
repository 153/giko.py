#!/usr/bin/python3

import datetime
import getopt
import sys
import time

import socketio
import requests

from plugin import blackjack
from plugin import craps
from plugin import bank
from plugin import memo
from plugin import quotes

sio = socketio.Client()
session = requests.Session()

Users = {}
my_id = ""
pid = ""
api = ""
anon_name = "Spy"

plugins = ["blackjack", "craps", "bank", "quotes", "memo",]

def main():
    global api
    server = "play.gikopoi.com"
    area = "for"
    room = "bar"
    character = "naito_npc"
    name = "giko.py"
    password = ""

    if "poipoi" in server:
        api = "/api"

    logon(server, area, room, character, name, password)

    print([Users[u] for u in Users])

    while True:
        val = input()
        sio.emit("user-msg", val)
        pass
    
    return

def logon(server, area, room, character, name,  password):
    global my_id
    global pid

    url = "https://" + server
    wss = "ws://" + server + ":8085/socket.io/"
    print("[+] Connect")
    connect_value = {"userName": name,
                     "characterId": character,
                     "areaId": area,
                     "roomId": room,
                     "password": password}
    connect_response = session.post(f"{url}{api}/login", connect_value)
    connect_json = connect_response.json()
    if not connect_json['isLoginSuccessful'] is True:
        print("Not able to login")
        return

    print("[+] Connected")
    user_id = str(connect_json['userId'])
    pid = str(connect_json['privateUserId'])
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
    
    my_id = user_id
    print(f"id: {user_id}")
    sio.connect(wss, headers={"private-user-id": pid})
    time.sleep(2)
    get_users(session, url, area, room)
    return

def get_users(s:requests.Session, server, area, room):
    print("[+] Get Rooms Users")
    val = s.get(f'{server}{api}/areas/{area}/rooms/{room}',
                headers={"Authentication": f"Bearer {pid}"})
    if(val.status_code == 200):
        users = val.json()['connectedUsers'];
        print("[+] found {}".format(str(len(users))))
        for user in users:
            global Users
            Users[user['id']] = user['name']
            if len(user['name']) == 0:
                Users[user['id']] = anon_name

def get_username(userid):
    try:
        return Users[userid]
    except:
        return anon_name

def send_message(msg):
    sio.emit("user-msg", msg)
    sio.emit("user-msg", "")
    
@sio.event
def connect():
    print("[+] I'm connected!")

@sio.event
def connect_error(data):
    print("[+] The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('server-user-joined-room')
def user_join(data):
    try:
        global Users
        user = [data['id'], data['name']]
        if data['id'] == my_id:
            return
        if len(data['name']) == 0:
            user[1] = anon_name
        Users[user[0]] = user[1]
        tstamp = datetime.datetime.now().strftime("%H:%M")
        print(tstamp, "{} joined".format(user[1]))
        
    except Exception as ex:
        print(ex)
        pass
    
    print([Users[u] for u in Users])

@sio.on('server-user-left-room')
def user_leave(data):
    try:
        global Users
        tstamp = datetime.datetime.now().strftime("%H:%M")
        print(tstamp, "{} left".format(Users[data]))
        del Users[data]
        
    except Exception as ex:
        print(ex)
        pass

    print([Users[u] for u in Users])
        
    
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
    
    if "◇" in namespace:
        namespace = namespace.replace("◇", "◆")
    tstamp = datetime.datetime.now().strftime("%H:%M")
    print('{} < {} > {}'.format(tstamp, author, namespace))
    
    for i in plugins:
        cmd = getattr(eval(i), "cmd")
        output.append(cmd(author, namespace))
    output = [i for i in output if i]
    if len(output):
        # need to rewrite list compression for multi-line messages
        
        if isinstance(output[0], list):
            output = [o for oo in output for o in oo]
                            
        if len(output):
            for o in output:
                send_message(o)
                time.sleep(1)


if __name__ == "__main__":
    main()
