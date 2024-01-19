#!/usr/bin/python3
# written by wav 2024-01-19

import re
import time
import threading
import datetime
import socketio
import asyncio
import requests
from random import choices, random, choice
from colored import Fore, Back, Style
from colorama import just_fix_windows_console
just_fix_windows_console()

NAME = 'gipy'
ROOM = 'admin'
AREA = 'for'

anonName = "Spy"
Users = {}
textgenapi = "http://127.0.0.1:5000/v1/completions"
historyLength = 30
messageHistory = []

def GetUsername(userid):
    try:
        return Users[userid]
    except:
        return anonName

def FormatMessage(author, content):
    return author + ": " + content + "\n"

class Logger: # ive never made a logger b4 but i felt like it could be useful :]
    def Log(self, txt, logtype = "INFO"):
        out = self.Timestamp()
        logcolours = {"INFO": Fore.blue, "ISSUE": Fore.light_red }
        out += f" {logcolours[logtype]}{logtype}    "
        out += Style.reset
        out += txt
        
        print(out)
    
    def Timestamp(self):
        return Fore.cyan + "{:%y-%m-%d %H:%M:%S}".format(datetime.datetime.now())

class Bot:
    def __init__(self, name, area, room):
        self.url = "https://play.gikopoi.com"
        self.api = f"{self.url}" # append /api to the url for gikopoipoi & hupoi
        self.ws = "ws://play.gikopoi.com:8085/socket.io/"
        self.name = name
        self.character = "naito_npc"
        self.area = area
        self.room = room
        self.Logger = Logger()
        self.sio = socketio.AsyncClient()
        self.session = requests.Session()
        self.messageProbability = 1.0
        self.messageActivateProbability = 0.02 # chance for any message to activate the bot
        self.activeDuration = 300 # how much time for high probability after activated
        self.lastActive = 0
        self.initialPrompt = ""
        self.generationParams = {
            "max_tokens": 100,
            "temperature": 0.9,
            "top_p": 0.98,
            "typical_p": 1.0,
            "repetition_penalty": 1.11,
            "top_k": 50,
            "top_a": 0.0,
            "tfs": 1.0,
            "stop": ["###", "\n", "</s>"],
            "seed": -1,
            "stream": False,
        }

        
        # event callbacks - idk if theres a better way to do this... YOLO!
        @self.sio.event
        async def connect():
            await self.OnConnected()
        
        @self.sio.event
        async def connect_error():
            await self.OnConnectionError()
        
        @self.sio.event
        async def disconnect():
            await self.OnDisconnected()
        
        @self.sio.on('server-user-joined-room')
        async def user_join(user):
            await self.OnUserJoined(user)
        
        @self.sio.on('server-user-left-room')
        async def user_leave(user):
            await self.OnUserLeft(user)
        
        @self.sio.on('server-msg')
        async def server_msg(user, message):
            await self.OnMessage(user, message)
        
        
        # connect and log in
        asyncio.run(self.Login())
    
    async def Login(self):
        connectionparameters = {"userName": self.name, "characterId": self.character, "areaId": self.area, "roomId": self.room, "password": ""}
        response = self.session.post(f"{self.api}/login", connectionparameters).json()
        if not response['isLoginSuccessful'] is True:
            self.Logger.Log("login attempt was unsuccessful!", "ISSUE")
            return
        
        self.Logger.Log("Connected!")
        self.id = str(response['userId'])
        self.pid = str(response['privateUserId'])
        
        version = str(response["appVersion"])
        s = " ".join([
            datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S %Z (%z)"), self.id,
            "window.EXPECTED_SERVER_VERSION:", version,
            "loginMessage.appVersion:", version,
            "DIFFERENT: false"
        ])
        self.session.post(f"{self.url}/client-log", data = s, headers = {"Content-Type": "text/plain"})
        self.Logger.Log(f"userId= {self.id}")
        
        await self.sio.connect(self.ws, headers={"private-user-id": self.pid})
        global Users
        Users = self.GetUsers()
        return
    
    def GetUsers(self):
        userlist = {}
        val = self.session.get(f'{self.api}/areas/{self.area}/rooms/{self.room}', headers={"Authentication": f"Bearer {self.pid}"})
        if(val.status_code == 200):
            users = val.json()['connectedUsers']
            self.Logger.Log(f"Users found: {len(users)}")
            for user in users:
                userlist[user['id']] = user['name']
                if len(user['name']) == 0:
                    userlist[user['id']] = anonName
        return userlist
    
    async def OnConnected(self):
        print(self.name)
        
    async def OnConnectionError(self):
        self.Logger.Log("The connection failed!", "ISSUE")
    
    async def OnDisconnected(self):
        self.Logger.Log("Disconnected!")
    
    async def OnUserJoined(self, userdata): # blatantly stole this
        try:
            global Users
            user = [userdata['id'], userdata['name']]
            if userdata['id'] == self.id:
                return
            if len(userdata['name']) == 0:
                user[1] = anonName
            Users[user[0]] = user[1]
            self.Logger.Log(f"{user[1]} joined.")
            
        except Exception as ex:
            print(ex)
            pass
        pass
    
    async def OnUserLeft(self, userdata):
        print(userdata)
        try:
            global Users
            self.Logger.Log(f"{GetUsername(userdata)} left.")
            del Users[userdata]
            
        except Exception as ex:
            print(ex)
            pass
    
    async def OnMessage(self, authorid, message):
        if len(message) == 0:
            return
        if authorid == self.id:
            return
        
        author = GetUsername(authorid)
        author = author.split("◆", 1)[0]
        
        msg = FormatMessage(author, message)
        #cache message history
        global messageHistory
        if len(messageHistory) <= historyLength:
            messageHistory.append(msg)
        else:
            messageHistory.pop(0)
            messageHistory.append(msg)
        
        print(messageHistory)
        
        # if the name of the bot is mentioned without any alphabetic characters on either side OR if prolonged the name like "gipyyyyy"
        if re.search(fr'(^|[^a-zA-Z]){self.name}([^a-zA-Z]|$)', message, re.IGNORECASE) or re.search(fr'(^|[^a-zA-Z]){self.name}[a-zA-Z]+{self.name[-1]}([^a-zA-Z]|$)', message, re.IGNORECASE):
            print("substring found")
            self.lastActive = int(time.time())
            await self.SendMessage(messageHistory)
        elif int(time.time()) - self.lastActive > self.activeDuration:
            if random() <= self.messageProbability:
                await self.SendMessage(messageHistory)
        else:
            if random() <= self.messageActivateProbability:
                await self.SendMessage(messageHistory)
        
    async def Prompt(self, messagehistory):
        try:
            data = self.generationParams.copy()
            data["prompt"] = self.initialPrompt + "\n"
            for message in messagehistory:
                data["prompt"] = data["prompt"] + message
            data["prompt"] = data["prompt"] + self.name + ":"
            print(data)
            response = requests.post(textgenapi, headers={"Content-Type": "application/json"}, json=data, verify=False)
            print(response.json())
            time.sleep(0.1)
            return response.json()["choices"][0]["text"]
        except:
            return ""
            
    async def SendMessage(self, messagehistory):
        response = await self.Prompt(messagehistory)
        if response != "":
            self.Logger.Log(response)
            await self.sio.emit("user-msg", response)
        
    
    


if __name__ == '__main__': 
    client = Bot(NAME, AREA, ROOM)
