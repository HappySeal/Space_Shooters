import pygame,sys,os,math
pygame.init()
displayW=650
displayH=650
gameDisplay = pygame.display.set_mode((displayW,displayH))
CAPTION = "Space Shooters"
clock = pygame.time.Clock()
RED = (255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
WHITE=(255,255,255)
jetImg = pygame.image.load("Jet.gif")
laserImg = pygame.image.load("Laser.png")
laserWav = pygame.mixer.Sound("laser.wav")

class Laser(pygame.sprite.Sprite):
    def __init__(self,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        laserWav.set_volume(0.5)
        laserWav.play()
        self.org_laser = laserImg
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
            self.kill()

class Jet(object):
    def __init__(self,x,y,org_image):
        self.x = x
        self.y = y
        self.org_image = org_image
        self.image = self.org_image.copy()
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.angle = self.get_angle(pygame.mouse.get_pos())
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
    def move(self,speedx,speedy):
        self.get_angle(pygame.mouse.get_pos())
        self.x+= speedx
        self.y += speedy
    def get_event(self,event,objects):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            objects.add(Laser(self.absCenter()[0],self.absCenter()[1],self.angle))
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
        error = False
        jet = Jet(displayH/2 - jetImg.get_rect().center[0],displayW/2 - jetImg.get_rect().center[0],jetImg)
        jet.draw()
        speedx = 0
        speedy =0
        while not error:
            gameDisplay.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        speedy = -5
                    elif event.key == pygame.K_s:
                        speedy = 5
                    elif event.key == pygame.K_d:
                        speedx = 5
                    elif event.key == pygame.K_a:
                        speedx = -5
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        speedy = 0
                    elif event.key == pygame.K_s:
                        speedy = 0
                    elif event.key == pygame.K_d:
                        speedx = 0
                    elif event.key == pygame.K_a:
                        speedx = 0
                jet.get_event(event,self.objects)
            jet.move(speedx,speedy)
            jet.draw()
            #jet.drawLine(pygame.mouse.get_pos())
            self.update()
            self.objects.draw(self.screen)
            caption = "{} - FPS :{:.2f}".format(CAPTION,clock.get_fps())
            pygame.display.set_caption(caption)
            pygame.display.update()
            clock.tick(60)

if __name__ == '__main__':
    Game(displayH,displayW)