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
address = 'fc00:1337::17' #change to address of host pc
port = 6667 #default port for irc
#global lists/dictionaries for easy reference.
client_li = []
connection_li = []
users = {}
channel_li = {}
connection_di={}


#TO-DO: add try/except. error handler which drops connections
class IRC_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def createChannels(self):
        channel_li['#test'] =[]
        print("Created default channel #test")        

    #start socket
    def startServer(self):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #change for ipv6 to AF_INET6
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host,self.port))
        print("Server started!")
        self.createChannels()
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
                    users[self.user]=[]
                    connection_di[self.user]=self
                    self.welcomeUser()
                    #print the thin

        except (ConnectionResetError, BrokenPipeError) as e:
            origin.handleException(e)

    def welcomeUser(self):
        self.message(socket.gethostname() + " 001 %s :Hi, welcome to Rushed IRC" % self.nickname)
        self.message(socket.gethostname() + " 002 %s :The host is: " % self.nickname + socket.gethostname() + "Version 1" )
        self.message(socket.gethostname() + " 003 %s :Server was created December 2020" % self.nickname)

    def send(self, groups): #for channel and private messages PRIVMSG
        target = groups[0]
        message = groups[1]
        #to tell its for a channel
        messageToSend = (self.nickname+'!'+self.user+'@'+socket.gethostname()+' PRIVMSG ' + target +' '+message)
        if '#' in target:
            for username in channel_li[target]:
                    if username != self.user:
                        connection_di[username].message(messageToSend)

        else:
            if target in connection_di:
                print("!!!!Sending private message!!!")
                connection_di[target].message(messageToSend)


    def connectToChannel(self, channel): #JOIN

        if self.user in users and str(channel) in channel_li:
            if (not (str(channel) in users[self.user])):

                users[self.user].append(str(channel))
                channel_li[str(channel)].append(self.user)

                print(self.user + " Has connected to the channel: " + str(channel))

                connectingUser = self.user
                connectingNick = self.nickname

                #connecting to channel
                for username in channel_li[channel]:  
                    connection_di[username].message(connectingNick + '!' + connectingUser +'@' + socket.gethostname() + ' JOIN ' + channel) #Let other users know that this client has joined
                self.message(socket.gethostname() + ' 331 ' + self.nickname + ' ' + str(channel) + ' Testing channel for AC31008-Networks')

                #listing names
                for username2 in channel_li[channel]:    
                    self.message(socket.gethostname() + ' 353 ' + username2 + ' = ' + str(channel) + ' :'+username2)
                self.message(socket.gethostname() + ' 366 ' + self.nickname + ' ' + str(channel) + ' :End of NAMES list')

            else:
                self.message(socket.gethostname() + ' 443 ' + self.user + ' ' +
                                   str(channel) + ' :already in channel')

        elif self.user in users and str(channel) not in channel_li:
            channel_li[str(channel)] =[]
            print("Created new channel: ", str(channel))
            users[self.user].append(str(channel))
            channel_li[str(channel)].append(self.user)
            print(self.user + " Has connected to the channel: " + str(channel))
            for username in channel_li[str(channel)]:                     
                connection_di[username].message(self.nickname + '!' + self.user +'@' + socket.gethostname() + ' JOIN ' + str(channel)) #Let other users know that this client has joined
            self.message(socket.gethostname() + ' 331 ' + self.nickname + ' ' + str(channel) + ' No topic set')

        
    def disconnect(self, group):
        channel = str(group[0])
        reason = str(group[1]) #PART
        if self.user in users and channel in channel_li:
            if self.user in channel_li[channel] and channel in users[self.user]:

                users[self.user].remove(channel)
                channel_li[channel].remove(self.user)
                print(self.user + ' has disconnected from ' +  channel)
                for username in channel_li[channel]:
                    connection_di[username].message(self.nickname + '!' + self.user +'@' + socket.gethostname() + ' PART ' + channel + reason)
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
            self.handleException(e)

    def handleException(self, e):
        print(e)
        if self.user != "" and self.nickname != "" and e.__class__.__name__ != 'BrokenPipeError':
            connection_li.remove(self.connection)
            client_li.remove(self)

            self.connection.close()
            print('Connection dropped by: ' + str(self.address))

    def message(self, message): 
        messageToSend = (":"+message+"\r\n").encode()
        self.connection.sendall(messageToSend)

    #Need a message handling sectio4n. 
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
                        self.send(groups)
                        print("privmsg")
                    elif(irc == 'join'):
                        #run connect to channel
                        self.connectToChannel(groups[0])
                    elif(irc == 'part'):
                        self.disconnect(groups)
                    elif(irc == 'who'):
                        #run who
                        print("who")
                    elif(irc == 'quit'):
                        self.remove_client()
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

        

