import socket
from socket import timeout
import threading
import sys
import logging
import time
special_words = [b'ping',b'pong',b'end',b'\n>>>>']
end_of_msg_word = b'\n>>>>'
class ConnectionManager:
	def __init__(self):
		self.connections = []
		self.run = False
		self.connection_id = 0
		self.raise_exceptions = False
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format,level=logging.INFO,datefmt='%H:%M:%S')
	def start_server(self,host_name,port,callback,n_connections = None,timeout = 5):
		logging.info("Starting server...")
		sock = socket.socket()
		server_addr = (host_name,port)
		sock.settimeout(timeout)
		sock.bind(server_addr)
		sock.listen(n_connections)
		self.server_thread = threading.Thread(target = self.listen_for_connections, args = (sock,))
		self.server_thread.setDaemon(True)
		self.server_callback = callback
		self.timeout = timeout
		self.millis = []
		self.server_thread.start()
	def listen_for_connections(self,socket):
		self.run = True
		logging.info("Listening for connections")
		while self.run:
			try:
				conn,addr = socket.accept()
				logging.info("Connection Found.")
				self.connections.append({})
				self.connections[self.connection_id]["address"] = addr
				self.connections[self.connection_id]["thread"] = threading.Thread(target = self.on_client_msg,args = (conn,self.connection_id))
				self.connections[self.connection_id]["thread"].setDaemon(True)
				self.connections[self.connection_id]["thread"].start()
				self.connections[self.connection_id]["socket"] = conn
				self.connections[self.connection_id]["msgs"] = []
				self.connections[self.connection_id]["ping"] = 999
				self.millis.append(0) 
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
	def on_client_msg(self,connection,id):
		ping_sent = False
		connection.settimeout(self.timeout)
		self.millis[id] = int(round(time.time()*1000))
		self.connections[id]["active"] = True
		running_msg = b''
		while self.run and self.connections[id]["active"]:
			try:
				data = connection.recv(1024)
				data = running_msg + data
				running_msg = b''
				msgs = data.split(end_of_msg_word)
				for i in range(len(msgs)):
					if msgs[i] == b'':
						continue
					if msgs[i] == b'pong':
						ping_sent = False
						cur_millis = int(round(time.time()*1000))
						self.connections[id]["ping"] = cur_millis - self.millis[id]
						logging.info("Leg between server and " + str(id) + ":" + str(cur_millis - self.millis[id]))
					else:
						if (i == (len(msgs) - 1)):
							running_msg = msgs[i]
						else: 
							self.server_callback(msgs[i],id)
			except timeout:
				if ping_sent:
					self.connections[id]["active"] = False
					logging.info("Shutting down connection to " + str(id))
				else:
					logging.info("Sending Ping To " + str(id))
					self.millis[id] = int(round(time.time()*1000))
					connection.send(b'ping' + b'\n>>>>')
					ping_sent = True
			except Exception as e:
				logging.info(e)
				self.connections[id]["active"] = False
				if self.raise_exceptions:
					raise e
		self.connections[id]["active"] = False
		connection.close()
	def send_to_client(self,msg,id):
		if msg.find(end_of_msg_word) != -1:
			raise Exception(msg.decode('utf-8') + " contains end of msg string: " + end_of_msg_word.decode('utf-8'))
		if msg in special_words:
			raise Exception(msg.decode('utf-8') + " is a special word")
		self.connections[id]["socket"].send(msg + end_of_msg_word)
	def send_to_all_clients(self,msg):
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				self.send_to_client(msg,i)
	def connect_to_server(self,address,port,callback,timeout = 5):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		server_addr = (address,port)
		sock.connect(server_addr)
		self.client_callback = callback
		self.client_socket = sock
		sock.settimeout(timeout)
		self.client_thread = threading.Thread(target = self.on_server_msg,args = (sock,))
		self.client_thread.setDaemon(True)
		self.client_thread.start()
	def on_server_msg(self,sock):
		logging.info("Listening for server messages.")
		self.run = True
		self.client_sock_active = True
		running_msg = b''
		while self.run and self.client_sock_active:
			try:
				data = sock.recv(1024)
				data = running_msg + data
				running_msg = b''
				msgs = data.split(end_of_msg_word)
				for i in range(len(msgs)):
					if msgs[i] == b'':
						continue
					if msgs[i] == b'ping':
						logging.info("Sending Pong To Server")
						sock.send(b'pong' + end_of_msg_word)
					else:
						if (i == (len(msgs) - 1)):
							running_msg = msgs[i]
						else: 
							self.client_callback(msgs[i])
			except timeout:
				continue
			except Exception as e:
				self.client_sock_active = False
				logging.info(e)
				if self.raise_exceptions:
					raise e
		self.client_sock_active = False
		sock.close()
	def send_to_server(self,msg):
		if msg.find(end_of_msg_word) != -1:
			raise Exception(msg.decode('utf-8') + " contains end of msg string: " + end_of_msg_word.decode('utf-8'))
		if msg in special_words:
			raise Exception(msg.decode('utf-8') + " is a special word")
		self.client_socket.send(msg + end_of_msg_word)
	def disconnect(self):
		self.run = False
		self.client_sock_active = False
		for i in range(len(self.connections)):
			self.connections[i]["active"] = False
	def client_socket_active(self):
		return self.client_sock_active
	def server_still_listening(self):
		return self.run
	def get_active_clients(self):
		out = []
		for i in range(len(self.connections)):
			if self.connections[i]["active"]:
				out.append(i)
		return out
	def join_all_threads(self):
		self.disconnect()
		if hasattr(self,"client_thread") and self.client_thread.isAlive():
			self.client_thread.join()
		for i in range(len(self.connections)):
			if self.connections[i]["thread"].isAlive():
				self.connections[i]["thread"].join()
	def change_client_callback(self,callback):
		self.client_callback = callback
	def change_server_callback(self,callback):
		self.server_callback = callback
	def get_connection(self,id):
		return self.connections[id]
	def disconnect_client(self,id):
		logging.info("Stopping Connection to " + str(id))
		self.connections[id]["active"] = False
	def ping_all(self):
		for con in self.connections:
			if con["active"]:
				con["socket"].send(b'ping' + end_of_msg_word)