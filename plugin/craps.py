import random
import copy
from . import bank

state = {}

def cmd(player, msg):
    msg = msg.split()
    commands = ["!craps", "!roll", "!help"]
    output = []

    if msg[0] in commands:
        if msg[0] == "!help":
            output.append("Craps commands: !craps <win/lose> <amt>, "
                          "!roll")
        elif msg[0] == "!craps":
            amt = 1
            if len(msg) > 2:
                try:
                    amt = int(msg[2])
                except:
                    pass
                if amt < 1:
                    amt = 1
                if msg[1] in ["win", "lose"]:
                    output += play("deal", player, msg[1], amt)
                else:
                    output += play("deal", player, "win", amt)
            elif len(msg) == 2:
                if msg[1] in ["win", "lose"]:
                    output += play("deal", player, msg[1], 1)
                else:
                    try:
                        amt = int(msg[1])
                    except:
                        pass
                    if amt < 1:
                        amt = 1
                    output += play("deal", player, "win", amt)
                    
            elif len(msg) == 1:
                output += play("deal", player, "win", 1)
            else:
                output.append(
                    "You need to start a game with "
                    "!craps <win/lose> (pick one), optionally "
                    "followed by a stake.")
        elif msg[0] == "!roll":
            output += play("roll", player)
            
        return output
    
def play(mode="", player="", style="", amt=1):
    global state
    output = []
    test = bank.check_balance(player)

    if bank.check_balance(player, 1) < 1:
        bank.deposit(player, 10)
    if bank.check_balance(player, 1) < amt:
        amt = bank.check_balance(player, 1)

    if mode == "deal":
        if player in state:
            output.append("can't start a new game while you're still playing")
        elif style == "win":
            output += roll(player, [7, 11], [2, 3, 12], amt)
        elif style == "lose":
            output += roll(player, [2, 3, 12], [7, 11], amt)
    elif mode == "roll":
        if player in state:
            output += roll(player, state[player][0],
                           state[player][1], state[player][2])
        else:
            output.append("You need to start a game first!")
            
    return output


def roll(player="", win=[], lose=[], amt=1):
    global state
    output = []
    dices = [random.randint(1, 6), random.randint(1, 6)]
    total = sum(dices)
    
    if total in win:
        bank.deposit(player, amt)
        output.append(f"{player} rolled {total} {dices} -- "
                      f"You won {amt}, {player}! "
                      f"You now have {bank.check_balance(player, 1)}"
                      " gikocoins.")
        if player in state: del state[player]
    elif total in lose:
        bank.deduct(player, amt)
        output.append(f"{player} rolled {total} {dices} -- "
                      f"You lost {amt}, {player}! "
                      f"You now have {bank.check_balance(player, 1)}"
                      " gikocoins.")                      
        if player in state: del state[player]
    else:
        if len(win) == 2:
            state[player] = [[total], [7], amt]
            output.append(f"{player} rolled {total} {dices}, "
                          f"now roll {total} to win or 7 to lose.")
        elif len(win) == 3:
            state[player] = [[7], [total], amt]
            output.append(f"{player} rolled {total} {dices}, "
                          f"now roll 7 to win or {total} to lose.")
        else:
            output.append(f"{player} rolled {total} {dices}, "
                          f"aiming for {win}, lose is {lose}. "
                          f"Roll again, {player}!")
    return output
            
print("Craps plugin loaded")
