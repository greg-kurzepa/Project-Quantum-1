import pygame, sys, struct, glob
from math import *
pygame.init()

spritenames = [f for f in glob.glob("images//*.png")]
sprites = [pygame.image.load(n) for n in spritenames] #loads the tileset in
currenttile = 0

screenpos = pygame.math.Vector2(-640, -360)

class Wall(pygame.sprite.Sprite): #wall sprite class
    def __init__(self, pos, tile, tileID):
        pygame.sprite.Sprite.__init__(self)
        self.tileID = tileID
        self.image = pygame.Surface((40, 40))
        self.image.blit(tile, (0, 0))
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect().move(self.pos.__mul__(40).__sub__(screenpos))

    def move(self):
        self.rect = self.image.get_rect().move(self.pos.__mul__(40).__sub__(screenpos))

walls = pygame.sprite.Group([ #add a wall at (0, 0) to a group
    Wall((0, 0), sprites[0], 0),
])

size = width, height = 1280, 720  #size of the window in pixels
screen = pygame.display.set_mode(size)  #screen is the screen object

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit(0)  #closes the window if program is closed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL): #if ctrl + s is pressed saves to a .lvl binary file
                f = open("testlevel.lvl", "wb")
                f.write(bytearray(struct.pack("i", walls.sprites().__len__())))
                for w in walls.sprites():
                    f.write(bytearray(struct.pack("f", w.pos.x)))
                    f.write(bytearray(struct.pack("f", w.pos.y)))
                    f.write(bytearray(struct.pack("i", w.tileID))) #writes the tile id of the tile in the tileset
                f.close()
            if event.key == pygame.K_q: #q and e swap between tiles in the tileset
                currenttile -= 1
                if currenttile < 0:
                    currenttile = sprites.__len__() - 1
            if event.key == pygame.K_e:
                currenttile += 1
                if currenttile >= sprites.__len__():
                    currenttile = 0


    buttons = pygame.mouse.get_pressed()
    pos = pygame.mouse.get_pos()
    abscell = ((pos[0] + screenpos.x % 40) // 40 + screenpos.x // 40, (pos[1] + screenpos.y % 40) // 40 + screenpos.y // 40) #the cell the user's mouse is positioned in (absolute)
    if buttons[0]: #while holding left click will add tiles
        empty = True
        for w in walls.sprites():
            if w.pos.x == abscell[0] and w.pos.y == abscell[1]:
                empty = False
                break
        if empty:
            walls.add(Wall(abscell, sprites[currenttile], currenttile))
    elif buttons[2]: #while holding right click will remove tiles
        for w in walls.sprites():
            if w.pos.x == abscell[0] and w.pos.y == abscell[1]:
                walls.remove(w)
                break

    keys = pygame.key.get_pressed() #pan view with arrow keys
    if keys[pygame.K_UP]:
        screenpos.y -= 1
    if keys[pygame.K_DOWN]:
        screenpos.y += 1
    if keys[pygame.K_LEFT]:
        screenpos.x -= 1
    if keys[pygame.K_RIGHT]:
        screenpos.x += 1

    for w in walls.sprites():
        w.move()

    screen.fill([100,100,100])  #RGB colour to fill the screen

    #draw a grid
    dx = -(screenpos.x % 40)
    dy = -(screenpos.y % 40)
    for x in range(size[0] // 40 + 2):
        pygame.draw.line(screen, (40, 40, 40), (x * 40 + dx, 0), (x * 40 + dx, size[1]))
    for y in range(size[1] // 40 + 2):
        pygame.draw.line(screen, (40, 40, 40), (0, y * 40 + dy), (size[0], y * 40 + dy))

    walls.draw(screen)
    screen.blit(sprites[currenttile], (0, 0))
    pygame.display.flip()  #this updates the screen