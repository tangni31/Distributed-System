import time, math, threading
import socket
from sys import argv
from multiprocessing import Pool


BUFSIZ = 4096
CONTROL = '127.0.0.1'
CONTROL_PORT = 3000
CONTROL_ADDR = (CONTROL, CONTROL_PORT)
HOST = '127.0.0.1'


def run(count):
    start = time.time()
    task(count)
    end = time.time()
    runtime = (end - start) * 1000
    returnData = str(int(runtime))
    print(returnData)
    S.sendto(returnData.encode(), CONTROL_ADDR)


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
    #p = Pool()
    port = int(argv[1])
    ADDR = (HOST, port)
    S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    S.bind(ADDR)
    while True:
        data, addr = S.recvfrom(BUFSIZ)
        print('Received from %s:%s.' % addr)
        t = threading.Thread(target=run(int(data.decode())), name='taskThread')
        t.start()
