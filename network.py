# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import socket
import select
import pickle
################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        #initialize the socket connection
        self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        print ("Socket created")
        self.s.setblocking(False)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('',port))
        print ("Socket binded")
        self.s.listen(5)
        #Empty client list
        self.client = []
        
    def send_map(self, map_file, player):
        if len(sys.argv) == 2:
            map_file = DEFAULT_MAP
            player.sendall(b"maps/map0")
            ack = player.recv(1024)          #ack confirmation
        if len(sys.argv) == 3:
            map_file = sys.argv[2]
            if map_file == "maps/map0":
                player.sendall(b"maps/map0")
                ack = player.recv(1024)          #ack confirmation
            else:
                player.sendall(b"maps/map1")
                ack = player.recv(1024)          #ack confirmation
        else:
            print("Usage: {} port [map_file]".format(sys.argv[0]))
            sys.exit()
        return map_file

    def send_fruits(self, model, player):
        self.model = model 
        send_fruits = pickle.dumps(model.fruits)
        player.sendall(send_fruits)
        ack = player.recv(1024)
            
    def send_characters(self, model, player):
        self.model = model
        send_character = pickle.dumps(model.characters)
        player.sendall(send_character)
        ack = player.recv(1024)

    # time event        
    def tick(self, dt):
        (ready_to_read,_,_) = select.select(self.client+[self.s], [], [])
        for sock in ready_to_read:
            if sock == self.s and ready_to_read:
                player, addr = self.s.accept()
                print("{} connected".format(addr))
                map_file = "" # this variable will contain the chosen map by client
                map_file = self.send_map(map_file, player)   #this function load the map and send it to the client
                print("Loaded map by the server {}".format(map_file))
                my_fruits = self.send_fruits(self.model, player)
                print("Fucking fruits sent".format(my_fruits))
                my_characters = self.send_characters(self.model, player)
                print("Fucking characters sent!".format(my_characters))
                

        return True

################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        #connecting to the game server
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        self.sock.connect((host, port))
        print("Connected to the game server")
        print("Host: {} Port: {}".format(self.host, self.port))

        #receiving the map
        the_map = self.sock.recv(4096)  #receiving the correct map
        print("received map by client {}".format(the_map.decode()))
        self.sock.send(b"ACK")          #ack confrimation 
        model.load_map(the_map)         #Load the map 

        #receiving fruits
        fruits = self.sock.recv(4096)
        map_fruits = pickle.loads(fruits)
        self.sock.send(b"ACK")          #ack to confirm receiving fruits
        self.model.fruits = map_fruits
        print("well received")

        #receiving characters
        characters = self.sock.recv(4096)
        map_characters = pickle.loads(fruits)
        self.sock.send(b"ACK")
        self.model.characters = map_characters
        print("fucking characters well received!")
        

        
    
    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction): #Floki:I completed this function from bomber.py
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        if not self.model.player: return True
        nickname = self.model.player.nickname
        if direction in DIRECTIONS:
            self.model.move_character(nickname, direction)
        # ...
        return True

    def keyboard_drop_bomb(self):               #Floki:I completed this function from bomber.py
        print("=> event \"keyboard drop bomb\"")
        if not self.model.player: return True
        nickname = self.model.player.nickname
        self.model.drop_bomb(nickname)
        # ...
        return True


    
    # time event

    def tick(self, dt):
        return True
