import random, threading

sensibleG = [100, 100, 100] # goal function  for sensible routing
HOST = [4000, 5000, 6000] #host addr
LOCK = threading.Lock()


def sensibleRouting(host, time, a=0.2):
    global sensibleG
    if host == HOST[0]:
        ind = 0
    elif host == HOST[1]:
        ind = 1
    else:
        ind = 2
    sensibleP = []
    gi = (1 - a) * sensibleG[ind] + a * time #update weight
    p = random.random()
    LOCK.acquire()
    sensibleG[ind] = gi
    sum_ = sum(1 / gj for gj in sensibleG)
    for i in range(3):
        sensibleP += (1 / sensibleG[i]) / sum_, #update probability p
    LOCK.release()
    if p <= sensibleP[0]:
        ind = 0
    elif p <= sensibleP[0] + sensibleP[1]:
        ind = 1
    else:
        ind = 2

    return ind
