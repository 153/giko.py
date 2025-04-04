import re
import time
import wikipedia
from imdb import Cinemagoer
from pytubefix import YouTube

def cmd(author, msg):
    # look for imdb, youtube, wikipedia, 4chan
    output = []
    if "imdb.com/title/tt" in msg:
        urls = re.findall("((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", msg)
        for u in urls:
            for x in u:
                if "imdb.com/title/tt" in x:
                    output.append(imdb(x))
    if "youtu.be" in msg or "youtube.com/watch?v=" in msg:
        try:
            output.append(youtube(msg))
        except:
            pass
    msg = msg.split()
    if msg[0] == "!imdb":
        if len(msg) > 2:
            msg[1] = " ".join(msg[1:])
        output.append(imdb_search(msg[1]))
    if msg[0] == "!wiki":
        if len(msg) > 2:
            output.append(wiki(" ".join(msg[1:])))
        else:
            output.append(wiki(msg[1]))
    return output        

def imdb(url, skip_url=0):
    ia = Cinemagoer()
    if not skip_url:
        movie = url.split("/")[-2][2:]
    else:
        movie = url
        url = "https://imdb.com/title/tt" + url
    print(movie)
    movie = ia.get_movie(movie)
    try:
        airdate = movie['year']
    except:
        "0000"
    try:
        rating = movie['rating']
    except:
        rating = "0.0"
    try:
        runtime = movie['runtimes'][0]
    except:
        runtime = "0"
    return f"{movie} ({airdate}) 🕒{runtime} mins ⭐{rating}/10 -- {url}"

def imdb_search(query):
    ia = Cinemagoer()
    movie = ia.search_movie(query)[0]
    return imdb(movie.movieID, 1)

def wiki(query):
    print(query)
    results = wikipedia.search(query)
    print(" -", "\n - ".join(results))
    result = results[0]
    page = wikipedia.page(result, auto_suggest = False)
    url = page.url
    summary = wikipedia.summary(result, 2, auto_suggest=False )
    return " ".join([result, "::", summary, url])    

def youtube(msg):
    print(msg)
    try:
        video = YouTube(url=msg)
    except:
        return
    leng = yt_length(video.length)
    out = str(f"{video.title} [{leng}]")
    return out

def yt_length(vidl):
    diff = int(vidl)
    consts = [1, 1, 60, 3600, 86400, 604800, 2629746, 31556952]
    abbrv  = ['', 's', 'm', 'h', 'd', 'w', 'm', 'y']
    output = []
    for n, i in enumerate(consts):
        if i > diff:
            tmp = diff
            output.append(str(tmp//consts[n-1]) + abbrv[n-1])
            if abbrv[n-1] == 's':
                break
            while tmp >= consts[n-1]:
                tmp -= consts[n-1]
            if tmp//consts[n-2] != 0:
                output.append(str(tmp//consts[n-2]) + abbrv[n-2])
            break
    return "".join(output)

def chan(url):
    # https://boards.4chan.org/po/thread/611100
    # --> https://a.4cdn.org/po/thread/611100.json"
    # time
    # sub + com
    # replies
    # images
    # example: Torrents - the torrents are gone, but I am still seeding. (20 replies, 2 images) (11mo ago) https://boards.4chan.org/po/thread/611100
    
    
    start_url = "https://a.4cdn.org/"

    return

if __name__ == "__main__":
    po_thread = "https://boards.4chan.org/po/thread/611100"
    print(chan(po_thread))

print("Metadata plugin added")
