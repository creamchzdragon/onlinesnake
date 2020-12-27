import ConnectionManager
import time
import json
def on_c():
	pass
def on_d():
	pass
def on_pong(msg):
	print(msg.type)
	print(msg.body)
man = ConnectionManager.Client('localhost',50000,on_c,on_d)
man.set_type_callback("PONG",on_pong)
man.connect()
msg = ConnectionManager.Message("PING","")
man.send_to_server(msg)
while man.run:
	pass