import random
import copy
from . import bank

state = {}
# {player: [hand, dealer, deck, amount]}

suits = {"hearts": "♥",
         "spades": "♠",
         "clubs": "♣",
         "diamonds": "♦"
         }

def cmd(player, msg):
    msg = msg.split()
    bj_play_commands = ["!deal", "!hit", "!stand"]
    output = []

    if msg[0] in bj_play_commands:
        if msg[0] == "!deal":
            amt = 1
            if len(msg) > 1:
                try:
                    amt = int(msg[1])
                except:
                    amt = 1
            if amt < 1:
                amt = 1
            output += play("deal", player, amt)
        elif msg[0] == "!hit":
            output += play("hit", player)
        elif msg[0] == "!stand":
            output += play("stand", player)
    elif msg[0] == "!help":
        output.append("Blackjack commands: !deal <bet amount>, !hit, !stand")
    return output

def play(mode="", player="", amt=1):
    global state
    output = []
    bj = False
    
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
        try:
            if len(state[player][0]):
                output.append(f"You give up on your old hand and lose {state[player][3]} "
                              f"gikocoins, and start a new round, wagering {amt}")
                bank.deduct(player, state[player][3])
                del state[player]
                output += play(mode, player, amt)
                return output
        except:
            pass
            
        deck = {"hearts": [i+1 for i in range(13)],
                "spades": [i+1 for i in range(13)],
                "clubs": [i+1 for i in range(13)],
                "diamonds": [i+1 for i in range(13)]}
        hand, dealer = [], []
        
        state[player] = []
        deck, hand = deal(deck, hand)
        deck, hand = deal(deck, hand)
        deck, dealer = deal(deck, dealer)

        bj_check = [i[1] for i in hand]
        bj_check = sorted([a if (a < 11) else 10 for a in bj_check])
        if bj_check == [1, 10]:
            bj = True

        total = 0
        for h in hand:
            if h[1] > 10:
                total += 10
            else:
                total += h[1]
        state[player] = [hand, dealer, deck, amt]
        output.append(cnt_total(player, bj))

    elif mode == "hit":
        try:
            hand = state[player][0]
            dealer = state[player][1]
            deck = state[player][2]
            amt = state[player][3]
        except:
            output.append("You need to start a hand.")
            return output
        deck, hand = deal(deck, hand)

        total = 0
        for h in hand:
            if h[1] > 10:
                total += 10
            else:
                total += h[1]
        
        if total > 21:
            output.append(cnt_total(player))
            bank.deduct(player, amt)
            output.append(" ".join(
                ["Oops! You bust!",
                 "You now have",
                 str(bank.check_balance(player, 1)),
                 "gikocoins."]))
            state[player] = []

        else:
            state[player] = [hand, dealer, deck, amt]
            output.append(cnt_total(player))
            
    elif mode == "stand":
        try:
            hand = state[player][0]
            dealer = state[player][1]
            deck = state[player][2]
            amt = state[player][3]
        except:
            output.append("You need to start a hand.")
            return output
        
        total = 0
        for h in hand:
            if h[1] > 10:
                total += 10
            else:
                total += h[1]
        dtotal = dealer[0][1]
        if dtotal > 10:
            dtotal = 10
            
        while dtotal < 17:
            deck, dealer = deal(deck, dealer)
            if dealer[-1][1] > 10:
                dtotal += 10
            else:
                dtotal += dealer[-1][1]
        output.append(cnt_total(player))
        if dtotal > 21:
            bank.deposit(player, amt)
            output.append(" ".join(
                ["The dealer bust, you won!",
                 "You now have",
                 str(bank.check_balance(player, 1)),
                 "gikocoins."]))
        elif dtotal == total:
            output.append(" ".join(
                ["Push: you get your money back.",
                 "You now have",
                 str(bank.check_balance(player, 1)),
                 "gikocoins."]))
        elif dtotal > total:
            bank.deduct(player, amt)
            output.append(" ".join(
                ["The dealer beat you, you lose.",
                 "You now have",
                 str(bank.check_balance(player, 1)),
                 "gikocoins."]))
        else:
            bank.deposit(player, amt)
            output.append(" ".join(
                ["You beat the dealer. Good job!",
                 "You now have",
                 str(bank.check_balance(player, 1)),
                 "gikocoins."]))
        state[player] = []
    if bj:
        bank.deposit(player, (2 * amt))
        output.append(" ".join(
            ["You got a blackjack! Double your money!",
             "You now have",
             str(bank.check_balance(player, 1)),
             "gikocoins."]))
        state[player] = []
    return output
        
def deal(deck=[], hand=[]):
    suit = random.choice(list(deck.keys()))
    card = random.choice(deck[suit])
    hand.append([suit, card])
    deck[suit].pop(deck[suit].index(card))
    return deck, hand

def cnt_total(player, bj=False):
    global state
    cards = state[player]
    player_score = 0
    dealer = 0

    player_array = copy.deepcopy(cards[0])
    dealer_array = copy.deepcopy(cards[1])

    for n, p in enumerate(player_array):
        names = {11: "J", 12: "Q", 13: "K"}
        if p[1] > 10:
            p[1] = names[p[1]]
        player_array[n] = str(suits[p[0]] + str(p[1]))
    player_array = "(" + "/".join(player_array) + ")"

    for n, p in enumerate(dealer_array):
        names = {11: "J", 12: "Q", 13: "K"}
        if p[1] > 10:
            p[1] = names[p[1]]
        dealer_array[n] = str(suits[p[0]] + str(p[1]))
    if len(dealer_array) < 2:
        dealer_array.append("??")
    dealer_array = "(" + "/".join(dealer_array) + ")"

    for c in cards[0]:
        if c[1] > 10:
            player_score += 10
        else:
            player_score += c[1]
    for c in cards[1]:
        if c[1] > 10:
            dealer += 10
        else:
            dealer += c[1]
    return f"You have {player_score} {player_array} and the dealer has {dealer} {dealer_array}"

print("Blackjack plugin loaded")
