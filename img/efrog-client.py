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
      Mymessage = "Connected to server"
      if (str(Mymessage)!=""):
        Chatarea.config(state=NORMAL) 
        Chatarea.insert(INSERT, "Me: " + Mymessage + "\n")
        Chatarea.config(state=DISABLED)
      #erase previous message in Entry Box
      #entryMessage.delete(0,END)

def SendMsgToServer(): # send message to server
      #alias = "Client"
      global alias

      Clientmessage = " is now connected to the game server"
      if (str(Clientmessage)!="" and str(Clientmessage)!="Type your message here..."):
        
        if (alias==""): #Need to input name of the user.
          alias = tkinter.simpledialog.askstring("Username","Please enter player name.")

        s.sendto(alias.encode('ascii')+ Clientmessage.encode('ascii'),server)

def SendMsgToServer_and_ShowMsgFromMe(): # bind to button send
      SendMsgToServer()
      
      # Separate socket to receive Cells coordinate from server
      #iConnect_Cells = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
      #iConnect_Cells.bind((host,port))
      #iConnect_Cells.setblocking(0)
                  
      #ShowMsgFromMe()
      #entryMessage.delete(0,END)

def OnEnter(event):
      SendMsgToServer()
      entryMessage.delete(0,END)
      #ShowMsgFromMe()

def exitWindow(event): #close window
      s.close()
      rootwindow.destroy()
      quit()

def ShowMsgFromServer(name,sock):
     global clients
     global Name
     global Cells_x
     global Cells_y     
     
     while 1:
      try:
       while 1:
        data = s.recv(4096) #listen to server
        #ClientName = data.split(":")
        print(data)
        
        msg = str(data.decode('ascii')).strip()
        
        if "Coord" in msg: #intercept message from server with Coord and strip to get coordinator for cells
            Cells_x = float(msg.split(",")[1])
            Cells_y = float(msg.split(",")[2])
            print(str(Cells_x)+""+str(Cells_y))
        else:

              msg = msg.split("-")[0]
                  
              #Put message on Chat area
              Chatarea.config(state=NORMAL)
              Chatarea.insert(INSERT, str(msg) + "\n")
              Chatarea.config(state=DISABLED)

              Name = str(data.decode('ascii')).strip()
              Name = Name.split(" is")[0]
              ipPort = str(data.decode('ascii')).split("-")[1]
              #print(ipPort)
              clients = Name

              #THIS SHOULD RUN and display names of chatters to the List box
              #if clients not in allClients:
              if allClients.get(Name) == None:
                allClients[Name] = ipPort

                if not Name == alias: # Should not display own name on the list
                      NameListArea.insert(1, Name) #PUT NAME ON THE LIST
                      NameListArea.bind("<Double-1>",OnDoubleClickNameList)

      except:
       pass

def clearText(event): # clear the text "Type your message here"
      entryMessage.delete(0,END)

def OnDoubleClickNameList(event): # send invitation to chatter on the chatter list
      global InvitedChatter
      InvitedChatter = Name
      inviteChatter = messagebox.askyesno("Invite Chatter","Invite to Play e-frog?")

      if inviteChatter:
        #NameListArea.curselection() 
        #print(NameListArea.get(NameListArea.curselection()))
        foundMatchIpPort = allClients.get(NameListArea.get(NameListArea.curselection()))
        
        if not foundMatchIpPort == None:
              #print (foundMatchIpPort)
              foundMatchIpPort = foundMatchIpPort.replace('(','')
              foundMatchIpPort = foundMatchIpPort.replace(')','')
              foundMatchIpPort = foundMatchIpPort.replace('\'','')
              IpOnly = foundMatchIpPort.split(",")[0]
              #print(IpOnly)
              uri="PYRO:daemonGameStarter@"+IpOnly+":4000" #Identify the Daemon
              call=Pyro4.Proxy(uri)
              x = call.ask_connection(host,alias) #get free port of the host and send player name
              if x: # if invited clicked yes

                  # if chatmate accept invitation then connect to it
                  iConnect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                  iConnect.connect((IpOnly,x[1]))

                  #create new window for Iconnect Only Connection- this should not call NewWindow func
                  #threading.Thread(target = iConnectNewWindow,args = (IpOnly,iConnect)).start() #run the dialog box to private chat
                  threading.Thread(target = iConnect_StartGame,args = (IpOnly,iConnect,InvitedChatter)).start() #run the dialog box to private chat
           
def RunDaemon():
      daemon.requestLoop() # start the event loop of the RMI daemon server


def get_free_tcp_port():
      tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      tcp.bind(('', 0))
      addr, port = tcp.getsockname()
      tcp.close()
      return port


##### I CONNECT START Frog Game Code as a single user #####


def iConnect_StartGame(ip,sock,InvitedOpponent):

        #Connect to the daemon of the server to execute cells coordinates
        uri="PYRO:daemonCellsStarter@192.168.56.101:4001" #Identify the Daemon
        call=Pyro4.Proxy(uri)
        x = call.GenerateCells_function() #get free port of the host and send player name


      #My socket as the receiver CHECK EXER 3 REGARDING THIS... ICONNECT SECTION
        iConnect_sock = sock 
        
        pygame.init()
        colors_players = [(37,7,255),(35,183,253),(48,254,241),(19,79,251),(255,7,230),(255,7,23),(6,254,13)]
        colors_cells = [(80,252,54),(36,244,255),(243,31,46),(4,39,243),(254,6,178),(255,211,7),(216,6,254),(145,255,7),(7,255,182),(255,6,86),(147,7,255)]

        colors_viruses = [(66,254,71)]
        screen_width, screen_height = (1200,800)
        surface = pygame.display.set_mode((1200,800))
        #surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        t_surface = pygame.Surface((95,25),pygame.SRCALPHA) #transparent rect for score
        t_lb_surface = pygame.Surface((200,278),pygame.SRCALPHA) # WIDTH, HEIGHT of transparent rect for leaderboard box
        t_surface.fill((50,50,50,80))
        t_lb_surface.fill((50,50,50,80))
        pygame.display.set_caption("e.frog")
        cell_list = list()
        venus_cell_list = list()
        #enemy_list = list()
        clock = pygame.time.Clock()

        img_dir = path.join(path.dirname(__file__), 'img')

        background_image = pygame.image.load(path.join(img_dir,"bg.jpg")).convert()
        background_image_rect = background_image.get_rect()
        egg_image = pygame.image.load(path.join(img_dir,"egg.png")).convert()
        tadpole_image = pygame.image.load(path.join(img_dir,"tadpole.png")).convert()
        frog_image = pygame.image.load(path.join(img_dir,"frog.png")).convert()

        #START GAME
        gameOver = False
        gameRunning = True
        my_move_x = 0
        my_move_y = 0
        my_mass = 0 # my size to be pass to opponent

        try:
            font = pygame.font.Font(None,20)
            big_font = pygame.font.Font(None,30)
            game_over_font = pygame.font.Font(None,100)
        except:
            print("Font file not found: arial.ttf")
            font = pygame.font.SysFont('arial.ttf',20,True)
            big_font = pygame.font.SysFont('arial.ttf',24,True)


        def drawText(message,pos,color=(255,255,255)):
                surface.blit(font.render(message,1,color),pos)

        def drawText_size(message,pos,color=(255,255,255)):
                surface.blit(font.render(message,20,color),pos)

        def getDistance(pos1,pos2):
            px,py = pos1
            p2x,p2y = pos2
            diffX = math.fabs(px-p2x)
            diffY = math.fabs(py-p2y)

            return ((diffX**2)+(diffY**2))**(0.5)


##### SEND GET ICONNECT DATA #######

        def send_opponent_data_iConnect(name,sock): # send player data to chat mate

                iConnect_sock = sock
                global alias
                global my_move_x
                global my_move_y

                #MyMove = "Helllooooo" #my_move_x,my_move_y

                
                while 1:
                  try:
                    while 1:
                      my_move_x_str = str(my_move_x)
                      my_move_y_str = str(my_move_y)
                      #iConnect_sock.send(my_move_x_str.encode('ascii')+b","+ my_move_y_str.encode('ascii'))
                      iConnect_sock.send(my_move_x_str.encode('ascii'))
                      #print("Sending Data to Opponent from iConnect 1 "+MyMove)
                      #print(my_move_x_str+","+my_move_y_str)
                  except:
                    pass

        def get_opponent_data_iConnect(name,sock):

                #global iConnect_sock
              
            global opp_move_x_iconnect
            global opp_move_y_iconnect
            global opp_mass_iconnect
            global opp_score_iconnect

            while 1:
                  try:
                    while 1:

                      data = iConnect_sock.recv(2048) #listen to opponent player movement
                      #print("---------------------------------------------n")
                      OpponentMouseCoordinate = str(data.decode('ascii')).strip()
                      opp_move_x_iconnect = float(OpponentMouseCoordinate.split(",")[0])
                      opp_move_y_iconnect = float(OpponentMouseCoordinate.split(",")[1])
                      opp_mass_iconnect = float(OpponentMouseCoordinate.split(",")[2])
                      opp_score_iconnect = OpponentMouseCoordinate.split(",")[3]
                      
                      #opp_move_x = float(int_opp_move_x)
                      #opp_move_y = float(int_opp_move_y)
                      
                      #print ("Player 1 MCoordinate "+)
                      #print ("Get X "+str(opp_move_y_iconnect))
                      #print ("Get Y "+int_opp_move_y)
                  except Exception as e:
                    print(e)


        class Camera:
            def __init__(self):
                self.x = 0
                self.y = 0

                self.width = screen_width
                self.height = screen_height
                self.zoom = 0.5

            def centre(self,blobOrPos):
                if(isinstance(blobOrPos,Player)):
                    p = blobOrPos
                    self.x = (p.startX-(p.x*self.zoom))-p.startX+((screen_width/2))
                    self.y = (p.startY-(p.y*self.zoom))-p.startY+((screen_height/2))

                elif(type(blobOrPos) == tuple):
                    self.x,self.y = blobOrPos

        class Player:
            def __init__(self,surface,name = ""):
                self.startX = self.x = random.randint(100,400)
                self.startY = self.y = random.randint(100,400)
                self.mass = 5
                self.surface = surface
                self.color = colors_players[random.randint(0,len(colors_players)-1)]
                self.name = name
                self.pieces = list()
                piece = Piece(surface,(self.x,self.y),self.color,self.mass,self.name)

                global my_move_x
                global my_move_y
                #global opp_move_x_iconnect
                #global opp_move_y_iconnect
                global iConnect_sock

            def update(self):

                  self.move()
                  self.collisionDetection()

            def update_opponent(self):
                global opp_mass_iconnect
                self.move_opponent(sock)
                #self.mass = opp_mass_iconnect
                print ('Opp mass from update opponent of ICOnnect'+str(opp_mass_iconnect))
                #self.get_opponent_data() #get data from opponent -eg. movement, name etc.

            def collisionDetection(self):
                global gameOver
                global gameRunning
                
                for cell in cell_list:
                    if(getDistance((cell.x,cell.y),(self.x,self.y)) <= self.mass/2):
                        self.mass+=0.5
                        #my_mass = self.mass
                        cell_list.remove(cell)

                for venus_cell in venus_cell_list:
                    if(getDistance((venus_cell.x,venus_cell.y),(self.x,self.y)) <= 15):
                        #self.mass+=0.5
                        gameRunning = False
                        print("COLLIDE WITH Venus")
                        game_over()


            def move(self):

                global my_move_x
                global my_move_y
                #global my_move_y
                #iConnect_sock
             
                if (gameRunning!=False):

                    dX,dY = pygame.mouse.get_pos()
                    rotation = math.atan2(dY-(float(screen_height)/2),dX-(float(screen_width)/2))*180/math.pi
                    speed = 2-1 #orig is 2-1
                    vx = speed * (90-math.fabs(rotation))/90
                    vy = 0

                    if(rotation < 0):
                        vy = -speed + math.fabs(vx)
                    else:
                        vy = speed - math.fabs(vx)
                    self.x += vx
                    self.y += vy

                    my_move_x = self.x
                    my_move_y = self.y
                    my_mass = self.mass
                    my_score = int(blob.mass*2)
                    my_move_coord = str(my_move_x)+","+str(my_move_y)+","+str(my_mass)+","+str(my_score)

                    iConnect_sock.send(my_move_coord.encode('ascii')) # send my position to Opponent

                    #print("I connect My Score "+str(my_score))


            def move_opponent(self,sock):
                  #global opp_move_x
                  #global opp_move_y

                  
                  if (gameRunning!=False):

                    self.x = opp_move_x_iconnect
                    self.y = opp_move_y_iconnect
                    #print("THIS IS IT OPP move x"+str(opp_move_x_iconnect))

          
            def feed(self):
                pass

            def split(self):
                pass

            def draw(self,cam):
                score = int(blob.mass*2)
                size_expand = score + 8 # sprite to cover the circle

                col1 = (255,255,255)
                col2 = (34,34,34)
                col3 = (0,178,0)
                zoom = cam.zoom
                x = cam.x
                y = cam.y
                
                
                if(score >= 100 and score > 50):
                    image = pygame.transform.scale(frog_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col3,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
                elif(score >= 50 and score < 100):
                    image = pygame.transform.scale(tadpole_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col2,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                    
                else:
                    #TEMPLATE - parameter for pygame.draw.circle(Surface, color, pos, radius, width=0)
                    image = pygame.transform.scale(egg_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col1,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                if(len(self.name) > 0): ## Display name of the player
                	fw, fh = font.size(self.name)
                	drawText(self.name, (self.x*cam.zoom+cam.x-int(fw/2),self.y*cam.zoom+cam.y-int(fh/2)),(50,50,50))


            def drawOpponent(self,cam):
                score_Opponent = int(opp_mass_iconnect*2)
                size_expand =8 #score + 8 # sprite to cover the circle

                col1 = (255,255,255)
                col2 = (34,34,34)
                col3 = (0,178,0)            
                
                if(score_Opponent >= 100 and score_Opponent > 50):
                    image = pygame.transform.scale(frog_image,(int(opp_mass_iconnect*6),int(opp_mass_iconnect*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col3,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
                elif(score_Opponent >= 50 and score_Opponent < 100):
                    image = pygame.transform.scale(tadpole_image,(int(opp_mass_iconnect*6),int(opp_mass_iconnect*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col2,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                    
                else:
                    #TEMPLATE - parameter for pygame.draw.circle(Surface, color, pos, radius, width=0)
                    image = pygame.transform.scale(egg_image,(int(opp_mass_iconnect*6),int(opp_mass_iconnect*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col1,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                if(len(self.name) > 0): ## Display name of the player
                	fw, fh = font.size(self.name)
                	drawText(self.name, (self.x*cam.zoom+cam.x-int(fw/2),self.y*cam.zoom+cam.y-int(fh/2)),(50,50,50))


        class Piece:
            def __init__(self,surface,pos,color,mass,name,transition=False):
                self.x,self.y = pos
                self.mass = mass
                self.splitting = transition
                self.surface = surface
                self.name = name

            def draw(self):
                pass

            def update(self):
                if(self.splitting):
                    pass

        class Cell:
            def __init__(self,surface):
                self.x = Cells_x #random.randint(20,1980)
                self.y = Cells_y #random.randint(20,1980)
                self.mass = 10 #2
                self.surface = surface
                self.color = (255,0,0) #(0,140,35)

            def draw(self,cam):
                pygame.draw.circle(self.surface,self.color,(int((self.x*cam.zoom+cam.x)),int(self.y*cam.zoom+cam.y)),int(self.mass*cam.zoom))

        def spawn_cells(numOfCells):
            for i in range(numOfCells):
                cell = Cell(surface)
                cell_list.append(cell)


        class venus_Cell:
            def __init__(self,surface):
                self.x = random.randint(20,1980)
                self.y = random.randint(20,1980)
                self.mass = 15
                self.surface = surface
                self.color = (255,38,255)

            def draw(self,cam):
                pygame.draw.circle(self.surface,self.color,(int((self.x*cam.zoom+cam.x)),int(self.y*cam.zoom+cam.y)),int(self.mass*cam.zoom))

        def spawn_venus_Cells(numOfCells):
            for i in range(numOfCells):
                venus_cell = venus_Cell(surface)
                venus_cell_list.append(venus_cell)

        def draw_grid():
            for i in range(0,2001,20):
                pygame.draw.line(surface,(80,195,216),(0+camera.x,i*camera.zoom+camera.y),(2001*camera.zoom+camera.x,i*camera.zoom+camera.y),1) # x-axis grid
                pygame.draw.line(surface,(80,195,216),(i*camera.zoom+camera.x,0+camera.y),(i*camera.zoom+camera.x,2001*camera.zoom+camera.y),1) # y-axis grid    


        def draw_HUD():

            global score

            w,h = font.size("Score: "+str(int(blob.mass*2))+" ")
            surface.blit(pygame.transform.scale(t_surface,(w,h)),(20,screen_height-30))
            surface.blit(t_lb_surface,(screen_width-160,35))
            
            surface.blit(big_font.render("Leaderboard",0,(255,255,255)),(screen_width-157,20))
            drawText("Opponent: "+ str(opp_score_iconnect),(screen_width-157,20+25))
            drawText("My score: "+ str(int(blob.mass*2)),(screen_width-157,20+25*2))
            #drawText(str(int(blob.mass*2)),(screen_width-157,20+25*11))
            #drawText("My Score: "+str(int(blob.mass*2)),(screen_width-157,20+25*11))

            #score = int(blob.mass*2)
            
            #if(score >= 15):
            #    drawText("10. My Player",(screen_width-157,20+25*10))
            #else:
            #    drawText("10. Player 10",(screen_width-157,20+25*10),(210,0,0))

        def game_over():
            #global gameRunning
            #drawText_size("GAME OVER",(screen_width/2, screen_height/4))
            surface.blit(game_over_font.render("GAME OVER",10,(255,255,255)),(screen_width/2-120, screen_height/2-20))
            pygame.display.flip()
            gameRunning = False
            time.sleep(5)
            pygame.quit()

        # INITIALIZE SETTING
        camera = Camera()
        blob = Player(surface,alias)
        Opponent = Player(surface,InvitedOpponent)
        spawn_cells(2)

       
        #spawn_Enemy(1)
        spawn_venus_Cells(1) #venus playtrap numbers

        
      # start receiving/sending data from the opponents

        #new_iConnect_send_rt = threading.Thread(target = send_opponent_data_iConnect,args = ("SendThread",sock))
        #new_iConnect_send_rt.start()
        new_iConnect_get_rt = threading.Thread(target = get_opponent_data_iConnect,args = ("RecvThread",sock))
        new_iConnect_get_rt.start()
        
        while(gameRunning!=False):
            clock.tick(60) # 60 frames per second
            for e in pygame.event.get():
                if(e.type == pygame.KEYDOWN):
                    if(e.key == pygame.K_ESCAPE):
                        pygame.quit()
                        quit()
                    if(e.key == pygame.K_SPACE):
                        blob.split()
                    if(e.key == pygame.K_w):
                        blob.feed()
                if(e.type == pygame.QUIT):
                    pygame.quit()
                    quit()
            
            #update section
            blob.update()
            #Enemy.update()
            Opponent.update_opponent()
            camera.zoom = .5 #updated for steady zoom - recommeneded is 5

            #camera.centre(blob2)
            camera.centre(blob)

            #Draw section
            #surface.fill((77,210,255))
            surface.blit(background_image, background_image_rect)
            #surface.fill((0,0,0))
            draw_grid()
            for c in cell_list: #display food cells
                c.draw(camera)
            for v in venus_cell_list: #display venus trap
                v.draw(camera)
            blob.draw(camera)
            Opponent.drawOpponent(camera)
            draw_HUD()

            #display updated graphics
            pygame.display.flip()

####END Frog game Code


##### START Frog Game Code as a single user #####
def StartGame(ip,sock,OpponentNamePass):

        #Connect to the daemon of the server to execute cells coordinates
        uri="PYRO:daemonCellsStarter@192.168.56.101:4001" #Identify the Daemon
        call=Pyro4.Proxy(uri)
        x = call.GenerateCells_function() #get free port of the host and send player name


        StartGame_sock = sock #socket as the receiver
        OpponentName = OpponentNamePass
        time.sleep(2) #game start count down

        
        pygame.init()
        colors_players = [(37,7,255),(35,183,253),(48,254,241),(19,79,251),(255,7,230),(255,7,23),(6,254,13)]
        colors_cells = [(80,252,54),(36,244,255),(243,31,46),(4,39,243),(254,6,178),(255,211,7),(216,6,254),(145,255,7),(7,255,182),(255,6,86),(147,7,255)]
        colors_viruses = [(66,254,71)]
        screen_width, screen_height = (1200,800)
        surface = pygame.display.set_mode((1200,800))
        #surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        t_surface = pygame.Surface((95,25),pygame.SRCALPHA) #transparent rect for score
        t_lb_surface = pygame.Surface((200,278),pygame.SRCALPHA) # WIDTH, HEIGHT of transparent rect for leaderboard box
        t_surface.fill((50,50,50,80))
        t_lb_surface.fill((50,50,50,80))
        pygame.display.set_caption("e.frog")
        cell_list = list()
        venus_cell_list = list()
        #enemy_list = list()
        clock = pygame.time.Clock()

        img_dir = path.join(path.dirname(__file__), 'img')

        background_image = pygame.image.load(path.join(img_dir,"bg.jpg")).convert()
        background_image_rect = background_image.get_rect()
        egg_image = pygame.image.load(path.join(img_dir,"egg.png")).convert()
        tadpole_image = pygame.image.load(path.join(img_dir,"tadpole.png")).convert()
        frog_image = pygame.image.load(path.join(img_dir,"frog.png")).convert()

        #START GAME
        gameOver = False
        gameRunning = True
        my_move_x = 0
        my_move_y = 0
        my_mass = 0 # my size to be pass to opponent

        try:
            font = pygame.font.Font(None,20)
            big_font = pygame.font.Font(None,30)
            game_over_font = pygame.font.Font(None,100)
        except:
            print("Font file not found: arial.ttf")
            font = pygame.font.SysFont('arial.ttf',20,True)
            big_font = pygame.font.SysFont('arial.ttf',24,True)


        def drawText(message,pos,color=(255,255,255)):
                surface.blit(font.render(message,1,color),pos)

        def drawText_size(message,pos,color=(255,255,255)):
                surface.blit(font.render(message,20,color),pos)

        def getDistance(pos1,pos2):
            px,py = pos1
            p2x,p2y = pos2
            diffX = math.fabs(px-p2x)
            diffY = math.fabs(py-p2y)

            return ((diffX**2)+(diffY**2))**(0.5)

##### SEND GET StartGame DATA #######

        def send_opponent_data_StartGame(name,sock): # send player data to opponent
                global alias
                global my_move_x
                global my_move_y
                #StartGame_my_sock = sock

                #MyMove = "Helllooooo" #my_move_x,my_move_y
                while 1:
                  try:
                    while 1:
                        my_move_x_str = str(my_move_x)
                        my_move_y_str = str(my_move_y)
                        #OpponentPlayer.send(my_move_x_str.encode('ascii')+b","+ my_move_y_str.encode('ascii'))
                        OpponentPlayer.send(my_move_x_str.encode('ascii'))
                        #StartGame_my_sock.send(my_move_y_str.encode('ascii'))
                        #print("***********************************")
                  except Exception as e:
                    print(e)


        def get_opponent_data_StartGame(name,sock):

                MeAsServer_sock = sock
                print("ME AS SERVER"+str(StartGame_sock))
                global OpponentPlayer
                global opp_move_x_StartGame
                global opp_move_y_StartGame
                global opp_mass_StartGame
                global opp_score_StartGame
                
                (OpponentPlayer,(ip,port)) = MeAsServer_sock.accept() #accept connection from the opponent

                while 1:
                  try:
                    while 1:
                      data = OpponentPlayer.recv(2048) #listen to opponent player movement
                      #OpponentMouseCoordinate = str(data.decode('ascii'))
                      #print("Getting OPPONENT DATA from GameStarted of 2 def "+str(data.decode('ascii')))
                      
                      OpponentMouseCoordinate = str(data.decode('ascii')).strip()
                      opp_move_x_StartGame = float(OpponentMouseCoordinate.split(",")[0])
                      opp_move_y_StartGame = float(OpponentMouseCoordinate.split(",")[1])
                      opp_mass_StartGame = float(OpponentMouseCoordinate.split(",")[2])
                      opp_score_StartGame = OpponentMouseCoordinate.split(",")[3]
                      
                      #opp_move_x = float(int_opp_move_x)
                      #opp_move_y = float(int_opp_move_y)
                      #print ("MCoordinate "+OpponentMouseCoordinate.split(",")[0])
                      #print ("Get X "+int_opp_move_x)
                      #print ("THIS iS RESULT of Get y "+str(opp_move_y_StartGame))
                  except Exception as e:
                    print(e)


        class Camera:
            def __init__(self):
                self.x = 0
                self.y = 0
                self.width = screen_width
                self.height = screen_height
                self.zoom = 0.5

            def centre(self,blobOrPos):
                if(isinstance(blobOrPos,Player)):
                    p = blobOrPos
                    self.x = (p.startX-(p.x*self.zoom))-p.startX+((screen_width/2))
                    self.y = (p.startY-(p.y*self.zoom))-p.startY+((screen_height/2))

                elif(type(blobOrPos) == tuple):
                    self.x,self.y = blobOrPos

        class Player:
            def __init__(self,surface,name = ""):
                self.startX = self.x = random.randint(100,400)
                self.startY = self.y = random.randint(100,400)
                self.mass = 5
                self.surface = surface
                self.color = colors_players[random.randint(0,len(colors_players)-1)]
                self.name = name
                self.pieces = list()
                piece = Piece(surface,(self.x,self.y),self.color,self.mass,self.name)

                global my_move_x
                global my_move_y
                #global opp_move_x_StartGame
                #global opp_move_y_StartGame
                global StartGame_sock

            def update(self):
                  
                  self.move()
                  self.collisionDetection()

            def update_opponent(self):
                global opp_mass_StartGame                
                self.move_opponent(sock)
                #self.mass = opp_mass_StartGame USE COLLISION DETECTION HERE...
                print ('Opp mass from update opponent of StartGame '+str(opp_mass_StartGame))

            def collisionDetection(self):
                global gameOver
                global gameRunning
                
                for cell in cell_list:
                    if(getDistance((cell.x,cell.y),(self.x,self.y)) <= self.mass/2):
                        self.mass+=0.5
                        cell_list.remove(cell)

                for venus_cell in venus_cell_list:
                    if(getDistance((venus_cell.x,venus_cell.y),(self.x,self.y)) <= 15):
                        #self.mass+=0.5
                        gameRunning = False
                        print("COLLIDE WITH Venus")
                        game_over()


            def move(self):
                global my_move_x
                global my_move_y
                #global StartGame_sock
             
                if (gameRunning!=False):

                    dX,dY = pygame.mouse.get_pos()
                    rotation = math.atan2(dY-(float(screen_height)/2),dX-(float(screen_width)/2))*180/math.pi
                    speed = 2-1 #orig is 2-1
                    vx = speed * (90-math.fabs(rotation))/90
                    vy = 0

                    if(rotation < 0):
                        vy = -speed + math.fabs(vx)
                    else:
                        vy = speed - math.fabs(vx)
                    self.x += vx
                    self.y += vy

                    my_move_y = self.y
                    my_move_x = self.x
                    my_mass = self.mass
                    my_score = int(blob.mass*2)
                    my_move_coord = str(my_move_x)+","+str(my_move_y)+","+str(my_mass)+","+str(my_score)
                    #print("StartGame My Score Is "+str(my_score))

                    #try:                    
                    OpponentPlayer.send(my_move_coord.encode('ascii')) # send position to Opponent
                          #print('Should Send...')
                    #except Exception as e:
                          #print(StartGame_sock)
                          #print(e)


            def move_opponent(self,sock):


                  if (gameRunning!=False):

                    self.x = opp_move_x_StartGame
                    self.y = opp_move_y_StartGame
                    #print("THIS IS IT Opp move x"+str(opp_move_x_StartGame))


            def feed(self):
                pass

            def split(self):
                pass

            def draw(self,cam):
                score = int(blob.mass*2)
                size_expand = score + 8 # sprite to cover the circle

                col1 = (255,255,255)
                col2 = (34,34,34)
                col3 = (0,178,0)
                zoom = cam.zoom
                x = cam.x
                y = cam.y
                
                
                if(score >= 100 and score > 50):
                    image = pygame.transform.scale(frog_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col3,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
                elif(score >= 50 and score < 100):
                    image = pygame.transform.scale(tadpole_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col2,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                    
                else:
                    #TEMPLATE - parameter for pygame.draw.circle(Surface, color, pos, radius, width=0)
                    image = pygame.transform.scale(egg_image,(int(self.mass*6),int(self.mass*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col1,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                if(len(self.name) > 0): ## Display name of the player
                	fw, fh = font.size(self.name)
                	drawText(self.name, (self.x*cam.zoom+cam.x-int(fw/2),self.y*cam.zoom+cam.y-int(fh/2)),(50,50,50))


            def drawOpponent(self,cam):
                score_Opponent = int(opp_mass_StartGame*2)
                size_expand = 8 #score + 8 # sprite to cover the circle

                col1 = (255,255,255)
                col2 = (34,34,34)
                col3 = (0,178,0)            
                
                if(score_Opponent >= 100 and score_Opponent > 50):
                    image = pygame.transform.scale(frog_image,(int(opp_mass_StartGame*6),int(opp_mass_StartGame*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col3,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
                elif(score_Opponent >= 50 and score_Opponent < 100):
                    image = pygame.transform.scale(tadpole_image,(int(opp_mass_StartGame*6),int(opp_mass_StartGame*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col2,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                    
                else:
                    #TEMPLATE - parameter for pygame.draw.circle(Surface, color, pos, radius, width=0)
                    image = pygame.transform.scale(egg_image,(int(opp_mass_StartGame*6),int(opp_mass_StartGame*6)))
                    image.set_colorkey((0,0,0))
                    self.surface.blit(image,(int(self.x*cam.zoom+cam.x-size_expand),int(self.y*cam.zoom+cam.y-size_expand)))
                    #pygame.draw.circle(self.surface,col1,(int(self.x*cam.zoom+cam.x),int(self.y*cam.zoom+cam.y)),int(self.mass/2*zoom))
                if(len(self.name) > 0): ## Display name of the player
                	fw, fh = font.size(self.name)
                	drawText(self.name, (self.x*cam.zoom+cam.x-int(fw/2),self.y*cam.zoom+cam.y-int(fh/2)),(50,50,50))



        class Piece:
            def __init__(self,surface,pos,color,mass,name,transition=False):
                self.x,self.y = pos
                self.mass = mass
                self.splitting = transition
                self.surface = surface
                self.name = name

            def draw(self):
                pass

            def update(self):
                if(self.splitting):
                    pass

        class Cell:
            def __init__(self,surface):
                self.x = Cells_x #random.randint(20,1980)
                self.y = Cells_y #random.randint(20,1980)
                self.mass = 10 #2
                self.surface = surface
                self.color = (255,0,0)#(0,140,35)

            def draw(self,cam):
                pygame.draw.circle(self.surface,self.color,(int((self.x*cam.zoom+cam.x)),int(self.y*cam.zoom+cam.y)),int(self.mass*cam.zoom))

        def spawn_cells(numOfCells):
            for i in range(numOfCells):
                cell = Cell(surface)
                cell_list.append(cell)


        class venus_Cell:
            def __init__(self,surface):
                self.x = random.randint(20,1980)
                self.y = random.randint(20,1980)
                self.mass = 15
                self.surface = surface
                self.color = (255,38,255)

            def draw(self,cam):
                pygame.draw.circle(self.surface,self.color,(int((self.x*cam.zoom+cam.x)),int(self.y*cam.zoom+cam.y)),int(self.mass*cam.zoom))

        def spawn_venus_Cells(numOfCells):
            for i in range(numOfCells):
                venus_cell = venus_Cell(surface)
                venus_cell_list.append(venus_cell)

        def draw_grid():
            for i in range(0,2001,20):
                pygame.draw.line(surface,(80,195,216),(0+camera.x,i*camera.zoom+camera.y),(2001*camera.zoom+camera.x,i*camera.zoom+camera.y),1) # x-axis grid
                pygame.draw.line(surface,(80,195,216),(i*camera.zoom+camera.x,0+camera.y),(i*camera.zoom+camera.x,2001*camera.zoom+camera.y),1) # y-axis grid    


        def draw_HUD():

            global score

            w,h = font.size("Score: "+str(int(blob.mass*2))+" ")
            surface.blit(pygame.transform.scale(t_surface,(w,h)),(20,screen_height-30))
            surface.blit(t_lb_surface,(screen_width-160,35))
            
            surface.blit(big_font.render("Leaderboard",0,(255,255,255)),(screen_width-157,20))
            drawText("Opponent: "+ str(opp_score_StartGame),(screen_width-157,20+25))
            drawText("My score: "+ str(int(blob.mass*2)),(screen_width-157,20+25*2))
            #drawText("My Score: "+ str(int(blob.mass*2)),(screen_width-157,20+25*11))

            #score = int(blob.mass*2)
            
            #if(score >= 15):
             #   drawText("10. My Player",(screen_width-157,20+25*10))
            #else:
             #   drawText("10. Player 10",(screen_width-157,20+25*10),(210,0,0))

        def game_over():
            #global gameRunning
            #drawText_size("GAME OVER",(screen_width/2, screen_height/4))
            surface.blit(game_over_font.render("GAME OVER",10,(255,255,255)),(screen_width/2-120, screen_height/2-20))
            pygame.display.flip()
            gameRunning = False
            time.sleep(5)
            pygame.quit()



        # INITIALIZE SETTING
        camera = Camera()
        blob = Player(surface,alias)
        Opponent = Player(surface,OpponentName)
        spawn_cells(2)
        #spawn_Enemy(1)
        spawn_venus_Cells(1) #venus playtrap numbers

        
        # start receiving/sending data from the opponents

        #new_StartGame_send_rt = threading.Thread(target = send_opponent_data_StartGame,args = ("SendThread",sock))
        #new_StartGame_send_rt.start()
        new_StartGame_get_rt = threading.Thread(target = get_opponent_data_StartGame,args = ("RecvThread",sock))
        new_StartGame_get_rt.start()

        
        while(gameRunning!=False):
            clock.tick(60) # 60 frames per second
            for e in pygame.event.get():
                if(e.type == pygame.KEYDOWN):
                    if(e.key == pygame.K_ESCAPE):
                        pygame.quit()
                        quit()
                    if(e.key == pygame.K_SPACE):
                        blob.split()
                    if(e.key == pygame.K_w):
                        blob.feed()
                if(e.type == pygame.QUIT):
                    pygame.quit()
                    quit()
            
            #update section
            blob.update()
            #Enemy.update()
            Opponent.update_opponent()
            camera.zoom = .5 #updated for steady zoom - recommeneded is 5

            #camera.centre(blob2)
            camera.centre(blob)

            #Draw section
            #surface.fill((77,210,255))
            surface.blit(background_image, background_image_rect)
            #surface.fill((0,0,0))
            draw_grid()
            for c in cell_list: #display food cells
                c.draw(camera)
            for v in venus_cell_list: #display venus trap
                v.draw(camera)
            blob.draw(camera)
            Opponent.drawOpponent(camera)
            draw_HUD()

            #display updated graphics
            pygame.display.flip()

####END Frog game Code
 
#Opponent position when I ask connection
opp_move_x_iconnect = 0
opp_move_y_iconnect = 0

#Opponent position when I am the server
opp_move_x_StartGame = 0
opp_move_y_StartGame = 0

#Opponent mass
opp_mass_iconnect = 5
opp_mass_StartGame = 5

#Opponent scoring
opp_score_iconnect = 0
opp_score_StartGame = 0

#Cells position initialise and will be gathered from the server
Cells_x = 0
Cells_y = 0
        
#GUI Begin
free_port = get_free_tcp_port() # free port to be used for new instance of the game

rootwindow = Tk()
rootwindow.title("CLIENT w/ Static Host- Network Chat App")
rootwindow.minsize(width=600, height=500)
rootwindow.maxsize(width=750, height=550)
rootwindow.bind("<Control-Key-x>",exitWindow)
rootwindow.attributes("-topmost", False)

#Create a chat window
Chatarea = Text(rootwindow, bd=0, bg="white", height="8", width="50", font="Arial")
Chatarea.insert(END, "------------------------------- Activities -----------------------------\n")
Chatarea.config(state=DISABLED)

#Create a window for the name of chatters
NameListArea = Listbox(rootwindow, bd=0, bg="white", height="8", width="50", font="Arial")
#displayNamesOfChatter()

#Bind a scrollbar to the Chat window
scrollbar = Scrollbar(rootwindow, command=Chatarea.yview, cursor="arrow")
Chatarea['yscrollcommand'] = scrollbar.set

# Connnect to server
button = Button(rootwindow, text="Connect2Server", command=SendMsgToServer_and_ShowMsgFromMe)
# Create game
button2 = Button(rootwindow, text="Create Game", command=lambda: StartGame("192.168.56.101",free_port))
#button2.bind("<Double-1>",StartGame("192.168.56.101",free_port))

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
button.place(x=320,y=420, width=150)
button2.place(x=120,y=420, width=150)

#connection using TCP
#alias = "Client"
#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
#s.connect(("10.0.5.207",5000))


host="192.168.56.101" ########## IP port of this machine ##########
port = 0
alias = ""
allClients = {} #array for the list of the name of the chatters

server = ("192.168.56.101",5000) ########## IP port of the SERVER ##########
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((host,port))
s.setblocking(0)

print ("Client Chat is running")
print ("------------------------------------------------------------------")

#PYRO4 for RMI
@Pyro4.expose
class StartGame_As_Opponent():
      def ask_connection(self,ip,OpponentNamePass):
        print("this is the ip"+ip)
        OpponentName = OpponentNamePass
        if messagebox.askyesno("Accept","Accept invitation to join game?"):
                  global free_port
                  global host
                  #Start the socket using TCP for private chat - this enables the chatmate to connect
                  new_sMine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                  #new_sMine.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
                  new_sMine.bind((host,free_port)) ########### IP and Port of machine ##########
                  new_sMine.listen(5)
                  
                  threading.Thread(target = StartGame,args = (ip,new_sMine,OpponentName)).start() #run the dialog box to private chat

                  return True, free_port

        else:
                  return False

daemon = Pyro4.Daemon(host=host, port=4000)                # make a Pyro daemon
daemon.register(StartGame_As_Opponent,"daemonGameStarter")   # register the greeting maker as a Pyro object

rt = threading.Thread(target = ShowMsgFromServer,args = ("RecvThread",s))
threading.Thread(target = RunDaemon).start() #run daemon loop
rt.start()

rootwindow.mainloop()
#GUI End
