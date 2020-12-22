#classes - Server, client?

#references: https://github.com/jrosdahl/miniircd/blob/master/miniircd, https://realpython.com/python-sockets/, https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c,
#            https://tools.ietf.org/html/rfc2813, https://python-irc.readthedocs.io/en/latest/_modules/irc/server.html, https://www.geeksforgeeks.org/simple-chat-room-using-python/
#            https://stackoverflow.com/questions/20471816/how-does-the-select-function-in-the-select-module-of-python-exactly-work
#            https://www.programcreek.com/python/example/258/select.select, https://realpython.com/python-sockets/#handling-multiple-connections



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
connection_li = []
users = {}
channel_li = {}
connection_di={}


#TO-DO: add try/except. error handler which drops connections

#Server class or a server object
class IRC_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    #function to create the default test channel
    def createChannels(self):
        channel_li['#test'] =[]
        print("Created default channel #test")        

    #starts server socket
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
        server_sock.setblocking(False)
        connection_li.append(server_sock)
        while True: #infinite loop
            read_ready, _, _ = select.select(connection_li, [], [], None)
            for connection in read_ready:#loops through all active connections and processes there requests/accepts new connections.
                if connection == server_sock: 
                    #function to add a connection
                    self.acceptConnection(server_sock)
                else:
                    #function which handles servicing connections. 
                    self.serviceConnection(connection)

    #function to accept a connection
    def acceptConnection(self, server_socket):
        client_socket, client_address = server_socket.accept()
        new_client = ClientConnection(client_socket, client_address)
        new_client.add_client()

    #function to service a connection. The part of the server that processes client sockets
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


    ##sets the users nickname and welcomes to server, checks if suername is unique and available
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
            

    #Sets the users username and real name, adds the connection to the connections dictionary and welcomes the user
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

    #Have to welcome user to server when they succesfully set a NICK and USER.
    def welcomeUser(self):
        self.message(socket.gethostname() + " 001 %s :Hi, welcome to Rushed IRC " % self.nickname)
        self.message(socket.gethostname() + " 002 %s :The host is: " % self.nickname + socket.gethostname() + " Version 1" )
        self.message(socket.gethostname() + " 003 %s :Server was created December 2020" % self.nickname)
        self.message(socket.gethostname() + " 004 %s :Your host is : " % self.nickname + socket.gethostname()+" Version 1 No available modes")


    #for channel and private messages PRIVMSG
    def send(self, groups): 
        target = groups[0]
        message = groups[1]
        #creating the message to send
        messageToSend = (self.nickname+'!'+self.user+'@'+socket.gethostname()+' PRIVMSG ' + target +' '+message)

        #to tell its for a channel
        if '#' in target:
            for username in channel_li[target]:
                    if username != self.user:
                        connection_di[username].message(messageToSend)

        #if not for channel must be for a private message
        else:
            #need to lookup nick from username
            usernameFromFunc = self.getUsername(target)
            if usernameFromFunc != 0:                
                if usernameFromFunc in connection_di:#connection dictionary maps to usernames, we inputing nick. need a function which gets a matching username and nick
                    print("!!!!Sending private message too ", usernameFromFunc, " !!!!")
                    connection_di[usernameFromFunc].message(messageToSend)
            else:
                print("TRIED TO SEND A MESSAGE BUT NO MATCHING USERNAME WAS FOUND")

    #function for joining a channel
    def connectToChannel(self, channel): #JOIN
        #checks if valid user and valid channel
        if self.user in users and str(channel) in channel_li:
            #checks to see if user is already in channel
            if (not (str(channel) in users[self.user])):

                users[self.user].append(str(channel))
                channel_li[str(channel)].append(self.user)

                print(self.user + " Has connected to the channel: " + str(channel))

                connectingUser = self.user
                connectingNick = self.nickname

                #connecting to channel
                #https://tools.ietf.org/html/rfc2812#section-3.2.1
                for username in channel_li[channel]:  
                    connection_di[username].message(connectingNick + '!' + connectingUser +'@' + socket.gethostname() + ' JOIN ' + channel) #Let other users know that this client has joined
                self.message(socket.gethostname() + ' 331 ' + self.nickname + ' ' + str(channel) + ' Testing channel for AC31008-Networks')

                #Showing users in the channel(RPL_NAMREPLY).
                for username2 in channel_li[channel]:    
                    self.message(socket.gethostname() + ' 353 ' + username2 + ' = ' + str(channel) + ' :'+username2)
                self.message(socket.gethostname() + ' 366 ' + self.nickname + ' ' + str(channel) + ' :End of NAMES list')

            else:
                self.message(socket.gethostname() + ' 443 ' + self.user + ' ' + str(channel) + ' :already in channel')

        #elif to check that user is valid and to deal with handling a channel that hasnt been created yet
        elif self.user in users and channel not in channel_li:
            #if a valid channel name then create the channel and add the user to it
            if '#' in str(channel):
                channel_li[channel] =[]
                print("Created new channel: ", str(channel))
                users[self.user].append(channel)
                channel_li[channel].append(self.user)
                connectingUser = self.user
                connectingNick = self.nickname
                print(self.user + " Has connected to the channel: " + str(channel))
                for username in channel_li[channel]:                     
                    connection_di[username].message(connectingNick + '!' + connectingUser +'@' + socket.gethostname() + ' JOIN ' + channel) #Let other users know that this client has joined
                self.message(socket.gethostname() + ' 331 ' + self.nickname + ' ' + str(channel) + ' No topic set')

        
    def disconnect(self, group):
        channel = str(group[0])
        reason = str(group[1]) 
        connectingUser = self.user
        connectingNick = self.nickname
        if self.user in users and channel in channel_li:
            if self.user in channel_li[channel] and channel in users[self.user]:

                users[self.user].remove(channel)
                channel_li[channel].remove(self.user)
                print(self.user + ' has disconnected from ' +  channel)
                for username in channel_li[channel]:
                    connection_di[username].message(connectingNick + '!' + connectingUser +'@' + socket.gethostname() + ' PART ' + channel + " :" +reason)
                return True

        return False
            

    #function needed to keep track of all active clients
    def add_client(self): 
        connection_li.append(self.connection)
        client_li.append(self)

    #function which returns the right connection for serviceConnections()
    def get_client(socket): 
        for client in client_li:
            if client.connection == socket:
                return client

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

    #used to encode a message and then send it on the socket.
    #uses sendall instead of send to make sure all of the message is sent.
    def message(self, message): 
        messageToSend = (":"+message+"\r\n").encode()
        self.connection.sendall(messageToSend)

    #Message parsing function that takes the recieved data and trys to match it to an implemented IRC command.
    #this is needed to determine what a client is trying to do.
    def messageParser(self, data): #data is the data passed in from serviceconnection a method from the IRC server class
        
        #dictionary of irc commands used for comparing the message to
        #uses regex to compare the layout of a message to an irc command.
        ircCommands = {
            'user': r'USER\s(.*)\s(.*)\s(.*)\s:(.*)',
            'nick': r'NICK\s(.*)',
            'privmsg': r'PRIVMSG\s(.*)\s:(.*)',
            'join': r'JOIN\s(.*)',
            'part': r'PART\s(.*)\s:(.*)',
            'quit': r'QUIT\s(.*)'
        }

        message = data.split('\r\n')
        for m in message:
            for irc in ircCommands:
                match = re.search(ircCommands[irc], m) #https://docs.python.org/3/library/re.html
                if(match):#if there is a matching irc command
                    #this is needed to split the match into the different parts of the message ie  PART {group[0]} {:group[1]}
                    groups=match.groups() #https://www.tutorialspoint.com/What-is-the-groups-method-in-regular-expressions-in-Python
                    if(irc == 'user'):
                        self.setUser(groups)
                    elif(irc == 'nick'):
                        self.setNickname(groups)
                    elif(irc == 'privmsg'):
                        self.send(groups)
                    elif(irc == 'join'):
                        self.connectToChannel(groups[0])
                    elif(irc == 'part'):
                        self.disconnect(groups)
                    elif(irc == 'quit'):
                        self.remove_client()
                    else:
                        print("No matching command!")

    #function to stop multiple of the same nicknames
    def nicknameAvailable(self, nickname):
        for user in client_li:
            if user.nickname == nickname:
                return 1
            return 0

    #function to stop multiple of the same usernames
    def usernameAvailable(self, user):
        for users in client_li:
            if users.user == user:
                print("USERNAME IN USE")
                return 1
            return 0

    #Function which is used for sending private messages.
    #Needed as PRIVMSG uses a nickname and our dictionary stores usernames
    def getUsername(self, nickname):
        print("now in getUsername")
        for users in client_li:  
            print(users.nickname, " - ", users.user)
            if users.nickname == nickname:
                print("!!returning user!!")
                return users.user
        return 0

#MAIN PROGRAM. RUNS THIS FUNCTION TO START SERVER
def main():
    server = IRC_Server(address, port)
    server_sock = server.startServer()
    server.listenForConnection(server_sock)

main()

        

