from . import bank

state = {"active": False, "creator": "", "sides": [], "bets": {}}

def cmd(player, msg):
    msg = msg.split()
    commands = ["!startbet", "!endbet", "!bet"]
    output = []

    if not len(msg) or msg[0] not in commands:
        return output

    if msg[0] == "!startbet":
        if len(msg) >= 2 and msg[1].lower() == "cancel":
            output += cancel(player)
        elif len(msg) >= 3:
            output += create(player, msg[1], msg[2])
        else:
            output.append("!startbet <side1> <side2> -- starts a new bet. "
                          "!startbet cancel -- the creator cancels and refunds everyone.")

    elif msg[0] == "!bet":
        if len(msg) >= 3:
            output += wager(player, msg[1], msg[2])
        else:
            output.append("!bet <side> <amount>")

    elif msg[0] == "!endbet":
        if len(msg) >= 2 and msg[1].lower() == "win":
            if len(msg) < 3:
                output.append("!endbet win <side>")
            else:
                output += resolve(player, " ".join(msg[2:]))
        else:
            output.append("!endbet win <side> -- the creator declares the winner and closes the bet.")

    return output


def create(player, side_a, side_b):
    global state
    if state["active"]:
        return [f"There's already an active bet: {state['sides'][0]} vs {state['sides'][1]}, "
               f"started by {state['creator']}."]
    if side_a.lower() == side_b.lower():
        return ["The two sides need to be different."]

    state = {"active": True, "creator": player,
             "sides": [side_a, side_b], "bets": {}}
    return [f"{player} started a bet: {side_a} vs {side_b}! "
           f"Use !bet <side> <amount> to place your bet. "
           f"Only {player} can close it with !endbet win <side>."]


def wager(player, side, amt):
    global state
    if not state["active"]:
        return ["There's no active bet. Start one with !startbet <side1> <side2>."]

    sides = state["sides"]
    matched = next((s for s in sides if s.lower() == side.lower()), None)
    if matched is None:
        return [f"Invalid side. Pick either {sides[0]} or {sides[1]}."]

    if player in state["bets"]:
        b = state["bets"][player]
        return [f"You already bet {b['amount']} on {b['side']}. You can't change your bet."]

    bank.check_balance(player)
    try:
        amt = int(amt)
    except:
        return ["!bet <side> <amount> -- amount has to be a number."]

    if amt < 1:
        return ["Minimum bet is 1 gikocoin."]

    balance = bank.check_balance(player, 1)
    if amt > balance:
        return [f"You don't have {amt} gikocoins, you only have {balance}."]

    bank.deduct(player, amt)
    state["bets"][player] = {"side": matched, "amount": amt}
    return [f"{player} bet {amt} gikocoins on {matched}!"]


def resolve(player, winning_side):
    global state
    if not state["active"]:
        return ["There's no active bet."]
    if player != state["creator"]:
        return [f"Only {state['creator']} can close this bet."]

    sides = state["sides"]
    matched = next((s for s in sides if s.lower() == winning_side.lower()), None)
    if matched is None:
        return [f"Invalid side. Pick either {sides[0]} or {sides[1]}."]

    bets = state["bets"]
    output = []

    if not len(bets):
        output.append(f"{matched} won! But nobody placed any bets.")
        state["active"] = False
        return output

    winners = {p: b for p, b in bets.items() if b["side"] == matched}
    losers = {p: b for p, b in bets.items() if b["side"] != matched}
    winning_pool = sum(b["amount"] for b in winners.values())
    losing_pool = sum(b["amount"] for b in losers.values())

    output.append(f"{matched} won! Payouts:")

    if winning_pool == 0:
        output.append("Nobody bet on the winning side, so the house keeps it all. Tough luck.")
    else:
        for p, b in winners.items():
            share = losing_pool * (b["amount"] / winning_pool)
            payout = int(round(b["amount"] + share))
            bank.deposit(p, payout)
            output.append(f"{p} wins {payout} gikocoins (bet {b['amount']} on {matched}). "
                          f"Now has {bank.check_balance(p, 1)}.")

    for p in losers:
        output.append(f"{p} lost their bet.")

    state["active"] = False
    state["bets"] = {}
    return output


def cancel(player):
    global state
    if not state["active"]:
        return ["There's no active bet to cancel."]
    if player != state["creator"]:
        return [f"Only {state['creator']} can cancel this bet."]

    for p, b in state["bets"].items():
        bank.deposit(p, b["amount"])

    output = [f"{player} canceled the bet. Everyone's money has been refunded."]
    state["active"] = False
    state["bets"] = {}
    return output


print("Bets plugin loaded")