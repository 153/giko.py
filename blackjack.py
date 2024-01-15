#!/usr/bin/python3

import random

state = {}
leaders = {"Archduke": 9999}

# TODO: new players start with 20 tokens
# you can gamble with as much tokens as you want
# and you can't drop below 1 token

def play(mode="", player=""):
    global state
    global leaders
    
    output = []

    if not player in leaders:
        leaders[player] = 0
        
    if mode == "deal":
        try:
            if len(state[player][0]):
                output.append("You give up and start a new hand.")
        except:
            pass
            
        deck = {"heart": [i+1 for i in range(13)],
                "spade": [i+1 for i in range(13)],
                "club": [i+1 for i in range(13)],
                "diamond": [i+1 for i in range(13)]}
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
            leaders[player] -= 1
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
            leaders[player] += 1
        elif dtotal == total:
            output.append("Push: you get your money back.")
        elif dtotal > total:
            output.append("The dealer beat you, you lose.")
            leaders[player] -= 1
        else:
            output.append("You beat the dealer. Good job!")
            leaders[player] += 1
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
    return f"You have {player_score} and the dealer has {dealer}"

def see_leaders():
    global leaders 
    leaderboard = [[i, leaders[i]] for i in leaders]
    leaderboard.sort(key = lambda x: x[1], reverse=True)
    return str(leaderboard)

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
