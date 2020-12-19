#classes - Server, client?

#references: https://github.com/jrosdahl/miniircd/blob/master/miniircd, https://realpython.com/python-sockets/, https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c,
#            https://tools.ietf.org/html/rfc2813, https://python-irc.readthedocs.io/en/latest/_modules/irc/server.html, https://www.geeksforgeeks.org/simple-chat-room-using-python/

#imports
import socket  
import select  
import sys  
from thread import *
#Server Section
address = 'localhost' #change to address of host pc
port = 6667 #default port for irc
#global dictionaries for easy reference.
user_dict = {}
channel_dict = {}
coonection_dict = {}

class IRC_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def createChannels():
        channel_dict['#test'] =[]
        print("Created default channel #test")        

    #start socket
    def startServer(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #change for ipv6 to AF_INET6
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host,self.port))
        return sock

    #Listen and create a new connection to the server
    def listenForConnection(self, server_socket):
        server_sock.listen()
        print("Listening for connections")
        while True:
            connection, user_address = sock.accept()
            new_client = ClientConnection(connection, user_address)#will reference user class!
            threading.Thread(target=ClientConnection.listen).start()
    

#Class for the client connection
class ClientConnection:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.nickname = ""
        self.user = ""
        self.realname = ""

    def send(self, message):
        
    def receive(self):

    def connect(self, channel):
        
    def disconnect(self, channel):

    def listen(self):

#user and channel management
#functions that the class functions reference
def add_client():

def remove_client():

def connect():
    
def disconnect():

def message():


#Need a message handling section. Use regex. look at miniircd server source code. 


def main():
    server = IRC_Server(address, port)
    server_sock = server.startServer()
    server.listenForConnection(server_sock)

main()

        

