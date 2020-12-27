import ConnectionManager
import json
import time
def on_c(a):
	pass
def on_d(a):
	pass
def on_ping(msg,id):
	global man
	print("PING")
	msg = ConnectionManager.Message("PONG",str(id))
	man.send_to_all_clients(msg)
man = ConnectionManager.Server('',50000,on_c,on_d)
man.set_type_callback("PING",on_ping)
man.start()
while man.run:
	pass

