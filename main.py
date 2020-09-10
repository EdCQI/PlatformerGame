""" 
 - Revisar colisión entre player y más de una platform-->player.pos.x entre límites de plats
pasar de una plat a otra sobrepuesta
 - Modificar eventos en update de game-->update de player también checa eventos!
"""
import pygame as pg, sys
import random, math
import os #setup the folder and point to the right place when loading images

from pygame.locals import *
from config import *
from sprites import * 

class Game():
    def __init__(self):
        #config iniciales, iniciar el programa
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((ANCHO,ALTO))
        pg.display.set_caption(TITULO)
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(FONT_NAME) #el nombre que más se parezca 
        self.running = True #controla el loop principal
        self.load_data()
    def load_data(self):
        self.dir = os.path.dirname(__file__) #location of actual folder
        img_dir = os.path.join(self.dir,'img')
        self.sound_dir = os.path.join(self.dir,'sound') #le pongo self porque necesito acceder a él desde otros métodos
        #leo el puntaje más alto guardado
        with open(os.path.join(self.dir,SCORE_FILE),'r') as txt:
            try:
                self.maxscore = int(txt.read())
            except:
                self.maxscore = 0
        self.spritesheet = Spritesheet(os.path.join(img_dir,SPRITESHEET_FILE))
        self.jump_sound = pg.mixer.Sound(os.path.join(self.sound_dir,'Jump.wav'))
        self.powerup_sound = pg.mixer.Sound(os.path.join(self.sound_dir,'Powerup.wav'))
        #only one stream music at once! stream--> va leyendo y tocando en vez de cargar toda la pieza en memoria
        #es mejor usar .ogg en vez de wav o mp3 porque está comprimido
        #no se puede cargar toda la música de antemano;sólo cuando se va a usar

    def new(self):
        #reiniciar config iniciales para juego nuevo
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates() 
        #LayeredUpdates es Group diferente que permite dibujar sprites según jerarquía (dibujarlos en orden)-->quién hasta arriba, quién después,etc
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.nubes = pg.sprite.Group()
        self.player = Player(self)
        #self.all_sprites.add(self.player)#NO adherimos player porq se adhiere solo, al __init__
        for plat in PLATFORM_LIST: #crea las plataformas de inicio            
            Platform(self,*plat) #no se asigna a variable porque se adhiere automaticamente a los grupos en __init__
            #self.platforms.add(p) #se adhiere en el __init__
            #self.all_sprites.add(p)
        for i in range(4): #crea las nubes de inicio
            c = Nube(self) 
            c.rect.y += ALTO/2 #las recorro porque se crean arriba de la pantalla siempre
        self.mob_timer = 0 #inicializo timer para crear mobs cada x tiempo
        """self.p1 = Platform(0,ALTO-35,ANCHO,35) 
        self.p2 = Platform(ANCHO/2-40,ALTO-205,100,35)
        self.platforms.add(self.p1)
        self.platforms.add(self.p2)
        self.all_sprites.add(p1)
        self.all_sprites.add(p2)"""
        self.run()
    def run(self):  #game loop
        pg.mixer.music.load(os.path.join(self.sound_dir,'HappyTune.ogg'))
        pg.mixer.music.play(loops=-1) #loops the music when it ends
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500) #500 ms un fade de música cuando sea game over
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP: #para considerar qué tanto presiono tecla y saltar más/menos
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()
            """if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    player.shoot()"""
    def update(self):
        self.all_sprites.update() #todos los sprites tienen método "update"
        #poner un mob o no??
        now = pg.time.get_ticks()
        if now - self.mob_timer > MOB_FREQ + random.choice([0,-3000,-2000,-1000,1000,2000,3000]):
            self.mob_timer = now
            mob = Mob(self)
        #colisiones con mobs
        mob_hits = pg.sprite.spritecollide(self.player,self.mobs,False,pg.sprite.collide_mask)
        """si hay demasiados sprites con masks, el programa se puede enlentecer, así que si habrá varios y quiero
        usar masks, podría: 
        1) checar si hay colisiones ordinarias (con rectángulos)
        2) si las hubo, ahora sí preguntar por colisión mediante masks. Esto agilizará el programa, pues no estaría
        todo el tiempo checando si hubo colisiones con masks"""
        if mob_hits:
            self.playing = False #bandera controla loop de "game.new"; al salir del loop se ejecuta función game over
        #colisiones con platforms
        if 0 < self.player.vel.y: #SOLO si está cayendo, chocará con plats
            hits = pg.sprite.spritecollide(self.player,self.platforms,False)
            #hits es lista de objetos con los que colisionó, pero no están en orden cronológico!!
            #el primer objeto no es necesariamente el primero con el que colisionó
            if hits: 
                """los_bottoms = [h.rect.centery for h in hits]
                lowest = hits[ max(range(len(los_bottoms)), key=los_bottoms.__getitem__) ] #devuelve índice donde está el mayor"""
                lowest = hits[0]
                for h in hits:
                    if h.rect.bottom > lowest.rect.bottom:
                        lowest = h
                #print("player.pos.x: {}, lowestRectLeftRight: {} {}, player.pos.y: {}".format(self.player.pos.x,lowest.rect.left,lowest.rect.right,self.player.pos.y))
                if True:#lowest.rect.left <= self.player.pos.x <= lowest.rect.right:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top + 1 #más uno para que no parpadee la imagen por estar cayendo siempre
                        self.player.vel.y = 0 #no acc porq acc.y siempre = GRAVITY!
                        self.player.jumping = False
        #scroll the window
        if self.player.rect.y <= ALTO/2: #mitad superior de pantalla
            self.player.pos.y += max(abs(self.player.vel.y),2)
            for m in self.mobs:
                m.rect.y += max(abs(self.player.vel.y),2) 
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y),2) 
                if plat.rect.top > ALTO + 30: #+30 para q aún sea posible caer sobre ella 
                    plat.kill()
                    self.score += 10
            #crear nubes aleatoriamente
            if random.randrange(0,100) < 10:
                Nube(self)
            for n in self.nubes: #movemos nubes junto con pantalla (scroll nubes)
                n.rect.y += max(abs(self.player.vel.y / random.randrange(2,4)), 2) #random para moverlas a menor velocidad
        #colisiones con powerups
        pow_hits = pg.sprite.spritecollide(self.player,self.powerups,True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False #para evitar el jump_cut 
                self.powerup_sound.play()
        #deslizar pantalla cuando cae jugador
        if self.player.rect.bottom > ALTO:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y,10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        #GAME OVER cuando ya no hay platforms porque se deslizaron porque cayó jugador
        if len(self.platforms) == 0:
            self.playing = False #bandera controla loop de "game.new"; al salir de él se ejcuta función game over
        #crear nuevas platforms
        while len(self.platforms) < 6:
            #w = random.randrange(90,250)
            #h = random.randrange(15,35)
            x = random.randrange(0,ANCHO-100)
            y = random.randrange(-70,-20)
            Platform(self,x,y) #no es necesario asignarlo a variable
            #self.platforms.add(p) #se adhiere a grupos en __init__
            #self.all_sprites.add(p) #se adhiere automatic a grupos
                
    def draw(self):
        self.screen.fill(L_BLUE)
        self.all_sprites.draw(self.screen)
        #la línea de abajo ya no es necesaria porque usamos LayeredUpdates en all_sprites Group
        #self.screen.blit(self.player.image,self.player.rect) #nos aseguramos de dibujar al player hasta el frente
        self.draw_text(str(self.score),20,BLACK,ANCHO/2,10)
        #self.screen.blit(bg,bg_rect)
        pg.display.flip()
    def draw_text(self,text,size,color,x,y):
        font = pg.font.Font(self.font_name,size)
        text_surf = font.render(text,True,color) #True antialiasing
        text_rect = text_surf.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surf,text_rect)
    def start_screen(self):
        self.screen.fill(L_BLUE)
        self.draw_text(TITULO,30,BLACK,ANCHO/2,200)
        self.draw_text("Salta con SPACE y muévete con flechas",20,BLACK,ANCHO/2,ALTO/2)
        self.draw_text("Oprime una tecla...",25,PURPLE,ANCHO/2,ALTO*3/4)
        self.draw_text("Puntaje máximo alcanzado: "+str(self.maxscore),25,PURPLE,ANCHO/2,ALTO*3/4+50)
        pg.display.flip()
        pg.mixer.music.load(os.path.join(self.sound_dir,'Forest_Ambient.ogg'))
        pg.mixer.music.play(loops=-1)
        self.wait_key()
        pg.mixer.music.fadeout(500)


    def gameOver_screen(self):
        if not self.running: #si oprimí tache(exit) ya no se muestra esta screen
            return #break out of function
        self.screen.fill(PURPLE)
        self.draw_text("GAME OVER!",30,BLACK,ANCHO/2,ALTO/2)
        self.draw_text("Puntos alcanzados: " + str(self.score),30,YELLOW,ANCHO/2,ALTO/2+50)
        self.draw_text("Oprime una tecla para reiniciar...",20,BLACK,ANCHO/2,ALTO*3/4)
        if self.maxscore < self.score:
            self.maxscore = self.score
            self.draw_text("ALCANZASTE UN NUEVO RÉCORD DE PUNTOS!!",30,YELLOW,ANCHO/2,ALTO/2+120) 
            with open(os.path.join(self.dir,SCORE_FILE),'w') as txt:
                txt.write(str(self.maxscore))
        else:
            self.draw_text("Puntaje máximo alcanzado: "+str(self.maxscore),25,BLACK,ANCHO/2,ALTO*3/4+50)
        pg.display.flip()
        pg.mixer.music.load(os.path.join(self.sound_dir,'Forest_Ambient.ogg'))
        pg.mixer.music.play(loops=-1)
        self.wait_key()
        pg.mixer.music.fadeout(500)
        
    def wait_key(self):
        self.clock.tick(FPS)
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.playing = False
                    self.running = False #lo adherí yo
                if event.type == pg.KEYUP:
                    waiting = False


g = Game()
g.start_screen() #establece g.running
while g.running:
    g.new() #g.playing controla loop interno 
    g.gameOver_screen() #si "tache",se le pasa bandera y no se muestra gameOver screen
pg.quit()
