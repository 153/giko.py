import time
from pytube import YouTube

def cmd(author, msg):
    if "youtu.be" not in msg:
        if "youtube.com/watch?v=" not in msg:
            return
    try:
        video = YouTube(url=msg)
    except:
        return
    leng = length(video.length)
    out = str(f"{video.title} [{leng}]")
    return out

def length(vidl):
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

print("Youtube plugin loaded")
