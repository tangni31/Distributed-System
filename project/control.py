from socket import *
import random, time, threading
from sys import argv
import os
from multiprocessing import Pool, Manager

from algorithms import roundRobin, equal, sensibleRouting


ALPHA = 0.2 #memory parameter
TOTAL_JOB = 30 # total jobs
JOB_RATE = 200 #  jobs / sec
serverNames = ['10.10.1.2', '10.10.1.1', '10.10.1.4']
serverPorts = [5000, 5000, 5000]


LOCK = threading.Lock()

BUFSIZ = 1024


def algorithm(ind, time, INDEX):
    pass
    #if argv[1] == "EQ":
    #res = equal()
    #elif argv[1] == 'RR':
    #INDEX[0] = roundRobin(ind)
    #else:
    #res = sensibleRouting(ind, time, ALPHA)


def task_gen(RUN_TIME, INDEX):
    #data = random.randint(90000,120000)
    data = 200000
    send(str(data), RUN_TIME, INDEX)


def send(data,RUN_TIME, INDEX):
    global TOTAL_RUN_TIME
    ind = INDEX[0]
    clientSocket = socket(AF_INET, SOCK_STREAM)
    serverName, serverPort = serverNames[ind],serverPorts[ind]
    addr = (serverName, serverPort)
    print(addr)
    clientSocket.connect(addr)
    clientSocket.send(data.encode('utf-8'))
    returnData = clientSocket.recv(BUFSIZ)
    clientSocket.close()
    runTime = float(returnData)
    #algorithm(ind, runTime, INDEX), #update host index
    #print('Run time is: {:.2f} ms'.format(runTime))#float(returnData.decode('utf-8'))))
    RUN_TIME += runTime,



def assign_task(RUN_TIME, INDEX):
    worker = threading.Thread(target=task_gen(RUN_TIME, INDEX), name='workerThread')
    worker.start()
    worker.join()


if __name__ == '__main__':
    manager = Manager()
    #INDEX = manager.list()
    #INDEX += 0,
    INDEX = [0]
    RUN_TIME = manager.list()
    p = Pool()
    prv = time.time()
    cnt = 0
    t1 = time.time()
    while cnt < TOTAL_JOB:
        now = time.time()
        if now - prv > 1/JOB_RATE:
            print(INDEX)
            #print (now-prv)
            prv = now
            p.apply_async(assign_task, args=(RUN_TIME,INDEX,))
            INDEX[0] += 1
            INDEX[0] %= 3
            #p.apply_async(task_gen, args=(INDEX, RUN_TIME,))
            cnt += 1
    p.close()
    p.join()
    t2 = time.time()
    print('average task run time is: {:.2f} ms'.format(sum(RUN_TIME) / TOTAL_JOB))
