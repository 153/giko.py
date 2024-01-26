#!/usr/bin/python3

import asyncio
import os
import time
import threading

outfn = "./irc/irc.rizon.net/#gikopoi/out"
infn = "./irc/irc.rizon.net/#gikopoi/in"

NICK = "gikobot"
logfile = []
outq = {}
modified = 0
lastread = int(time.time())

def cmd(player, msg):
    if msg.startswith("!"):
        return
    with open(infn, "a") as sender:
        sender.write(f"<{player}> {msg} \n")

def queued_msgs():
    global lastread
    if lastread < modified:
        qd = [outq[i] for i in outq if i > lastread]
        qd = [i for i in qd if not i.startswith(f"<{NICK}>")]
        lastread = modified
        if len(qd): print(qd)
        return qd

def get_change():
    global logfile
    global modified

    while True:
        last_modified = round(os.stat(outfn).st_mtime)
        if last_modified == modified:
            pass
        else:
            with open(outfn, "r") as test:
                test = test.read().splitlines()
            if len(test) == 1:
                pass
            test = test[len(logfile):]
            logfile += test
            modified = last_modified
            yield from test
                    
        time.sleep(0.5)

def printer():
    while True:
        for i in get_change():
            if len(i) < 5:
                continue
            elif i[11] == "<":
                i = i.split()
                outq[int(i[0])] = " ".join(i[1:])
                
            
b = threading.Thread(target=printer)
b.start()

print("IRC relay plugin loaded")
