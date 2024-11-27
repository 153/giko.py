import re
from imdb import Cinemagoer

def cmd(author, msg):
    if "imdb.com/title/tt" in msg:
#        try:
        urls = re.findall("((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", msg)
        for u in urls:
            for x in u:
                if "imdb.com/title/tt" in x:
                    return imdb(x)
    msg = msg.split()
    if msg[0] == "!imdb":
        if len(msg) > 2:
            msg[1] = " ".join(msg[1:])
        return imdb_search(msg[1])
#       except:
#            return 

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

print("Metadata plugin added")
