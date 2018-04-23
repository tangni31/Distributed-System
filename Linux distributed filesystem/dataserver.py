#!/usr/bin/env python
"""
Author: David Wolinsky
Version: 0.03

Description:
The XmlRpc API for this library is:
  get(base64 key)
    Returns the value associated with the given key using a dictionary
      or an empty dictionary if there is no matching key
    Example usage:
      rv = rpc.get(Binary("key"))
      print rv => Binary
      print rv.data => "value"
  put(base64 key, base64 value)
    Inserts the key / value pair into the hashtable, using the same key will
      over-write existing values
    Example usage:  rpc.put(Binary("key"), Binary("value"))
  print_content()
    Print the contents of the HT
  read_file(string filename)
    Store the contents of the Hahelperable into a file
  write_file(string filename)
    Load the contents of the file into the Hahelperable

Changelog:
    0.03 - Modified to remove timeout mechanism for data.
"""

import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest, shelve
from datetime import datetime, timedelta
from xmlrpclib import Binary
from collections import defaultdict


# Presents a HT interface
class SimpleHT:
  def __init__(self):
    global disk
    #self.data = defaultdict(list)
    self.replica0 = disk['0']#replica in disk
    self.replica1 = disk['1']
    self.replica2 = disk['2']
    self.replica = [self.replica0,self.replica1,self.replica2] #replica in memory

  def count(self):
    return len(self.data)

  def traverse(self, path):
    j = int(path[-1])
    #print('j',j)
    path = path[:-1]
    p = self.replica[j]
    if path == '':#root
    	return p
    #print(p)
    else: 
    	for i in path.split('/') :
		p = p[i] if len(i) > 0 else p
    	#print(p)   
    	return p

  def ping(self):#return true if client successful connect to server
    print('ping success')
    return True
  
  # Retrieve something from the HT
  def get(self, key):
    key = key.data
    d = self.traverse(key)
    print('read',d)
    d = pickle.dumps(d)
    d = Binary(d)
    return d

  # Insert something into the HT
  def put(self, key, value):
    global disk
    value = pickle.loads(value.data)
    #print(value)	#value sent to server is a list contain data and its replica index: [[data],index]
    j = int(value[-1]) #value[-1] is the index of replica
    d = self.replica[j]
    dd = disk[str(j)]	#d replica in server; dd replica in disk
    key = key.data	
    value_input = value[0]#value[0] is the data
    if key =='':
	d = value_input
	self.replica[j] = d
	dd = value_input
	disk[str(j)] = dd
    else: 			  
    	d1 = key[key.rfind('/')+1:]
    	key = key[:key.rfind('/')]
    	for i in key.split('/') :
		d = d[i] if len(i) > 0 else d 
		dd = dd[i] if len(i) > 0 else dd
    	d[d1] = value_input
    	dd[d1] = value_input
    disk.sync() #write data into disk
    print('-----------------replica 0----------------------')
    print('replica 0',self.replica[0])
    print('-----------------replica 1---------------------')
    print('replica 1',self.replica[1])	
    print('-----------------replica 2---------------------')
    print('replica 2',self.replica[2])
    return True

  # Load contents from a file
  def read_file(self, filename):
    f = open(filename.data, "rb")
    self.data = pickle.load(f)
    f.close()
    return True

  # Write contents to a file
  def write_file(self, filename):
    f = open(filename.data, "wb")
    pickle.dump(self.data, f)
    f.close()
    return True

  # Print the contents of the hashtable
  def print_content(self):
    print self.data
    return True

def main(): 
  port = int(sys.argv[int(sys.argv[1])+2])
  print('port number:',port)
  name = 'data_store' +str(sys.argv[1])
  server_num = len(sys.argv[2:])
  print('total servers:',server_num)
  #creat/read data file store in disk
  global disk 
  disk = shelve.open(name, flag ='c',writeback = True)
  if disk == {}:# if disk is empty, that means data in disk lost or this is the first time start the server 
	print('empty data files in disk')
	print('try to find replica')
	flag = 0
	for j in range(0,3): #j=0,1,2:recover replica 0,1,2
		for i in range(1,3):
			if j == 2:
				i += server_num - 3	
			#recover data from other 2 disk files 
			name_rep = 'data_store'+str((int(sys.argv[1])+i)%server_num)
			#print(name_rep)
			try:
				disk_rep = shelve.open(name_rep, flag ='r')#read from other servers' disk files
			except:
				continue
			rep_key = str((i+j)%3)
			try:
				print(disk_rep[rep_key])
			except:
				continue
			if disk_rep[rep_key] != defaultdict(list): #files in the other replica is not empty
				print('loading data from replica disk:',name_rep) #recover data
				disk[str(j)] = disk_rep[rep_key]
				disk.sync()
				flag = 1 #replica found, set flag to 1
				break
			else:
				continue		
	if flag == 0:
		print('no replica found, initialize server') #if not other replica founded, initialize server
  		disk['0'] = defaultdict(list)	#replica0
  		disk['1'] = defaultdict(list) 	#replica1
		disk['2'] = defaultdict(list)	#replica2	
		disk.sync()
  	else:
		print('data loaded from replica disk')
  else:
	print('load data from disk')
	
	print(disk['0'])
  print('data loaded')
  serve(port)
'''
	optlist, args = getopt.getopt(sys.argv[1:], "", ["port=", "test"])
  ol={}
  for k,v in optlist:
    ol[k] = v
  port = 51234
  if "--port" in ol:
    port = int(ol["--port"])
  if "--test" in ol:
    sys.argv.remove("--test")
    unittest.main()
  return
  '''

# Start the xmlrpc server
def serve(port):
  file_server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', port))
  file_server.register_introspection_functions()
  sht = SimpleHT()
  file_server.register_function(sht.get)
  file_server.register_function(sht.put)
  file_server.register_function(sht.print_content)
  file_server.register_function(sht.read_file)
  file_server.register_function(sht.write_file)
  file_server.register_function(sht.ping)##add ping
  file_server.serve_forever()

# Execute the xmlrpc in a thread ... needed for testing
class serve_thread:
  def __call__(self, port):
    serve(port)

# Wrapper functions so the tests don't need to be concerned about Binary blobs
class Helper:
  def __init__(self, caller):
    self.caller = caller

  def put(self, key, val, ttl):
    return self.caller.put(Binary(key), Binary(val), ttl)

  def get(self, key):
    return self.caller.get(Binary(key))

  def write_file(self, filename):
    return self.caller.write_file(Binary(filename))

  def read_file(self, filename):
    return self.caller.read_file(Binary(filename))

class SimpleHTTest(unittest.TestCase):
  def test_direct(self):
    helper = Helper(SimpleHT())
    self.assertEqual(helper.get("test"), {}, "DHT isn't empty")
    self.assertTrue(helper.put("test", "test", 10000), "Failed to put")
    self.assertEqual(helper.get("test")["value"], "test", "Failed to perform single get")
    self.assertTrue(helper.put("test", "test0", 10000), "Failed to put")
    self.assertEqual(helper.get("test")["value"], "test0", "Failed to perform overwrite")
    self.assertTrue(helper.put("test", "test1", 2), "Failed to put" )
    self.assertEqual(helper.get("test")["value"], "test1", "Failed to perform overwrite")
    time.sleep(2)
    self.assertEqual(helper.get("test"), {}, "Failed expire")
    self.assertTrue(helper.put("test", "test2", 20000))
    self.assertEqual(helper.get("test")["value"], "test2", "Store new value")

    helper.write_file("test")
    helper = Helper(SimpleHT())

    self.assertEqual(helper.get("test"), {}, "DHT isn't empty")
    helper.read_file("test")
    self.assertEqual(helper.get("test")["value"], "test2", "Load unsuccessful!")
    self.assertTrue(helper.put("some_other_key", "some_value", 10000))
    self.assertEqual(helper.get("some_other_key")["value"], "some_value", "Different keys")
    self.assertEqual(helper.get("test")["value"], "test2", "Verify contents")

  # Test via RPC
  def test_xmlrpc(self):
    output_thread = threading.Thread(target=serve_thread(), args=(51234, ))
    output_thread.setDaemon(True)
    output_thread.start()

    time.sleep(1)
    helper = Helper(xmlrpclib.Server("http://127.0.0.1:51234"))
    self.assertEqual(helper.get("test"), {}, "DHT isn't empty")
    self.assertTrue(helper.put("test", "test", 10000), "Failed to put")
    self.assertEqual(helper.get("test")["value"], "test", "Failed to perform single get")
    self.assertTrue(helper.put("test", "test0", 10000), "Failed to put")
    self.assertEqual(helper.get("test")["value"], "test0", "Failed to perform overwrite")
    self.assertTrue(helper.put("test", "test1", 2), "Failed to put" )
    self.assertEqual(helper.get("test")["value"], "test1", "Failed to perform overwrite")
    time.sleep(2)
    self.assertEqual(helper.get("test"), {}, "Failed expire")
    self.assertTrue(helper.put("test", "test2", 20000))
    self.assertEqual(helper.get("test")["value"], "test2", "Store new value")

if __name__ == "__main__":
  main()
