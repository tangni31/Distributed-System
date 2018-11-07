from socket import *
import random, time, threading
from sys import argv
import os
from multiprocessing import Pool, Manager

from algorithms import roundRobin, equal, sensibleRouting


ALPHA = 0.2 #memory parameter
TOTAL_JOB = 20 # total jobs
JOB_RATE = 20 #  jobs / sec
serverNames = ['localhost', 'localhost', 'localhost']
serverPorts = [4000, 5000, 6000]

LOCK = threading.Lock()
INDEX = 0
BUFSIZ = 1024


def algorithm(ind, time):
    global INDEX
    if argv[1] == "EQ":
        res = equal()
    elif argv[1] == 'RR':
        res = roundRobin(ind)
    else:
        res = sensibleRouting(ind, time, ALPHA)
    LOCK.acquire()
    INDEX = res
    LOCK.release()


def task_gen(ind, RUN_TIME):
    #data = random.randint(90000,120000)
    data = 100000
    send(str(data), ind, RUN_TIME)


def send(data, ind, RUN_TIME):
    global TOTAL_RUN_TIME
    clientSocket = socket(AF_INET, SOCK_STREAM)
    serverName, serverPort = serverNames[ind],serverPorts[ind]
    addr = (serverName, serverPort)
    #print(addr)
    clientSocket.connect(addr)
    clientSocket.send(data.encode('utf-8'))
    returnData = clientSocket.recv(BUFSIZ)
    clientSocket.close()
    runTime = float(returnData)
    algorithm(ind, runTime) #update host index
    #print('Run time is: {:.2f} ms'.format(runTime))#float(returnData.decode('utf-8'))))
    RUN_TIME += runTime,


def assign_task(RUN_TIME):
    worker = threading.Thread(target=task_gen(INDEX, RUN_TIME), name='workerThread')
    worker.start()
    worker.join()


if __name__ == '__main__':
    manager = Manager()
    RUN_TIME = manager.list()
    p = Pool(10)
    prv = time.time()
    cnt = 0
    while cnt < TOTAL_JOB:
        now = time.time()
        if now - prv > 1/JOB_RATE:
            print (now-prv)
            prv = now
            p.apply_async(assign_task, args=(RUN_TIME,))
            #p.apply_async(task_gen, args=(INDEX, RUN_TIME,))
            cnt += 1
    p.close()
    p.join()
    print('average task run time is: {:.2f} ms'.format(sum(RUN_TIME) / TOTAL_JOB))

