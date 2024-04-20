import wikipedia

def cmd(author, msg):
    msg = msg.split()
    output = []
    
    if msg[0] == "!wiki":
        if len(msg) > 2:
            output.append(article(" ".join(msg[1:])))
        else:
            output.append(article(msg[1]))
    return output

def article(query):
    print(query)
    results = wikipedia.search(query)
    print(" -", "\n - ".join(results))
    result = results[0]
    page = wikipedia.page(result, auto_suggest = False)
    url = page.url
    summary = wikipedia.summary(result, 2, auto_suggest=False )
    return " ".join([result, "::", summary, url])

print("Wiki plugin loaded")

if __name__ == "__main__":
    print(cmd("Anon", "!wiki Mango cult"))
