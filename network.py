# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import socket
import select
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
        


            
    # time event        
    def tick(self, dt):
        (ready_to_read,_,_) = select.select(self.client+[self.s], [], [])
        for sock in ready_to_read:
            if sock == self.s and ready_to_read:
                player, addr = self.s.accept()
                print("{} connected".format(addr))
                def_map = self.model.map.load(DEFAULT_MAP)  #to modify
                player.send(b"def_map")     #to modify
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
        the_map = self.sock.recv(9).decode()  #to modify
        model.load_map(the_map)

        
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


    
    # time event

    def tick(self, dt):
        return True
