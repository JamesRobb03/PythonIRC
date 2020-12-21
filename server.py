#classes - Server, client?

#references: https://github.com/jrosdahl/miniircd/blob/master/miniircd, https://realpython.com/python-sockets/, https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c,
#            https://tools.ietf.org/html/rfc2813, https://python-irc.readthedocs.io/en/latest/_modules/irc/server.html, https://www.geeksforgeeks.org/simple-chat-room-using-python/

#imports
import socket  
import select 
import sys 
import string 
import re
#Server Section
address = '::1' #change to address of host pc
port = 6667 #default port for irc
#global lists/dictionaries for easy reference.
client_li = []
channel_li = {}
connection_li = []
users = {}


#TO-DO: add try/except. error handler which drops connections
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
    def listenForConnection(self, server_sock):
        #setting up selector
        server_sock.listen()
        print("Listening for connections on", address,":",str(port))
        #was using threading, however after reading these: https://realpython.com/python-sockets/#handling-multiple-connections
        #reading on select 
        #https://stackoverflow.com/questions/20471816/how-does-the-select-function-in-the-select-module-of-python-exactly-work
        #https://www.programcreek.com/python/example/258/select.select
        #decided to switch to the select module instead (might be bad cpu performance will have to check).
        server_sock.setblocking(False)
        connection_li.append(server_sock)
        while True: #infinite loop
            read_ready, _, _ = select.select(connection_li, [], [], None)
            for connection in read_ready:#loops through all active connections and processes there requests/adds new connection.
                if connection == server_sock: #If has the same socket as the server then open a new connection
                    #function to add a connection
                    self.acceptConnection(server_sock)
                else:
                    #function which handles servicing client connections. 
                    self.serviceConnection(connection)

    def acceptConnection(self, server_socket):
        client_socket, client_address = server_socket.accept()
        new_client = ClientConnection(client_socket, client_address)
        new_client.add_client()

    def serviceConnection(self, connectionSocket):
        client =  ClientConnection.get_client(connectionSocket)
        data = client.connection.recv(1024)
        if data:
           data = data.decode()
           client.messageParser(data)

#Class for the client connection
class ClientConnection:
    def __init__(self, connection, address):
        self.connection = connection #the socket
        self.address = address
        self.nickname = ""
        self.user = ""
        self.realname = ""

    #need setters for attributes
    #need to add extra steps in (curretnly just base functionality)
    #   inlcuding input and all that jazz

    def setNickname(self, groups):#NICK
        try:
            if self.nickname == "":
                self.nickname = groups[0]

            if self.user != "" and self.nickname == "":
                available = self.nicknameAvailable(self.nickname)
                if available != 0:
                    self.nickname = ""
                    print("Connection rejected.")
                    return False
                else:
                    self.welcomeUser()


        except (ConnectionResetError, BrokenPipeError) as e:
                origin.handleException(e)
            

    def setUser(self, groups):#USER
        try:
            if self.user != "":
                return False

            if self.nickname != "":
                usernamesetuser = groups[0]
                realnamesetuser = groups[3]
                available = self.usernameAvailable(usernamesetuser)
                if available != 0:
                    self.nickname = ""
                    print("Connection rejected.")
                    return False
                else:
                    self.user = usernamesetuser
                    self.realname = realnamesetuser
                    self.welcomeUser()
                    #print the thin

        except (ConnectionResetError, BrokenPipeError) as e:
            origin.handleException(e)

    def welcomeUser(self):
        self.message(socket.gethostname() + " 001 %s :Hi, welcome to Rushed IRC" % self.nickname)
        self.message(socket.gethostname() + " 002 %s :The host is: " % self.nickname + socket.gethostname() + "Version 1" )
        self.message(socket.gethostname() + " 003 %s :Server was created December 2020" % self.nickname)

    def send(self, message): #for channel and private messages PRIVMSG
        return
    def connectToChannel(self, channel): #JOIN
         if self.user in users and channel in channel_li:
            if (not (channel in users[self.user])):
                users[self.user].append(channel)
                channel_li[channel].append(self.user)
                print(self.user +  ' connected to ' + channel)
                return True

            else:
                self.message(':' + connection.gethostname() + ' 443 ' + self.user + ' ' +
                                   channel + ' :already in channel')

        return False
    
    except (ConnectionResetError, BrokenPipeError) as e:
        origin.handleException(e)
        
    def disconnect(self, channel): #PART
        if self.user in users and channel in channel_li:
            if self.user in channel_li[channel] and channel in users[self.user]:

                users[self.user].remove(channel)
                channel_li[channel].remove(self.user)
                print(self.user + ' has disconnected from ' +  channel)
                return True

        return False
            


    def add_client(self): #to keep track of all active clients
        connection_li.append(self.connection)
        client_li.append(self)

    def get_client(socket): #function which returns the right connection for serviceConnections()
        for client in client_li:
            if client.connection == socket:
                return client

    def who(self): #WHO
        return
    def ping(self):#PING
        return
    def remove_client(self): #QUIT
        try:
            
            raise Exception('quit')

        except (ConnectionResetError, BrokenPipeError, Exception) as e:
        origin.handleException(e)

    def handleException(self, e):
        print(e)
        if self.user != "" and self.nickname != "" and e.__class__.__name__ != 'BrokenPipeError':
            removeUser(self.nickname)
            self.conn.close()
            print('Connection dropped by: ' + str(self.address))

    def message(self, message): 
        messageToSend = (":"+message+"\r\n").encode()
        self.connection.sendall(messageToSend)

    #Need a message handling section. 
    def messageParser(self, data): #data is the data passed in from serviceconnection
        #Found this on a github repo for a python irc server (same assignment for this module but from last year)
        #have to reference!!!
        #https://github.com/CharlieHewitt/AC31008-Networks/blob/master/server.py 
        ircCommands = {
            'user': r'USER\s(.*)\s(.*)\s(.*)\s:(.*)',
            'nick': r'NICK\s(.*)',
            'privmsg': r'PRIVMSG\s(.*)\s:(.*)',
            'join': r'JOIN\s(.*)',
            'part': r'PART\s(.*) (:.*)',
            'who': r'WHO\s(.*)',
            'ping': r'PING\s(.*)',
            'quit': r'QUIT\s(.*)'
        }

        message = data.split('\r\n')
        for m in message:
            for irc in ircCommands:
                match = re.search(ircCommands[irc], m) #https://docs.python.org/3/library/re.html
                if(match):#if there is a matching irc command
                    groups=match.groups() #https://www.tutorialspoint.com/What-is-the-groups-method-in-regular-expressions-in-Python
                    if(irc == 'user'):
                        self.setUser(groups)
                    elif(irc == 'nick'):
                        self.setNickname(groups)
                    elif(irc == 'privmsg'):
                        #run send
                        print("privmsg")
                    elif(irc == 'join'):
                        #run connect to channel
                        print("join")
                    elif(irc == 'part'):
                        #run disconnect
                        print("part")
                    elif(irc == 'who'):
                        #run who
                        print("who")
                    elif(irc == 'ping'):
                        #run ping
                        print("ping")
                    elif(irc == 'quit'):
                        #run remove_client
                        print("quit")
                    else:
                        print("No matching command!")

    def nicknameAvailable(self, nickname):
        for user in client_li:
            if user.nickname == nickname:
                return 1
            return 0

    def usernameAvailable(self, user):
        for users in client_li:
            if users.user == user:
                print("USERNAME IN USE")
                return 1
            return 0

#MAIN PROGRAM. RUNS THIS FUNCTION TO START SERVER
def main():
    server = IRC_Server(address, port)
    server_sock = server.startServer()
    server.listenForConnection(server_sock)

main()

        

