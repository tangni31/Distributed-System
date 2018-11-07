import random, threading

sensibleG = [100, 100, 100] # goal function  for sensible routing

LOCK = threading.Lock()

def roundRobin(ind):
    ind += 1
    ind %= 3
    return ind


def equal():
    l = [0, 1, 2]
    return random.choice(l)


def sensibleRouting(ind, time, a=0.2):
    global sensibleG
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
