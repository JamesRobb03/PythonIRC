
#!/usr/bin/python3
import socket
import datetime
import requests

SERVER = "localhost"
PORT = 6667
CHANNEL = "#test"

IRCSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect():
	IRCSoc.connect((SERVER, PORT))

def login():
    IRCSoc.send("USER Bot networksBot server :Bot\r\n".encode())
    IRCSoc.send("NICK Bot\r\n".encode())

def join():
	IRCSoc.send("JOIN #test\r\n".encode())
	print("Server Joined")

def ping():
    IRCSoc.send("PONG :pingisn\r\n".encode())
    print("PONGED")
      


def listen():
	while(True):
		buffer = IRCSoc.recv(1024)
		message = buffer.decode()

		if("PING :" in message):
			ping()
		else:
			messageRespond(message)

		print(buffer)

def messageRespond(message):
    #TODO repond to any message e.g. "!hello" "!slap"
    #TODO swap NICK with username

    if ("!hello" in message):
        #Below is to identify username
        st = ':'
        ed = '!'
        un = message [message.find(st)+len(st):message.find(ed)]

        #Below responds with Hello and date and time
        IRCSoc.send(("PRIVMSG #test :Hello" + un + "My name is BasicBot \r\n").encode())
        date = datetime.datetime.now()
        IRCSoc.send(("PRIVMSG #test :The time is: "+ date.strftime("%X")+"\r\n").encode())

    elif ("!slap" in message):
        #Below is to identify username
        st = ':'
        ed = '!'
        un = message [message.find(st)+len(st):message.find(ed)]

        #Below is to respond to a slap.
        IRCSoc.send(("PRIVMSG #test :Slapped " + un + " around a bit with a large trout \r\n").encode())

    #TODO Private Message Response
    elif ("PRIVMSG Bot" in message or ("PRIVMSG Bot" in message and "!" in message)):
        st = ':'
        ed = '!'
        un = message [message.find(st)+len(st):message.find(ed)]

        #respond with a fact
        res = requests.get('https://uselessfacts.jsph.pl/random.txt?language=en')
        IRCSoc.send(("PRIVMSG " + un + " :Here is a fact! " + str(res) + "\r\n").encode())


connect()
login()
join()
listen()
