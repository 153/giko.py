import random
from . import bank

def cmd(player, msg):
    msg = msg.split()
    commands = ["!spin", "!help"]
    output = []

    if msg[0] in commands:
        if msg[0] == "!help":
            output.append("Roulette commands: !spin <bet> <amt>, "
                          "where bets are 0-36, even/odd, "
                          "low/high, first/second/third (dozens)")
        elif msg[0] == "!spin":
            if len(msg) == 2:
                output += spin(player, msg[1], 1)
            elif len(msg) == 3:
                output += spin(player, msg[1], msg[2])

    return output

def spin(player, bet, amt):
    output = []
    result = random.randint(0, 36)

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
    
    table = [str(i) for i in range(0, 37)]
    win = {"even": [int(i) for i in table[1:] if not (int(i) % 2)],
           "odd": [int(i) for i in table[1:] if (int(i) % 2)],
           "low": range(1, 19), "high": range(19, 37),
           "first": range(1, 13), "second": range(13, 25),
           "third": range(25, 37)}

    if bet in win:
           if result in win[bet]:
               payout = amt
               if bet in ["first", "second", "third"]:
                   payout = payout * 2
               bank.deposit(player, amt)
               output.append(f"{player} spun {result}, and won {payout} from "
                             f"the wager of {amt} on {bet} numbers! You now have "
                             f"{bank.check_balance(player, 1)} gikocoins")
           else:
               bank.deduct(player, amt)
               output.append(f"{player} spun {result}, and lost "
                             f"the wager of {amt} on {bet} numbers! You now have "
                             f"{bank.check_balance(player, 1)} gikocoins")
    
    elif bet in table:
        if bet == str(result):
            payout = 35 * amt
            bank.deposit(player, payout)
            output.append(f"{player} spun {result} and won {payout}! "
                          f"You now have {bank.check_balance(player, 1)} gikocoins")
        else:
            bank.deduct(player, amt)
            output.append(f"{player} spun {result} and lost! "
                          f"You now have {bank.check_balance(player, 1)} gikocoins")
    else:
        output.append("Please enter !spin <bet> <amt>, where "
                      "bet is a single number between 0 and 36 -- payout 35x // "
                      "even, odd, low (1-18), high (19-36) -- payout 1x // "
                      "or first (1-12), second (13-24), or third (25-36) "
                      "-- payout 2x.")
    return output

print("Roulette plugin loaded")
