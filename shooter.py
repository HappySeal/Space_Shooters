import pygame,sys,os,math,time,random

from pygame.locals import *
from pyganim import *
pygame.init()
displayW=650
displayH=650
flags = DOUBLEBUF
gameDisplay = pygame.display.set_mode((displayW,displayH),flags)
gameDisplay.set_alpha(None)
CAPTION = "Space Shooters"
clock = pygame.time.Clock()
RED = (255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
WHITE=(255,255,255)

jetImg = pygame.image.load("sprites/jets/Jet.gif")
laserImg = pygame.image.load("sprites/projectiles/Laser.png")
laserBadImg = pygame.image.load("sprites/projectiles/Laserbad.png")
laserWav = pygame.mixer.Sound("sounds/laser.wav")
backgroundImg = pygame.image.load("sprites/background.png")

explosionsWav = [pygame.mixer.Sound("sounds/explosion1.wav"),
                 pygame.mixer.Sound("sounds/explosion2.wav"),
                 pygame.mixer.Sound("sounds/explosion3.wav")]
contactWav = pygame.mixer.Sound("sounds/contact.wav")
badjetImg = pygame.image.load("sprites/jets/JetBad.png")
explosion = [("sprites/explosions/explosion_0.png",0.1),
              ("sprites/explosions/explosion_1.png",0.1),
              ("sprites/explosions/explosion_2.png",0.1),
              ("sprites/explosions/explosion_3.png",0.1),
              ("sprites/explosions/explosion_4.png",0.1)]

mainJetX = displayH/2 - jetImg.get_rect().center[0]
mainJetY = displayH/2 - jetImg.get_rect().center[1]

vectors = [0,0,0,0]
lasers = []
lasersBad = []
badLasers = []
enemies = []
particles = []
objectsALL = pygame.sprite.Group()
def explosionEff(i):
    explosionsWav[i].set_volume(1.5)
    explosionsWav[i].play()
def contactEff():
    contactWav.set_volume(0.5)
    contactWav.play()
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = image_file
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
    def update(self,display):
        display.blit(self.image,self.rect)
class Particle(pygame.sprite.Sprite):
    def __init__(self,dest,surf,list):
        pygame.sprite.Sprite.__init__(self)
        self.x = dest[0]
        self.y = dest[1]
        self.surf = surf
        self.list = list
        self.animation = PygAnimation(self.list,False)
        self.image = self.animation.getCurrentFrame()
        self.rect = self.image.get_rect(center=dest)
        self.animation.play()
        self.duration = 0.5
        self.startTime = time.time()
        particles.append(self)
    def remove(self):
        self.kill()
    def update(self,display):
        self.animation.blit(self.surf,(self.x,self.y))
        if time.time() - self.startTime >= self.duration:
            self.kill()
            particles.remove(self)
    def draw(self):
        print("no")
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,objects):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.hp = 10
        self.objects = objects
        self.org_enemy = badjetImg
        self.image = self.org_enemy.copy()
        self.rect = self.image.get_rect(center=(x,y))
        self.move = [self.rect.x,self.rect.y]
        self.angleDeg = self.get_angle()
        self.angleRad = math.radians(self.angleDeg)
        self.speed_multiplier = 4
        self.speed = ((self.speed_multiplier*math.sin(self.angleRad)),
                      (self.speed_multiplier*math.cos(self.angleRad)))
        self.laserCooldown = 2
        self.lastShot = time.time()
        enemies.append(self)
    def absCenter(self):
        return self.org_enemy.get_rect().center[0]+int(self.move[0]),self.org_enemy.get_rect().center[1]+int(self.move[1])
    def get_angle(self):
        pos1 = (mainJetY-self.absCenter()[1],mainJetX-self.absCenter()[0])
        deg = 270-math.degrees(math.atan2(*pos1))
        self.image = pygame.transform.rotate(self.org_enemy,deg)
        return 270-math.degrees(math.atan2(*pos1))
    def remove(self,display):
        for laser in lasers:
             if pygame.sprite.collide_rect(self,laser):
                lasers.remove(laser)
                laser.kill()
                if self.hp-1 != 0:
                    contactEff()
                self.hp-=1
                if self.hp <= 0:
                    explosionEff(int(time.time())%3)
                    self.objects.add(Particle(self.absCenter(),gameDisplay,explosion))
                    try:
                        enemies.remove(self)
                    except ValueError:
                        print(" ")
                    self.kill()
    def moveCal(self):
        self.absCenter()
        self.angleDeg = self.get_angle()
        self.angleRad = math.radians(self.angleDeg)
        self.speed = (-(self.speed_multiplier*math.sin(self.angleRad)),
                      -(self.speed_multiplier*math.cos(self.angleRad)))
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
    def update(self,display):
        if time.time() - self.lastShot >= self.laserCooldown:
            objectsALL.add(LaserBad(self.absCenter()[0],self.absCenter()[1],self.angleDeg))
            self.lastShot = time.time()
        self.remove(display)
        self.moveCal()

    def draw(self):
        gameDisplay.blit(self.image,(self.x,self.y))
    def drawLine(self):
        pygame.draw.line(gameDisplay,GREEN,(self.absCenter()[0],self.absCenter()[1]),(mainJetX,mainJetY))
class Laser(pygame.sprite.Sprite):
    def __init__(self,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        lasers.append(self)
        laserWav.set_volume(0.5)
        laserWav.play()
        self.org_laser = laserImg
        self.angle = math.radians(angle+180)
        self.image = pygame.transform.rotate(self.org_laser,angle)
        self.rect = self.image.get_rect(center=(x,y))
        self.move = [self.rect.x,self.rect.y]
        self.speed_multiplier = 15
        self.speed = ((self.speed_multiplier*math.sin(self.angle)),
                      (self.speed_multiplier*math.cos(self.angle)))
    def update(self,display):
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
        self.remove(display)

    def remove(self,display):
        if not self.rect.colliderect(display):
            lasers.remove(self)
            self.kill()
class LaserBad(pygame.sprite.Sprite):
    def __init__(self,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        lasersBad.append(self)
        laserWav.set_volume(0.5)
        laserWav.play()
        self.org_laser = laserBadImg
        self.angle = math.radians(angle+180)
        self.image = pygame.transform.rotate(self.org_laser,angle)
        self.rect = self.image.get_rect(center=(x,y))
        self.move = [self.rect.x,self.rect.y]
        self.speed_multiplier = 10
        self.speed = ((self.speed_multiplier*math.sin(self.angle)),
                      (self.speed_multiplier*math.cos(self.angle)))
    def update(self,display):
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
        self.remove(display)
    def remove(self,display):
        if not self.rect.colliderect(display):
            lasersBad.remove(self)
            self.kill()

class Jet(object):
    def __init__(self,x,y,org_image):
        self.x = x
        self.y = y
        self.org_image = org_image
        self.image = self.org_image.copy()
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.angle = self.get_angle(pygame.mouse.get_pos())
        self.cooldown = 0.000000001
        self.lastTime = time.time()
    def absCenter(self):
        return self.image.get_rect().center[0]+self.x,self.image.get_rect().center[1]+self.y
    def draw(self):
        gameDisplay.blit(self.image,(self.x,self.y))
    def drawLine(self,mouse):
        pygame.draw.line(gameDisplay,RED,(self.absCenter()[0],self.absCenter()[1]),(mouse[0],mouse[1]))
    def get_angle(self,mouse):
        pos1 = (mouse[1]-self.absCenter()[1],mouse[0]-self.absCenter()[0])
        self.angle = 270-math.degrees(math.atan2(*pos1))
        self.image = pygame.transform.rotate(self.org_image,self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    def moveCal(self,speed):
        self.get_angle(pygame.mouse.get_pos())
        vectorsCal = (vectors[1]-vectors[3],vectors[0]-vectors[2])
        vectorDeg = 180-math.degrees(math.atan2(*vectorsCal))
        vectorRad = math.radians(vectorDeg)
        if vectorsCal != (0,0):
            self.move(speed*math.sin(vectorRad),speed*math.cos(vectorRad))
    def move(self,speedx,speedy):
        self.x+= speedx
        self.y += speedy
    def get_event(self,event,objects):
        if pygame.mouse.get_pressed()[0]:
            try:
                while time.time() - self.lastTime >= self.cooldown:
                    objects.add(Laser(self.absCenter()[0],self.absCenter()[1],self.angle))
                    self.lastTime = time.time()
            except AttributeError:
                pass
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            objects.add(Enemy(64,64,objects))
class Game(object):
    def __init__(self,displayW,displayH):
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.dw = displayW
        self.dh = displayH
        self.objects = pygame.sprite.Group()
        self.Main()

    def text_objects(self,text,font):
        textSurface = font.render(text,True,WHITE)
        return textSurface,textSurface.get_rect()
    def text_display(self,text,x,y):
        normalText = pygame.font.Font("font.ttf",10)
        TextSurf , TextRect = self.text_objects(text,normalText)
        TextRect.center = (x,y)
        gameDisplay.blit(TextSurf,TextRect)
        pygame.display.update()
    def update(self):
        self.objects.update(self.screen_rect)
    def Main(self):
        global mainJetY,mainJetX
        error = False
        jet = Jet(mainJetX,mainJetY,jetImg)
        jet.draw()



        while not error:
            objectsALL = self.objects
            gameDisplay.fill(BLACK)
            bg = Background(backgroundImg,(0,0))
            gameDisplay.blit(bg.image,bg.rect)
            #print(len(enemies),len(particles))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        vectors[0] = 1
                    elif event.key == pygame.K_s:
                        vectors[2] = 1
                    elif event.key == pygame.K_d:
                        vectors[1] = 1
                    elif event.key == pygame.K_a:
                        vectors[3] = 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        vectors[0] = 0
                    elif event.key == pygame.K_s:
                        vectors[2] = 0
                    elif event.key == pygame.K_d:
                        vectors[1] = 0
                    elif event.key == pygame.K_a:
                        vectors[3] = 0
                jet.get_event(event,self.objects)
            jet.moveCal(10)
            jet.draw()
            mainJetX = jet.x + jetImg.get_rect().center[0]
            mainJetY = jet.y + jetImg.get_rect().center[1]
            #jet.drawLine(pygame.mouse.get_pos())

            self.update()
            self.objects.draw(self.screen)
            caption = "{} - FPS :{:.2f}".format(CAPTION,clock.get_fps())
            pygame.display.set_caption(caption)
            pygame.display.update()
            clock.tick(60)

if __name__ == '__main__':
    Game(displayH,displayW)