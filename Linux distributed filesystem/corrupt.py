#!/usr/bin/env python

import xmlrpclib, pickle, random, binascii
from xmlrpclib import Binary
from sys import argv, exit

'''
This corrupt.py is used for simulate data corruption in data server, it can randomly corrupt one block in a file. it takes arguments in the following format:
python corrupt.py <server port> <path> <replica index>
for example: to corrupt flie '/a/1.txt' in server 2222's replica 1:
python corrupt.py 2222 '/a/1.txt' 1

'''

def corrupt(server_port,path,index):
	server = xmlrpclib.ServerProxy("http://localhost:" + str(server_port))
	data = pickle.loads(server.get(Binary(path)).data)#read data from server
	j = random.randint(0,len(data)-1)	
	d = data[j]  #randomly choose one block from data file
	print('corrupt data in server port: '+str(server_port)+' replica: '+str(argv[3]))
	print('before corruption: ',d)
	i = random.randint(0,len(d)-1)#randomly choose one byte from block
	dd = d[i]
	dd_byte = str.encode(d)
	dd_barr = bytearray(dd_byte)
	i = random.randint(0,len(dd_barr)-1)
	k = random.randint(0,10)
	dd_barr[i] = int((dd_barr[i]+k)%64)
	dd_byte = bytes(dd_barr)
	dd_corrupt = bytes.decode(dd_byte)
	dd_corrupt = str(dd_corrupt)
	data[j] = dd_corrupt
	data = [data,index]
	print('after corruption: ',dd_corrupt)
	server.put(Binary(path[-1]), Binary(pickle.dumps(data)))#put corrupt data back


def hex_to_char(data):
	return binascii.unhexlify(data)

def char_to_hex(data):
	data = str.encode(data)
	return binascii.hexlify(data)

if __name__ == '__main__':
	if len(argv) != 4:
        	print('Please input server port path and replica number(0, 1 or 2)')
        	exit(1)
	server_port = argv[1]
	path = argv[2]+argv[3]
	index = argv[3]#argv[3]=replica number(0,1,2) which replica in server to corrupt
	corrupt(server_port,path,index)

