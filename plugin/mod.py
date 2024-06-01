import copy
import re
import requests
import time

from . import bank

with open("secret.txt", "r") as secret:
    secret = secret.read().splitlines()[0].strip()

site = "https://play.gikopoi.com/"
ulist = site + "user-list"
kick = site + "kick-ip"
ban = site + "ban-ip"
login = {"pwd": secret}
whitelist = ["giko.py", "Archduke", "issue maker"]
white_id = []

users = {}
ips = {}

def cmd(player, msg):
    output = []
    msg2 = msg.split()
    commands = ["!kickname", "!kickid", "!banname", "!banid",
                "!banlist", "!baninfo", "!test"]
    if msg2[0] in commands:
        target = msg[(len(msg2[0]) + 1):]
        
        if msg2[0] == "!kickname":
            output.append(handle_user(player, "kick", target))
        elif msg2[0] == "!kickid":
            output.append(handle_user(player, "kick", None, target))
        elif msg2[0] == "!banname":
            return False
            output.append(handle_user(player, "ban", target))
        elif msg2[0] == "!banid":
            return False
            output.append(handle_user(player, "ban", None, target))
        elif msg2[0] == "!banlist":
            output.append(ban_list())
        elif msg2[0] == "!baninfo":
            if len(msg2) > 1:
                output.append(ban_info(msg2[1]))
            else:
                output.append(ban_list())
        if msg2[0] == "!test":
            get_users()
            print(users)
            print("\n\n")
            print(ips)
        return output

def time_since(bantime):
    now = int(time.time())
    diff = now - int(bantime)
    consts = [1, 1, 60, 3600, 86400, 604800, 2629746, 31556952]
    abbrv  = ['', 's', 'm', 'h', 'd', 'w', 'm', 'y']
    output = []
    for n, i in enumerate(consts):
        if i > diff:
            tmp = diff
            output.append(str(tmp//consts[n-1]) + abbrv[n-1])
            if abbrv[n-1] == 's':
                break
            while tmp >= consts[n-1]:
                tmp -= consts[n-1]
            if tmp//consts[n-2] != 0:
                output.append(str(tmp//consts[n-2]) + abbrv[n-2])
            break
    return "".join(output)

def ban_log(ip="", name="", player=""):
    now = str(int(time.time()))
    with open("data/bans.txt", "r") as bans:
        bans = bans.read().splitlines()
    bans.append(" ".join([ip, now, name, "\t", player]))
    bans = "\n".join(bans)
    with open("data/bans.txt", "w") as banlist:
        banlist = banlist.write(bans)

def ban_list(loud=1):
    output = []
    blist = []
    with open("./data/bans.txt", "r") as bans:
        bans = bans.read().splitlines()
    for n, b in enumerate(bans):
        b = b.split("\t")
        b[0] = b[0].split()
        if len(b[0]) > 3:
            b[0][2] = " ".join(b[0][2:])
        b = [*b[0], b[1]]
        blist.append(b)
        output.append(f"(#{n+1}) {b[2]}, "
                      f"{time_since(b[1])} ago")
    if loud:
        return " ".join(output)
    else:
        return blist

def ban_info(banno):
    try:
        banno = int(banno)
    except:
        return "Please enter a valid integer, eg 1, 5, 11, etc"

    bt = []
    
    with open("./data/bans.txt", "r") as bans:
        bans = bans.read().splitlines()
    if banno > len(bans):
        return "We don't have that many bans in our database: " \
            + f"we only have {len(bans)} bans, not {banno}."
    for n, b in enumerate(bans):
        b = b.split("\t")
        b[0] = b[0].split()
        if len(b[0]) > 3:
            b[0][2] = " ".join(b[0][2:])
        b = [*b[0], b[1]]
        if (n+1) == banno:
            bt = b
            break
        
    bt = f"(#{banno}) {bt[2]} was banned " \
        + f"{time_since(b[1])} ago by {bt[-1]}"
    return bt

    
def get_users():
    global white_id
    auth = copy.deepcopy(login)
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
            if users[u][0] == username:
                attempted_user.append(u)
        if len(attempted_user) == 0:
            return "Sorry, I was unable to find someone with that exact name."
        elif len(attempted_user) > 1:
            return "There are multiple people with that name. " \
                + "Please use kick-by-id feature rather than " \
                + "kick-by-name."
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
        elif mode == "ban":
            return ban_user(player, attempted_user)

def kick_user(player, uid):
    balance = bank.check_balance(player, 1)
    auth = copy.deepcopy(login)
    
    for i in users[uid][1]:
        auth[i] = True
    if uid not in users:
        return "Unspecified error"
    if balance < 100:
        return f"Sorry {player}, you need at least 100 gikocoins to " \
            + f"kick someone. You only have {balance} gikocoins."
    bank.deduct(player, 100)
    kicker = requests.post(kick, data=auth)
    print(kicker.text)
    return f"{player} successfully kicked {users[uid][0]} and now has " \
    + f"{balance - 100} gikocoins remaining."

def ban_user(player, uid):
    balance = bank.check_balance(player, 1)
    auth = copy.deepcopy(login)
        
    for i in users[uid][1]:
        auth[i] = True

    if uid not in users:
        return "Unspecified error"
    if balance < 1000:
        return f"Sorry {player}, you need at least 1000 gikocoins to " \
            + f"ban someone. You only have {balance} gikocoins."
    bank.deduct(player, 1000)
    kicker = requests.post(ban, data=auth)
    print(kicker.text)
    for i in users[uid][1]:
        ban_log(i, users[uid][0], player)
    return f"{player} successfully banned {users[uid][0]} and now has " \
    + f"{balance - 1000} gikocoins remaining."

def unban_user(player, banned):
    blist = ban_list(0)
    print(blist)

def fmt_userlist(data):
    global users
    global ips
    
    data = data.split("<input type")[2:-1]
    for d in data:
        pattern = "name='([a-z0-9\-]+)'"
        name = d.split("  &lt;")[1].split("&gt;")[-2]
        ip = d.split("streaming: ")[-1].split("</label>")[0][2:]
        if "," in ip:
            ip = ip.split(",")
        else:
            ip = [ip]
        uid = re.findall(pattern, d)[0]
        for i in ip:
            if i in ips:
                ips[i].append([uid, name])
            else:
                ips[i] = [[uid, name]]
        users[uid] = [name, ip]

print("Mod plugin loaded.")
