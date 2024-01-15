import random
import copy
import bank

state = {}

# TODO: new players start with 20 tokens
# you can gamble with as much tokens as you want
# and you can't drop below 1 token

suits = {"hearts": "♥",
         "spades": "♠",
         "clubs": "♣",
         "diamonds": "♦"
         }

def cmd(player, msg):
    msg = msg.split()
    bj_play_commands = ["!deal", "!hit", "!stand"]
    bj_other = ["!money"]
    output = []

    if msg[0] in bj_play_commands:
        if msg[0] == "!deal":
            output += play("deal", player)
        elif msg[0] == "!hit":
            output += play("hit", player)
        elif msg[0] == "!stand":
            output += play("stand", player)
    elif msg[0] == "!help":
        output.append("Blackjack commands: !deal, !hit, !stand, !money")
    return output

def play(mode="", player=""):
    global state
    
    output = []
    test = bank.check_balance(player)
    
    if bank.check_balance(player, 1) < 1:
        bank.deposit(player, 5)
        
    if mode == "deal":
        try:
            if len(state[player][0]):
                output.append("You give up and start a new hand.")
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
        total = 0
        for h in hand:
            if h[1] > 10:
                total += 10
            else:
                total += h[1]
        state[player] = [hand, dealer, deck]
        output.append(cnt_total(player))

    elif mode == "hit":
        try:
            hand = state[player][0]
            dealer = state[player][1]
            deck = state[player][2]
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
            output.append("Oops! You bust!")
            bank.deduct(player, 1)
            state[player] = []

        else:
            state[player] = [hand, dealer, deck]
            output.append(cnt_total(player))
            
    elif mode == "stand":
        try:
            hand = state[player][0]
            dealer = state[player][1]
            deck = state[player][2]
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
        while (dtotal < total) or (dtotal <= 17):
            deck, dealer = deal(deck, dealer)
            if dealer[-1][1] > 10:
                dtotal += 10
            else:
                dtotal += dealer[-1][1]
        output.append(cnt_total(player))
        if dtotal > 21:
            output.append("The dealer bust, you won!")
            bank.deposit(player, 1)
        elif dtotal == total:
            output.append("Push: you get your money back.")
        elif dtotal > total:
            output.append("The dealer beat you, you lose.")
            bank.deduct(player, 1)
        else:
            output.append("You beat the dealer. Good job!")
            bank.deposit(player, 1)
        state[player] = []
    return output
        
def deal(deck=[], hand=[]):
    suit = random.choice(list(deck.keys()))
    card = random.choice(deck[suit])
    hand.append([suit, card])
    deck[suit].pop(deck[suit].index(card))
    return deck, hand

def cnt_total(player):
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

def main():
    while True:
        command = input("[n/h/s] ")
        if command == "n":
            print(play("deal", "player"))
        elif command == "h":
            print(play("hit", "player"))
        elif command == "s":
            print(play("stand", "player"))
        elif command == "l":
            print(see_leaders())

if __name__ == "__main__":
    main()

print("Blackjack plugin loaded")
