import ConnectionManager
import time
import json
man = ConnectionManager.ConnectionManager()
def on_msg(data):
	print(data)
man.connect_to_server('localhost',50000,on_msg)
man.send_to_server(b'JOIN:steve')
