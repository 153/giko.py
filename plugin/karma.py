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
        if msg[0] == "!karma":
            output = view_karma(" ".join(msg[1:]))
            return [output]

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

def change_karma(term, mode):
    global karmadb
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
print("karma loaded")
