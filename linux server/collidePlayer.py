import struct

cdef int x
cdef int sidelen # stores width & height of a tile
cdef int lvl[100][2]
cdef int lenlvl = 0

cdef int a
lenlvl = 32
for a in range(32):
    lvl[a][0] = 40*a
    lvl[a][1] = 200

def loadlvl(dire, name):
    global lvl, lenlvl
    lenlvl = 0
    
    lowest = -1000000
    f = open(dire + "\\data\\" + name + ".lvl", "rb") #opens test level file
    filecontent = f.read()
    a = struct.unpack("i", filecontent[:4])[0] #reads how many tiles (walls) to read
    for i in range(a):
        pos = struct.unpack("ff", filecontent[(8 * i + 4):(8 * (i + 1) + 4)]) #creates all tile (wall) sprites and adds them to the group
        if pos[1] > lowest: lowest = pos[1] #finds the lowest tile to set oob boundary
        lvl[lenlvl][0] = pos[0]*40
        lvl[lenlvl][1] = pos[1]*40
        lenlvl += 1
    f.close()

#returns which direction of motion should be set to 0
def collision(float tlx, float tly, float brx, float bry, int dim): # dim is the width/height of each tile (both always the same so only need 1 variable)
    global lvl

    # loop variables
    cdef int i
    cdef int j

    # bools; 0 or 1
    cdef int xSetZero = 0
    cdef int ySetZero = 0
    cdef int isColliding = 0
    cdef int grounded = 0
    cdef int walled = 0

    # non-bools
    cdef int sideBack = -1 # testing variable
    
    cdef int collideCount = 0
    cdef float s[4]
    cdef float xNew = tlx # x coord of topleft of player
    cdef float yNew = tly # y coord of topleft of player
    cdef int resetSide
    cdef float smallestSub
    cdef int vcounter
    cdef int hcounter
    cdef int width = int(round(brx - tlx)) + 1
    cdef int height = int(round(bry - tly)) + 1
    #print(width, height)

    for i in range(lenlvl): # if any of these are positive then an intersection is possible
        resetSide = -1
        smallestSub = 1000000
        hcounter = 0
        vcounter = 0
        s = [brx - lvl[i][0], (lvl[i][0] + dim) - tlx, (lvl[i][1] + dim) - tly, bry - lvl[i][1]]
        #print(s)
        sa = [lvl[i][0] - int(round(width)), lvl[i][0] + dim, lvl[i][1] + dim, lvl[i][1] - int(round(height))]
                    
        # submerged right
        if s[0] >= 0 and s[0] <= width:
            smallestSub = s[0]
            resetSide = 0
            hcounter += 1
        
        # submerged left
        if s[1] >= 1 and s[1] <= width:
            if s[1] < smallestSub:
                smallestSub = s[1]
                resetSide = 1
            hcounter += 1
            
        # submerged up
        if s[2] >= 1 and s[2] <= height:
            if s[2] < smallestSub:
                smallestSub = s[2]
                resetSide = 2
            vcounter += 1
            
        # submerged down
        if s[3] >= 0 and s[3] <= height:
            if s[3] < smallestSub:
                resetSide = 3
            vcounter += 1

        if hcounter > 0 and vcounter > 0:
            collideCount += 1
            isColliding = 1
            if (resetSide == 0 or resetSide == 1) and hcounter < 2:
                xSetZero = 1
                xNew = sa[resetSide]
            if (resetSide == 2 or resetSide == 3) and vcounter < 2:
                ySetZero = 1
                yNew = sa[resetSide]
                sideBack = resetSide
                if resetSide == 3: grounded = 1

        if hcounter > 0 and s[3] >= -1 and s[3] < 0:
            grounded = 1
        if vcounter == 2 and s[0] >= -1 and s[0] < 0:
            walled = -1
        if vcounter == 2 and s[1] >= -1 and s[1] < 0:
            walled = 1

    return(isColliding, xSetZero, ySetZero, xNew, yNew, grounded, walled, collideCount, sideBack)
