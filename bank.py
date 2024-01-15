import os

bankfn = "bank.txt"
moneys = {}
bankfile = []

if not os.path.exists(bankfn):
    with open(bankfn, "w") as bankfile:
        bankfile.write("Archduke 9999")
with open(bankfn, "r") as bankfile:
    bankfile = bankfile.read().splitlines()

for entry in bankfile:
    entry = entry.split()
    if len(entry) > 2:
        entry = [" ".join(entry[:-1]), entry[-1]]
    moneys[entry[0]] = int(entry[1])

def cmd(player, msg):
    msg = msg.split()
    bank_cmds = ["!wealth", "!balance", "!create", "!send", "!help"]
    output = []

    if msg[0] in bank_cmds:
        if msg[0] == "!wealth":
            output.append(wealth())
        elif msg[0] == "!balance":
            if len(msg) > 2:
                msg[1] = " ".join(msg[1:])
                output.append(check_balance(msg[1]))
            else:
                output.append(check_balance(player))
        elif msg[0] == "!create":
            output.append(add_entry(player))
        elif msg[0] == "!send":
            print(player, msg[2], msg[1])
            if len(msg) < 3:
                output.append("!send <amount> <playername>")
                return output
            elif len(msg) > 3:
                msg[2] = " ".join(msg[2:])
            try:
                msg[1] = int(msg[1])
            except:
                output.append("!send <amount> <playername>")
                return output
            print(player, msg[2], msg[1])
            output.append(send_money(player, msg[2], msg[1]))
        elif msg[0] == "!help":
            output.append("Bank commands: !wealth , !create , !balance <player> , !send <amount> <player>")

    return output
        
        
                
        
def write_file():
    bankfile = []
    for m in moneys:
        bankfile.append(" ".join([m, str(moneys[m])]))
    with open(bankfn, "w") as newbank:
        newbank.write("\n".join(bankfile))

def check_balance(player, silent=0):
    if player in moneys:
        if silent:
            return int(moneys[player])
        return f"{player} has {moneys[player]} gikocoins"
    if silent:
        return 0
    return add_entry(player)
    
def add_entry(player, silent=0):
    if not player in moneys:
        moneys[player] = 20
        write_file()
        if silent: return
        return "Welcome to GikoBank, you now have 20 GikoCoins"
    if silent: return
    return "You already have an account and you have" + check_balance(player)

def deposit(player, amt):
    moneys[player] += amt
    write_file()

def deduct(player, amt):
    moneys[player] -= amt
    write_file()
        
def send_money(sender="", target="", amt=0, silent=0):
    amt = int(amt)
    if amt < 1:
        return
    elif sender not in moneys:
        if not silent:
            return "You don't have any gikocoins"
        else: return
    elif target not in moneys:
        if not silent:
            return f"{target} doesn't have any gikocoins"
        else: return
    elif amt > moneys[sender]:
        if not silent:
            return f"Sorry, you don't have {amt}, you have {moneys[sender]}"
        else: return
    else:
        moneys[sender] -= amt
        moneys[target] += amt
        write_file()
        if not silent:
            return f"You sent {target} {amt} gikocoins"
        return

def wealth():
    index = [[m, moneys[m]] for m in moneys]
    index.sort(key = lambda x: x[1], reverse=True)
    index = index[:5]
    index = " / ".join([": ".join([i[0], str(i[1])]) for i in index])
    return "Top 5: " + index

print("Bank plugin loaded")
