import pygame, sys, random, math
import os #setup the folder and point to the right place when loading images
from pygame.locals import *

from config import *
#from sprites import *

#set up assets (term form art and sound for game)
game_folder = os.path.dirname(__file__) #get current path
img_folder = os.path.join(game_folder,"img") #concatenates various path components with exactly one directory separator
sound_folder = os.path.join(game_folder,"sound")
font_name = pygame.font.match_font("arial")
R, G, B = 0, 255, 0 #inicializa colores del shield

def draw_text(surf,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text, True, (200,200,200))
    #                               alias(pixelado)/anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y) #where in surface will text be
    surf.blit(text_surface,text_rect)
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)
def draw_shield(surf,x,y,player):
    global R,G,B

    if player.shield < 0: #para que no llene de color raro
        player.shield, R, G = 0, 255, 0
    ancho_barra, alto_barra = 100, 10
    fill = (player.shield/player.max_shield)*ancho_barra
    out_rect = pygame.Rect(x,y,ancho_barra,alto_barra)
    fill_rect = pygame.Rect(x,y,fill,alto_barra)
    pygame.draw.rect(surf,(int(R),int(G),B),fill_rect)
    pygame.draw.rect(surf,(255,255,255),out_rect,3)
def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        im_rect = img.get_rect()
        im_rect.x = x + im_rect.width*i
        im_rect.y = y
        surf.blit(img,im_rect)
def show_go_screen():
    screen.blit(bg,bg_rect)
    draw_text(screen,"ARDILLA ASESINA!",50,ANCHO/2,ALTO/4)
    draw_text(screen,"Te mueves con flechas y disparas con SPACE",30,ANCHO/2,ALTO/2)
    draw_text(screen,"Pulsa una tecla para empezar!",20,ANCHO/2,ALTO*3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #running, game_over = False, False
                #sys.exit()
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

class Player(pygame.sprite.Sprite): #sprite for player
    def __init__(self):
        global imagenes, ANCHO, ALTO

        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(os.path.join(img_folder,"ardillaLoca.png")).convert() #slow game if not convert
        self.image = pygame.transform.scale(imagenes["ardillilla.png"],(108,144)) #img ardillaLoca es 108x144
        #self.image.set_colorkey((255,255,255)) #which color to ignore or make transparent
        self.rect = self.image.get_rect()
        #self.radio = math.sqrt( (self.rect.width/2)**2 + (self.rect.height/2)**2 ) #90.0/radius 72.0
        self.radius = int(self.rect.width/2)
        #pygame.draw.circle(self.image,(0,255,255),self.rect.center,45)
        self.rect.bottom = ALTO
        self.y_speed = 5
        self.max_shield = 100
        self.shield = self.max_shield
        self.lives = 3
        self.hidden = False #no muestro sprite cuando muere
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.powerup_timer = pygame.time.get_ticks()

    def update(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] and self.rect.left >= 0:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT] and self.rect.right <= ANCHO:
            self.speedx = 5
        else:
            self.speedx = 0
        self.rect.x += self.speedx
        #unhide if hiden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.bottom = ALTO
        #timeout for powerups
        if self.power >=2 and pygame.time.get_ticks()-self.powerup_timer > 4000:
            self.power -= 1
            self.powerup_timer = pygame.time.get_ticks()

    def shoot(self):
        if self.power == 1:
            bullet = Bullet(self.rect.centerx,self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
        elif self.power >= 2:
            bullet1 = Bullet(self.rect.left,self.rect.centery)
            bullet2 = Bullet(self.rect.right,self.rect.centery)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            bullets.add(bullet1)
            bullets.add(bullet2)
            shoot_sound.play()
    def hide(self): #hide player temporarily when dead
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (int(ANCHO/2),ALTO*2) #lo escondo fuera de la pantalla
    def powerup(self):
        self.power += 1
        self.powerup_timer = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        global imagenes, ANCHO, ALTO

        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(os.path.join(img_folder,"meteor.png")).convert() #slow game if not convert
        self.image_orig = random.choice(meteor_imgs)
        self.image_orig.set_colorkey((0,0,0)) #which color to ignore or make transparent
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        #self.radio = math.sqrt( (self.rect.width/2)**2 + (self.rect.height/2)**2 )
        self.radius = int(self.rect.width*0.8/2)
        #pygame.draw.circle(self.image,(0,255,255),self.rect.center,20)
        self.rect.x = random.randrange(0,ANCHO-self.rect.width)
        self.rect.y = random.randrange(-160,-100) #arrancan desde arriba de la pantalla
        self.speedy = random.randrange(1,8)
        self.speedx = random.randrange(-3,3)
        self.rot = 0
        self.rotspeed = random.randrange(-15,15)
        self.last_update = pygame.time.get_ticks()
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rotspeed)%360
            new_image = pygame.transform.rotate(self.image_orig,self.rot) 
            ##cada rotación hace perder info, por eso se usa la img original
            #lo siguiente es para centrar la imagen al rotarla, pues cada rotación cambia el rect.center
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy 
        self.rect.x += self.speedx
        if self.rect.top > ALTO or self.rect.right < 0 or self.rect.left > ANCHO:
            self.rect.x = random.randrange(0,ANCHO-self.rect.width)
            self.rect.y = random.randrange(-100,-40) #arrancan desde arriba de la pantalla
            self.speedy = random.randrange(1,8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        global imagenes

        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(os.path.join(img_folder,"laser.png")).convert()
        self.image = imagenes["laser.png"]
        #self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill() #removes sprites from groups it maybe in 

class Pow(pygame.sprite.Sprite):
    def __init__(self,center):
        global imagenes

        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["cheetos.png","pizza.png"])
        self.image = imagenes[self.type]
        #self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 8
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > ALTO:
            self.kill() #removes sprites from groups it maybe in 


class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size): #le envío centro de sprite que explota y tipo de explosión(grande,small,player)
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = exp_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 #empiezo con mprimer imagen
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 #how fast the explosion appears
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(exp_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = exp_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


#every time you finish drawing, you gotta flip the screen
#flip = double buffering (pantalla atrás)
#after drawing everything, flip the display
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((ANCHO,ALTO))
pygame.display.set_caption(TITULO)
clock = pygame.time.Clock()
#LOAD GRAPHICS
nom_imgs = ["ardillilla.png","laser.png","purple.png","pizza.png","cheetos.png"] 
bg_colors = [(255,255,255),(0,0,0),(0,0,0),(0,0,0),(255,255,255)]
imagenes = {}
for j,i in enumerate(nom_imgs,0):
    imagenes[i] = pygame.image.load(os.path.join(img_folder,i)).convert()
    imagenes[i].set_colorkey(bg_colors[j])
para_mini_rect = imagenes["ardillilla.png"].get_rect() #adquero rect para saber tamaño original y escalar img mini
imagenes["mini_ardilla"] = pygame.transform.scale(imagenes["ardillilla.png"],(int(para_mini_rect.width/6),int(para_mini_rect.height/6)))
#pwup_imgs = dict(("pizza","cheetos"),())
nom_meteors = ["meteor1.png","meteor2.png","meteor3.png","meteor4.png",
                "meteor5.png","meteor6.png","meteor7.png","meteor8.png"]
meteor_imgs = []
for i in nom_meteors:
    meteor_imgs.append(pygame.image.load(os.path.join(img_folder,i)).convert())
exp_anim = {}
exp_anim["g"] = [] #explosión grande
exp_anim["s"] = [] #explosión small
exp_anim["player"] = [] #explosión del player
for i in range(9):
    filename = "regularExplosion0{}.png".format(i)
    img = pygame.image.load(os.path.join(img_folder,filename)).convert()
    img.set_colorkey((0,0,0))
    img_g = pygame.transform.scale(img,(75,75))
    exp_anim["g"].append(img_g)
    img_s = pygame.transform.scale(img,(30,30))
    exp_anim["s"].append(img_s)
    #explosiones player
    filename = "sonicExplosion0{}.png".format(i)
    img = pygame.image.load(os.path.join(img_folder,filename)).convert()
    img.set_colorkey((0,0,0))
    exp_anim["player"].append(img)
bg = pygame.transform.scale(imagenes["purple.png"],(ANCHO,ALTO))
bg_rect = bg.get_rect()
#LOAD SOUND
shoot_sound = pygame.mixer.Sound(os.path.join(sound_folder,"laser_sound.wav"))
nom_exp = ("Explosion.wav","Explosion2.wav","power.wav","shield.wav","dieExplosion.wav")
exp_sound = []
for s in nom_exp:
    exp_sound.append(pygame.mixer.Sound(os.path.join(sound_folder,s)))
exp_sound = dict(zip(nom_exp,exp_sound))
#pygame.mixer.music.load(os.path.join(sound_folder,"NAME!!!.ogg o wav"))
#pygame.mixer.music.set_volume(0.5)

#Game loop
i = 1
#pygame.mixer.music.play(loops=-1) #loops keeps music playing
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        #Define sprites group
        all_sprites = pygame.sprite.Group() #collection of sprites
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        #creo objetos
        player = Player()
        all_sprites.add(player)
        for i in range(8): #creo y adhiero mobs
            newmob()
        puntos = 0
    clock.tick(FPS) #loop at the right speed
    #eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    
    #update
    all_sprites.update()
    #collisions??
    #axis-aligned/circular/pixel perfect bounding box
    #axis-->rectangles overlap is faster,pixel perfect much slower
    hits1 = pygame.sprite.groupcollide(mobs,bullets,True,True) #last True KILLS sprite(deletes it)
    for h in hits1: #hit mobs deleted will be replaced
        newmob()
        puntos += (60-int(h.radius*0.3)) #suma puntos según tamaño de mob 
        random.choice( [ exp_sound["Explosion.wav"],exp_sound["Explosion2.wav"] ] ).play() #alguno entre los dos primeros son sonidos de exp, el otro es dieExplosion de jugador
        expl = Explosion(h.rect.center,"g")
        all_sprites.add(expl)
        if random.random() > 0.85: #rand devuelve num entre 0 y 1
            pow = Pow(h.rect.center)
            powerups.add(pow)
            all_sprites.add(pow)
    hits2 = pygame.sprite.spritecollide(player,mobs,True,pygame.sprite.collide_circle) #args-->which sprite against which group
    #returns a list of colliding objects           should colliding mobs disappear
    for h in hits2:
        newmob()
        player.shield -= h.radius 
        R = 0 + (255/player.max_shield)*((player.max_shield-player.shield)) #color de la barra del shield
        G = 255 - (255/player.max_shield)*((player.max_shield-player.shield)) 
        expl = Explosion(h.rect.center,"s")
        all_sprites.add(expl)
        #exp_sound[0].play()
        if player.shield <= 0:
            death_exp = Explosion(player.rect.center,"player")
            exp_sound["dieExplosion.wav"].play() #el último es dieExplosion
            all_sprites.add(death_exp)
            player.lives -= 1 
            player.shield = player.max_shield
            R, G = 0, 255
            player.hide()
        print(i,player.radius,player.rect.width/2,int(R),int(G))
        i += 1
    #check if player hits powerup
    hits3 = pygame.sprite.spritecollide(player,powerups,True)
    for h in hits3:
        if h.type == "pizza.png":
            player.shield += random.randrange(10,30)
            if player.shield > 100:
                player.shield = 100
            R = 0 + (255/player.max_shield)*((player.max_shield-player.shield))
            G = 255 - (255/player.max_shield)*((player.max_shield-player.shield))
            exp_sound["shield.wav"].play() 
        elif h.type == "cheetos.png":
            player.powerup()
            exp_sound["power.wav"].play()

    #if player died and explosion finished playing:
    if player.lives == 0 and not death_exp.alive(): #alive()--> boolean wheter sprite exists in any group
        game_over = True
    #draw/render AND flip
    screen.fill((0,0,0)) #amarillo
    screen.blit(bg,bg_rect)
    all_sprites.draw(screen)
    draw_text(screen,"PUNTOS:"+str(puntos),20,ANCHO/2-50,10)
    if player.lives: draw_shield(screen,5,5,player)
    draw_lives(screen,ANCHO/2+50,10,player.lives,imagenes["mini_ardilla"])
    pygame.display.flip()










"""
def load_data(self):
    pass
def new(self):
    #inicializa todas variables y hace setup para nuevo juego
    self.all_sprites = pygame.sprite.Group()
    self.player = Player(self,0,0)
def run(self):
    self.playing = True #False to end game
    while self.playing:
        self.dt = self.clock.tick(FPS)/1000
        self.events()
        self.update()
        self.draw()
def quit(self):
    pygame.quit()
    sys.exit()
def update(self): #update portion of game loop
    self.all_sprites.update()
def draw_grid(self):
    for x in range(0,ANCHO,TILESIZE):
        pygame.draw.line(self.screen, (0,100,255), (x,0),(x,ALTO))
    for y in range(0,ALTO,TILESIZE):
        pygame.draw.line(self.screen, (0,100,255), (y,0),(ANCHO,y))
def draw(self):
    self.screen.fill(col_fondo)
    self.draw_grid()
    self.all_sprites.draw(self.screen)
    pygame.display.flip()
def events(self):
    for events in pygame.events.get():
        if event.type == pygame.QUIT:
            self.quit() """