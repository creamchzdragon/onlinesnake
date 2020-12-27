import sys
import random
import pygame
import ConnectionManager
import json
import logging
import time
SCREEN_HEIGHT = 480
SCREEN_WIDTH = 480
GRID_SQUARE_PIXELS = 20
GRID_HEIGHT = int(SCREEN_HEIGHT / GRID_SQUARE_PIXELS)
GRID_WIDTH = int(SCREEN_WIDTH / GRID_SQUARE_PIXELS)
SCREEN_DIM = pygame.math.Vector2(SCREEN_WIDTH,SCREEN_HEIGHT)
GRID_DIM = pygame.math.Vector2(GRID_HEIGHT,GRID_WIDTH)
ASSETS_DIRECTORY = "./assets/"
player_colors = ["red","blue","yellow"]
base_starting_point = pygame.math.Vector2(GRID_WIDTH / 4, GRID_HEIGHT / 4)
width_mult = pygame.math.Vector2(12, 0)
hieght_mult = pygame.math.Vector2(0, 12)
starting_points = [base_starting_point , base_starting_point + width_mult , base_starting_point + hieght_mult , base_starting_point + width_mult + hieght_mult]
used_player_colors = []
starting_dirs = ["up","down","left","right"]
def on_server_connection(id):
	pass
def on_server_disconnect(id):
	pass
def on_client_connect():
	pass
def on_client_disconnect():
	pass
server = ConnectionManager.Server('',50000,on_server_connection,on_server_disconnect)
client = ConnectionManager.Client('localhost',50000,on_client_connect,on_client_disconnect)
server.raise_exceptions = True
client.raise_exceptions = True
#can use pygame.math.Vector2
up = pygame.math.Vector2(0,-1)
down = pygame.math.Vector2(0,1)
left = pygame.math.Vector2(-1,0)
right = pygame.math.Vector2(1,0)
players = []
client_id = -1
food = [GRID_HEIGHT / 2, GRID_WIDTH / 2]
tiles = {
	"grid": "grid.png",
	"snake": {
		"green":{
			"head": {
				"one_block": {
					"up": "green_snake_1block_head_up.png",
					"down": "green_snake_1block_head_down.png",
					"left": "green_snake_1block_head_left.png",
					"right": "green_snake_1block_head_right.png"
				},
				"up": "green_snake_head_up.png",
				"down": "green_snake_head_down.png",
				"left": "green_snake_head_left.png",
				"right": "green_snake_head_right.png"
			},
			"body": {
				"vertical": "green_snake_vertical.png",
				"horizontal": "green_snake_horizontal.png",
				"up_to_right": "green_snake_up_to_right.png",
				"up_to_left": "green_snake_up_to_left.png",
				"down_to_right": "green_snake_down_to_right.png",
				"down_to_left": "green_snake_down_to_left.png"
			},
			"tail": {
				"up": "green_snake_tail_up.png",
				"down": "green_snake_tail_down.png",
				"left": "green_snake_tail_left.png",
				"right": "green_snake_tail_right.png"
			}
		},
		"red":{
			"head": {
				"one_block": {
					"up": "red_snake_1block_head_up.png",
					"down": "red_snake_1block_head_down.png",
					"left": "red_snake_1block_head_left.png",
					"right": "red_snake_1block_head_right.png"
				},
				"up": "red_snake_head_up.png",
				"down": "red_snake_head_down.png",
				"left": "red_snake_head_left.png",
				"right": "red_snake_head_right.png"
			},
			"body": {
				"vertical": "red_snake_vertical.png",
				"horizontal": "red_snake_horizontal.png",
				"up_to_right": "red_snake_up_to_right.png",
				"up_to_left": "red_snake_up_to_left.png",
				"down_to_right": "red_snake_down_to_right.png",
				"down_to_left": "red_snake_down_to_left.png"
			},
			"tail": {
				"up": "red_snake_tail_up.png",
				"down": "red_snake_tail_down.png",
				"left": "red_snake_tail_left.png",
				"right": "red_snake_tail_right.png"
			}
		},
		"yellow":{
			"head": {
				"one_block": {
					"up": "yellow_snake_1block_head_up.png",
					"down": "yellow_snake_1block_head_down.png",
					"left": "yellow_snake_1block_head_left.png",
					"right": "yellow_snake_1block_head_right.png"
				},
				"up": "yellow_snake_head_up.png",
				"down": "yellow_snake_head_down.png",
				"left": "yellow_snake_head_left.png",
				"right": "yellow_snake_head_right.png"
			},
			"body": {
				"vertical": "yellow_snake_vertical.png",
				"horizontal": "yellow_snake_horizontal.png",
				"up_to_right": "yellow_snake_up_to_right.png",
				"up_to_left": "yellow_snake_up_to_left.png",
				"down_to_right": "yellow_snake_down_to_right.png",
				"down_to_left": "yellow_snake_down_to_left.png"
			},
			"tail": {
				"up": "yellow_snake_tail_up.png",
				"down": "yellow_snake_tail_down.png",
				"left": "yellow_snake_tail_left.png",
				"right": "yellow_snake_tail_right.png"
			}
		},
		"blue":{
			"head": {
				"one_block": {
					"up": "blue_snake_1block_head_up.png",
					"down": "blue_snake_1block_head_down.png",
					"left": "blue_snake_1block_head_left.png",
					"right": "blue_snake_1block_head_right.png"
				},
				"up": "blue_snake_head_up.png",
				"down": "blue_snake_head_down.png",
				"left": "blue_snake_head_left.png",
				"right": "blue_snake_head_right.png"
			},
			"body": {
				"vertical": "blue_snake_vertical.png",
				"horizontal": "blue_snake_horizontal.png",
				"up_to_right": "blue_snake_up_to_right.png",
				"up_to_left": "blue_snake_up_to_left.png",
				"down_to_right": "blue_snake_down_to_right.png",
				"down_to_left": "blue_snake_down_to_left.png"
			},
			"tail": {
				"up": "blue_snake_tail_up.png",
				"down": "blue_snake_tail_down.png",
				"left": "blue_snake_tail_left.png",
				"right": "blue_snake_tail_right.png"
			}
		}
	},
	"food": "food.png"	
}

def get_player_color():
	global player_colors
	global used_player_colors
	for color in player_colors:
		if color not in used_player_colors:
			used_player_colors.append(color)
			return color
def remove_used_color(color):
	global used_player_colors
	used_player_colors.remove(color)
def grid_to_pixels(vect2):
	return vect2 * GRID_SQUARE_PIXELS
def load_assets(tiles):
	for key in tiles:
		if type(tiles[key]) is dict:
			tiles[key] = load_assets(tiles[key])
		else:
			tiles[key] = pygame.image.load(ASSETS_DIRECTORY + tiles[key])
	return tiles
class Snake:
	def __init__(self,g_width,g_height,tiles,color = "green"):
		self.squares = [pygame.math.Vector2(GRID_WIDTH / 2 ,GRID_HEIGHT / 2)]
		self.direction = random.choice([up,down,left,right])
		self.g_width = g_width
		self.g_height = g_height
		self.tiles = tiles
		self.color = color
	def can_move(self):
		if((self.squares[0] + self.direction).x < 0):
			return False
		if((self.squares[0] + self.direction).y < 0):
			return False
		if((self.squares[0] + self.direction).x >= self.g_width):
			return False
		if((self.squares[0] + self.direction).y >= self.g_height):
			return False
		for i in range(1,len(self.squares)):
			if((self.squares[0] + self.direction) == self.squares[i]):
				return False
		return True
	def can_online_move(self,snakes):
		start = self.can_move()
		if not start:
			return start
		for i in range(1,len(snakes)):
			for sq in snakes[i].squares:
				if((self.squares[0] + self.direction) == sq or self.squares[0] == sq):
					return False
		for sq1 in self.squares:
			for i in range(1,len(snakes)):
				for sq2 in snakes[i].squares:
					if sq1 == sq2:
						return False
		return True

	def draw_snake(self,surface):
		#draw head first
		if(len(self.squares) == 1):
			if(self.direction == up):
				surface.blit(self.tiles["snake"][self.color]["head"]["one_block"]["up"] , grid_to_pixels(self.squares[0]))
			elif(self.direction == down):
				surface.blit(self.tiles["snake"][self.color]["head"]["one_block"]["down"] , grid_to_pixels(self.squares[0]))
			elif(self.direction == left):
				surface.blit(self.tiles["snake"][self.color]["head"]["one_block"]["left"] , grid_to_pixels(self.squares[0]))
			elif(self.direction == right):
				surface.blit(self.tiles["snake"][self.color]["head"]["one_block"]["right"] , grid_to_pixels(self.squares[0]))
		else:
			if(self.squares[1] == self.squares[0] + down):
				surface.blit(self.tiles["snake"][self.color]["head"]["up"] , grid_to_pixels(self.squares[0]))
			elif(self.squares[1] == self.squares[0] + up):
				surface.blit(self.tiles["snake"][self.color]["head"]["down"] , grid_to_pixels(self.squares[0]))
			elif(self.squares[1] == self.squares[0] + right):
				surface.blit(self.tiles["snake"][self.color]["head"]["left"] , grid_to_pixels(self.squares[0]))
			elif(self.squares[1] == self.squares[0] + left):
				surface.blit(self.tiles["snake"][self.color]["head"]["right"] , grid_to_pixels(self.squares[0]))
			#iterate through body
			for i in range(1,len(self.squares) - 1):
				#horizontal
				if((self.squares[i - 1] == self.squares[i] + left and self.squares[i + 1] == self.squares[i] + right) or 
					(self.squares[i - 1] == self.squares[i] + right and self.squares[i + 1] == self.squares[i] + left)):
					surface.blit(self.tiles["snake"][self.color]["body"]["horizontal"] , grid_to_pixels(self.squares[i]))
				#vertical
				elif((self.squares[i - 1] == self.squares[i] + up and self.squares[i + 1] == self.squares[i] + down) or 
					(self.squares[i - 1] == self.squares[i] + down and self.squares[i + 1] == self.squares[i] + up)):
					surface.blit(self.tiles["snake"][self.color]["body"]["vertical"] , grid_to_pixels(self.squares[i]))
				#top_right
				elif((self.squares[i - 1] == self.squares[i] + up and self.squares[i + 1] == self.squares[i] + right) or 
					(self.squares[i - 1] == self.squares[i] + right and self.squares[i + 1] == self.squares[i] + up)):
					surface.blit(self.tiles["snake"][self.color]["body"]["up_to_right"] , grid_to_pixels(self.squares[i]))
				#top_left
				elif((self.squares[i - 1] == self.squares[i] + up and self.squares[i + 1] == self.squares[i] + left) or 
					(self.squares[i - 1] == self.squares[i] + left and self.squares[i + 1] == self.squares[i] + up)):
					surface.blit(self.tiles["snake"][self.color]["body"]["up_to_left"] , grid_to_pixels(self.squares[i]))
				#down_right
				elif((self.squares[i - 1] == self.squares[i] + down and self.squares[i + 1] == self.squares[i] + right) or 
					(self.squares[i - 1] == self.squares[i] + right and self.squares[i + 1] == self.squares[i] + down)):
					surface.blit(self.tiles["snake"][self.color]["body"]["down_to_right"] , grid_to_pixels(self.squares[i]))
				#down_left
				elif((self.squares[i - 1] == self.squares[i] + down and self.squares[i + 1] == self.squares[i] + left) or 
					(self.squares[i - 1] == self.squares[i] + left and self.squares[i + 1] == self.squares[i] + down)):
					surface.blit(self.tiles["snake"][self.color]["body"]["down_to_left"] , grid_to_pixels(self.squares[i]))
			#tail
			if(self.squares[-2] == self.squares[-1] + up):
				surface.blit(self.tiles["snake"][self.color]["tail"]["up"] , grid_to_pixels(self.squares[-1]))
			elif(self.squares[-2] == self.squares[-1] + down):
				surface.blit(self.tiles["snake"][self.color]["tail"]["down"] , grid_to_pixels(self.squares[-1]))
			elif(self.squares[-2] == self.squares[-1] + left):
				surface.blit(self.tiles["snake"][self.color]["tail"]["left"] , grid_to_pixels(self.squares[-1]))
			elif(self.squares[-2] == self.squares[-1] + right):
				surface.blit(self.tiles["snake"][self.color]["tail"]["right"] , grid_to_pixels(self.squares[-1]))
	def turn(self,direction):
		if(len(self.squares) == 1):
			self.direction = direction
			return True
		if((self.squares[0] + direction) != self.squares[1]):
			self.direction = direction
			return True
		return False
	def move(self):
		self.squares.insert(0,self.squares[0] + self.direction)
		self.squares.pop()
	def handle_keys(self,speedup):
	    for event in pygame.event.get():
	        if event.type == pygame.QUIT:
	            pygame.quit()
	            sys.exit()
	        elif event.type == pygame.KEYUP:
	        	if event.key == pygame.K_SPACE:
	        		speedup = False
	        elif event.type == pygame.KEYDOWN:
	            if event.key == pygame.K_UP:
	                self.turn(up)
	            elif event.key == pygame.K_DOWN:
	                self.turn(down)
	            elif event.key == pygame.K_LEFT:
	                self.turn(left)
	            elif event.key == pygame.K_RIGHT:
	                self.turn(right)
	            elif event.key == pygame.K_SPACE:
	            	speedup = True
	            elif event.key == pygame.K_ESCAPE:
	            	speedup = -1
	    return speedup
	def grow(self):
		self.squares.insert(0,self.squares[0] + self.direction)
	#list of lists to list of vec2
	def set_pos_from_array(self,pos):
		self.squares = []
		for p in pos:
			self.squares.append(pygame.math.Vector2(p[0],p[1]))
	#string dir to vec2 dir
	def set_dir_from_string(self,dir):
		if dir == "up":
			self.direction = up
		elif dir == "down":
			self.direction = down
		elif dir == "left":
			self.direction = left
		elif dir == "right":
			self.direction = right
	def get_pos_as_array(self):
		out = []
		for p in self.squares:
			out.append([p.x,p.y])
		return out
	def get_dir_as_string(self):
		if self.direction == up:
			return "up"
		elif self.direction == down:
			return "down"
		elif self.direction == left:
			return "left"
		elif self.direction == right:
			return "right"
class Food:
	def __init__(self,g_height,g_width,tiles):
		self.pos = pygame.math.Vector2(-1,-1)
		self.tiles = tiles
		self.g_height = g_height
		self.g_width = g_width
	def place(self,snake):
		rand_pos_num = random.randint(0, (self.g_height * self.g_width) - len(snake.squares))
		count = 0
		for y in range(self.g_height):
			for x in range(self.g_width):
				if((x,y) not in snake.squares):
					if(count == rand_pos_num):
						self.pos = pygame.math.Vector2(x,y)
						return
					else:
						count += 1
	def draw(self,surface):
		surface.blit(tiles["food"],grid_to_pixels(self.pos))
class OnlineFood(Food):
	def place(self,snakes):
		sum_of_squares = 0
		for s in snakes:
			sum_of_squares += len(s.squares)
		rand_pos_num = random.randint(0, (self.g_height * self.g_width) - sum_of_squares)
		count = 0
		squares = []
		for s in snakes:
			for q in s.squares:
				squares.append(q)
		for y in range(self.g_height):
			for x in range(self.g_width):
				if((x,y) not in squares):
					if(count == rand_pos_num):
						self.pos = pygame.math.Vector2(x,y)
						return
					else:
						count += 1
	def get_pos_as_array(self):
		return [self.pos.x,self.pos.y]
	def set_pos_from_array(self,arr):
		self.pos = pygame.math.Vector2(arr[0],arr[1])
def draw_grid(surface):
	global tiles
	for y in range(GRID_HEIGHT):
		for x in range(GRID_WIDTH):
			surface.blit(tiles["grid"], (x * GRID_SQUARE_PIXELS, y * GRID_SQUARE_PIXELS))
def snake_eat_food(snake,food):
	if(snake.squares[0] + snake.direction == food.pos):
		return True
	return False
def render_menu_options(surface,menu_options,selected_option):
	options_font = pygame.font.SysFont("monospace",32)
	starting_x = 72 + 20
	x_inc = 32
	for i in range(len(menu_options)):
		opt_text = ""
		if i == selected_option:
			opt_text = options_font.render(menu_options[i],1,(255,255,255))
		else:
			opt_text = options_font.render(menu_options[i],1,(155,155,155))
		opt_text_rect = opt_text.get_rect(midtop = (SCREEN_WIDTH / 2 , starting_x))
		surface.blit(opt_text,opt_text_rect)
		starting_x += x_inc
def main_menu_scene_loop(screen,clock):
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",72)
	snake_text = snake_font.render("SNAKE",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	menu_options = ["Play","Connect","Quit"]
	selected_menu_option = 0
	start_game = False
	goto_lobby = False
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected_menu_option -= 1
					if selected_menu_option < 0:
						selected_menu_option = len(menu_options) - 1
				elif event.key == pygame.K_DOWN:
					selected_menu_option = (selected_menu_option + 1) % len(menu_options)
				elif event.key == pygame.K_RETURN:
					if menu_options[selected_menu_option] == "Play":
						start_game = True
					elif menu_options[selected_menu_option] == "Quit":
						pygame.quit()
						sys.exit()
					elif menu_options[selected_menu_option] == "Connect":
						goto_lobby = True
		if start_game or goto_lobby:
			break
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		render_menu_options(surface,menu_options,selected_menu_option)
		screen.blit(surface,(0,0))
		pygame.display.update()
	if start_game:
		game_scene_loop(screen,clock)
	if goto_lobby:
		connect_menu_loop(screen,clock)
def connect_menu_loop(screen,clock):
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",72)
	snake_text = snake_font.render("Connect",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	menu_options = ["Start Lobby","Join Lobby","Back"]
	selected_menu_option = 0
	start_lobby = False
	join_lobby = False
	back = False
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected_menu_option -= 1
					if selected_menu_option < 0:
						selected_menu_option = len(menu_options) - 1
				elif event.key == pygame.K_DOWN:
					selected_menu_option = (selected_menu_option + 1) % len(menu_options)
				elif event.key == pygame.K_RETURN:
					if menu_options[selected_menu_option] == "Start Lobby":
						start_lobby = True
					elif menu_options[selected_menu_option] == "Join Lobby":
						join_lobby = True
					elif menu_options[selected_menu_option] == "Back":
						back = True
		if start_lobby or join_lobby or back:
			break
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		render_menu_options(surface,menu_options,selected_menu_option)
		screen.blit(surface,(0,0))
		pygame.display.update()
	if start_lobby:
		enter_name(screen,clock,lobby_loop)
	if join_lobby:
		enter_name(screen,clock,enter_ip)
	if back:
		main_menu_scene_loop(screen,clock)
def game_scene_loop(screen,clock):
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake = Snake(GRID_WIDTH,GRID_HEIGHT,tiles)
	food = Food(GRID_WIDTH,GRID_HEIGHT,tiles)
	food.place(snake)
	draw_grid(screen)
	snake.draw_snake(screen)
	food.draw(screen)
	tick = 0
	myfont = pygame.font.SysFont("monospace",72)
	score_font = pygame.font.SysFont("monospace",32)
	game_over = False
	score = 0
	speedup = False
	while(True):
		clock.tick(60)
		speedup = snake.handle_keys(speedup)
		draw_grid(surface)
		snake.draw_snake(surface)
		food.draw(surface)
		screen.blit(surface,(0,0))
		rendered_score = score_font.render("Score: {0}".format(score),1,(255,255,255))
		screen.blit(rendered_score,(0,0))
		frames_per_move = 60
		if(speedup == True):
			speedup_text = score_font.render("Speedup Active",1,(255,255,255))
			speedup_text_rect = speedup_text.get_rect(topright = (SCREEN_WIDTH,0))
			screen.blit(speedup_text,speedup_text_rect)
			frames_per_move = 15
		elif(speedup == -1):
			break
		if(game_over):
			game = myfont.render("Game",1,(255,255,255))
			over = myfont.render("Over",1,(255,255,255))
			game_rect = game.get_rect(center = (SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2 - 36))
			over_rect = over.get_rect(center = (SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2 + 36))
			screen.blit(game,game_rect)
			screen.blit(over,over_rect)
		elif(tick % frames_per_move == 0):
			if(snake_eat_food(snake,food)):
				snake.grow()
				food.place(snake)
				score += 1
			elif(snake.can_move()):
				snake.move()
			else:
				game_over = True
				#game over
				pass
		tick += 1
		pygame.display.update()
	main_menu_scene_loop(screen,clock)
def accept_connection(msg,id):
	global players
	global server
	players.append({"name":msg.body,"conn_id":id,"color":get_player_color(),"ping":999})
	res_msg = ConnectionManager.Message("IDEN",str(id))
	server.send_to_client(res_msg,id)

def render_players_in_lobby(players,surface,y_offset):
	text_font = pygame.font.SysFont("monospace",36)
	cnt = 0
	for player in players:
		player_name_text = text_font.render(player["name"],1,pygame.color.Color(player["color"]))
		player_name_text_rect = player_name_text.get_rect(topleft = (0,cnt * 36 + y_offset))
		player_ping_text = text_font.render(" " + str(player["ping"]) + "ms",1,(255,255,255))
		player_ping_text_rect = player_ping_text.get_rect(topleft = (player_name_text_rect.w,cnt * 36 + y_offset))
		surface.blit(player_name_text,player_name_text_rect)
		surface.blit(player_ping_text,player_ping_text_rect)
		cnt += 1
def check_on_players():
	global players
	global server
	remove = []
	for player in players:
		if player["conn_id"] == -1:
			continue
		connection = server.get_connection(player["conn_id"])
		if not connection["active"]:
			remove.append(player)
	for r in remove:
		remove_used_color(r["color"])
		players.remove(r)
def send_update():
	global players
	global server
	players_string = json.dumps(players)
	msg = ConnectionManager.Message("UPDT",players_string)
	server.send_to_all_clients(msg)
	for player in players:
		player["last_ping"] = int(round(time.time() * 1000))
	server.send_to_all_clients(ConnectionManager.Message("PING",""))
def start_game():
	global players
	global server
	for i in range(len(players)):
		players[i]["pos"] = [[starting_points[i].x,starting_points[i].y]]
		players[i]["dir"] = random.choice(starting_dirs)
		players[i]["alive"] = True
	msg = {"players":players,"food": [GRID_WIDTH / 2,GRID_HEIGHT / 2]}
	msg = json.dumps(msg)
	msg = ConnectionManager.Message("STRT",msg)
	server.send_to_all_clients(msg)
def on_ping(msg):
	global client
	client.send_to_server(ConnectionManager.Message("PONG",""))
def on_pong(msg,id):
	global server
	global players
	for player in players:
		if player["conn_id"] == id:
			player["ping"] = int(round(time.time() * 1000)) - player["last_ping"]
			break
def lobby_loop(screen,clock,name):
	global players
	global server
	global used_player_colors
	used_player_colors = []
	players = []
	player = {"name":name,"conn_id":-1,"color":"green","ping":0}#me!
	players.append(player)
	server.set_type_callback("JOIN",accept_connection)
	server.set_type_callback("UPDT",game_server_callback)
	server.set_type_callback("PONG",on_pong)
	server.start()
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",72)
	snake_text = snake_font.render("Lobby",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	menu_options = ["Start","Leave"]
	selected_menu_option = 0
	start = False
	leave = False
	tick = 0
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				server.disconnect()
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected_menu_option -= 1
					if selected_menu_option < 0:
						selected_menu_option = len(menu_options) - 1
				elif event.key == pygame.K_DOWN:
					selected_menu_option = (selected_menu_option + 1) % len(menu_options)
				elif event.key == pygame.K_RETURN:
					if menu_options[selected_menu_option] == "Start":
						start = True
					elif menu_options[selected_menu_option] == "Leave":
						server.disconnect()
						leave = True
		if start or leave:
			break
		if tick % 30 ==0:
			send_update()
		check_on_players()
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		render_menu_options(surface,menu_options,selected_menu_option)
		render_players_in_lobby(players,surface,288)
		screen.blit(surface,(0,0))
		pygame.display.update()
		tick = (tick + 1) % 1000000
	if start:
		start_game()
		online_game_loop(screen,clock,True)
	if leave:
		main_menu_scene_loop(screen,clock)
def enter_name(screen,clock,after_loop):
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",36)
	snake_text = snake_font.render("Enter Your Name:",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	next_loop = False
	name = ""
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key >= pygame.K_a and event.key <= pygame.K_z:
					if len(name) < 13:
						name += pygame.key.name(event.key)
				elif event.key == pygame.K_BACKSPACE:
					if len(name) > 0:
						name = name[:-1]
				elif event.key == pygame.K_RETURN:
					if len(name) != 0:
						next_loop = True
		if next_loop:
			break
		name_font = pygame.font.SysFont("monospace",36)
		name_text = name_font.render(name,1,(255,255,255))
		name_text_rect = name_text.get_rect(midtop = (SCREEN_WIDTH / 2, 92))
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		surface.blit(name_text,name_text_rect)
		screen.blit(surface,(0,0))
		pygame.display.update()
	if next_loop:
		after_loop(screen,clock,name)
def enter_ip(screen,clock,in_name):
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",36)
	snake_text = snake_font.render("Enter the host:",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	next_loop = False
	name = ""
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if ((event.key >= pygame.K_a and event.key <= pygame.K_z) or
						(event.key >= pygame.K_0 and event.key <= pygame.K_9) or 
							(event.key == pygame.K_PERIOD)):
					if len(name) < 13:
						name += pygame.key.name(event.key)
				elif event.key == pygame.K_BACKSPACE:
					if len(name) > 0:
						name = name[:-1]
				elif event.key == pygame.K_RETURN:
					if len(name) != 0:
						next_loop = True
		if next_loop:
			break
		name_font = pygame.font.SysFont("monospace",36)
		name_text = name_font.render(name,1,(255,255,255))
		name_text_rect = name_text.get_rect(midtop = (SCREEN_WIDTH / 2, 92))
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		surface.blit(name_text,name_text_rect)
		screen.blit(surface,(0,0))
		pygame.display.update()
	if next_loop:
		join_lobby_loop(screen,clock,in_name,name)
def on_id_msg(msg):
	global client_id
	client_id = int(msg.body)
def on_update_msg(msg):
	global players
	global start_game
	global food
	msg = msg.body
	msg = json.loads(msg)
	if start_game:
		players = msg["players"]
		food = msg["food"]
	else:
		players = msg
def on_start_msg(msg):
	global players
	global start_game
	msg = json.loads(msg.body)
	players = msg["players"]
	start_game = True
def game_server_callback(msg,id):
	global server
	global players
	global food
	msg = msg.body
	msg = json.loads(msg)
	for player in players:
		if player["conn_id"] == id:
			player["pos"] = msg["pos"]
			player["dir"] = msg["dir"]
			player["alive"] = msg["alive"]
			break
	rsp = {"players":players,"food":food}
	rsp = json.dumps(rsp)
	rsp = ConnectionManager.Message("UPDT",rsp)
	server.send_to_all_clients(rsp)
#update for server/client
def online_game_loop(screen,clock,is_server):
	global players
	global server
	global client
	global food
	global client_id
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snakes = []
	for player in players:
		if player["conn_id"] == client_id:
			snakes.insert(0,Snake(GRID_WIDTH,GRID_HEIGHT,tiles,player["color"]))
			snakes[0].set_pos_from_array(player["pos"])
		else:
			snakes.append(Snake(GRID_WIDTH,GRID_HEIGHT,tiles,player["color"]))
			snakes[-1].set_pos_from_array(player["pos"])
	local_food = OnlineFood(GRID_WIDTH,GRID_HEIGHT,tiles)
	local_food.set_pos_from_array(food)
	draw_grid(screen)
	for snake in snakes:
		snake.draw_snake(screen)
	local_food.draw(screen)
	tick = 0
	myfont = pygame.font.SysFont("monospace",72)
	score_font = pygame.font.SysFont("monospace",32)
	game_over = False
	score = 0
	speedup = False
	while(True):
		clock.tick(60)
		speedup = snakes[0].handle_keys(speedup)
		draw_grid(surface)
		local_food.set_pos_from_array(food)
		local_food.draw(surface)
		#load snakes from players
		idx = 1
		for player in players:
			if player["conn_id"] != client_id:
				snakes[idx].set_pos_from_array(player["pos"])
				snakes[idx].set_dir_from_string(player["dir"])
				idx += 1 
		for snake in snakes:
			snake.draw_snake(surface)
		screen.blit(surface,(0,0))
		rendered_score = score_font.render("Score: {0}".format(score),1,(255,255,255))
		screen.blit(rendered_score,(0,0))
		frames_per_move = 60
		if(speedup == True):
			speedup_text = score_font.render("Speedup Active",1,(255,255,255))
			speedup_text_rect = speedup_text.get_rect(topright = (SCREEN_WIDTH,0))
			screen.blit(speedup_text,speedup_text_rect)
			frames_per_move = 30
		elif(speedup == -1):
			break
		if(is_server):
			#check for food eaten and set its pos if not
			for snake in snakes:
				for pos in snake.squares:
					if pos == local_food.pos:
						local_food.place(snakes)
						food = local_food.get_pos_as_array()
						msg = {"players":players,"food":food}
						msg = json.dumps(msg)
						msg = ConnectionManager.Message("UPDT",msg)
						server.send_to_all_clients(msg)
		if(game_over):
			game = myfont.render("Game",1,(255,255,255))
			over = myfont.render("Over",1,(255,255,255))
			game_rect = game.get_rect(center = (SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2 - 36))
			over_rect = over.get_rect(center = (SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2 + 36))
			screen.blit(game,game_rect)
			screen.blit(over,over_rect)
		elif(tick % frames_per_move == 0):
			if(snake_eat_food(snakes[0],local_food)):
				snakes[0].grow()
				score += 1
			elif(snakes[0].can_online_move(snakes)):
				snakes[0].move()
			else:
				game_over = True
				players[0]["alive"] = False
			if is_server:
				players[0]["pos"] = snakes[0].get_pos_as_array()
				players[0]["dir"] = snakes[0].get_dir_as_string()
				msg = {"players":players,"food":food}
				msg = json.dumps(msg)
				msg = ConnectionManager.Message("UPDT",msg)
				server.send_to_all_clients(msg)
			else:
				msg = {"pos":snakes[0].get_pos_as_array(),"dir":snakes[0].get_dir_as_string(),"alive":(not game_over)}
				msg = json.dumps(msg)
				msg = ConnectionManager.Message("UPDT",msg)
				client.send_to_server(msg)
		tick += 1
		pygame.display.update()
	if is_server:
		server.disconnect()
		server.join_all_threads()
	else:
		client.disconnect()
		client.join_all_threads()
	main_menu_scene_loop(screen,clock)
def join_lobby_loop(screen,clock,name,ip):
	global client
	global players
	global start_game
	client.set_type_callback("IDEN",on_id_msg)
	client.set_type_callback("UPDT",on_update_msg)
	client.set_type_callback("STRT",on_start_msg)
	client.set_type_callback("PING",on_ping)
	try:
		client.disconnect()
		client.connect()
		msg = ConnectionManager.Message("JOIN",name)
		client.send_to_server(msg)
	except:
		main_menu_scene_loop(screen,clock)
	players = []
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	snake_font = pygame.font.SysFont("monospace",72)
	snake_text = snake_font.render("Lobby",1,(255,255,255))
	snake_text_rect = snake_text.get_rect(midtop = (SCREEN_WIDTH / 2, 20))
	menu_options = ["Leave"]
	selected_menu_option = 0
	start_game = False
	leave = False
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				client.disconnect()
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					if menu_options[selected_menu_option] == "Leave":
						client.disconnect()
						leave = True
		if leave or start_game:
			break
		if client.active() == False:
			leave = True
		surface.fill((0,0,0))
		surface.blit(snake_text,snake_text_rect)
		render_menu_options(surface,menu_options,selected_menu_option)
		render_players_in_lobby(players,surface,288)
		screen.blit(surface,(0,0))
		pygame.display.update()
	if leave:
		main_menu_scene_loop(screen,clock)
	if start_game:
		online_game_loop(screen,clock,False)
def main():
	global tiles
	pygame.init()
	clock = pygame.time.Clock()
	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	tiles = load_assets(tiles)
	main_menu_scene_loop(screen,clock)
main()
