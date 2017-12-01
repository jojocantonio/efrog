import socket
import sys
import time, random, math
import threading
from threading import Timer
from tkinter import *
from tkinter import messagebox
import tkinter.simpledialog
import Pyro4, pygame
from pygame.locals import *
from os import path

def ShowMsgFromMe():  # display my message to the chat area
  Mymessage = entryMessage.get()
  if (str(Mymessage)!=""):
    Chatarea.config(state=NORMAL)
    Chatarea.insert(INSERT, "Me: " + entryMessage.get() + "\n")
    Chatarea.config(state=DISABLED)
  #erase previous message in Entry Box
  #entryMessage.delete(0,END)

def SendMsgToClients(name,):
  #alias = "Server"
  #Servermessage = entryMessage.get()
  i=0
  while i!=2: #execute 2 times
    i = i+1
    Cell_x = random.randint(20,1980)
    Cell_y = random.randint(20,1980)
    Cell_coord = "Coord,"+str(Cell_x)+","+str(Cell_y)
    print(Cell_coord)

    for allClient in allClients:
        s.sendto(Cell_coord.encode('ascii'), allClient)

def SendMsgToClients_and_ShowMsgFromMe():
  SendMsgToClients()
  ShowMsgFromMe()

def OnEnter(event):
  SendMsgToClients()
  ShowMsgFromMe()
  
def exitWindow(event): #close window
  s.close()
  rootwindow.destroy()
  sys.exit()

def RunDaemon():
      daemon.requestLoop() # start the event loop of the RMI daemon server

def ShowMsgFromClients(name,sock): # show messages from client and collect the names of the chatter for list
 global clients
 global allClients
 #global chatter
 #global allchatter
 global Name

 while 1:
  try:
   while 1:
    data,addr = sock.recvfrom(1024)
    print ("New connection from "+str(addr))

    Name = str(data.decode('ascii'))
    #Display only the name of chatter on the list
    Name = Name.split(" is")[0]
    #chatter = Name #Collecting all the names - SHOULD BE ON THE SERVER SIDE
                  #if chatter not in allchatter:
                    #allchatter.append(chatter)

    #Put messages on ChatArea
    Chatarea.config(state=NORMAL)
    Chatarea.insert(INSERT, str(Name+" is now connected on server at " + str(addr)+ "\n"))
    Chatarea.config(state=DISABLED)

    clients = addr

    #THIS SHOULD RUN and display names of chatters to the List box
    if clients not in allClients:
      allClients.append(clients)
      NameListArea.insert(1, Name) #PUT NAME ON THE LIST
      
      #print (str(Name) + str(addr)) #NAME and IP ADDRESS OF THE CHATTERS that shoudl be transfered on the client side

    ip,port = addr
    
    data = data + str("-").encode('ascii') + str(addr).encode('ascii')
    
    for allClient in allClients:
      s.sendto(data, allClient)
      print(allClient)

  except:
   pass

#def clearText(event): # clear the text "Type your message here"
 # entryMessage.delete(0,END)


#GUI Begin
rootwindow = Tk()
rootwindow.title("SERVER - Network Chat App")
rootwindow.minsize(width=600, height=500)
rootwindow.maxsize(width=750, height=550)
rootwindow.bind("<Control-Key-x>",exitWindow)

#Create a chat window
Chatarea = Text(rootwindow, bd=0, bg="white", height="8", width="50", font="Arial")
Chatarea.insert(END, "------------------------------- Messages -----------------------------\n")
Chatarea.config(state=DISABLED)

#Create a window for the name of chatters
NameListArea = Listbox(rootwindow, bd=0, bg="white", height="8", width="50", font="Arial")

#Bind a scrollbar to the Chat window
scrollbar = Scrollbar(rootwindow, command=Chatarea.yview, cursor="arrow")
Chatarea['yscrollcommand'] = scrollbar.set

# send message to Chat area
button = Button(rootwindow, text="Send", command=SendMsgToClients_and_ShowMsgFromMe)

#create a window for typing your message
#entryMessage = Entry(rootwindow, bg="#FFE599", font="Arial")
#entryMessage.insert(0,"Type your message here...")
#entryMessage.bind("<Button-1>", clearText)
#entryMessage.bind("<Return>",OnEnter)

#positioning of the widgets
scrollbar.place(x=400,y=6, height=400)
Chatarea.place(x=6,y=6, height=400, width=400)
NameListArea.place(x=416,y=6, height=400, width=175)
#entryMessage.place(x=6,y=420, height=30, width=400)
button.place(x=420,y=420, width=100)

#connection using TCP
print ("Server Chat is running. Please wait for the Client to connect!")
print ("------------------------------------------------------------------")

host="192.168.56.101"
port=5000

alias = "Server"
alias = ""
allClients = []
allChatter = [] #array for the list of the name of the chatters

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((host,port))
s.setblocking(0) 

#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.bind(("127.0.0.1",5000)) #IP and Port of the server
#s.listen(5)


#PYRO4 for RMI
@Pyro4.expose
class GenerateCells():
      def GenerateCells_function(self):
        #print("this is the ip"+ip)
        #OpponentName = OpponentNamePass
        #if messagebox.askyesno("Accept","Accept invitation to join game?"):
                  #global free_port
                  #global host
                  #Start the socket using TCP for private chat - this enables the chatmate to connect
                  #new_sMine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                  #new_sMine.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
                  #new_sMine.bind((host,free_port)) ########### IP and Port of machine ##########
                  #new_sMine.listen(5)
                  
                  #threading.Thread(target = StartGame,args = (ip,new_sMine,OpponentName)).start() #run the dialog box to private chat
                  rq = threading.Thread(target = SendMsgToClients,args = ("RecvThread",))
                  rq.start()

                  #return True, free_port

        #else:
                  return False


daemon = Pyro4.Daemon(host=host, port=4001)                # make a Pyro daemon
daemon.register(GenerateCells,"daemonCellsStarter")   # register the greeting maker as a Pyro object

#listen to clients messages
rt = threading.Thread(target = ShowMsgFromClients,args = ("RecvThread",s))
threading.Thread(target = RunDaemon).start() #run daemon loop
rt.start()




rootwindow.mainloop()
#GUI End
