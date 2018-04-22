# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import socket
import select
import pickle

#the following importations are for testing
from view import *
from keyboard import *
from network import *
import sys
import pygame

#number of fruits
nb_fruits = 10
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
    
    def initialise_map_with_fruits(self, model):
        for _ in range(nb_fruits): model.add_fruit()
    '''
    def send_fruits(self, player):
        for i in range(nb_fruits):
            ### we dont send fruit.map for the moment because it's not important
            print("fruit pos to send {}".format( self.model.fruits[i].pos ))
            print("fruit pos x {}".format( self.model.fruits[i].pos[X] ))
            print("fruit pos y {}".format( self.model.fruits[i].pos[Y] ))
            player.sendall( self.model.fruits[i].pos[X] )
            ack = player.recv(1024) 
            playes.sendall( b"self.model.fruits[i].kind" )
            ack = player.recv(1024)
    '''
    def send_fruits(self):
        pickle_out = open("dict.pickle1","wb")
        pickle.dump(self.model.fruits, pickle_out)
        pickle_out.close()

    def send_character(self):
        pickle_out = open("dict.pickle2","wb")
        pickle.dump(self.model.characters, pickle_out)
        pickle_out.close()
        
    # time event        
    def tick(self, dt):
        (ready_to_read,_,_) = select.select(self.client+[self.s], [], [])
        for sock in ready_to_read:
            if sock == self.s and ready_to_read:
                player, addr = self.s.accept()
                print("{} connected".format(addr))
                # parse arguments
                # the following part is for sending the map (i.e name of map)
                map_file = "" # this variable will contain the chosen map by client
                map_file = self.send_map(map_file, player)
                print("Loaded map by the server {}".format(map_file))
                self.model.load_map(map_file)
                # the following part is for putin fruits randomly on the map
                self.initialise_map_with_fruits(self.model)
                view = GraphicView(self.model, "network map")
                view.tick(dt)
                #the following part is for sending fruits
                self.send_fruits()
                #the following part is for adding a character
                print("before adding character")
                self.model.add_character("me", isplayer = True)
                print("after adding character")
                clock = pygame.time.Clock()
                dt = clock.tick(0)
                view.tick(dt)
                print("viewing after adding character")
                #the following part is for sending the character
                self.send_character()
##                data = player.recv(4096)
##                print("Data received from player!")
##                data.decode("utf-8")
##                print("Data decoded!!")
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
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        self.sock.connect((host, port))
        print("Connected to the game server")
        print("Host: {} Port: {}".format(self.host, self.port))
        the_map = self.sock.recv(4096) #receiving the correct map
        print("received map by client {}".format(the_map.decode()))
        self.sock.send(b"ACK")          #ack confrimation for fruits
        model.load_map(the_map)         #Load map
        
        # ...
        
    

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
    
    #useful fonctions

    def receive_fruits(self):
        pickle_in = open("dict.pickle1","rb")
        self.model.fruits = pickle.load(pickle_in)

    def receive_character(self):
        pickle_in = open("dict.pickle2","rb")
        self.model.characters = pickle.load(pickle_in)

    # time event

    def tick(self, dt):
        #the following part is for receiving fruits
        self.receive_fruits()
        #the following part is for receiving the character
        self.receive_character()
        
        return True

