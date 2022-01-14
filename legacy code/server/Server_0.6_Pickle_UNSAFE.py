import socket, threading, sys, os, random, pickle, time, collidePlayer, struct

#storess all current and historical connections during this runtime
connections = []
#stores all lobbies currently not in a game
lobbies = []
#stores all games currently being played
games = []
#stores all players in a game
players = []
#stores all player inputs, corresponds 1 to 1 with players array
playerInputs = []

dire = os.getcwd()

tickInterval = 0.005
m = 1 #speed multiplier
timeFactor = 6

class Player:
    def __init__(self, username, team, pos, vel, width, height):
        self.pos = pos
        self.vel = vel
        self.width = width
        self.height = height
        self.walled = 0 # -1 for wall on right, 1 for wall on left
        self.lives = 3 # only used in battle royale mode
        self.team = team # 0 or 1
        self.sprinting = False
        self.grounded = False

        self.imgId = None
        self.animationMode = 0
        self.actionState = 0 # 0 is standing, 1 is walking left, 2 is walking right, 3 is running left, 4 is running right, 5 is jumping, 6 is smashing onto ground
        self.isAlive = True

        self.username = username
        self.isInGame = True

        #self.id = 0 # location of player in connections list
        #self.localId = localId # location of player in game player list

class Game:
    def __init__(self, gameType, playersLeft, team0flags, team1flags, arena, gameId):
        self.ps = [] #contains indexes of players in players list
        self.gameType = gameType #0 is ctf, 1 is battle royale
        self.isActive = True
        self.team0flags = team0flags #usually 3 to start with
        self.team1flags = team1flags
        self.arena = arena #integer id of arena being used for the game
        self.playersLeft = playersLeft #[team1 players left, team2 players left]
        self.gameId = gameId #location of object in games list

class Tile:
    def __init__(self, tl, width, height):
        self.tl = tl
        self.width = width
        self.height = height

class Level:
    def __init__(self, name, dire, tiles=None):
        if tiles == None: self.tiles = []
        else: self.tiles = tiles

        lowest = -1000000
        f = open(dire + "/" + name + ".lvl", "rb") #opens test level file
        filecontent = f.read()
        a = struct.unpack("i", filecontent[:4])[0] #reads how many tiles to read
        for i in range(a):
            pos = struct.unpack("ff", filecontent[(8 * i + 4):(8 * (i + 1) + 4)]) #creates all tile sprites and adds them to the group
            if pos[1] > lowest: lowest = pos[1] #finds the lowest tile to set oob boundary
            self.tiles.append(Tile([pos[0]*40, pos[1]*40], 40, 40))
        f.close()
        collidePlayer.loadlvl(dire, name)

class Connection:
    def __init__(self, client, username, isOnline, id):
        self.client = client
        self.username = username
        self.isOnline = isOnline
        self.id = id

    def terminate(self):
        try:
            self.isOnline = False
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
        except socket.error: pass

class Lobby:
    def __init__(self, name, host, type, capacity, waitingCount, connectedUsers):
        self.name = name
        self.host = host
        self.type = type
        self.capacity = capacity
        self.waitingCount = waitingCount
        self.connectedUsers = connectedUsers
        self.isClosed = False
        self.isStarting = False
        self.gamesIndex = None
        self.loopDone = False

class PlayerInput:
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False

#dummyPlayer = Player("dm", 1)
#dummyArr = [dummyPlayer, dummyPlayer]
dataLock = threading.Lock()
#dummyGame = Game("capture the flag", 2, 3, 3, 0, 0, [0, 1])

#allows the host to enter console commands to control the server's operation
def hostInput():
    global connections, lobbies, timeFactor, tickInterval

    while True:
        temp = input()
        if temp == "x": break
        elif temp == "lc":
            print("Connections {")
            for i in range(len(connections)):
                if i == len(connections)-1:
                    print(connections[i].username, connections[i].isOnline, "}")
                else: print(connections[i].username, connections[i].isOnline)
        # syntax: tickInterval <new interval in seconds>
        elif temp[:12] == "tickInterval":
            tickInterval = float(temp[13:])
            print("Set tickInterval to " + str(tickInterval))
        elif temp[:10] == "timeFactor":
            timeFactor = float(temp[11:])
            print("Set timeFactor to " + str(timeFactor))
        elif temp == "printplayers":
            for i in range(len(players)):
                print(str(i) + ": " + str(players[i].pos), str(players[i].vel))
        else:
            print("Invalid command")

    for i in connections:
        i.terminate()
    os._exit(1)

def lobbyClientManager(client, id):
    global players, connections, lobbies
    lobbyId = 0
    tempLobby = ""
    closeThread = False
    
    try:
        client.sendall(str(connections[id].username).encode())
        connections[id].username = client.recv(1024).decode() # allows for client to give a custom username
        while not closeThread:
            data = client.recv(1024).decode()
            if not data:
                connections[id].terminate()
                break
            data = data.split(":")

            #at this point, data[0] denotes action, data[1] denotes type of game, data[2] denotes lobby name
            if data[0] == "create": # create new lobby
                if any(Lobby.name == data[2] for Lobby in lobbies): # checks if lobbies array contains a lobby object with Lobby.name == data
                    client.sendall(b"already exists")
                else:
                    client.sendall(b"joining lobby")
                    lobbyId = len(lobbies)
                    lobbies.append(Lobby(data[2], client, data[1], 8, 1, [connections[id]]))
                    while True:
                        #data[0] is whether the client is starting the game, closing the room or doing nothing. data[1] is a secondary request
                        data = client.recv(1024).decode()
                        if not data:
                            lobbies[lobbyId].isClosed = True
                            connections[id].terminate()
                            break

                        if data == "start game":
                            lobbies[lobbyId].gamesIndex = len(games)
                            games.append(Game(lobbies[lobbyId].type, [len(lobbies[lobbyId].connectedUsers)/2, len(lobbies[lobbyId].connectedUsers)/2], 3, 3, 0, lobbies[lobbyId].gamesIndex))
                            lobbies[lobbyId].isStarting = True
                            lobbies[lobbyId].loopDone = False
                            for i in range(len(lobbies[lobbyId].connectedUsers)):
                                playersIndex = len(players)
                                games[lobbies[lobbyId].gamesIndex].ps.append(playersIndex)
                                if i <= len(lobbies[lobbyId].connectedUsers)/2:
                                    players.append(Player(lobbies[lobbyId].connectedUsers[i].username, 0, [0,0], [0,0], 40, 80))
                                    playerInputs.append(PlayerInput())
                                else:
                                    players.append(Player(lobbies[lobbyId].connectedUsers[i].username, 1, [0,0], [0,0], 40, 80))
                                    playerInputs.append(PlayerInput())

                                ntrd = threading.Thread(target=gameManager, args=(lobbies[lobbyId].connectedUsers[i].id, lobbies[lobbyId].gamesIndex, playersIndex, lobbies[lobbyId].type, lobbyId))
                                ntrd.daemon = True
                                ntrd.start()
                        
                            lobbies[lobbyId].loopDone = True
                            closeThread = True
                            break

                        elif data == "close room":
                            lobbies[lobbyId].isClosed = True
                            break
                        elif data == "lobby list": # sends all the information about the lobby
                            client.sendall((":".join([str(lobbies[lobbyId].capacity), str(lobbies[lobbyId].waitingCount), ",".join([x.username for x in lobbies[lobbyId].connectedUsers]), ",".join([str(x.isOnline) for x in lobbies[lobbyId].connectedUsers])])).encode())

            elif data[0] == "join": # join existing lobby
                lobbyId = -1
                for i in range(len(lobbies)):
                    if lobbies[i].name == data[2] and not lobbies[i].isClosed:
                        lobbies[i].connectedUsers.append(connections[id])
                        lobbies[i].waitingCount += 1
                        lobbyId = i
                        break
                if lobbyId == -1:
                    client.sendall(b"no such lobby")
                else:
                    client.sendall(b"joined successfully")
                    while True:
                        if lobbies[lobbyId].isStarting:
                            client.sendall(b"start game")
                            closeThread = True
                            break

                        elif lobbies[lobbyId].isClosed:
                            client.sendall(b"room closed")
                            break
                        else: # sends lobby data as well as recieving the lobby state of client
                            client.sendall((":".join(["lobby list", str(lobbies[lobbyId].capacity), str(lobbies[lobbyId].waitingCount), ",".join([x.username for x in lobbies[lobbyId].connectedUsers]), ",".join([str(x.isOnline) for x in lobbies[lobbyId].connectedUsers])])).encode())
                            data = client.recv(1024).decode()
                            if data == "leave room" or not data:
                                for i in range (len(lobbies[lobbyId].connectedUsers)):
                                    if lobbies[lobbyId].connectedUsers[i].client == client:
                                        del lobbies[lobbyId].connectedUsers[i]
                                lobbies[lobbyId].waitingCount -= 1
                                if not data: connections[id].terminate()
                                break
                        time.sleep(0.5)
    except socket.error:
        connections[id].terminate()

#This is the main chunk of code which manages each client while the main game is running.
def gameManager(connsId, gameId, playerId, mode, lobbyId):
    global lobbies
    while not lobbies[lobbyId].loopDone: pass

    global connections, games, players, playerInputs, m

    vRunMax = 0.25          # maximum speed when running
    aRun = 0.0007*m         # acceleration when running
    vSprintCoeff = 2        # acceleration of run when sprinting as a multiple of vRunMax
    jumpCoeff = 1.22         # for jumping
    jumpSprintCoeff = 1.2   # increase in height when jumping while sprinting
    frictionCoeff = 3       # acceleration of friction when not going left/right as a multiple of aRun
    vFallMax = 0.65         # maximum speed when falling
    aFall = 0.0025          # acceleration when falling

    #m = 1
    #vRunMax = 0.25*m          # maximum speed when running
    #aRun = 0.0007*m           # acceleration when running
    #vSprintCoeff = 2*m        # acceleration of run when sprinting as a multiple of vRunMax
    #jumpSprintCoeff = 1.2*m   # increase in height when jumping while sprinting
    #frictionCoeff = 3*m       # acceleration of friction when not going left/right as a multiple of aRun
    #vFallMax = 0.65*m         # maximum speed when falling
    #aFall = 0.0025*m          # acceleration when falling

    doneUp = False
    doneDown = False

    client = connections[connsId].client

    try:
        dat = client.recv(1024)
        if not dat:
            connections[connsId].terminate()
            players[playerId].isInGame = False
        else:
            sprintTimer = [None, None, None]
            sprintCoeff = 1
            disableRunAccTimer = 0.1

            client.sendall(pickle.dumps([games[gameId].arena, playerId]))
            dat = client.recv(1024)

            while True:
                startTime = time.time()

                client.sendall(pickle.dumps([games[gameId], players]))

                #receive data
                dat = client.recv(1024)
                if not dat:
                    connections[connsId].terminate()
                    players[playerId].isInGame = False
                    break
                else:
                    with dataLock:
                        playerInputs[playerId] = pickle.loads(dat) # data now contains player inputs. physics engine is below

                        if playerInputs[playerId].up:
                            if players[playerId].grounded and not doneUp:
                                if players[playerId].sprinting: players[playerId].vel[1] = -1*vFallMax*jumpCoeff*jumpSprintCoeff
                                else: players[playerId].vel[1] = -1*vFallMax*jumpCoeff
                                players[playerId].grounded = False
                            elif players[playerId].walled != 0 and not doneUp:
                                players[playerId].vel[1] = -1*vFallMax*jumpCoeff
                                players[playerId].vel[0] =  players[playerId].walled*vRunMax*jumpCoeff
                                players[playerId].walled = 0
                                disableRunAccTimer = time.time()
                        if not players[playerId].sprinting and (playerInputs[playerId].left or playerInputs[playerId].right):
                            if sprintTimer[0] and time.time() - sprintTimer[1] < 0.15 and sprintTimer[2]:
                                if (playerInputs[playerId].left and sprintTimer[0] == "left") or (playerInputs[playerId].right and sprintTimer[0] == "right"):
                                    print("sprinting!")
                                    players[playerId].sprinting = True
                                    sprintCoeff = vSprintCoeff
                                    sprintTimer = [None, None, None]
                            else:
                                if playerInputs[playerId].right:
                                    sprintTimer = ["right", time.time(), None]
                                elif playerInputs[playerId].left:
                                    sprintTimer = ["left", time.time(), None]

                        if sprintTimer[0] == "left" and not playerInputs[playerId].left: sprintTimer[2] = True
                        if sprintTimer[0] == "right" and not playerInputs[playerId].right: sprintTimer[2] = True
                        if sprintTimer[0] and players[playerId].walled: sprintTimer[0] = None

                        if playerInputs[playerId].up: doneUp = True
                        else: doneUp = False
                        if playerInputs[playerId].down: doneDown = True
                        else: doneDown = False

                        if time.time() - disableRunAccTimer >= 0.1:
                            if playerInputs[playerId].left and players[playerId].vel[0] - (aRun*timeFactor*sprintCoeff) > -1*vRunMax*sprintCoeff:
                                players[playerId].vel[0] -= sprintCoeff*aRun * timeFactor
                            if playerInputs[playerId].right and players[playerId].vel[0] + (aRun*timeFactor*sprintCoeff) < vRunMax*sprintCoeff:
                                players[playerId].vel[0] += sprintCoeff*aRun * timeFactor

                        if not players[playerId].grounded:
                            players[playerId].vel[1] += aFall * timeFactor
                        if players[playerId].grounded:
                            if players[playerId].vel[0] > 0 and not (playerInputs[playerId].right or playerInputs[playerId].left):
                                if players[playerId].vel[0] - aRun*frictionCoeff * timeFactor >= 0: players[playerId].vel[0] -= aRun*frictionCoeff * timeFactor
                                else: players[playerId].vel[0] = 0
                            elif players[playerId].vel[0] < 0 and not (playerInputs[playerId].right or playerInputs[playerId].left):
                                if players[playerId].vel[0] + aRun*frictionCoeff * timeFactor <= 0: players[playerId].vel[0] += aRun*frictionCoeff * timeFactor
                                else: players[playerId].vel[0] = 0

                        if not (playerInputs[playerId].right or playerInputs[playerId].left) or players[playerId].walled:
                            players[playerId].sprinting = False
                            sprintCoeff = 1

                        players[playerId].grounded = False
                        players[playerId].walled = 0
                        collisionInfo = collidePlayer.collision(players[playerId].pos[0] + players[playerId].vel[0], players[playerId].pos[1] + players[playerId].vel[1], players[playerId].pos[0] + players[playerId].vel[0] + 39, players[playerId].pos[1] + players[playerId].vel[1] + 79, 40)
                        #collisionInfo = collidePlayer.collision(players[playerId].pos[0], players[playerId].pos[1], players[playerId].pos[0] + 40, players[playerId].pos[1] + 80, 40)
                        if bool(collisionInfo[0]): # if colliding
                            if bool(collisionInfo[1]): players[playerId].vel[0] = 0
                            if bool(collisionInfo[2]): players[playerId].vel[1] = 0
                            players[playerId].pos[0] = collisionInfo[3]
                            players[playerId].pos[1] = collisionInfo[4]
                        players[playerId].walled = collisionInfo[6]
                        players[playerId].grounded = bool(collisionInfo[5])

                        players[playerId].pos[0] += players[playerId].vel[0] * timeFactor
                        players[playerId].pos[1] += players[playerId].vel[1] * timeFactor

                while time.time() - startTime < tickInterval: pass
    except socket.error:
        connections[connsId].terminate()
        players[playerId].isInGame = False

levels = []
levels.append(Level("testlevel3", dire))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as host:
    host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 52971
    host.bind(("0.0.0.0", port))
    host.listen(64)
    print("Listening on port", port)

    #starts a new thread where the host can input commands to control what the server does
    ntrd = threading.Thread(target=hostInput)
    ntrd.daemon = True
    ntrd.start()

    idCounter = 0
    while True:
        #accepts the connection and adds it to the active connections array
        conn, addr = host.accept()
        print("New connection: ", addr)

        randint = random.randint(10000, 99999)
        while any(Connection.username == randint for Connection in connections):
            randint = random.randint(10000, 99999)

        connections.append(Connection(conn, randint, True, len(connections)))

        #starts a new thread which manages the new connection
        ntrd = threading.Thread(target=lobbyClientManager, args=[conn, idCounter]) #id counter is the index position of the client in connections[]
        ntrd.daemon = True
        ntrd.start()

        idCounter += 1
