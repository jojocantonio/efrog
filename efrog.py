import pygame,random,math,time
from pygame.locals import *

pygame.init()
colors_players = [(37,7,255),(35,183,253),(48,254,241),(19,79,251),(255,7,230),(255,7,23),(6,254,13)]
colors_cells = [(80,252,54),(36,244,255),(243,31,46),(4,39,243),(254,6,178),(255,211,7),(216,6,254),(145,255,7),(7,255,182),(255,6,86),(147,7,255)]
colors_viruses = [(66,254,71)]
screen_width, screen_height = (1200,800)
surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
t_surface = pygame.Surface((95,25),pygame.SRCALPHA) #transparent rect for score
t_lb_surface = pygame.Surface((200,278),pygame.SRCALPHA) # WIDTH, HEIGHT of transparent rect for leaderboard box
t_surface.fill((50,50,50,80))
t_lb_surface.fill((50,50,50,80))
pygame.display.set_caption("e.frog")
cell_list = list()
venus_cell_list = list()
clock = pygame.time.Clock()

background_image = pygame.image.load("images/bg.jpg").convert()

#START GAME
gameOver = False
gameRunning = True


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

    def update(self):
        self.move()
        self.collisionDetection()

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
                gameOver = True


    def move(self):
     
        if (gameOver==False):

            dX,dY = pygame.mouse.get_pos()
            rotation = math.atan2(dY-(float(screen_height)/2),dX-(float(screen_width)/2))*180/math.pi
            speed = 2-1 #orig is 5-1
            vx = speed * (90-math.fabs(rotation))/90
            vy = 0

            if(rotation < 0):
                vy = -speed + math.fabs(vx)
            else:
                vy = speed - math.fabs(vx)
            self.x += vx
            self.y += vy
        else:
          game_over()
         

    def feed(self):
        pass

    def split(self):
        pass

    def draw(self,cam):

        score = int(blob.mass*2)

        col1 = (255,255,255)
        col2 = (34,34,34)
        col3 = (0,178,0)
        zoom = cam.zoom
        x = cam.x
        y = cam.y
        
        
        if(score >= 100 and score > 50):
            pygame.draw.circle(self.surface,col3,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
        elif(score >= 50 and score < 100):
            pygame.draw.circle(self.surface,col2,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
        else:
            pygame.draw.circle(self.surface,col1,(int(self.x*cam.zoom+cam.x-8),int(self.y*cam.zoom+cam.y-8)),int(self.mass/2*zoom))
        #pygame.draw.circle(self.surface,col2,(int(self.x*zoom+x),int(self.y*zoom+y)),int(self.mass/5*zoom))

        #egg = pygame.image.load("images/egg.png")
        #self.surface.blit(egg,(int(self.x*cam.zoom+cam.x-60),int(self.y*cam.zoom+cam.y-60)))
        #egg = pygame.transform.scale(egg,(20,20))
#
        #if(len(self.name) > 0):
            #fw, fh = font.size(self.name)
            #drawText(self.name, (self.x*cam.zoom+cam.x-int(fw/2),self.y*cam.zoom+cam.y-int(fh/2)),(50,50,50))

       

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
        self.x = random.randint(20,1980)
        self.y = random.randint(20,1980)
        self.mass = 2
        self.surface = surface
        self.color = (0,140,35)

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
    drawText("1. Player 1",(screen_width-157,20+25))
    drawText("2. Player 2",(screen_width-157,20+25*2))
    drawText("3. Player 3",(screen_width-157,20+25*3))
    drawText("4. Player 4",(screen_width-157,20+25*4))
    drawText("5. Player 5",(screen_width-157,20+25*5))
    drawText("6. Player 6",(screen_width-157,20+25*6))
    drawText("7. Player 7",(screen_width-157,20+25*7))
    drawText("8. Player 8",(screen_width-157,20+25*8))
    drawText("9. Player 9",(screen_width-157,20+25*9))
    #drawText(str(int(blob.mass*2)),(screen_width-157,20+25*11))
    drawText("My Score: " + str(int(blob.mass*2)),(screen_width-157,20+25*11))

    score = int(blob.mass*2)
    
    if(score >= 15):
        drawText("10. My Player",(screen_width-157,20+25*10))
    else:
        drawText("10. Player 10",(screen_width-157,20+25*10),(210,0,0))

def game_over():
    #drawText_size("GAME OVER",(screen_width/2, screen_height/4))
    surface.blit(game_over_font.render("GAME OVER",10,(255,255,255)),(screen_width/2-120, screen_height/2-20))
    pygame.display.flip()
    gameRunning = False



# INITIALIZE SETTING
camera = Camera()
blob = Player(surface,"Player1")
spawn_cells(1000)
spawn_venus_Cells(50) #venus playtrap numbers


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
    
    blob.update()
    camera.zoom = 5 #revised for steady zoom
    camera.centre(blob)
    #surface.fill((77,210,255))
    surface.blit(background_image, [0,0])
    #surface.fill((0,0,0))
    draw_grid()
    for c in cell_list: #display food cells
        c.draw(camera)
    for v in venus_cell_list: #display venus trap
        v.draw(camera)
    blob.draw(camera)
    draw_HUD()
    pygame.display.flip()

    