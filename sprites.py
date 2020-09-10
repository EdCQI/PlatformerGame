import pygame as pg, random, os
from config import *
from pygame.locals import *

vec = pg.math.Vector2

class Spritesheet: #utility for loading and parsing (break into components) spritesheets
    def __init__(self,filename):
        #no usamos scale para hacer spritesheet más chica porque cambian ya no nos servirían
        #los valores del archivo xml que viene por default
        self.spritesheet = pg.image.load(filename).convert()
    def get_image(self,x,y,w,h): #tomar una imagen de una spritesheet
        #sería más práctico leer el xml de spritesheet, pero lo haremos manual
        image = pg.Surface((w,h))
        image.blit(self.spritesheet,(0,0),(x,y,w,h))#última tupla toma sólo una parte de toda la img
        image = pg.transform.scale(image,(w//2,h//2)) # la mitad porq está muy grande
        return image
class Player(pg.sprite.Sprite):
    def __init__(self,game):
        self.groups = game.all_sprites
        self._layer = PLAYER_LAYER #en qué layer está para dibujarlo en orden. Debe ir antes de sprite.__init__()
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game #referencia a clase juego
        self.load_images() #todas las imgs para animaciones
        self.image = self.stand_imgs[0]
        """self.image = pg.Surface((50,80)) #ancho,alto
        self.image.fill(YELLOW)"""
        self.rect = self.image.get_rect()
        self.pos = vec(ANCHO/2, ALTO/2)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rect.center = (ANCHO/2,ALTO/2)
        self.walking = False
        self.jumping = False
        self.flying = False
        self.frame = 0
        self.last_update = 0 #for tracking when to change frame
    def load_images(self):
        self.stand_imgs = [self.game.spritesheet.get_image(614,1063,120,191), #información en archivo .xml
                            self.game.spritesheet.get_image(690,406,120,201)]
        self.walk_r_imgs = [self.game.spritesheet.get_image(678,860,120,201),
                            self.game.spritesheet.get_image(692,1458,120,207)]
        self.walk_l_imgs = []
        for i in self.walk_r_imgs:
            self.walk_l_imgs.append(pg.transform.flip(i,True,False)) #flip horizontally and vertically-->True,False
        self.jump_imgs = [self.game.spritesheet.get_image(382,763,150,181)]
        for img in self.stand_imgs + self.walk_r_imgs + self.walk_l_imgs + self.jump_imgs:
            img = img.set_colorkey(BLACK)

    def update(self):
        #acc.x debe ser 0 a menos que presionemos tecla
        self.acc = vec(0,GRAVITY) #comentando esto se vuelve resorte
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC #también puede usarse acc[0]
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        #equations of motion
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5*self.acc
        if abs(self.vel.x) < 0.5: #para q no siga disminuyendo sin llegar a cero, porque afecta bandera self.walking
            self.vel.x = 0
        #animation
        self.animate()
        #limit movements
        if self.pos.x < 0 - self.rect.width/2:
            self.pos.x = ANCHO + self.rect.width/2 
        if self.pos.x > ANCHO + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        """if self.pos.x < 0 + self.rect.width/2:
            self.pos.x = 0 + self.rect.width/2
        elif ANCHO - self.rect.width/2 < self.pos.x:
            self.pos.x = ANCHO - self.rect.width/2"""
        self.rect.midbottom = self.pos
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0: self.walking = True
        else: self.walking = False
        if self.walking:
            if now - self.last_update > 100:
                self.last_update = now
                self.frame = (self.frame + 1) % len(self.walk_r_imgs) #podría ser self.walk_l_imgs
                bottom = self.rect.bottom
                if self.vel.x > 0: #walking to the right
                    self.image = self.walk_r_imgs[self.frame]
                else:
                    self.image = self.walk_l_imgs[self.frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            if now - self.last_update > 200: #500 miliseg
                self.last_update = now
                bottom = self.rect.bottom #guardo bottom anterior para que la sig fig tenga el mismo
                self.frame = (self.frame + 1) % len(self.stand_imgs)
                self.image = self.stand_imgs[self.frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom 
        #después de saber qué image tendrá (por eso se hace en "animate"), declaramos mask
        #creamos mask para pixel perfect collision; usar SELF.mask para que lo encuentre rápido la función collide
        #se puede crear mask de diferentes formas; la más sencilla es usando superficie:
        self.mask = pg.mask.from_surface(self.image) #masks ignoran background de image
    def jump(self):
        if self.flying == False: #si no está volando sólo brinca si está sobre plataforma
            #checo si un pixel abajo hay una plataforma (es decir, si estoy parado sobre una)
            self.rect.bottom += 1 + 1 #más uno para mayor confianza
            hits = pg.sprite.spritecollide(self,self.game.platforms,False)
            self.rect.bottom -= 1 + 1 
            if hits and not self.jumping:
                self.vel.y = -PLAYER_JUMP #imprimo velocidad inicial
                self.jumping = True
                self.game.jump_sound.play()
        else:
            self.vel.y = -PLAYER_JUMP
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -PLAYER_JUMP/8:
                self.vel.y = -PLAYER_JUMP/8

class Platform(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.platforms
        self._layer = PLAT_LAYER
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.imgs = [self.game.spritesheet.get_image(0,960,380,94),
                    self.game.spritesheet.get_image(0,864,380,94),
                    self.game.spritesheet.get_image(0,288,380,94),
                    self.game.spritesheet.get_image(0,0,380,94)]
        self.image = random.choice(self.imgs)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        if random.randrange(0,100) < PCT_POWERUPS:
            Pow(self.game,self)

class Pow(pg.sprite.Sprite):
    def __init__(self,game,plat):
        self.groups = game.all_sprites, game.powerups
        self._layer = POW_LAYER
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['boost'])
        #self.imgs = [self.game.spritesheet.get_image(0,960,380,94),
        #            self.game.spritesheet.get_image(0,864,380,94)]
        self.image = self.game.spritesheet.get_image(820,1805,71,70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top -10
    def update(self):
        self.rect.bottom = self.plat.rect.top - 10
        if not self.game.platforms.has(self.plat): #si existe la plataforma en el grupo
            self.kill() #delete self from any sprite group

class Mob(pg.sprite.Sprite):
    def __init__(self,game):
        self.groups = game.all_sprites, game.mobs
        self._layer = MOB_LAYER
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566,510,122,139)
        self.image_down = self.game.spritesheet.get_image(568,1534,122,135)
        self.image_up.set_colorkey(BLACK)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100,ANCHO+100])
        self.vx = random.randrange(1,5)
        if self.rect.centerx > ANCHO: #si sale desde la derecha,su vel es negativa
            self.vx *= -1
        self.rect.y = random.randrange(0,ALTO/2) #mitad sup de pantalla
        self.vy = 0
        self.dy = 0.5 #para dar aceleración arriba-abajo suave
    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1 
        center = self.rect.center #rastrear dónde está porq ambos sprites son de tamño distinto; para evitar problemas
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.mask = pg.mask.from_surface(self.image) #mask
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > ANCHO+100 or self.rect.right < -100:
            self.kill()
         
class Nube(pg.sprite.Sprite):
    def __init__(self,game):
        self.groups = game.all_sprites, game.nubes
        self._layer = NUBE_LAYER
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        img_dir = os.path.join(self.game.dir,'img')
        self.imgs = []
        for i in range(1,4): #cloud1, cloud2, cloud3
            nube = os.path.join(img_dir,"cloud{}.png".format(i))
            self.imgs.append(pg.image.load(nube).convert())
        self.image = random.choice(self.imgs)
        self.image = pg.transform.scale(self.image, (random.randrange(20,150),random.randrange(20,80)) )
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0,ANCHO-self.rect.width)
        self.rect.y = random.randrange(-500,-50)
    def update(self):
        if self.rect.top > ALTO + 10:
            self.kill()
        
        
