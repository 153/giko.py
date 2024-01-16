memodb = "memos.txt"

def cmd(player, msg):
    global outbox
    output = []
    msg = msg.split()
    commands = ["!mail", "!help"]

    if player in outbox:
        mc = len(outbox[player])
        for n, i in enumerate(outbox[player]):
            email = f"{player}: ({n+1}/{mc}) {i}"
            output.append(email)
        del outbox[player]
        writememos()
            
    if msg[0] in commands:
        if msg[0] == "!help":
            output.append("Memo commands: !mail <username> || <message> (seperate username from message with || )")
        elif msg[0] == "!mail":
            output.append(sendmail(player, msg[1:]))
    return output

def line_to_memo(line):
    if isinstance(line, str):
        line = line.split(" ")
    pos = line.index("||")
    send_to = " ".join(line[:pos])
    email = " ".join(line[int(pos + 1):])
    email = [send_to, email]
    return email

def sendmail(sender, message):
    global outbox
    if "||" not in message:
        return "Syntax: !mail <username> || <message>, eg !mail Archduke || Hello"

    email = line_to_memo(message)
    send_to = email[0]
    
    if send_to in outbox:
        if len(outbox[send_to]) >= 5:
            return "Sorry, outbox full."
        outbox[send_to].append(email[1])
    else:
        outbox[send_to] = [email[1]]
    writememos()
    return "Message queued for " + send_to

def writememos():
    memolist = []
    for m in outbox:
        for n in outbox[m]:
            memolist.append(" || ".join([m, n]))
    memolist = "\n".join(memolist)
    with open(memodb, "w") as memofile:
        memofile.write(memolist)

def loadmemos():
    global outbox
    outbox = {}
    
    with open(memodb) as memofile:
        memofile = memofile.read().splitlines()
    for m in memofile:
        if len(m.strip()) == 0:
            pass
        email = line_to_memo(m)
        send_to, email = email[0], email[1]
        if send_to not in outbox:
            outbox[send_to] = []
        outbox[send_to].append(email)
    return outbox
    
outbox = loadmemos()
print("Memo plugin loaded.")
