#classes - Server, client?

#references: https://github.com/jrosdahl/miniircd/blob/master/miniircd, https://realpython.com/python-sockets/, https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c,
#            https://tools.ietf.org/html/rfc2813, https://python-irc.readthedocs.io/en/latest/_modules/irc/server.html, https://www.geeksforgeeks.org/simple-chat-room-using-python/

#imports
import socket  
import select 
import sys 
import string 

#Server Section
address = 'localhost' #change to address of host pc
port = 6667 #default port for irc
#global lists/dictionaries for easy reference.
client_li = []
channel_li = []
connection_li = []

class IRC_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def createChannels():
        channel_dict['#test'] =[]
        print("Created default channel #test")        

    #start socket
    def startServer(self):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #change for ipv6 to AF_INET6
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host,self.port))
        print("Server started!")
        return sock

    #Listen and create a new connection to the server
    def listenForConnection(self, server_socket):
        #setting up selector
        server_sock.listen()
        print("Listening for connections on ", address,":",str(port))
        #was using threading, however after reading these: https://realpython.com/python-sockets/#handling-multiple-connections
        #reading on select 
        #https://www.oreilly.com/library/view/python-standard-library/0596000960/ch07s03.html
        #https://stackoverflow.com/questions/20471816/how-does-the-select-function-in-the-select-module-of-python-exactly-work
        #https://www.programcreek.com/python/example/258/select.select
        #we decided to switch to the select module instead (might be bad cpu performance will have to check).
        server_sock.setblocking(False)
        connection_li.append(server_sock)
        while True: #infinite loop
            read_ready, _, _ = select.select(connection_li, [], [], None)
            for connection in read_ready:#loops through all active connections and processes there requests/adds new connection.
                if connection == server_sock: #If has the same socket as the server then open a new connection
                    #function to add a connection
                    acceptConnection(server_sock)
                else:
                    serviceConnection()

    def acceptConnection(self, server_socket):
        client_socket, client_address = server_socket.accept()
        new_client = Client(client_socket, client_address)
        new_client.add_client()

    def serviceConnection(self):
        client =  ClientConnection.getClient()
        data = client.connection.recv(1024)
        if data:
           data = data.decode()
           client.messageParser(data)

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

    def add_client(self):

    def remove_client(self):

    def message(self): #for channel and private messages

    #Need a message handling section. 
    def messageParser(self):


def main():
    server = IRC_Server(address, port)
    server_sock = server.startServer()
    server.listenForConnection(server_sock)

main()

        

