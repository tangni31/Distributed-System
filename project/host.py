import time, math, threading
from socket import *
from sys import argv


BUFSIZ = 1024


def run(count, clientSocket):
    start = time.time()
    task(count)
    end = time.time()
    runtime = (end - start) * 1000
    returnData = str(runtime)
    clientSocket.send(returnData.encode('utf-8'))
    clientSocket.close()


def task(count):
    i = 2
    while i < count:
        isprime = True
        for x in range(2, int(math.sqrt(i) + 1)):
            if i % x == 0:
                isprime = False
                break
        #if isprime:
            #print(i)
        i += 1


if __name__ == '__main__':
    port = int(argv[1])
    host = '127.0.0.1'
    ADDR = (host, port)
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    tcpSocket.bind(ADDR)
    #set the max number of tcp connection
    tcpSocket.listen(5)
    while True:
        print('waiting for connection on ' + ADDR[0] + ":"+ str(ADDR[1]))
        clientSocket, clientAddr = tcpSocket.accept()
        print('conneted from: %s' % clientAddr[0])
        data = clientSocket.recv(BUFSIZ)
        t = threading.Thread(target=run(int(data), clientSocket), name='taskThread')
        t.start()
        t.join()
