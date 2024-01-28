import random

def cmd(author, msg):
    msg = msg.split()
    commands = ["!dhamma", "!random", "!add", "!8ball", "!fortune", "!bible"]
    output = []
    
    if msg[0] in commands:
        if msg[0] == "!random":
            output.append(get_quote("giko-quotes.txt"))
        elif msg[0] == "!dhamma":
            output.append(get_quote("dhammapada.txt"))
        elif msg[0] == "!bible":
            output.append(get_quote("bible.txt"))
        elif msg[0] == "!8ball":
            output.append(get_quote("8ball.txt"))
        elif msg[0] == "!fortune":
            output.append(get_quote("fortunes.txt"))
        elif msg[0] == "!add":
            output.append("Suggest new quotes here: "
                          "https://bbs.gikopoi.com/thread/1705384771/")
    return output

def get_quote(fn):
    with open(f"./quotedb/{fn}") as quotedb:
        quotedb = quotedb.read().splitlines()
    quote = random.choice(quotedb)
    return quote

print("Quotes plugin loaded")
