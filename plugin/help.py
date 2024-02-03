helptable = {"blackjack":
             "Blackjack commands: !deal <bet amount>, !hit, !stand, "
             "!dd (double down)",

             "craps":
             "Craps commands: !craps <win/lose> <amt>, !roll <sidebet> <amt>",

             "roulette":
             "Roulette commands: !spin <bet> <amt>, where bets are 0-36, even/odd, "
             "low/high, first/second/third (dozens)",

             "poker":
             "Poker commands: !poker <amt>, !drop <cards> (like !drop 0, !drop 1 2)",

             "bank":
             "Bank commands: !wealth , !create , !balance <player> , "
             "!send <amount> <player>",

             "quotes":
             "Quote commands: !dhamma, !bible, !random, !8ball, !fortune, !tarot, !add <quote>",

             "fortune":
             "Fortune commands: !fortune , !8ball , !tarot , !iching ",

             "memo":
             "Memo commands: !mail <username> || <message> "
             "(seperate username from message with || )",

             "kick":
             "Kick commands: !kickname <name>, !kickid <id>",

             "ban":
             "Ban commands: !banname <name>, !banid <id>, "
             "!banlist, !baninfo <num>",

             "finance":
             "Finance commands: !stock <ticker>, !convert <value> <cur1> <cur2> (use 2 letter country code)"
             }

def cmd(player, msg):
    msg = msg.split()
    output = []
    topics = helptable.keys()
    if msg[0] == "!help":
        if len(msg) == 1:
            output.append("List of topics (type !help <topic>): " \
                          + ", ".join(topics))
        elif msg[1] in topics:
            output.append(helptable[msg[1]])

    return output

print("Help plugin loaded")
