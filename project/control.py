import socket
import random, time, threading
from sys import argv
import os
from multiprocessing import Pool, Manager, Process

from algorithms import roundRobin, equal, sensibleRouting


ALPHA = 0.2 #memory parameter
TOTAL_JOB = 10 # total jobs
JOB_RATE = 2 #  jobs / sec
serverNames = ['127.0.0.1', '127.0.0.1', '127.0.0.1']
serverPorts = [4000, 5000, 6000]
BUFSIZ = 4096



def task_gen(S, INDEX):
    #data = random.randint(90000,120000)
    data = 400000
    send(S, str(data), INDEX)


def send(S, data,INDEX):
    ind = INDEX[0]
    serverName, serverPort = serverNames[ind],serverPorts[ind]
    addr = (serverName, serverPort)
    print(addr)
    print(S.type)
    S.sendto(data.encode(), addr)


def receive(S, RUN_TIME, INDEX):
    while True:
        returnData, host = S.recvfrom(BUFSIZ)
        print("received from: " + str(host[0]))
        runTime = float(returnData.decode())
        RUN_TIME += runTime,
        if argv[1] == 'SR':
            INDEX[0] = sensibleRouting(host[1], runTime, ALPHA)
            print('-----------------------')
            print(INDEX[0])


def assign_task(S, INDEX):
    worker = threading.Thread(target=task_gen(S, INDEX), name='workerThread')
    worker.start()
    worker.join()


if __name__ == '__main__':
    manager = Manager()
    S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    S.bind(('127.0.0.1', 3000))
    RUN_TIME = manager.list()
    INDEX = manager.list()
    INDEX += 0,
    recv_pro = Process(target=receive, args=(S, RUN_TIME, INDEX,))
    recv_pro.start()
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
            p.apply_async(assign_task, args=(S, INDEX,))
            if argv[1] == 'RR':
                INDEX[0] += 1
                INDEX[0] %= 3
            elif argv[1] == 'EQ':
                INDEX[0] = random.choice([0,1,2])
            else:
                INDEX[0] = INDEX[0]
            cnt += 1
    p.close()
    p.join()
    t2 = time.time()
    while len(RUN_TIME) < TOTAL_JOB:
        continue
    print('average task run time is: {:.2f} ms'.format((sum(RUN_TIME)) / TOTAL_JOB))
