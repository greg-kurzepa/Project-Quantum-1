import pygame, sys, threading, time, pickle, socket, struct, math, os, timeit, ast
pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

dire = os.getcwd()
background = pygame.image.load(dire + "\\mainMenuBackground.png").convert()
menuItems = []
#images that appear in main menu are below
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuSettingsButton.png").convert(), (250, 50)))         # 0
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuSettingsButtonOn.png").convert(), (250, 50)))       # 1
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuCTFButton.png").convert(), (450, 50)))              # 2
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuCTFButtonOn.png").convert(), (450, 50)))            # 3
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuBRButton.png").convert(), (350, 50)))               # 4
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\mainMenuBRButtonOn.png").convert(), (350, 50)))             # 5
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\settingsMusic.png").convert_alpha(), (450, 50)))            # 6
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\settingsHostIP.png").convert(), (500, 50)))                 # 7
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\backButton.png").convert(), (150, 50)))                     # 8
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\backButtonOn.png").convert(), (150, 50)))                   # 9
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\settingsVolumeScroll.png").convert_alpha(), (19, 35)))      # 10
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\roomIDBox.png").convert(), (500, 50)))                      # 11
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyCreateButton.png").convert(), (200, 50)))              # 12
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyCreateButtonOn.png").convert(), (200, 50)))            # 13
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyJoinButton.png").convert(), (150, 50)))                # 14
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyJoinButtonOn.png").convert(), (150, 50)))              # 15
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyJoinButtonDisabled.png").convert(), (150, 50)))        # 16
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyCreateButtonDisabled.png").convert(), (200, 50)))      # 17
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyLeave.png").convert(), (150, 50)))                     # 18
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyLeaveOn.png").convert(), (150, 50)))                   # 19
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyCloseRoom.png").convert(), (300, 50)))                 # 20
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyCloseRoomOn.png").convert(), (300, 50)))               # 21
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyStart.png").convert(), (150, 50)))                     # 22
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyStartOn.png").convert(), (150, 50)))                   # 23
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\roomIDBoxNoInput.png").convert(), (200, 50)))               # 24
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyUser.png").convert(), (30, 30)))                       # 25
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\lobbyUserHost.png").convert(), (30, 30)))                   # 26
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\settingsSFX.png").convert_alpha(), (450, 50)))              # 27
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\settingsUsername.png").convert(), (550, 50)))               # 28
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\leaveButton.png").convert(), (150, 50)))                    # 29
menuItems.append(pygame.transform.scale(pygame.image.load(dire+"\\leaveButtonOn.png").convert(), (150, 50)))                  # 30
#images that appear ingame are below
gameItems = []
gameItems.append(pygame.transform.scale(pygame.image.load(dire+"\\gameOptionsCog.png").convert(), (50, 50)))                  # 0
gameItems.append(pygame.transform.scale(pygame.image.load(dire+"\\gameOptionsCogOn.png").convert(), (50, 50)))                # 1
backdrop1 = pygame.image.load(dire+"\\backdrop1.png").convert()
tileImg = pygame.image.load(dire+"\\data\\images\\tile.png")

class RenderUsername:
    def __init__(self, username):
        self.username = username
        self.renderedUsername = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render(username, True, [0,0,0])

class Lobby:
    def __init__(self, capacity=8 , waitingCount=0 , cuUsernames=[] , cuIsOnline=[] ):
        self.capacity = capacity
        self.waitingCount = waitingCount
        self.cuUsernames = cuUsernames
        self.cuIsOnline = cuIsOnline

class TextBox:
    global screen

    def __init__(self, topleft, bottomright, maxLength, text):
        self.topleft = topleft
        self.bottomright = bottomright
        self.text = text
        self.colour = [255,255,255]
        self.text_surface = gameFont.render(self.text, True, self.colour)
        self.active = False
        self.maxLength = maxLength

    def handle_event(self, event, mousePos):
        if mousePos[0] >= self.topleft[0] and mousePos[1] >= self.topleft[1] and mousePos[0] <= self.bottomright[0] and mousePos[1] <= self.bottomright[1]:
            pygame.mouse.set_cursor((8, 16), (0, 0), *cursor) #puts the cursor into text input mode
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.maxLength:
                self.text += event.unicode
            self.text_surface = gameFont.render(self.text, True, self.colour)

    def draw(self, x, y): #for ip input, (262,604)
        screen.blit(self.text_surface, [x,y])

#MAKE THIS MORE ADAPTIVE to be usable in multiple scenarios
class VolumeScroll:
    def __init__(self, centre, lMax, rMax, scrollType, initialVolume = None):
        if not initialVolume: initialVolume = 0.5
        self.topleft = [lMax+initialVolume*(rMax-lMax)-9, centre[1]-17]
        self.bottomright = [lMax+initialVolume*(rMax-lMax)+9, centre[1]+17]
        self.centre = [lMax+initialVolume*(rMax-lMax), centre[1]]
        self.active = False
        self.lMax = lMax
        self.rMax = rMax
        self.scrollType = scrollType

    def handle_event(self, mousePos, mousePressed):
        global sfxvolume, musicvolume

        if self.active:
            if mousePressed[0]:
                if mousePos[0] >= self.lMax and mousePos[0] <= self.rMax:
                    self.centre[0] = mousePos[0]
                    self.topleft[0] = mousePos[0] - 9
                    self.bottomright[0] = mousePos[0] + 9
            else:
                self.active = False
        elif mousePos[0] >= self.topleft[0] and mousePos[1] >= self.topleft[1] and mousePos[0] <= self.bottomright[0] and mousePos[1] <= self.bottomright[1] and mousePressed[0] and not self.active:
            self.active = True
        if self.scrollType == "music":
            musicvolume = (self.centre[0] - self.lMax)/(self.rMax - self.lMax)
            pygame.mixer.music.set_volume(musicvolume)
        elif self.scrollType == "sfx":
            sfxvolume = (self.centre[0] - self.lMax)/(self.rMax - self.lMax)

    def draw(self):
        screen.blit(menuItems[10], menuItems[10].get_rect(center=(self.centre)))

class Player:
    def __init__(self):
        self.pos = [0,0]
        self.vel = [0,0]
        self.lives = 3 # only used in battle royale mode
        self.team = 0 # 0 or 1
        self.imgId = None
        self.powerup = 0
        self.actionState = 0 # 0 is standing, 1 is walking left, 2 is walking right, 3 is running left, 4 is running right, 5 is jumping, 6 is smashing onto ground
        self.isAlive = True
        self.username = ""

    def unpack(self, bin):
        bin = bin.split(";")
        self.pos = list(map(float, bin[0].split(":")))
        self.vel = list(map(float, bin[1].split(":")))
        self.lives = int(bin[2])
        self.team = int(bin[3])
        self.powerup = int(bin[4])
        self.actionState = int(bin[5])
        self.isAlive = ast.literal_eval(bin[6])
        self.username = str(bin[7])

class Game:
    def __init__(self):
        self.ps = [] #contains indexes of players in players list
        self.isActive = True
        self.team0flags = 3 #usually 3 to start with
        self.team1flags = 3

    def unpack(self, bin):
        global players
        values = bin.decode().split(",")
        self.ps = list(map(int, values[1].split("|")))
        self.isActive = ast.literal_eval(values[2])
        self.team0flags = int(values[3])
        self.team1flags = int(values[4])

        packedPlayers = values[0].split("|")
        tempArr = []
        for i in range(len(packedPlayers)):
            if i in self.ps:
                tempArr.append(Player())
                tempArr[i].unpack(packedPlayers[i])
            else:
                tempArr.append(None)
        players = tempArr

class Tile:
    def __init__(self, tl, img = tileImg, width = 40, height = 40):
        self.tl = tl
        self.width = width
        self.height = height
        self.img = img

class Level:
    def __init__(self, name, dire, tiles = None):
        if tiles == None: self.tiles = []
        else: self.tiles = tiles

        lowest = -1000000
        f = open(dire + "\\data\\" + name + ".lvl", "rb") #opens test level file
        filecontent = f.read()
        a = struct.unpack("i", filecontent[:4])[0] #reads how many tiles to read
        for i in range(a):
            pos = struct.unpack("ff", filecontent[(8 * i + 4):(8 * (i + 1) + 4)]) #creates all tile sprites and adds them to the group
            if pos[1] > lowest: lowest = pos[1] #finds the lowest tile to set oob boundary
            self.tiles.append(Tile([pos[0]*40, pos[1]*40]))
        f.close()

class PlayerInput:
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def pack(self):
        return(",".join([str(self.left), str(self.right), str(self.up), str(self.down)]))

cursor = pygame.cursors.compile(pygame.cursors.textmarker_strings) #loads text input cursor
gameFont = pygame.font.Font(dire+"\\SuperMario256.ttf", 26)
pygame.display.set_caption("Mario Party Py")
hostIP = ""
musicvolume = 0.5
sfxvolume = 0.5
ipInput = TextBox([256, 598], [537, 631], 15, hostIP)
settingsUsername = TextBox([306, 388], [587, 421], 15, "")
roomIdInput = TextBox([256, 168], [537, 201], 9, "")
settingsVolume = VolumeScroll([350, 545], 222, 478, "music") #range: 272-400-528
settingsSFX = VolumeScroll([350, 475], 222, 478, "sfx")
renderedUsernames = []
players = []
menuMode = "selection"
clientCommand = ""
gameType = ""
connectingMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("connecting to server", True, [255,255,255])
connectedMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("connected", True, [255,255,255])
connectedState = 0
currentMsg = ""
currentLobby = ""
doneAction = False
topleftMsg = ""
level = None
levelNames = ["testlevel3"]
game = Game()
playerId = None
clientCommand2 = 0
inp = PlayerInput()

#scOffset = [640,360]
scOffset = [50,300]
scVel = [0,0]
scAcc = [0,0]

pygame.mixer.music.load(dire + "\\mainMenuTheme.mp3")
pygame.mixer.music.set_volume(musicvolume)
pygame.mixer.music.play(-1)

def connectionManager():
    doMainGame = False
    print("connecting with ip", hostIP)
    global clientCommand, currentMsg, currentLobby, settingsUsername, connectedState, level, game, inp, players, playerId, clientCommand2

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((hostIP, 52971))
        except socket.error:
            connectedState = 3 #failure
            return(0)
        connectedState = 1
        time.sleep(0.5)
        connectedState = 2

        try:
            data = client.recv(1024).decode()
            if not data:
                clientCommand = "disconnected by server"
            else:
                if settingsUsername.text == "": settingsUsername.text = "user" + data
                client.sendall(settingsUsername.text.encode())

                while True:
                    if doMainGame: break
                    while clientCommand == "":
                        pass
                    if clientCommand == "create":
                        clientCommand = ""
                        client.sendall(("create:" + gameType + ":" + roomIdInput.text).encode())
                        data = client.recv(1024).decode()
                        if not data:
                            clientCommand = "disconnected by server"
                            break
                        elif data == "already exists":
                            currentMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 16).render("A lobby with this name already exists or has existed", True, [255,255,255])
                        else:
                            clientCommand = "go to lobby (create)"
                            while True:
                                time.sleep(0.5)
                                if clientCommand == "start game":
                                    client.sendall(clientCommand.encode())
                                    clientCommand = "starting game"
                                    doMainGame = True
                                    break
                                elif clientCommand == "close room":
                                    client.sendall(clientCommand.encode())
                                    clientCommand = ""
                                    currentLobby = ""
                                    break
                                else:
                                    client.sendall(b"lobby list")
                                    data = client.recv(1024).decode()
                                    if not data:
                                        clientCommand = "disconnected by server"
                                        break
                                    else:
                                        data = data.split(":")
                                        currentLobby = Lobby(data[0], data[1], data[2].split(","), data[3].split(","))

                    elif clientCommand == "join":
                        clientCommand = ""
                        client.sendall(("join:" + gameType + ":" + roomIdInput.text).encode())
                        data = client.recv(1024).decode()
                        if not data:
                            clientCommand = "disconnected by server"
                            break
                        elif data == "no such lobby":
                            currentMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 16).render("No such lobby exists", True, [255,255,255])
                        else:
                            clientCommand = "go to lobby (join)"
                            while True:
                                data = client.recv(1024).decode()
                                if not data:
                                    clientCommand = "disconnected by server"
                                    break
                                else:
                                    if data == "start game":
                                        clientCommand = "starting game"
                                        doMainGame = True
                                        break
                                    elif data == "room closed":
                                        currentMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 16).render("Host closed the room", True, [255,255,255])
                                        clientCommand = "host closed the room"
                                        break
                                    elif data.split(":")[0] == "lobby list":
                                        data = data.split(":")
                                        currentLobby = Lobby(data[1], data[2], data[3].split(","), data[4].split(","))
                                        if clientCommand == "leave room":
                                            client.sendall(clientCommand.encode())
                                            clientCommand = ""
                                            currentLobby = ""
                                            break
                                        else:
                                            client.sendall(b"no change")

                    elif clientCommand == "close connection":
                        try:
                            client.shutdown(socket.SHUT_RDWR)
                            client.close()
                        except socket.error: pass
                        clientCommand = ""
                        break

                if doMainGame:
                    client.sendall(b"ready")
                    data = client.recv(1024)
                    if not data:
                        clientCommand2 = "Disconnected by server"
                    else:
                        data = data.decode().split(",")
                        level = Level(levelNames[int(data[0])], dire)
                        playerId = int(data[1])
                        client.sendall(b"ready")

                        while True:
                            data = client.recv(1024)
                            if not data:
                                clientCommand2 = "Disconnected by server"
                                break
                            game.unpack(data)

                            client.sendall(inp.pack().encode())

        except socket.error:
            clientCommand2 = "Disconnected by server"
            clientCommand = "Disconnected by server"
            return(0)

def connectingUI():
    trd = threading.Thread(target = connectionManager)
    trd.daemon = True
    trd.start()

    screen.blit(connectingMsg, [45,213])
    pygame.display.flip()
    while connectedState == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
    if connectedState == 3:
        return(3)
    screen.blit(background, [0,0])
    screen.blit(connectedMsg, [45,213])
    pygame.display.flip()
    while connectedState == 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
    return(2)

def fallMenuFunc(counter): # child of fallMenu function
    if counter >= 0: return round(1/110 * (-(counter**2) + 2*counter*4.472136))
    else: return 0

def fallLobbyJoin(start, end, inc):
    for i in range(start, end, inc):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        screen.blit(background, [0,0])
        screen.blit(menuItems[18], menuItems[18].get_rect(topleft=([45+fallMenuFunc(i), 590])))
        screen.blit(menuItems[24], menuItems[24].get_rect(topleft=([45+fallMenuFunc(i), 160])))

        pygame.display.flip()

def fallLobbyCreate(start, end, inc):
    for i in range(start, end, inc):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        screen.blit(background, [0,0])
        screen.blit(menuItems[22], menuItems[22].get_rect(topleft=([45+fallMenuFunc(i), 590])))
        screen.blit(menuItems[20], menuItems[20].get_rect(topleft=([170+45+fallMenuFunc(i), 590])))
        screen.blit(menuItems[24], menuItems[24].get_rect(topleft=([45+fallMenuFunc(i), 160])))

        pygame.display.flip()

def fallLobby(start, end, inc):
    for i in range(start, end, inc):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        screen.blit(background, [0,0])
        screen.blit(menuItems[11], menuItems[11].get_rect(topleft=([45+fallMenuFunc(i), 160]))) # room id
        screen.blit(menuItems[17], menuItems[17].get_rect(topleft=([520+45+fallMenuFunc(i), 160]))) # create
        screen.blit(menuItems[16], menuItems[16].get_rect(topleft=([220+520+45+fallMenuFunc(i), 160]))) # join
        screen.blit(menuItems[8], menuItems[8].get_rect(topleft=([45+fallMenuFunc(i), 590]))) # back

        pygame.display.flip()
    
def fallSettings(start, end, inc): #roll in (230,0,-1), roll out (0,230,1)
    for i in range(start, end, inc):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        screen.blit(background, [0,0])
        screen.blit(menuItems[6], menuItems[6].get_rect(topleft=([45+fallMenuFunc(i), 520])))
        screen.blit(menuItems[7], menuItems[7].get_rect(topleft=([45+fallMenuFunc(i), 590])))
        screen.blit(menuItems[8], menuItems[8].get_rect(topright=([1280-(45+fallMenuFunc(i)), 590])))

        pygame.display.flip()

def fallMenu(start, end, inc, correction): # animates moving main menu buttons
    global screen

    for i in range(start, end, inc): #roll in (450,0,-1), roll out (0,450,1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
        
        screen.blit(background, [0,0])
        screen.blit(menuItems[0], menuItems[0].get_rect(topleft=([45+fallMenuFunc(i+correction[0]), 590])))
        screen.blit(menuItems[2], menuItems[2].get_rect(topleft=([45+fallMenuFunc(i+correction[1]), 520])))
        screen.blit(menuItems[4], menuItems[4].get_rect(topleft=([45+fallMenuFunc(i+correction[2]), 450])))

        pygame.display.flip()

def mainGame(mode):
    global clientCommand2, inp, game, players, scOffset, musicvolume
    inOptions = False
    scrollInterval = 0.05
    offsetCoeff = [0,0]
    doneAction = False

    optionsMusic = VolumeScroll([395, 115], 267, 523, "music", musicvolume) #range: 272-400-528
    optionsSFX = VolumeScroll([395, 45], 267, 523, "sfx", sfxvolume)

    while not level: pass
    while True:
        if clientCommand2 == "Disconnected by server": return
        mousePos = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()
        if doneAction == True and not mousePressed[0]:
            doneAction = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    inOptions = not inOptions
            if inOptions:
                optionsMusic.handle_event(mousePos, mousePressed)
                optionsSFX.handle_event(mousePos, mousePressed)

        inp.up, inp.down, inp.left, inp.right = False, False, False, False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: inp.left = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: inp.right = True
        if keys[pygame.K_w] or keys[pygame.K_UP]: inp.up = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: inp.down = True 

        scOffset = [-players[playerId].pos[0] + (1280*(0.5 + offsetCoeff[0]*0.1)), -players[playerId].pos[1] + 320]
        if offsetCoeff[0] - players[playerId].vel[0]/2000 >= 1: offsetCoeff[0] = 1
        elif offsetCoeff[0] - players[playerId].vel[0]/2000 <= -1: offsetCoeff[0] = -1
        else: offsetCoeff[0] -= players[playerId].vel[0]/2000
        #if players[playerId].vel != 0:
        #    offsetCoeff[1] += players[playerId].vel[1]/2000

        screen.fill([100,100,100])
        screen.blit(backdrop1, backdrop1.get_rect(topleft=([0,-720])))
        for o in level.tiles:
            screen.blit(o.img, (int(o.tl[0] + scOffset[0]), int(o.tl[1] + scOffset[1])))
        for i in range(len(game.ps)):
            pygame.draw.rect(screen, [0,0,220], pygame.Rect(int(players[game.ps[i]].pos[0] + scOffset[0]), int(players[game.ps[i]].pos[1] + scOffset[1]), 40, 80))

        #options cog
        if mousePos[0] >= 20 and mousePos[0] <= 70 and mousePos[1] >= 20 and mousePos[1] <= 70:
            screen.blit(gameItems[1], gameItems[1].get_rect(topleft=([20, 20])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                inOptions = not inOptions
        else:
            screen.blit(gameItems[0], gameItems[0].get_rect(topleft=([20, 20])))

        if inOptions:
            # leave button
            if mousePos[0] >= 90 and mousePos[0] <= 240 and mousePos[1] >= 160 and mousePos[1] <= 210:
                screen.blit(menuItems[30], menuItems[30].get_rect(topleft=([90, 160])))
                if mousePressed[0] and not doneAction:
                    leaveGame = True
                    break
            else:
                screen.blit(menuItems[29], menuItems[29].get_rect(topleft=([90, 160])))

            # sfx and music volume
            screen.blit(menuItems[27], menuItems[27].get_rect(topleft=([90, 20])))
            screen.blit(menuItems[6], menuItems[6].get_rect(topleft=([90, 90])))
            optionsSFX.draw()
            optionsMusic.draw()

        pygame.display.flip()

#User interface before entering game
while True:
    mousePos = pygame.mouse.get_pos()
    mousePressed = pygame.mouse.get_pressed()
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    if doneAction == True and not mousePressed[0]:
        doneAction = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        if menuMode == "settings":
            ipInput.handle_event(event, mousePos)
            settingsSFX.handle_event(mousePos, mousePressed)
            settingsVolume.handle_event(mousePos, mousePressed)
            settingsUsername.handle_event(event, mousePos)
        if menuMode == "lobby":
            roomIdInput.handle_event(event, mousePos)
            if mousePos[0] >= 565 and mousePos[0] <= 765 and mousePos[1] >= 160 and mousePos[1] <= 210 and event.type == pygame.MOUSEBUTTONDOWN:
                clientCommand = "create"
            elif mousePos[0] >= 785 and mousePos[0] <= 935 and mousePos[1] >= 160 and mousePos[1] <= 210 and event.type == pygame.MOUSEBUTTONDOWN:
                clientCommand = "join"
    
    screen.blit(background, [0,0])

    if clientCommand == "disconnected by server":
        topleftMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("Disconnected by server", True, [255,255,255])
        menuMode = "selection"
        clientCommand = ""
        if menuMode == "lobby":
            fallLobby(0, 230, 4)
        elif menuMode == "lobbyJoin":
            fallLobbyJoin(0, 230, 1)
        elif menuMode == "lobbyCreate":
            fallLobbyCreate(0, 230, 1)
        fallMenu(450, 0, -1, [0,0,0])
    
    if menuMode == "selection":
        #battle royale button
        if mousePos[0] >= 45 and mousePos[0] <= 395 and mousePos[1] >= 450 and mousePos[1] <= 500:
            screen.blit(menuItems[5], menuItems[5].get_rect(topleft=([45, 450])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                fallMenu(0, 450, 1, [0, 0, -200])
                if connectingUI() == 2:
                    menuMode = "lobby"
                    gameType = "battle royale"
                    topleftMsg = ""
                    fallLobby(230, 0, -4)
                else:
                    topleftMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("Could not connect to server", True, [255,255,255])
                    fallMenu(450, 0, -1, [0, 0, 0])
        else:
            screen.blit(menuItems[4], menuItems[4].get_rect(topleft=([45, 450])))

        #capture the flag button
        if mousePos[0] >= 45 and mousePos[0] <= 495 and mousePos[1] >= 520 and mousePos[1] <= 570:
            screen.blit(menuItems[3], menuItems[3].get_rect(topleft=([45, 520])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                fallMenu(0, 450, 1, [0, -200, 0])
                if connectingUI() == 2:
                    menuMode = "lobby"
                    gameType = "capture the flag"
                    topleftMsg = ""
                    fallLobby(230, 0, -4)
                else:
                    topleftMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("Could not connect to server", True, [255,255,255])
                    fallMenu(450, 0, -1, [0, 0, 0])
        else:
            screen.blit(menuItems[2], menuItems[2].get_rect(topleft=([45, 520])))

        #settings button
        if mousePos[0] >= 45 and mousePos[0] <= 295 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[1], menuItems[1].get_rect(topleft=([45, 590])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                topleftMsg = ""
                fallMenu(0, 450, 1, [-200, 0, 0])
                menuMode = "settings"
                fallSettings(230, 0, -1)
        else:
            screen.blit(menuItems[0], menuItems[0].get_rect(topleft=([45, 590])))

    if menuMode == "settings": #1235, 590 topright
        screen.blit(menuItems[6], menuItems[6].get_rect(topleft=([45, 520])))
        screen.blit(menuItems[7], menuItems[7].get_rect(topleft=([45, 590])))
        screen.blit(menuItems[27], menuItems[27].get_rect(topleft=([45, 450])))
        screen.blit(menuItems[28], menuItems[28].get_rect(topleft=([45, 380])))

        ipInput.draw(262, 604)          #ip text box
        settingsUsername.draw(312, 394) #username text box
        settingsSFX.draw()              #sfx volume slider
        settingsVolume.draw()           #volume slider

        #back button
        if mousePos[0] <= 1235 and mousePos[0] >= 1085 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[9], menuItems[9].get_rect(topright=([1235, 590])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                hostIP = ipInput.text
                fallSettings(0, 230, 1)
                menuMode = "selection"
                fallMenu(450, 0, -1, [0,0,0])
        else:
            screen.blit(menuItems[8], menuItems[8].get_rect(topright=([1235, 590])))

    if menuMode == "lobby":
        screen.blit(menuItems[11], menuItems[11].get_rect(topleft=([45, 160])))
        screen.blit(menuItems[8], menuItems[8].get_rect(topleft=([45, 590])))

        #create button
        if len(roomIdInput.text) == 0:
            screen.blit(menuItems[17], menuItems[17].get_rect(topleft=([565, 160])))
        elif mousePos[0] >= 565 and mousePos[0] <= 765 and mousePos[1] >= 160 and mousePos[1] <= 210:
            screen.blit(menuItems[13], menuItems[13].get_rect(topleft=([565, 160])))
        else:
            screen.blit(menuItems[12], menuItems[12].get_rect(topleft=([565, 160])))

        #join button
        if len(roomIdInput.text) == 0:
            screen.blit(menuItems[16], menuItems[16].get_rect(topleft=([785, 160])))
        elif mousePos[0] >= 785 and mousePos[0] <= 935 and mousePos[1] >= 160 and mousePos[1] <= 210:
            screen.blit(menuItems[15], menuItems[15].get_rect(topleft=([785, 160])))
        else:
            screen.blit(menuItems[14], menuItems[14].get_rect(topleft=([785, 160])))

        #back button
        if mousePos[0] >= 45 and mousePos[0] <= 195 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[9], menuItems[9].get_rect(topleft=([45, 590])))
            if mousePressed[0] and not doneAction:
                doneAction = True
                clientCommand = "close connection"
                fallLobby(0, 230, 4)
                menuMode = "selection"
                currentMsg = ""
                fallMenu(450, 0, -1, [0,0,0])
        else:
            screen.blit(menuItems[8], menuItems[8].get_rect(topleft=([45, 590])))

        roomIdInput.draw(262, 174)

    if menuMode == "lobbyJoin":
        if clientCommand == "host closed the room":
            clientCommand = ""
            menuMode = "lobby"
            fallLobbyJoin(0, 230, 1)
            fallLobby(230, 0, -4)

        if mousePos[0] >= 45 and mousePos[0] <= 195 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[19], menuItems[19].get_rect(topleft=([45, 590])))
            if mousePressed[0] and not doneAction:
                clientCommand = "leave room"
                menuMode = "lobby"
                fallLobbyJoin(0, 230, 1)
                fallLobby(230, 0, -4)
        else:
            screen.blit(menuItems[18], menuItems[18].get_rect(topleft=([45, 590]))) #leave lobby

        screen.blit(menuItems[24], menuItems[24].get_rect(topleft=([45, 160]))) #lobby id
        roomIdInput.draw(262, 174)

    if menuMode == "lobbyCreate":
        if mousePos[0] >= 45 and mousePos[0] <= 195 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[23], menuItems[23].get_rect(topleft=([45, 590])))
            if mousePressed[0] and not doneAction:
                clientCommand = "start game"
        else:
            screen.blit(menuItems[22], menuItems[22].get_rect(topleft=([45, 590]))) #start

        if mousePos[0] >= 215 and mousePos[0] <= 515 and mousePos[1] >= 590 and mousePos[1] <= 640:
            screen.blit(menuItems[21], menuItems[21].get_rect(topleft=([215, 590])))
            if mousePressed[0] and not doneAction:
                clientCommand = "close room"
                menuMode = "lobby"
                fallLobbyCreate(0, 230, 2)
                fallLobby(230, 0, -4)
        else:
            screen.blit(menuItems[20], menuItems[20].get_rect(topleft=([215, 590]))) #close room

        screen.blit(menuItems[24], menuItems[24].get_rect(topleft=([45, 160]))) #lobby id
        roomIdInput.draw(262, 174)

    if menuMode == "lobbyCreate" or menuMode == "lobbyJoin": # puts players in current lobby on screen
        if clientCommand == "starting game":
            clientCommand = ""
            menuMode = "ingame"
            fadeSurface = pygame.Surface((1280,720))
            for i in range(255):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: 
                        sys.exit()
                fadeSurface.set_alpha(i)
                screen.blit(background, [0,0])
                screen.blit(fadeSurface, [0,0])
                pygame.display.flip()
                temp1 = i / 255
                if musicvolume - temp1 >= 0: pygame.mixer.music.set_volume(musicvolume - temp1)
                time.sleep(0.002)
            pygame.mixer.music.stop()
            mainGame(gameType)
            topleftMsg = pygame.font.Font(dire+"\\SuperMario256.ttf", 20).render("Disconnected by server", True, [255,255,255])
            menuMode = "selection"
            clientCommand = ""
            fallMenu(450, 0, -1, [0,0,0])

        elif currentLobby != "":
            for i in range(len(currentLobby.cuUsernames)):
                if currentLobby.cuIsOnline[i]:
                    if i == 0:
                        screen.blit(menuItems[26], menuItems[26].get_rect(topleft=([45, 230+i*40])))
                    else:
                        screen.blit(menuItems[25], menuItems[25].get_rect(topleft=([45, 230+i*40])))
                    
                    if any(RenderUsername.username == currentLobby.cuUsernames[i] for RenderUsername in renderedUsernames):
                        for j in range(len(renderedUsernames)):
                            if renderedUsernames[j].username == currentLobby.cuUsernames[i]:
                                screen.blit(renderedUsernames[j].renderedUsername, [86, 237+i*40])
                    else:
                        renderedUsernames.append(RenderUsername(currentLobby.cuUsernames[i]))
                        screen.blit(renderedUsernames[-1].renderedUsername, [86, 237+i*40])

    if clientCommand == "go to lobby (join)":
        clientCommand = ""
        menuMode = "lobbyJoin"
        currentMsg = ""
        fallLobby(0, 230, 4)
        fallLobbyJoin(230, 0, -1)
    elif clientCommand == "go to lobby (create)":
        clientCommand = ""
        menuMode = "lobbyCreate"
        currentMsg = ""
        fallLobby(0, 230, 4)
        fallLobbyCreate(230, 0, -1)

    if currentMsg != "":
        screen.blit(currentMsg, [45, 213])
    if topleftMsg != "":
        screen.blit(topleftMsg, [0, 0])

    pygame.display.flip()
