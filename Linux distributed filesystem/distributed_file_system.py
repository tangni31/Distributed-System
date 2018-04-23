#!/usr/bin/env python

import logging, xmlrpclib, pickle, random
from xmlrpclib import Binary
from collections import defaultdict
from errno import ENOENT, ENOTEMPTY
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import time as times
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

bsize = 8	#block size = 8(not include checksum)
data_server_list = []
replica_num = 3 	#3 replicas for each block

class Memory(LoggingMixIn, Operations,):

    def __init__(self):    
        self.fd = 0

    def hashpath(self,path):  #find the first server to store the file using hash function
	server = int((int(str(hash(path))[-1])+int(str(hash(path))[-2])+int(str(hash(path))[-3])))
	server = server % server_num
	return server

    def crc16(self,data):  #checksum using CRC16
	a = 0xFFFF
	b = 0xA001
	for byte in data:
		a ^= ord(byte)
		for i in range(8):
			last = a%2
			a >>= 1
			if last == 1:
				a ^= b
	s = hex(a).upper()
	return s[2:4] + s[4:6]


    def chmod(self, path, mode):
	p = getdata(mata_server, path)
        p['st_mode'] &= 0o770000
        p['st_mode'] |= mode
	putdata(mata_server, path, p)
        return 0

    def chown(self, path, uid, gid):
        p = getdata(mata_server, path)
        p['st_uid'] = uid
        p['st_gid'] = gid
        putdata(mata_server, path, p)

    def create(self, path, mode):
	mata = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                     st_size=0, st_ctime=time(), st_mtime=time(),
                     st_atime=time())
	putdata(mata_server, path, mata)
        self.fd += 1
	data = [[]]
	server = self.hashpath(path)
	for i in range(replica_num):
		for server in range(server_num):
			data = [[],i]
			putdata(data_server_list[server],path,data)
        return self.fd

    def getattr(self, path, fh = None):
	p = getdata(mata_server, path)
	#print(p)
	if p == 'error': #move keyerror into matasever
		raise FuseOSError(ENOENT)     
        return {attr:p[attr] for attr in p.keys() if attr != 'files'}

    def getxattr(self, path, name, position=0):
       
	p = getdata(mata_server, path)
        attrs = p.get('attrs', {})
        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
	p = getdata(mata_server, path)
        attrs = p.get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
	mata = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time(),files={})
	path_parent = path[:path.rfind('/')]
	if path_parent == '':
		path_parent = '/'
	parent = getdata(mata_server, path_parent)
	parent['st_nlink'] += 1
	putdata(mata_server, path_parent, parent)
	putdata(mata_server, path, mata)
	data = [defaultdict(list)]
	for server in range(server_num): #make folder in every server
		for i in range(replica_num): #make folder in every replica
			data = [defaultdict(list),i]
			putdata(data_server_list[server],path,data)	

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read_data(self,server,path): #read data from different server and put them together
	rep_list = []
	server_corrup = [] 
	path_corrup = []
	data_file = []
	data_dic = []	
	path_temp = path
	server_temp = server
	for k in range(replica_num):
		rep_list.append(k)
	for j in range(replica_num):
		err = 0	
		s = random.choice(rep_list)#randomly choose one replica to read
		rep_list.remove(s)
		server = (server_temp+s)%server_num		 
		path = path_temp+str(s)#s:replica index in server 
		print('path',path)		 	
		try:
			data = getdata(data_server_list[server], path)
			if type(data) == list: #read files from server
				for da in data:
					new_checksum = self.crc16(da[:-4])  #calculate new checksum
					if new_checksum != da[-4:]:   #data corruption
						print('error! data corruption')
						server_corrup.append(server)#save corruption sever and path
						path_corrup.append(path)
						err = 1
						break #find another replica
					else:
						data_file.append(da[:-4])#no corruption, read data
				if err == 1:
					continue
				for v in range(len(server_corrup)):
					print('recover data')
					putdata(data_server_list[server_corrup[v]],path_corrup[v],data) #write back to the corruption server, recover corrupted data
				break
			else:
				data_dic.append(data)#read folder from server
				break
		except: 
			continue
	
	d = [data_file]	
	for i in range(1,server_num):
		data_file = []
		server_corrup = [] 
		path_corrup = []
		rep_list = []
		for k in range(replica_num):
			rep_list.append(k)
		for j in range(replica_num):
			err = 0	
			s = random.choice(rep_list) #randomly choose one replica to read
			rep_list.remove(s)
			#s = 0	
			server = (server_temp+s+i)%server_num		 
			path = path_temp+str((s)%replica_num)#s:replica index in server 
			try:
				data = getdata(data_server_list[server], path)
				if type(data) == list:
					for da in data:
						new_checksum = self.crc16(da[:-4])  #calculate new checksum
						if new_checksum != da[-4:]:   #data corruption
							print('error! data corruption')
							server_corrup.append(server)
							path_corrup.append(path)
							err = 1
							break
						else:
							data_file.append(da[:-4])
					if err == 1:
						continue
					d.append(data_file)
					for v in range(len(server_corrup)):
						putdata(data_server_list[server_corrup[v]],path_corrup[v],data) #write back to the corruption server
					break
				else: 
					data_dic.append(data)
				break
		
			except: 
				continue
	if type(data) == defaultdict:
		return data_dic
	else:
		#print(d)
		x=[]
		for i in range(len(d[0])):
			x.append( d[0][i])#put all the string from different server together
			try:
				x.append(d[1][i])
				x.append(d[2][i])
				x.append(d[3][i])
			except IndexError:
				pass
		return x 	

    def read(self, path, size, offset, fh):
	server = self.hashpath(path)
	print('read',path)
	print('read',server)
        d = self.read_data(server,path)
	print(d)
	p = getdata(mata_server, path)
        if offset + size > p['st_size']:
            size = p['st_size'] - offset
        dd = ''.join(d[offset//bsize : (offset + size - 1)//bsize + 1])
        dd = dd[offset % bsize:offset % bsize + size]
        return dd

    def readdir(self, path, fh):
        p = getdata(mata_server, path)
	p = p['files']
        return ['.', '..'] + [x for x in p ]

    def readlink(self, path):
	server = self.hashpath(path) 
        d = self.read_data(server,path)
	return ''.join(d)

    def removexattr(self, path, name):
	p = getdata(mata_server, path)
        attrs = p.get('attrs', {})
        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
	old_parent = old[:old.rfind('/')]
	new_parent = new[:new.rfind('/')]
	po = getdata(mata_server, old_parent)
	po1 = old[old.rfind('/')+1:]
	pn = getdata(mata_server, new_parent)
	if po1 in pn['files']:
		pn['files'].pop(po1)
		pn['st_nlink'] -= 1
	pn1 = new[new.rfind('/')+1:]
        if po['files'][po1]['st_mode'] & 0o770000 == S_IFDIR:
            po['st_nlink'] -= 1
            pn['st_nlink'] += 1
        pn['files'][pn1] = po['files'].pop(po1)
	print('po',po)	
	print('pn',pn)
	if old_parent == '':#root
		old_parent ='/'
	if new_parent == '':
		new_parent = '/'
	if old_parent != new_parent:
		putdata(mata_server, old_parent, po)
	putdata(mata_server, new_parent, pn)
	server_do = self.hashpath(old)
	do_list = self.read_data(server_do,old_parent)
	do1 = old[old.rfind('/')+1:]
	if old_parent == new_parent:
		server_dn = server_do
	else:
		server_dn = self.hashpath(new)	
	dn_list = self.read_data(server_dn,new_parent)
	dn1 = new[new.rfind('/')+1:]
	dos = []
	dns=[]
	for i in range(server_num):#
		dn = dn_list[i]
		if do1 in dn:		
			dn.pop(do1)
		do = do_list[i]
		dn[dn1] = do.pop(do1)
		dos.append(do)
		dns.append(dn[dn1])
	i = 0  #delete old file
	for do in dos:
		for f in range(0,replica_num): 
			data = [do,f]
			putdata(data_server_list[(self.hashpath(old)+i+f)%server_num], old_parent, data)
		i+=1		
	i = 0 #put new file
	for x in dns:		
		for j in range(0,replica_num): 
			data = [x,j]
			putdata(data_server_list[(self.hashpath(new)+i+j)%server_num], new, data)
		i+=1	
		

    def rmdir(self, path):
	tar = path[path.rfind('/')+1:]
	parent = path[:path.rfind('/')]
	p = getdata(mata_server, parent)
        if len(p['files'][tar]['files']) > 0:
            raise FuseOSError(ENOTEMPTY)
        p['files'].pop(tar)
        p['st_nlink'] -= 1
	putdata(mata_server, parent, p)

    def setxattr(self, path, name, value, options, position=0):
	p = getdata(mata_server, path)
        attrs = p.setdefault('attrs', {})
        attrs[name] = value
	putdata(mata_server, path, p)

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
	tar = target[target.rfind('/')+1:]
	parent = target[:target.rfind('/')]
	p = getdata(mata_server, parent)
        p['files'][tar] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
                                  st_size=len(source))
	putdata(mata_server, parent, p)
	data = [source[i:i+bsize] for i in range(0, len(source), bsize)]
	server = self.hashpath(target)
	for j in range(len(data)):
		data[j] += self.crc16(data[j])#add checksum
	for i in range(0,replica_num):
		self.writedata(data,(server+i+j)%server_num,target,i)
	return True
	
	
    def writedata(self,data,server,path,j):#j:index of the replica, j=0, 1 or 2
	if len(data) < server_num:
		data_0 = [data[0]]
		data_0 = [data_0] 
		data_0.append(j)  # [[data],j] send both data and its replica index to server together with a list
		ack = putdata(data_server_list[server], path, data_0)
		for i in range (1,server_num):
			try:
				#data0 = [data[i]]
				data1 = [[data[i]]]
				data1.append(j)
				putdata(data_server_list[(server+i)%server_num], path, data1)
			except IndexError:
				pass
	else:
		data_total = []
		for k in range(server_num):
			datax = [[data[k]]]
			data_total.append(datax)
		for i in range(server_num,len(data)):
			data_total[i%server_num][0].append(data[i])
		for t in range(server_num):
			data_total[t].append(j)
		h = 0
		for d in data_total:
			putdata(data_server_list[(server+h)%server_num], path, d)
			h += 1
		
    def truncate(self, path, length, fh=None):
	server = self.hashpath(path)
	xx = self.read_data(server,path)
        xx = [(xx[i] if i < len(xx) else '').ljust(bsize, '\x00') for i in range(length//bsize)] \
                + [(xx[length/bsize][:length % bsize] if length//bsize < len(xx) else '').ljust(length % bsize, '\x00')]
	for i in range(replica_num):
        	self.writedata(xx,(server+i)%server_num,path,i)
	p = getdata(mata_server, path)
        p['st_size'] = length
	putdata(mata_server, path, p)

    def unlink(self, path):
	parent = path[:path.rfind('/')]
	tar = path[path.rfind('/')+1:]
	p = getdata(mata_server, parent)
        p['files'].pop(tar)
	if parent == '':
		parent = '/' #root
	putdata(mata_server, parent, p)
	d = self.read_data(0 , parent)
	d1 = path[path.rfind('/')+1:]
	for i in range(server_num):####delete all the files
		if d1 in d[i]:
        		d[i].pop(d1)
		for j in range(replica_num):
			data = [d[i],j]
			putdata(data_server_list[(i)%server_num], parent, data)
				

    def utimens(self, path, times = None):
        now = time()
        atime, mtime = times if times else (now, now)
	p = getdata(mata_server, path)
        p['st_atime'] = atime
        p['st_mtime'] = mtime
	putdata(mata_server, path, p)

    def write(self, path, data, offset, fh):
	server = self.hashpath(path)
	p = getdata(mata_server, path)
	parent = path[:path.rfind('/')]
	xx = self.read_data(server,path)
        if offset > p['st_size']:
            xx = [(xx[i] if i < len(xx) else '').ljust(bsize, '\x00') for i in range(offset//bsize)] \
                    + [(xx[offset/bsize][:offset % bsize] if offset//bsize < len(xx) else '').ljust(offset % bsize, '\x00')]
        size = len(data)
        sdata = [data[:bsize - (offset % bsize)]] + [data[i:i+bsize] for i in range(bsize - (offset % bsize), size, bsize)]
        blks = range(offset//bsize, (offset + size - 1)//bsize + 1)
        mod = blks[:]
        mod[0] = (xx[blks[0]][:offset % bsize] if blks[0] < len(xx) else '').ljust(offset % bsize, '\x00') + sdata[0]
        if len(mod[0]) != bsize and blks[0] < len(xx):
            mod[0] = mod[0] + xx[blks[0]][len(mod[0]):]
        mod[1:-1] = sdata[1:-1]
        if len(blks) > 1:
            mod[-1] = sdata[-1] + (xx[blks[-1]][len(sdata[-1]):] if blks[-1] < len(xx) else '')
        xx[blks[0]:blks[-1] + 1] = mod
        p['st_size']= offset + size if offset + size > p['st_size'] else p['st_size']
	putdata(mata_server, path, p)
	print(xx)
	for i in range (len(xx)): #add checksum before write to server
		xx[i] += self.crc16(xx[i])
	for i in range(replica_num): #write to servers
		self.writedata(xx,(server+i)%server_num,path,i)
        return size


def ping_server(data_server_list): #make sure all servers are available before write
	for server in data_server_list:
		try:
			server.ping()
		except:
			return False
	return True


def putdata(server, key, value): 
	if ping_server(data_server_list) == True:	
    		ack = server.put(Binary(key), Binary(pickle.dumps(value)))
		print('ack',ack)
		return ack
	else:
		print('error: server down')#ping_server retrun False: at least one server is down, keep retrying
		print('retry in 1 second')
		times.sleep(1)
		putdata(server, key, value)

def getdata(server, key):
	return pickle.loads(server.get(Binary(key)).data)

def main(sports):			
	mata_server = xmlrpclib.ServerProxy("http://localhost:" + str(int(sports[0])))
	for sport in sports[1:]:
		data_server = xmlrpclib.ServerProxy("http://localhost:" + str(int(sport)))
		data_server_list.append(data_server)
	return mata_server , data_server_list

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    server_num = len(argv)-3
    sports = argv[2:]
    mata_server,data_server_list = main(sports)
    fuse = FUSE(Memory(), argv[1], foreground=True, debug=True)
