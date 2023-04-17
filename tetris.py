from random import choice
import keyboard
import pygame
from copy import deepcopy
import time
from os import system
import tkinter as tk

# Create the main window
tkinter_screen = tk.Tk()
tkinter_screen.title("Extra input for queues and stuff")
tkinter_screen.geometry("400x300")

queuelabel = tk.Label(tkinter_screen, text = "Queue")
queuelabel.pack()

queuebox = tk.Entry(tkinter_screen)
queuebox.insert(0, "*p7")
queuebox.pack()

clearlabel = tk.Label(tkinter_screen, text = "Lines to be cleared")
clearlabel.pack()

clearbox = tk.Entry(tkinter_screen)
clearbox.insert(0, "4")
clearbox.pack()

das = 83
softdropdelay = 200

controls = {
"left" : "move_left",
"right" : "move_right",
"w" : "reset",
"up" : "clockwise_rotate",
"s" : "counterlockwise_rotate",
"d" : "full_rotate",
"x" : "harddrop",
"down" : "softdrop",
"z" : "hold",
}

def loadfumen(fumen):
    global nopieceboard
    if(not fumentoload == ""):
        system(f"node decode.js {fumen} > ezsfinder.txt")
        tempboard = open("ezsfinder.txt").read()
        tempboard = tempboard.replace("_", defaultboardcharacter)
        tempboard = tempboard.splitlines()
        fulllengthboard = []
        for i in range(boardheight - len(tempboard)):
            fulllengthboard.append([defaultboardcharacter for j in range(boardlength)])
        for i in tempboard:
            fulllengthboard.append([char for char in i])
        nopieceboard = deepcopy(fulllengthboard)
        drawallpieces()

fumentoload = ""
#fumentoload = "v115@fgzhBe3hCe4hAe4hBe2hCe3hAe4hAeyhJeAgH"
boardlength = 10
boardheight = 15
defaultboardcharacter = ","
board = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]
nopieceboard = deepcopy(board)
allboards = []
startx = 150
starty = 180
blocksize = 32
blockwidth = 2

pygame.init()
s = pygame.display.set_mode((boardlength * blocksize + 10 * blocksize + 300, boardheight * blocksize + 8 * blocksize))
s.fill((20, 20, 20))

#Define color codes
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 100, 0)
RESET = (20, 20, 20)

scorevalues = {
1 : 100,
2 : 300,
3 : 500,
4 : 800,
"t1" : 800,
"t2" : 1200,
"t3" : 1600,
}

# Define the pieces dictionary with color codes as keys
pieces = {
    'I': {
        'shape': [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        'color': CYAN,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [-1, 0], [2, 0], [-1, 0], [2, 0]],
            1 : [[-1, 0], [0, 0], [0, 0], [0, 1], [0, -2]],
            2 : [[-1, 1], [1, 1], [-2, 1], [1, 0], [-2, 0]],
            3 : [[0, 1], [0, 1], [0, 1], [0, -1], [0, 2]]
        }
    },
    'J': {
        'shape': [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ],
        'color': BLUE,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            1 : [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            2 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            3 : [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]]
        }
    },
    'L': {
        'shape': [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ],
        'color': ORANGE,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            1 : [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            2 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            3 : [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]]
        }
    },
    'O': {
        'shape': [
            [1, 1],
            [1, 1]
        ],
        'color': YELLOW,
        'spawnposition' : 4,
        'srs' : {
            0 : [[0, 0]],
            1 : [[0, -1]],
            2 : [[-1, -1]],
            3 : [[-1, 0]]
        }
    },
    'S': {
        'shape': [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ],
        'color': GREEN,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            1 : [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            2 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            3 : [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
        }
    },
    'T': {
        'shape': [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ],
        'color': MAGENTA,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            1 : [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            2 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            3 : [[0, 0], [-1, 0], [-1, -1], [0, 2]]
        }
    },
    'Z': {
        'shape': [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ],
        'color': RED,
        'spawnposition' : 3,
        'srs' : {
            0 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            1 : [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            2 : [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            3 : [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]]
        }
    },
    defaultboardcharacter : {
        'shape' : [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ],
        'color': RESET,
        'spawnposition' : 3
    }
}

def rotate(matrix):
    transposed = list(zip(*matrix))
    rotated = [list(row[::-1]) for row in transposed]
    return rotated

def placeable(piece, rotation, column, row):
    currentpieceboard = deepcopy(pieces[piece]["shape"])

    for i in range(rotation):
        currentpieceboard = rotate(currentpieceboard)

    for piecerowindex, piecerow in enumerate(currentpieceboard):
        for piececolumnindex, piecevalue in enumerate(piecerow):
            if(piecevalue == 1):
                if(column + piececolumnindex < 0 or row + piecerowindex < 0):
                    return False
                if(row + piecerowindex >= boardheight):
                    return False
                if(column + piececolumnindex >= boardlength):
                    return False
                if(nopieceboard[row + piecerowindex][column + piececolumnindex] != defaultboardcharacter):
                    return False
    return True

def putpiece(piece, rotation, column, row, board = board):
    if(placeable(piece, rotation, column, row)):
        currentpieceboard = pieces[piece]["shape"].copy()

        for i in range(rotation):
            currentpieceboard = rotate(currentpieceboard)

        for piecerowindex, piecerow in enumerate(currentpieceboard):
            for piececolumnindex, piecevalue in enumerate(piecerow):
                if(piecevalue == 1):
                    board[row + piecerowindex][column + piececolumnindex] = piece

def get_filled_rows(board):
    filled_rows = []
    for row in board:
        if all(square != defaultboardcharacter for square in row):
            filled_rows.append(board.index(row))
    return filled_rows

def clear_filled_rows(board):
    global combo, score, combocount, b2b
    gointob2b = False
    filled_rows = get_filled_rows(board)
    if(len(filled_rows) > 0):
        combo = True

        if(currentpiece == "T"):
            if(nopieceboard[currentpiecey][currentpiecex] != defaultboardcharacter):
                gointob2b = True
            if(currentpiecex + 2 < boardlength and nopieceboard[currentpiecey][currentpiecex + 2] != defaultboardcharacter):
                gointob2b = True
            if(tspinkick == True):
                gointob2b = True

        for row in filled_rows:
            del board[row]
            board.insert(0, [defaultboardcharacter for _ in range(boardlength)])
        score += tabulatescore(len(filled_rows), gointob2b)

    else:
        combo = False
        combocount = 0

combo = False
b2b = False
combocount = 0
score = 0
tspinkick = False

def tabulatescore(linescleared, activateb2b):
    global combo, combocount, b2b
    currentscore = scorevalues[linescleared]
    if(b2b):
        currentscore += (0.5 * scorevalues[linescleared])

    currentscore += combocount * 50

    if(linescleared == 4 or activateb2b):
        b2b = True
    else:
        b2b = False

    if(combo):
        combocount += 1

    return(int(currentscore))

ogbag = [char for char in "IOSZJLT"]
bag = deepcopy(ogbag)

def piecepick():
    global bag
    piecepicked = choice(bag)
    bag.remove(piecepicked)
    if(len(bag) == 0):
        bag = deepcopy(ogbag)
    return piecepicked

currentpiece = piecepick()
queue = [piecepick() for i in range(5)]
holdpiece = ""
currentpiecerotation = 0
currentpiecex = pieces[currentpiece]["spawnposition"]
currentpiecey = 0

def kicksubtract(kicktable1, kicktable2):
    subtractedkicktable = []
    for kick1, kick2 in zip(kicktable1, kicktable2):
        subtractedkicktable.append([kick1[0] - kick2[0], kick1[1] - kick2[1]])
    return subtractedkicktable

def rotatepiece(rotation):
    global currentpiecerotation, currentpiece, currentpiecex, currentpiecey, tspinkick
    plsbreak = False
    kicks = kicksubtract(pieces[currentpiece]['srs'][currentpiecerotation], pieces[currentpiece]['srs'][(currentpiecerotation + rotation) % 4])
    for kicknumber, offset in enumerate(kicks):
        if placeable(currentpiece, (currentpiecerotation + rotation) % 4, currentpiecex + offset[0], currentpiecey + (offset[1] * -1)):
            if(currentpiece == "T" and kicknumber > 0):
                tspinkick = True
            else:
                tspinkick = False
            #print(f"offset of {offset[0]}x and {(offset[1] * -1)}y works")
            currentpiecex += offset[0]
            currentpiecey += (offset[1] * -1)
            currentpiecerotation = (currentpiecerotation + rotation) % 4
            break

def clockwise_rotate():
    rotatepiece(1)

def counterlockwise_rotate():
    rotatepiece(-1)

def full_rotate():
    rotatepiece(2)

def move(distance):
    global currentpiecerotation, currentpiecex
    if placeable(currentpiece, currentpiecerotation, currentpiecex + distance, currentpiecey):
        currentpiecex += distance

def move_left():
    move(-1)

def move_right():
    move(1)

piecesplaced = 0
allboards = []
allboards.append(deepcopy(nopieceboard))

def harddrop():
    global currentpiece, currentpiecerotation, currentpiecex, currentpiecey, allboards, piecesplaced, bag
    while placeable(currentpiece, currentpiecerotation, currentpiecex, currentpiecey):
        currentpiecey += 1
    currentpiecey -= 1
    putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey, nopieceboard)
    clear_filled_rows(nopieceboard)
    piecesplaced += 1
    allboards.append(deepcopy(nopieceboard))
    currentpiece = queue[0]
    queue.pop(0)
    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    board = deepcopy(nopieceboard)
    drawallpieces()
    drawqueue()

def undo():
    global nopieceboard, board
    if(len(allboards) > 1):
        nopieceboard = deepcopy(allboards[-2])
        board = deepcopy(nopieceboard)
        drawallpieces()
        allboards.pop(-1)

def softdrop():
    global currentpiecey
    while placeable(currentpiece, currentpiecerotation, currentpiecex, currentpiecey):
        currentpiecey += 1
    currentpiecey -= 1
    drawallpieces()

def hold():
    global currentpiece, holdpiece, currentpiecerotation, currentpiecex, currentpiecey
    if(holdpiece == ""):
        holdpiece = currentpiece
        currentpiece = queue[0]
        queue.pop(0)
        queue.append(piecepick())
    else:
        holdpiece, currentpiece = currentpiece, holdpiece

    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    drawinfopieces(-3, -3, defaultboardcharacter)
    drawinfopieces(-3, -3, holdpiece)

running = True

def grid(startx, starty, boardlength, boardheight, blocksize, blockwidth):
    for i in range(startx, startx + (boardlength * blocksize), blocksize):
        for j in range(starty, starty + (boardheight * blocksize), blocksize):
            rect = pygame.Rect(i, j, blocksize, blocksize)
            pygame.draw.rect(s, (255, 255, 255), rect, blockwidth)

def blockrenderer(x, y, color, smaller = False):
    global startx, starty, blocksize, blockwidth
    if(smaller):
        block = pygame.Rect(startx + (x * blocksize) + blocksize // 4, starty + (y * blocksize) + blocksize // 4, blocksize // 2, blocksize // 2)
    else:
        block = pygame.Rect(startx + (x * blocksize), starty + (y * blocksize), blocksize, blocksize)
    pygame.draw.rect(s, color, block, blocksize - 1)

def writetext(x, y, text, size):
    global startx, starty, blocksize, blockwidth
    font = pygame.font.SysFont(None, size)
    pytext = font.render(text, True, (255, 255, 255))
    s.blit(pytext, (startx + (x * blocksize), starty + (y * blocksize), blocksize, blocksize))

def drawinfopieces(x, y, piece):
    currentpieceboard = pieces[piece]["shape"]

    for piecerowindex, piecerow in enumerate(currentpieceboard):
        for piececolumnindex, piecevalue in enumerate(piecerow):
            if(piecevalue == 1):
                blockrenderer(y + piececolumnindex, x + piecerowindex, pieces[piece]["color"])

filledpieces = []

piecesindex = {
    "I": (0, 255, 255),
    "Z": (255, 0, 0),
    "S": (0, 255, 0),
    "J": (0, 0, 255),
    "L": (255, 100, 0),
    "T": (255, 0, 255),
    "O": (255, 255, 0),
    "G": (156, 156 , 156),
    " ": (20, 20, 20)
}

tetrominoes = f"IZSJLTO{defaultboardcharacter}"
piece = 0
smaller = False
filledpieces = []
xlocation = 8

def createcolorsquares():
    for v, i in enumerate(piecesindex):
        blockrenderer(boardlength + xlocation, v, piecesindex[i])

    blockrenderer(boardlength + xlocation, len(pieces) + 4, (0, 0, 255))

boxes = [
["Percent", -3, 0, ORANGE, "chance"],
["test2", -3, 2, CYAN]
]

def createtextboxes():
    for box in boxes:
        textbutton(box[0], box[1], box[2], box[3], 24)

def textbutton(text, x, y, color, size):
    for i in range(3):
        for j in range(2):
            blockrenderer(x + i, j + y, color)

    font = pygame.font.SysFont(None, size)
    pytext = font.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (1.5 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def drawallpieces():
    global board
    createtextboxes()
    createcolorsquares()

    putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey, board)

    for boardcolumnindex, boardcolumn in enumerate(board):
        for boardrowindex, boardvalue in enumerate(boardcolumn):
            blockrenderer(boardrowindex, boardcolumnindex, pieces[boardvalue]["color"])

    grid(startx, starty, boardlength, boardheight, blocksize, blockwidth)

    board = deepcopy(nopieceboard)

    if(len(queue) < 5):
        queue.append(piecepick())

    blockrenderer(-3.2, 4, RESET)
    blockrenderer(-3.2, 5, RESET)
    blockrenderer(-3.2, 6, RESET)
    blockrenderer(-3.2, 7, RESET)
    drawqueue()

def drawqueue():
    for pieceindex, piece in enumerate(queue):
        drawinfopieces(-3 + pieceindex * 3, boardlength + 2, defaultboardcharacter)
        drawinfopieces(-3 + pieceindex * 3, boardlength + 2 + (4 - len(pieces[piece]["shape"][0])), piece)

def reset():
    global holdpiece, currentpiece, queue, currentpiecerotation, currentpiecex, currentpiecey, nopieceboard, board, bag, score
    bag = deepcopy(ogbag)
    currentpiece = piecepick()
    queue = [piecepick() for i in range(5)]
    holdpiece = ""
    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    score = 0
    combocount = 0
    nopieceboard = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]

    board = deepcopy(nopieceboard)
    drawallpieces()
    drawinfopieces(-3, -3, defaultboardcharacter)

    for pieceindex, piece in enumerate(queue):
        drawinfopieces(-3 + pieceindex * 3, boardlength + 2, defaultboardcharacter)

putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey)
loadfumen(fumentoload)
drawallpieces()

dastimer = 0
softdroptimer = 0

dohold = {
"move_left" : {
    "timer" : "dastimer",
    "delay" : "das"
},
"move_right" : {
    "timer" : "dastimer",
    "delay" : "das"
},
"softdrop" : {
    "timer" : "softdroptimer",
    "delay" : "softdropdelay"
},
}

writetext(-3.2, -5, "Held Piece", 36)
writetext(boardlength + 2, -5, "Queue", 36)

piece = 1

def outputcode():
    temp = ""
    for row in board:
        for piece in row:
            if(piece == defaultboardcharacter):
                temp += "_"
            else:
                temp += piece
    system(f"node encode.js {temp} > ezsfinder.txt")
    outputfumen = open("ezsfinder.txt").read()[:-1]
    return(outputfumen)

def chance():
    queue = queuebox.get()
    clear = clearbox.get()
    print(queue, clear, outputcode())
    print(f"java -jar sfinder.jar percent --tetfu {outputcode()} --patterns {queue} --clear 4 -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    system(f"java -jar sfinder.jar percent --tetfu {outputcode()} --patterns {queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    output = open("ezsfinder.txt").read()
    print(output[output.find("success"):output.find("success") + 20].split()[2])

keyspressed = []

while running:
    for key in controls:
        if(keyboard.is_pressed(key)):
            drawallpieces()
            if(key in keyspressed):
                if(controls[key] in dohold):
                    if(eval(f"time.time() * 1000 > {dohold[controls[key]]['timer']} + {dohold[controls[key]]['delay']}")):
                        exec(f"{controls[key]}()")
            else:
                exec(f"{controls[key]}()")
                keyspressed.append(key)
                drawallpieces()
                if(controls[key] in dohold):
                    exec(f"{dohold[controls[key]]['timer']} = time.time() * 1000")
        else:
            if(key in keyspressed):
                keyspressed.remove(key)

    for event in pygame.event.get():
        if pygame.mouse.get_pressed()[0]:
            pos = list(pygame.mouse.get_pos())
            pos[0] = (pos[0] - startx) // blocksize
            pos[1] = (pos[1] - starty) // blocksize

            if(pos[0] >= 0 and pos[0] < boardlength and pos[1] >= 0 and pos[1] < boardheight):
                nopieceboard[pos[1]][pos[0]] = tetrominoes[piece]

            if(pos[0] == boardlength + xlocation and pos[1] >= 0 and pos[1] < len(pieces)):
                piece = pos[1]

            if(pos[0] == boardlength + xlocation and pos[1] >= 0 and pos[1] == len(pieces) + 4):
                outputcode()

            for box in boxes:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 2 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    print(f"{box[4]}()")
                    exec(f"{box[4]}()")

            drawallpieces()
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    tkinter_screen.update()
