#tamaño y título de pantalla
ANCHO, ALTO = 600, 600 
TITULO = "ARDILLA ASESINA"
FPS = 60
FONT_NAME = "arial"
#colores
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
L_BLUE = (0,255,255)
PURPLE = (255,0,255)
#player config
PLAYER_ACC = 1
PLAYER_FRICTION = -0.05
PLAYER_JUMP = 18 #velocidad inicial del salto
GRAVITY = 0.5
#propiedades de Game
BOOST_POWER = 30
PCT_POWERUPS = 20 #porcentaje de plataformas que tendrán powerups encima
MOB_FREQ = 5000 #miliseg en que aparece mob
PLAYER_LAYER = 2 #orden en el que se dibujarán en pantalla
MOB_LAYER = 2 #entre mayor sea, más "enfrente" se ve
POW_LAYER = 1
PLAT_LAYER = 1
NUBE_LAYER = 0
#plataformas
PLATFORM_LIST = [(200,ALTO-40),
                (ANCHO/2-40,ALTO-205),
                (40,ALTO-50),
                (ANCHO-100,10),
                (100,200),
                (300,400),
                (ANCHO/2,ALTO-250),
                (ANCHO/2-100,ALTO/2-100),
                (ANCHO-200,20),
                (0,ALTO-20),
                (ANCHO/2,ALTO-20),
                (ANCHO-200,ALTO-20)]
SCORE_FILE = "MaxScore.txt"
SPRITESHEET_FILE = "spritesheet_jumper.png"