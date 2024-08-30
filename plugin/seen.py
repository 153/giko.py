import time

seenfn = "./data/seen.txt"
seens = {}

def ld():
    global seens
    with open(seenfn, "r") as seenfile:
        seenfile = seenfile.read().splitlines()
    for entry in seenfile:
        entry = entry.split()
        if len(entry) > 2:
            entry = [entry[0], " ".join(entry[1:])]
        seens[entry[1]] = entry[0]

def upd(player):
    global seens
    now = int(time.time())
    seens[player] = now
    db = []
    for s in seens:
        db.append(" ".join([str(seens[s]), s]))
    db = "\n".join(db)
    with open(seenfn, "w") as newf:
        newf.write(db)
    ld()

def cmd(player, msg):
    msg = msg.split()
    output = []
    if msg[0] == "!seen":
        if len(msg) > 1:
            if len(msg) > 2:
                output.append(lookup(" ".join(msg[1:])))
            else:
                output.append(lookup(msg[1]))
    return output
            
def length(vidl):
    diff = int(vidl)
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

def lookup(player):
    ld()
    now = int(time.time())
    if player not in seens:
        return f"Sorry, I don't know when {player} was last here!"
    try:
        diff = now - int(seens[player])
    except:
        return
    diff = length(diff)
    return f"{player} was last seen {diff} ago"    

ld()
print("Seen plugin loaded")
