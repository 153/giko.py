import random
import re

karmadb = {}

def cmd(author, msg):
    output = []

    if msg[-2:] == "++":
        output = change_karma(msg[:-2], "plus")
        return [output]
    elif msg[-2:] == "--":
        output = change_karma(msg[:-2], "minus")
        return [output]
        
    else:
        if " " in msg:
            msg = msg.split(" ")
        else:
            msg = [msg]
        if msg[0] == "!karma":
            output = view_karma(" ".join(msg[1:]))
            return [output]
        if msg[0] == "!best":
            return [best()]
        if msg[0] == "!worst":
            return [worst()]

def ld_karma():
    global karmadb
    with open("./data/karma.txt") as numbers:
        numbers = numbers.read().strip().splitlines()
    for n in numbers:
        n = n.split(" ")
        if len(n) > 2:
            entry = " ".join(n[:-1])
        else:
            entry = n[0]
        num = int(n[-1])
        karmadb[entry] = num
    return karmadb

def change_karma(term, mode):
    ld_karma()
    term = term.lower()
    
    if "  " in term:
        term = re.sub(r"\s+", " ", term)
    term = term.strip()

    if term[0] == "!" or term[0] == "#":
        return
    if mode == "plus":
        if term in karmadb:
            karmadb[term] += 1
        else:
            karmadb[term] = 1
    elif mode == "minus":
        if term in karmadb:
            karmadb[term] -= 1
        else:
            karmadb[term] = -1
    upd_karma()
    return f"{term} now has {karmadb[term]} pts"
        
def view_karma(term):
    ld_karma()
    term = term.lower()
    if term in karmadb:
        return f"{term} has {karmadb[term]} points"

def upd_karma():
    op = []
    for k in karmadb:
        op.append(" ".join([str(k), str(karmadb[k])]))
    if len(op) > 1:
        out = "\n".join(op)
    else:
        out = str(op)
    with open("./data/karma.txt", "w") as outf:
        outf.write(out)
    ld_karma()

def best():
    ld_karma()
    karmal = []
    for k in karmadb:
        karmal.append([k, int(karmadb[k])])
    karmal.sort(key=lambda x: x[1])
    out = "The best things: "
    for k in karmal[::-1][:5]:
        out += f"{k[0]} ({k[1]}), "
    return out[:-1]
        
        
def worst():
    ld_karma()
    karmal = []
    for k in karmadb:
        karmal.append([k, int(karmadb[k])])
    karmal.sort(key=lambda x: x[1])
    out = "The worst things: "
    for k in karmal[:5]:
        out += f"{k[0]} ({k[1]}), "
    return out[:-2]    
    
ld_karma()
print("karma loaded")
