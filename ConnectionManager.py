import socket
from socket import timeout
import threading
import sys
import logging
import time
LEN_OF_TYPE = len(b'XXXX')
LEN_OF_SIZE = len(b'0x00000000')
LEN_OF_HEADER = LEN_OF_TYPE + LEN_OF_SIZE
MAX_LEN_OF_RECV = 4096
class Message:
	"""
	a class that defines a message passed between the the client and server
	"""
	def __init__(self,type: str = "XXXX",body: str = ""):
		global LEN_OF_TYPE
		"""
		constructor

		Args:
			type(str)-The type of the message, 4 characters long.
			body(str)-The body of the message.
		Throws:
			ValueError - If the type is not 4 characters long
		"""
		if len(type) != LEN_OF_TYPE:
			raise ValueError("The length of the type must be 4")
		self.type = type
		self.body = body
	def pack(self):
		global LEN_OF_SIZE
		"""
		This method packs the type,body, and size into a byte string.

		Returns:
			Byte String - The type, size(length of the body turned into a hex string), and body
		"""
		b_body = self.body.encode('utf-8')
		l = len(b_body)
		len_hex = hex(l)
		len_hex = len_hex[:2] + '0' * (LEN_OF_SIZE - len(len_hex)) + len_hex[2:]
		return self.type.encode('utf-8') + len_hex.encode('utf-8') + b_body
	def unpack(self,byte_string):
		global LEN_OF_TYPE
		global LEN_OF_HEADER
		"""
		This method unpacks a byte string into this class.
		
		Args:
			byte_string(Byte str) - The message in byte string for.
		"""
		self.type = byte_string[:LEN_OF_TYPE].decode('utf-8')
		self.body = byte_string[LEN_OF_HEADER:].decode('utf-8')
def get_size_of_msg(byte_str):
	global LEN_OF_TYPE
	"""
	This method gets the length of a mesage from the header byte string

	Args:
		byte_str(Byte String) - The header byte string

	Returns:
		The length in bytes of the message body
	"""
	byte_str = byte_str[LEN_OF_TYPE:]
	return int(byte_str,16)
def scramble(in_hex):
	""" This method scrambles the in hex and returns the scrambled hex."""
	num = int(in_hex,16)
	num = num ^ 2044882523
	num = hex(num)
	return num
class Client:
	def __init__(self,address,port,on_connect,on_disconnect,timeout = 1):
		self.run = False
		self.connection_id = -1
		self.raise_exceptions = False
		self.address = address
		self.port = port
		self.on_connect = on_connect
		self.on_disconnect = on_disconnect
		self.timeout = timeout
		self.scramble = True
		self.type_callbacks = {}
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format,level=logging.INFO,datefmt='%H:%M:%S')
	def connect(self):
		self.run = True
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		server_addr = (self.address,self.port)
		sock.connect(server_addr)
		sock.settimeout(self.timeout)
		self.socket = sock
		if self.scramble:
			data = sock.recv(12)
			sock.send(scramble(data.decode('utf-8')).encode('utf-8'))
		self.thread = threading.Thread(target = self.on_msg,args = (sock,))
		self.thread.setDaemon(True)
		self.thread.start()
	def on_msg(self,sock):
		logging.info("Listening for server messages.")
		self.run = True
		self.on_connect()
		while self.run:
			try:
				data = sock.recv(LEN_OF_HEADER)
				if data == b'':
					self.run = False
					continue
				body_len = get_size_of_msg(data)
				body = b''
				if body_len != 0:
					while body_len > 0:
						if body_len > MAX_LEN_OF_RECV:
							body += sock.recv(MAX_LEN_OF_RECV)
							body_len -= MAX_LEN_OF_RECV
						else:
							body += sock.recv(body_len)
							body_len = 0
				msg = Message()
				msg.unpack(data + body)
				if msg.type in self.type_callbacks.keys():
					self.type_callbacks[msg.type](msg)
				else:
					self.run = False
					raise Exception("Type: %s isnt defined in the callbacks" % msg.type)
			except timeout:
				continue
			except Exception as e:
				logging.info(e)
				self.run = False
				self.on_disconnect()
				if self.raise_exceptions:
					raise e
				break
		self.run = False
		sock.close()
	def send_to_server(self,msg: Message):
		self.socket.send(msg.pack())
	def disconnect(self):
		self.run = False
	def active(self):
		return self.run
	def set_type_callback(self,type: str,callback):
		self.type_callbacks[type] = callback
	def join_all_threads(self):
		self.thread.join()





class Server:
	def __init__(self,host_name,port,on_connect,on_disconnect,n_connections = None,timeout = 1):
		self.connections = []
		self.run = False
		self.connection_id = 0
		self.raise_exceptions = False
		self.host_name = host_name
		self.port = port
		self.n_connections = n_connections
		self.timeout = timeout
		self.on_connect = on_connect
		self.on_disconnect = on_disconnect
		self.scramble = True
		self.type_callbacks = {}
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format,level=logging.INFO,datefmt='%H:%M:%S')
	def start(self):
		logging.info("Starting server...")
		sock = socket.socket()
		server_addr = (self.host_name,self.port)
		sock.settimeout(self.timeout)
		sock.bind(server_addr)
		if self.n_connections == None:
			sock.listen()
		else:
			sock.listen(self.n_connections)
		self.server_thread = threading.Thread(target = self.listen_for_connections, args = (sock,))
		self.server_thread.setDaemon(True)
		self.server_thread.start()
	def listen_for_connections(self,socket):
		self.run = True
		logging.info("Listening for connections")
		while self.run:
			try:
				conn,addr = socket.accept()
				t = int(round(time.time() * 1000))
				t = hex(t)
				t = t[-10:]# last ten
				if self.scramble:
					conn.send(t.encode('utf-8'))
					data = conn.recv(12)
					data = data.decode('utf-8')
					if(data != scramble(t)):
						conn.close()
						return
				logging.info("Connection Found [" + str(addr) + "].")
				self.connections.append({})
				self.connections[self.connection_id]["address"] = addr
				self.connections[self.connection_id]["thread"] = threading.Thread(target = self.on_msg,args = (conn,self.connection_id))
				self.connections[self.connection_id]["thread"].setDaemon(True)
				self.connections[self.connection_id]["socket"] = conn
				self.connections[self.connection_id]["active"] = True
				self.connections[self.connection_id]["thread"].start()
				self.connection_id += 1
			except timeout:
				continue
			except Exception as e:
				self.run = False
				logging.info(e)
				if self.raise_exceptions:
					raise e
		logging.info("Server Stopped.")
		self.run = False
		socket.close()
	def on_msg(self,connection,id):
		ping_sent = False
		connection.settimeout(self.timeout)
		self.on_connect(id)
		while self.run and self.connections[id]["active"]:
			try:
				data = connection.recv(LEN_OF_HEADER)
				if data == b'':
					self.connections[id]["active"] = False
					continue
				body_len = get_size_of_msg(data)
				body = b''
				if body_len != 0:
					while body_len > 0:
						if body_len > MAX_LEN_OF_RECV:
							body += connection.recv(MAX_LEN_OF_RECV)
							body_len -= MAX_LEN_OF_RECV
						else:
							body += connection.recv(body_len)
							body_len = 0
				msg = Message()
				msg.unpack(data + body)
				if msg.type in self.type_callbacks.keys():
					self.type_callbacks[msg.type](msg,id)
				else:
					self.run = False
					raise Exception("Type: %s isnt defined in the callbacks" % msg.type)
			except timeout:
				continue
			except Exception as e:
				logging.info(e)
				self.connections[id]["active"] = False
				self.on_disconnect(id)
				if self.raise_exceptions:
					raise e
		self.connections[id]["active"] = False
		connection.close()
		self.on_disconnect(id)
	def set_type_callback(self,type: str,callback):
		self.type_callbacks[type] = callback
	def send_to_client(self,msg: Message,id: int):
		self.connections[id]["socket"].send(msg.pack())
	def send_to_all_clients(self,msg):
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				self.send_to_client(msg,i)
	def disconnect(self):
		self.run = False
		for i in range(len(self.connections)):
			self.connections[i]["active"] = False
	def server_still_listening(self):
		return self.run
	def get_active_clients(self):
		out = []
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				out.append(i)
		return out
	def active(self):
		return self.run
	def get_connection(self,id):
		return self.connections[id]
	def disconnect_client(self,id):
		logging.info("Stopping Connection to " + str(id))
		self.connections[id]["active"] = False
	def join_all_threads(self):
		self.server_thread.join()
		for i in range(len(self.connections)):
			self.connections[i]["thread"].join()

