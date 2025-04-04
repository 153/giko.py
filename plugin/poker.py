#!/usr/bin/python3

import random
import copy
from . import bank

state = {}
# {player: [deck, hand, amount]}

suits = {"hearts": "♥",
         "spades": "♠",
         "clubs": "♣",
         "diamonds": "♦"}

royals = {11: "J", 12: "Q", 13: "K", 1: "A"}

def cmd(player, msg):
    msg = msg.split()
    commands = ["!poker", "!drop"]
    output = []

    if msg[0] in commands:
        if msg[0] == "!poker":
            try: amt = int(msg[1])
            except: amt = 1
            output += play("draw", player, [], amt)
        elif msg[0] == "!drop":
            if len(msg) > 1:
                discard = " ".join(msg[1:])
                output += play("discard", player, discard)
            else: 
                output += play("discard", player, "0")
#                output.append("Please type a list of space-seperated cards to discard, like !drop 0, !drop 1, !drop 3 5")
    return output

def play(mode="", player="", discard="", amt=1):
    global state
    output = []

    bank.check_balance(player)
    try: amt = int(amt)
    except: amt = 1

    if amt < 1:
        amt = 1
    if amt > bank.check_balance(player, 1):
        amt = bank.check_balance(player, 1)
    if amt > 1000:
        amt = 1000   
    if amt < 1:
        bank.deposit(player, 5)
        amt = 1
    
    if mode == "draw":
        if player in state:
            bank.deduct(player, state[player][2])
            output.append(f"You forfeit {state[player][2]} and "
                          "begin a new game...")
            del state[player]
            output += play(mode, player, [], amt)
            return output
        deck = {"hearts": [i+1 for i in range(13)],
                "spades": [i+1 for i in range(13)],
                "clubs": [i+1 for i in range(13)],
                "diamonds": [i+1 for i in range(13)]}
        deck, hand = deal(deck, [])

        state[player] = [deck, hand, amt]
        output.append(f"{player}'s hand is now {fmthand(player)}, "
                      "enter some cards to discard (0 or 1-5)")
        
    elif mode == "discard":
        if player not in state:
            output.append(f"{player}, you need to start a game with !poker "
                          "before you can discard cards.")
            return output
        deck, hand = state[player][0], state[player][1]
        try:
            discard = [int(d) for d in discard.split(" ")]
        except:
            return ["Please type a space seperated list of cards to discard, eg !drop 0 or !drop 2 or !drop 1 2 4"]
        discard = [d for d in discard if d >= 0 if d < 6]
        discard = sorted(list(set(discard)), reverse=True)
        for d in discard:
            if d == 0:
                continue
            d -= 1
            hand.pop(d)
        deck, hand = deal(deck, hand)
        amt = state[player][2]
        state[player] = [deck, hand, amt]

        output.append(f"{player}'s hand is now {fmthand(player)}.")
        if reward(player):
            payout = reward(player)
            bank.deposit(player, payout)
            output.append(f"Congrats on the {check(player)} {player}, "
                          f"you won {payout} and now have "
                          f"{bank.check_balance(player, 1)} gikocoins!")
            del state[player]
        else:
            bank.deduct(player, state[player][2])
            output.append(f"Sorry {player}, you lost {amt} and now have "
                          f"{bank.check_balance(player, 1)} gikocoins.")
            del state[player]
    return output
    
def deal(deck=[], hand=[]):
    while len(hand) < 5:
        suit = random.choice(list(deck.keys()))
        card = random.choice(deck[suit])
        hand += [[suit, deck[suit].pop(deck[suit].index(card))]]
    return deck, hand

def check(player):
    hand = state[player][1]
    hsuits = [i[0] for i in hand]
    cards = sorted([i[1] for i in hand])
    matches = []

    scards = sorted(set((x, cards.count(x)) for x in cards if
                        cards.count(x) >= 2), key= lambda x: x[1],
                    reverse=True)

    if len(scards) == 1:
        if scards[0][1] == 2:
            if scards[0][0] > 10 or scards[0][0] == 1:
                matches.append("pair")
        elif scards[0][1] == 3:
            matches.append("3ofkind")
        elif scards[0][1] == 4:
            matches.append("4ofkind")

    elif len(scards) > 1:
        print(scards)
        if scards[0][1] == 2:
            matches.append("2pair")
        elif scards[0][1] == 3:
            matches.append("full house")
            
    if len(matches) == 0:
        mycards = sorted(cards)
        stcheck = list(range(min(mycards), max(mycards) +1))
        if mycards == stcheck:
            matches.append("straight")
        elif mycards[0] == 1:
            mycards = [*mycards[1:], 14]
            stcheck = list(range(min(mycards), max(mycards) +1))
            if mycards == stcheck:
                matches += ["straight", "royal"]

    if hsuits.count(hsuits[0]) == 5:
        matches.append("flush")
    if "flush" in matches and "royal" in matches:
        matches = ["royal flush"]
    elif "flush" in matches and "straight" in matches:
        matches = ["straight flush"]

    if len(matches):
        return matches[0]
    return matches

def fmthand(player):
    hand = state[player][1]
    nicehand = [[i[0], royals[i[1]]] if i[1] in royals else i
                for i in hand]
    nicehand = [f"{suits[card[0]]}{card[1]}" for card in nicehand]
        
    return f"({'/'.join([i for i in nicehand])})"

def reward(player):
    score = check(player)
        
    prizes = {"pair": 1, "2pair": 2, "3ofkind": 3,
              "straight": 4, "flush": 6, "full house": 9,
              "4ofkind": 25, "straight flush": 50,
              "royal flush": 800}
    if not len(score):
        return 0
    return state[player][2] * prizes[score]
    
print("Poker plugin loaded")

    
