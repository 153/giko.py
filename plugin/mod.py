import re
import requests

from . import bank

with open("secret.txt", "r") as secret:
    secret = secret.read().splitlines()[0].strip()

site = "https://play.gikopoi.com/"
ulist = site + "user-list"
kick = site + "kick"
auth = {"pwd": secret}
whitelist = ["giko.py", "Archduke", "issue maker"]
white_id = []

users = {}
ips = {}

def cmd(player, msg):
    output = []
    msg2 = msg.split()
    commands = ["!kickname", "!kickid"]
    if msg2[0] in commands:
        target = msg[(len(msg2[0]) + 1):]
        
        if msg2[0] == "!kickname":
            output.append(handle_user(player, "kick", target))
        elif msg2[0] == "!kickid":
            output.append(handle_user(player, "kick", None, target))
        return output 

def main():
    get_users()
    
def get_users():
    global white_id
    
    r = requests.post(ulist, data=auth)
    fmt_userlist(r.text)
    
    for ip in ips:
        for i in ips[ip]:
            if i[1] in whitelist:
                white_id += [i[0] for i in ips[ip]]
    white_id = list(set(white_id))

def handle_user(player, mode, username="", uid=""):
    get_users()
    
    attempted_user = []
    if username:
        if username in whitelist:
            return "Sorry, that user is whitelisted."
        for u in users:
            if users[u] == username:
                attempted_user.append(u)
        if len(attempted_user) == 0:
            return "Sorry, I was unable to find someone with that exact name."
        elif len(attempted_user) > 1:
            return "There are multiple people with that name. " \
                + "Please use ban-by-id feature rather than " \
                + "ban-by-name."
        else:
            attempted_user = attempted_user[0]
    elif len(uid):
        attempted_user = uid
        
    if attempted_user in white_id:
        return "Sorry, that user is whitelisted."
    
    if not attempted_user in users:
        return "Sorry, we couldn't find that user."
    else:
        if mode == "kick":
            return kick_user(player, attempted_user)

def kick_user(player, uid):
    balance = bank.check_balance(player, 1)
    auth[uid] = True
    if uid not in users:
        return "Unspecified error"
    if balance < 100:
        return f"Sorry {player}, you need at least 100 gikocoins to " \
            + f"ban someone. You only have {balance} gikocoins."
    bank.deduct(player, 100)
    kicker = requests.post(kick, data=auth)
    return f"{player} successfully kicked {users[uid]} and now has " \
    + f"{balance - 100} gikocoins remaining."

def fmt_userlist(data):
    global users
    global ips
    
    data = data.split("<input type")[2:-1]
    for d in data:
        pattern = "name='([a-z0-9\-]+)'"
        name = d.split("  &lt;")[1].split("&gt;")[-2]
        ip = d.split("streaming: ")[-1].split("</label>")[0][2:]
        uid = re.findall(pattern, d)[0]
        if ip in ips:
            ips[ip].append([uid, name])
        else:
            ips[ip] = [[uid, name]]
        users[uid] = name

print("Mod plugin loaded.")

