import random

def cmd(author, msg):
    msg = msg.split()
    commands = ["!dhamma", "!bible", "!quran", "!tao", "!sun",
                "!8ball", "!fortune", "!tarot", "!iching", "!futhark",
                "!zippy", "!jerk", "!kanye", "!zzazz", "!choose",
                "!random", "!add"]
    output = []
    
    if msg[0] in commands:
        if msg[0] == "!random":
            output.append(get_quote("giko-quotes.txt"))
        elif msg[0] == "!dhamma":
            output.append(get_quote("dhammapada.txt"))
        elif msg[0] == "!bible":
            output.append(get_quote("bible.txt"))
        elif msg[0] == "!quran":
            output.append(get_quote("quran.txt"))
        elif msg[0] == "!8ball":
            output.append(get_quote("8ball.txt"))
        elif msg[0] == "!fortune":
            output.append(get_quote("fortunes.txt"))
        elif msg[0] == "!tarot":
            output.append(get_quote("tarot.txt"))
        elif msg[0] == "!iching":
            output.append(get_quote("iching.txt"))
        elif msg[0] == "!tao":
            output.append(get_quote("tao.txt"))
        elif msg[0] == "!sun":
            output.append(get_quote("sun.txt"))
        elif msg[0] == "!zippy":
            output.append(get_quote("zippy.txt"))
        elif msg[0] == "!jerk":
            output.append(get_quote("jerk.txt"))            
        elif msg[0] == "!futhark":
            output.append(get_quote("futhark.txt"))
        elif msg[0] == "!kanye":
            output.append(get_quote("kanye.txt"))
        elif msg[0] == "!zzazz":
            output.append(zzazz())
        elif msg[0] == "!choose":
            output.append(chooser(msg))
        elif msg[0] == "!add":
            output.append("Suggest new quotes here: "
                          "https://bbs.gikopoi.com/thread/1705384771/")
    return output

def get_quote(fn):
    with open(f"./quotedb/{fn}") as quotedb:
        quotedb = quotedb.read().splitlines()
    quote = random.choice(quotedb)
    return quote

def zzazz():
    with open("./quotedb/giko-quotes.txt") as quotes:
        quotes = quotes.read().splitlines()
    quotes = [q for q in quotes if q.startswith("zzazzachu")]
    quote = random.choice(quotes)
    return quote

def chooser(msg):
    msg = " ".join(msg[1:])
    msg = msg.split(", ")
    msg = random.choice(msg)
    if msg.startswith("#die") or msg.startswith("#train"):
        return "Tricky boy!"
    return msg

print("Quotes plugin loaded")
