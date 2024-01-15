#!/bin/env python3
# Thanks Kafli!

import socketio
import requests
import datetime
import getopt
import sys
import time

class User:
    def __init__(self,name,userId):
        self.name = name
        self.userId = userId

Users = []

name = 'GikoPlayer'
room = 'silo'
sio = socketio.Client()


MSG = "user-msg"
MOVE = "user-move"

def main():
    global name
    global room
    try:
        opts, args = getopt.getopt(sys.argv[1:],"n:r:v",["name=","room=","verbose"])
    except getopt.getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    for o,a in opts:
        if o in ("-n","--name"):
            print("[?] Name {}".format(a))
            name = a
        elif o in ("-r","--room"):
            print("[?] Room {}".format(a))
            room = a
        else:
            print("{} : not valid".format(a))

    with requests.Session() as s:
        print("[+] Connect");
        connect_value = {'userName':name,'characterId':"kimono_shii",'areaId':"for",'roomId':room,'password':""}
        connect_response = s.post('https://play.gikopoi.com/login',connect_value)
        print(connect_response.text)
        connect_json = connect_response.json()
        print(connect_json)
        if connect_json['isLoginSuccessful'] == True:
            getUsers(s,room)
            print("[+] Connected")
            userId = str(connect_json['userId'])
            privateUserId = str(connect_json['privateUserId'])
            version = str(connect_json['appVersion'])


            send = datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S %Z (Central European Standard Time)')+" "+userId+" window.EXPECTED_SERVER_VERSION: "+version+" loginMessage.appVersion: "+version+" DIFFERENT: false"
            
            print(send)
            logToServer(s,send)
            print("id {} / pid {}".format(userId,privateUserId))
            sio.connect('https://play.gikopoi.com/',headers={"private-user-id":privateUserId})
            print("[+] Sio : ", sio.sid)

            time.sleep(2)
            for i in range(4):
                sio.emit(MOVE,"left")
                time.sleep(1)

            while(True):
                val = input()
                sio.emit(MSG,val)
                pass

def logToServer(s:requests.Session,msg):
    ret = s.post('https://play.gikopoi.com/client-log',data=msg.encode('utf-8'),headers={'Content-Type': 'text/plain'});
    print(ret.text)

def getUsers(s:requests.Session, room):
    print("[+] Get Rooms Users")
    val = s.get('https://play.gikopoi.com/areas/for/rooms/{}'.format(room));

    if(val.status_code == 200):
        users = val.json()['connectedUsers'];
        print("[+] found {}".format(str(len(users))))
        for user in users:
            Users.append(User(user['name'],user['id']))

def getUserName(userId):
    try:
        return next(obj for obj in Users if obj.userId == userId).name
    except:
        return "Not found :"
            
@sio.event
def connect():
    print("I'm connected!")
    time.sleep(2)

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('server-user-joined-room')
def user_join(data):
    try:
        u = User(data['name'],data['id'])
        Users.append(u)
        print("{} joined".format(u.name))
        time.sleep(1)
        if(u.name != name):
            sio.emit(MSG,"hello {}".format(u.name.split("◆")[0]))
        sio.emit(MSG,'')
    except Exception as ex:
        print(ex)
        pass

@sio.on('server-msg')
def server_msg(event,namespace):
    print('Msg {} {}'.format(getUserName(event),namespace))


if __name__ == '__main__':
    main()
