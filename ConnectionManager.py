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
	def unpack(self,byte_string: bytes):
		global LEN_OF_TYPE
		global LEN_OF_HEADER
		"""
		This method unpacks a byte string into this class.
		
		Args:
			byte_string(Byte str) - The message in byte string for.
		"""
		self.type = byte_string[:LEN_OF_TYPE].decode('utf-8')
		self.body = byte_string[LEN_OF_HEADER:].decode('utf-8')
def get_size_of_msg(byte_str: bytes):
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
def scramble(in_hex: str):
	""" This method scrambles the in hex and returns the scrambled hex."""
	num = int(in_hex,16)
	num = num ^ 2044882523
	num = hex(num)
	return num
class Client:
	""" This class represents a client connection

		Args:
			run(bool) - The running state of the client listen for message loop.
			raise_exceptions(bool) - defines wheter the loops should raise errors found to the user pogram.
			address(string) - The hos the client is connecting to.
			port(int) - The port the client is connecting to.
			on_connect(function) - The function that is called when the client successfully connects to the server. no params.
			on_disconnect(function) - The function that is called when the client disconnects from the server. no params.
			timeout(int) - The time it takes until the waiting for message loop times out. creates a faster response when a client disconnects.
			scramble(bool) - determines if the handshake protocol should be used.
			type_callbacks(dict(str,function)) - The callbacks that are called when the message type is received.
			socket(socket) - The raw socket connection.
			thread(thread) - The thread that the socket is running on.

	"""
	def __init__(self,address:str,port:int,on_connect,on_disconnect,timeout:int = 1):
		global scramble
		""" Constructor
		
		Args:
			address(str) - The address the client is trying to connect to.
			port(int) - The port the client is trying to connect to.
			on_connect(function()) - The function that is called when the client connects. No params.
			on_disconnect(function()) - The function that is called when the client disconnects. No params.
			timeout(int) - The timeout until the waiting for msg loop repeats.
			scramble_func(function(hex_str)) - The scramble function for the connections, returns a hex string.
		"""
		self.run = False
		self.raise_exceptions = False
		self.address = address
		self.port = port
		self.on_connect = on_connect
		self.on_disconnect = on_disconnect
		self.timeout = timeout
		self.scramble = True
		self.type_callbacks = {}
		self.scramble_func = scramble
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format,level=logging.INFO,datefmt='%H:%M:%S')
	def connect(self):
		"""connects to the server, calls the scramble function, and begins the wait for message loop."""
		self.run = True
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		server_addr = (self.address,self.port)
		sock.connect(server_addr)
		sock.settimeout(self.timeout)
		self.socket = sock
		if self.scramble:
			data = sock.recv(12)
			sock.send(self.scramble_func(data.decode('utf-8')).encode('utf-8'))
		self.thread = threading.Thread(target = self.on_msg,args = (sock,))
		self.thread.setDaemon(True)
		self.thread.start()
	def on_msg(self,sock: socket.socket):
		"""The message loop that recieves message from the server and sends them to the respective callback functions.
		Args:
			sock(socket) - The socket connection to the server.
		Throws:
			Exception - When the type from the message does not have a callback.
		"""
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
				if self.raise_exceptions:
					raise e
				break
		self.run = False
		sock.close()
		self.on_disconnect()
	def send_to_server(self,msg: Message):
		""" sends message to the server. closes socket and stops the message loop if the message is not sent correctly.
		Args:
			msg(Message) - the message to be sent to the server.
		"""
		sent = self.socket.send(msg.pack())
		if sent == 0:
			self.run = False
			self.socket.close()
	def disconnect(self):
		""" Stops teh message loop which closes teh socket."""
		self.run = False
	def active(self):
		"""returns whether the message loop is running"""
		return self.run
	def set_type_callback(self,type: str,callback):
		"""assigns the callback to the message type
		Args:
			type(str) - the type to assign the callback to
			callback(function) - the function assigned to the type, takes in a message parameter.
		"""
		self.type_callbacks[type] = callback
	def join_all_threads(self):
		"""joins the client thread"""
		self.thread.join()





class Server:
	"""This class represents a server connection.

	Args:
		connections(list)-The list of conenctions, past and present, the indicy represents the id the connection. This has the following structure:
				connections:[{
					"address": The ip adress of the connection. EX "127.0.0.1",
					"thread": The thread that the connection is running on,
					"socket": The socket object for the connections,
					"active": Signifies if the connection is still active,
				},
				...]
		run(bool) - signifies if the connections loop is active and all connection loops are active.
		connection_id (int) - tracks the id of the next connections.
		raise_exceptions (bool) - signifies if exceptions should be raised to the user of logged and continue.
		host_name (str) - The host of the server.
		port (int) - the port of the server.
		n_connections(int) - The maximum number of allowed connections.
		timeout(int) - THe number of second until the listening loop or the listne for message loop times out.
		on_connect(function(socket,address)) - The function that is called when a client initially connects.
		on_verification(function(int)) - The function that is called when the client has passed verification and is ready for data.
		on_disconnect(function(int)) - The function that is called when the client disconnects.
		scramble(bool) - signifies if the connections should be verified withe scramble function.
		scramble_func(function(hex_str)) - The scramble function for the server, returns a hex string.
		type_callbacks(dict(str,function(msg,id))) - The callbacks for a specific message type.
		server_thread(thread) - The thread that the listen for client loop is running on.
	"""
	def __init__(self,host_name: str,port: int,on_connect,on_verification,on_disconnect,n_connections = None,timeout = 1):
		"""constructor
		Args:
			host_name(str)-the ip of the host, IE "127.0.0.1" or ""
			port(int)-the port for the connection
			on_connect(function(socket,address))-The function called when a client connects to the server.
			on_verification(function(id))-The function called when the client is verified.
			on_diconnect(function(id))-The function called when the client disconnects.
			n_connections(int)-the maximum number of connections to the server
			timeout(int)-seconds until the listen foe connection loop or listen for message loop timeout.
		"""
		global scramble
		self.connections = []
		self.run = False
		self.connection_id = 0
		self.raise_exceptions = False
		self.host_name = host_name
		self.port = port
		self.n_connections = n_connections
		self.timeout = timeout
		self.on_connect = on_connect
		self.on_verification = on_verification
		self.on_disconnect = on_disconnect
		self.scramble = True
		self.scramble_func = scramble
		self.type_callbacks = {}
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format,level=logging.INFO,datefmt='%H:%M:%S')
	def start(self):
		"""This method start the server.

		This method starts the server and start the listen for connections thread
		"""
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
	def listen_for_connections(self,socket: socket.socket):
		"""
		This method listens for conections to the server.
		Args:
			socket(socket)-the socket that is listening for connections.
		"""
		self.run = True
		logging.info("Listening for connections")
		while self.run:
			try:
				conn,addr = socket.accept()
				if not self.on_connect(conn,addr):
					conn.close()
					continue
				t = int(round(time.time() * 1000))
				t = hex(t)
				t = t[-10:]# last ten
				if self.scramble:
					conn.send(t.encode('utf-8'))
					data = conn.recv(12)
					data = data.decode('utf-8')
					if(data != self.scramble_func(t)):
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
	def on_msg(self,connection:socket.socket,id: int):
		"""This method listens for messages from established connections and passes the message to the respective callback method.
		Args:
			connection(socket)-The socket connection for the client.
			id(int)-The connection Id of teh client.

		"""
		ping_sent = False
		connection.settimeout(self.timeout)
		self.on_verification(id)
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
				if self.raise_exceptions:
					raise e
		self.connections[id]["active"] = False
		connection.close()
		self.on_disconnect(id)
	def set_type_callback(self,type: str,callback):
		"""Sets the callback for the message type.
		Args:
			type(str)-The 4 character type of the message.
			callback(fuinction(Message,int))-The callback for the message

		"""
		self.type_callbacks[type] = callback
	def send_to_client(self,msg: Message,id: int):
		"""send the provided message to the client with this id.
		Args:
			msg(Message)-The message to send
			id(int)-The id of the client
		"""
		sent = self.connections[id]["socket"].send(msg.pack())
		if sent == 0:
			self.connections[id]["active"] = False
			self.connections[id]["socket"].close()
	def send_to_all_clients(self,msg:Message):
		"""Sends the message to all active clients
		Args:
			msg(Message)-The message to send
		"""
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				self.send_to_client(msg,i)
	def disconnect(self):
		"""Stops the listen for client loop and all active connections.
		"""
		self.run = False
		for i in range(len(self.connections)):
			self.connections[i]["active"] = False
	def get_active_clients(self):
		"""Get the list of active clients
		Returns:
			list - of active client ids
		"""
		out = []
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				out.append(i)
		return out
	def client_active(self,id: int):
		"""checks if a specific client is active.
		Args:
			id(int)-The id of the client we are checking
		"""
		return self.connections[id]["active"]
	def active(self):
		"""Returns wether or no the listen for connections thread, and listen for message threads are running
		"""
		return self.run
	def get_connection(self,id: int):
		"""get the connection from the id.
		Args:
			id(int)-The id of the connection
		"""
		return self.connections[id]
	def disconnect_client(self,id: int):
		"""disconnects a specific client.
		Args:
			id(int)-The id of the client we want to disconnect
		"""
		logging.info("Stopping Connection to " + str(id))
		self.connections[id]["active"] = False
		self.connections[id]["socket"].close()
	def join_all_threads(self):
		"""Joins the listen for client and active connectiosn threads.
		"""
		self.server_thread.join()
		for i in range(len(self.connections)):
			self.connections[i]["thread"].join()

