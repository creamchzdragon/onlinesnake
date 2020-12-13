import ConnectionManager
import json
import time
players = []
def init_callback(data,id):
	print("data recieved")
	data = data.decode('utf-8')
	print(data)
	data = json.loads(data)
	data["id"] = id
	print(data)
	players.append(data)
def gather_data(data,id):
	for i in range(len(players)):
		if players[i]["id"] == id:
			players[i]["Pos"] = json.loads(data.decode('utf-8'))["Pos"]
			print(players)
man = ConnectionManager.ConnectionManager()
man.start_server('',50000,init_callback,4)
time.sleep(30)
for i in range(len(players)):
	man.send_to_client(b'START',players[i]["id"])
man.change_server_callback(gather_data)
