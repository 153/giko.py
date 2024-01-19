import random
from . import bank

state = {}
# state[player] = [win, lose, amount]

def cmd(player, msg):
    msg = msg.split()
    commands = ["!craps", "!roll", "!help"]
    output = []

    if msg[0] in commands:
        if msg[0] == "!help":
            output.append("Craps commands: !craps <win/lose> <amt>, "
                          "!roll <sidebet> <amt>")
        elif msg[0] == "!craps":
            amt = 1
            if len(msg) > 2:
                try: amt = int(msg[2])
                except: pass
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
                    try: amt = int(msg[1])
                    except: pass
                    if amt < 1: amt = 1
                    output += play("deal", player, "win", amt)
                    
            elif len(msg) == 1:
                output += play("deal", player, "win", 1)
            else:
                output.append(
                    "You need to start a game with "
                    "!craps <win/lose> (pick one), optionally "
                    "followed by a stake.")
        elif msg[0] == "!roll":
            if not player in state:
                return ["You need to start a game with !craps before you can place sidebets."]
            side_bets = ["field", "seven", "craps", "two", "three", "eleven", "twelve"]
            if len(msg) >= 2:
                if msg[1] not in side_bets:
                    output.append("!roll <sidebet> <amt> -- side bets are "
                                  "field, seven (4:1), craps (7:1), two (30:1), "
                                  "twelve (30:1), eleven (15:1), three (15:1) "
                                  "-- single roll bets with great payouts!")
                else:
                    try:
                        sidebet = int(msg[2])
                    except: sidebet = 1
                    if sidebet < 1:
                        sidebet = 1
                    if sidebet > bank.check_balance(player, 1):
                        sidebet = bank.check_balance(player, 1)
                    if sidebet < 1:
                        bank.deposit(player, 5)
                        sidebet = 1
                    
                    output += play("roll", player, side=[msg[1], sidebet])
            else:
                output += play("roll", player)
            
        return output
    
def play(mode="", player="", style="", amt=1, side=[]):
    global state
    output = []

    bank.check_balance(player)
    try: amt = int(amt)
    except: amt = 1

    if amt < 1:
        amt = 1
    if amt > bank.check_balance(player, 1):
        amt = bank.check_balance(player, 1)
    if amt < 1:
        bank.deposit(player, 5)
        amt = 1

    if mode == "deal":
        if player in state:
            output.append(f"You forfeit {state[player][2]} and "
                          "begin a new game...")
            bank.deduct(player, amt)
            del state[player]
            output += play(mode, player, style, amt)
        elif style == "win":
            output += roll(player, [7, 11], [2, 3, 12], amt)
        elif style == "lose":
            output += roll(player, [2, 3, 12], [7, 11], amt)
    elif mode == "roll":
        if player in state:
            output += roll(player, state[player][0],
                           state[player][1], state[player][2],
                           side)
        else:
            output.append("You need to start a game first!")
            
    return output


def roll(player="", win=[], lose=[], amt=1, side=[]):
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
    if len(side):
        wager = side[1]
        sides = {"field": {3: wager, 4: wager, 9: wager, 10: wager, 
                           11: wager, 2: 2 * wager, 12: 3 * wager},
                 "seven": {7: 4 * wager},
                 "two": {2: 30 * wager},
                 "twelve": {12: 30 * wager},
                 "three": {3: 15 * wager},
                 "eleven": {11: 15 * wager},
                 "craps": {2: 7 * wager,
                           3: 7 * wager,
                           12: 7 * wager}}
        if total in sides[side[0]]:
            payout = sides[side[0]][total]
            bank.deposit(player, payout)
            output.append(f"{player}'s wager of {wager} on {side[0]} pays out "
                          f"{payout}, nice job, you now have "
                          f"{bank.check_balance(player, 1)} gikocoins")
        else:
            bank.deduct(player, wager)
            output.append(f"{player} lost his wager of {wager} on {side[0]}, "
                          f"you now have {bank.check_balance(player, 1)} gikocoins")
    return output
            
print("Craps plugin loaded")
