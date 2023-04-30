from random import choice
import keyboard
import pygame
from copy import deepcopy
import time
from os import system as ossystem
import tkinter as tk
import itertools
from bs4 import BeautifulSoup

#if you're looking to modify something, it's probably here
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

def generate_permutations(bag, permutation_length):
    elements = list(bag)

    if elements and elements[0] == '^':
        # Negate the list of elements
        elements = [p for p in "IOSZJLT" if p not in elements[1:]]
    else:
        elements = elements[1:-1] if elements[0] == '[' and elements[-1] == ']' else elements

    permutations = [[]]
    result = set()

    # Generate all permutations of the given length
    for i in range(permutation_length):
        permutations = [p + [e] for p in permutations for e in elements if e not in p]

    # Convert each permutation back to a string and add to the result set
    for p in permutations:
        result.add(''.join(p))

    # Convert the result set to a list and return it
    return list(result)

def combine_lists(lists):
    if not lists:
        return []

    result = []

    def combine(index, current):
        if index == len(lists):
            result.append(''.join(current))
            return
        for i in range(len(lists[index])):
            combine(index + 1, current + [lists[index][i]])

    combine(0, [])
    return result

def piececount(string):
    count = 0
    if("^" in string):
        string = [p for p in "IOSZJLT" if p not in string[string.index("^"):]]
    for char in string:
        if(char in "IOSZJLT"):
            count += 1
    return count

def sfinder_all_permutations(input_str):
    inputs = input_str.split(',')

    # Generate all permutations for each input
    permutations = []
    for input_str in inputs:
        input_str = input_str.replace("^", "[^]").replace("!", "p" + str(piececount(input_str)))
        if(not "p" in input_str):
            input_str += "p1"
        bag_with_brackets, permutation_length = input_str.split('p')
        if not permutation_length:
            permutation_length = 1

        bag = bag_with_brackets.replace('*', '[IOSZJLT]').replace('[','').replace(']','').upper()

        permutations.append(generate_permutations(bag, int(permutation_length)))

    return combine_lists(permutations)

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
defaultboardcharacter = "_"
board = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]
nopieceboard = deepcopy(board)
allboards = []
startx = 150
starty = 180
blocksize = 32
blockwidth = 1

debug = False
def system(command):
    global lastcommand
    if(debug):
        print(command)
    ossystem(command)

#<--Ezsfinder Jumping Point-->
#default values
parameters = [
["sfinder_fed_queue", "p", "*p7"],
["clear", "c", 4],
['saves', 'I||O||J||L||T||S||Z'],
['initial_b2b', "i_b2b", False],
['initial_combo', "i_cb", 0],
['b2b_end_bonus', 0],
['fill', 'I'],
['margin', 'O'],
['exclude', 'none'],
['second_queue', False],
['pieces_used', 3],
["cover_fumens", False],
["kicktable", "kicks/jstris180.properties"],
["mode", "normal"]
]

for i in parameters:
    exec("%s='%s'" % (i[0], i[-1]))

def chance():
    system(f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {sfinder_fed_queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    output = open("ezsfinder.txt").read()
    try:
        print(output[output.find("success"):output.find("success") + 20].split()[2])
    except:
        print("Something went wrong. Read the error message in console, and try again QwQ")

def minimals():
    system(f"java -jar sfinder.jar path -f csv -k pattern --tetfu {fumen} --patterns {sfinder_fed_queue} --clear {clear} -K kicks/jstris180.properties -d 180> ezsfinder.txt")
    system("sfinder-minimal output/path.csv > ezsfinder.txt")
    system("py true_minimal.py")

def special_minimals(minimal_type):
    system(f"java -jar sfinder.jar path -t {fumen} -p {sfinder_fed_queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    with open('output/path_unique.html', encoding = "utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    allfumen = soup.find('a')['href']
    allfumen = allfumen.replace("http://fumen.zui.jp/?", "")
    system(f"node glueFumens.js {allfumen} > input/field.txt")
    system(f"java -jar sfinder.jar cover -p {sfinder_fed_queue} -M {minimal_type} -K kicks/jstris180.properties -d 180> ezsfinder.txt")
    system("cover-to-path.py > ezsfinder.txt")
    system("sfinder-minimal output/cover_to_path.csv> ezsfinder.txt")
    system("true_minimal.py")

def t_spin_minimals():
    special_minimals("tsm")

def tetris_minimals():
    special_minimals("tetris")

def get_score():
    system(f"java -jar sfinder.jar path -t {fumen} -p {sfinder_fed_queue} --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    system(f"node avg_score_ezsfinderversion.js queue={sfinder_fed_queue} initialB2B={'false' if initial_b2b == 'false' else 'true'} initialCombo={initial_combo} b2bEndBonus={b2b_end_bonus} > ezsfinder.txt")
    score = open("ezsfinder.txt").read().splitlines()
    printingscores = True
    for v, i in enumerate(score):
        if(i == "{"):
            printingscores = False
        if(printingscores):
            print("There are %s queues that allow you to get %s" % (i.split(": ")[1], i.split(": ")[0]))
        if("average_covered_score" in i):
            print("On average, when the setup has a perfect clear, you would score %s points."% round(float(i.split(": ")[1][:-1]), 2))
            print("Factoring in pc chance (%s%%), the average score is %s" % (int(score[v + 1].split(": ")[1][:-1]) / int(score[-1]) * 100, round(float(i.split(": ")[1][:-1]) / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]), 2)))

def pc_finder():
    global visualizeboard, lastcommand
    count = 0
    highestvalue = 0
    for rowindex, row in enumerate(nopieceboard):
        if(highestvalue != 0):
            break
        for value in row:
            if(value != defaultboardcharacter):
                highestvalue = boardheight - rowindex
                break

    system(f"java -jar sfinder.jar path -t {fumen} -p {currentpiece + holdpiece + ','.join(queue)} --clear {highestvalue} > ezsfinder.txt")

    with open('output/path_unique.html', 'r', encoding = "utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    solutions = []

    for link in soup.find_all('a')[1:]:
        href = link.get('href')
        if href.startswith('http://fumen.zui.jp/?'):
            pieces = ''.join([i[0] for i in link.get_text().split(' ')])
            solutions.append([href, pieces])

    if(solutions != []):
        visualizeboard = choice(solutions)[0]
    else:
        lastcommand = "No solution, sorry"

pygame.init()
s = pygame.display.set_mode((boardlength * blocksize + 10 * blocksize + 600, boardheight * blocksize + 8 * blocksize))
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
GARBAGE = (128, 128, 128)
BLACK = (0, 0, 0)

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
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ],
        'color': CYAN,
        'spawnposition' : 2,
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
    'G': {
        'color': GARBAGE
    },
    defaultboardcharacter : {
        'shape' : [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ],
        'color': BLACK
    }
}


def loadtable(file):
    cardinals = "NESW"
    kicktable = open(file).read().splitlines()
    for kicklist in kicktable:
        if(kicklist != ""):
            piece = kicklist[0]
            rotation = [str(cardinals.index(i)) for i in kicklist.split(".")[1].split("=")[0]]
            rotation = ''.join(rotation)
            allkicks = kicklist.split("=")[1].replace("(", "[").replace(")", "], ")[:-2].replace("@", "")

            if("&" in allkicks):
                callpiece = allkicks.split(".")[0][1]
                callrotation = [str(cardinals.index(i)) for i in allkicks.split(".")[1]]
                callrotation = ''.join(rotation)
                allkicks = str(pieces[callpiece]["srs"][callrotation])

            allkicks = list(eval(allkicks))
            pieces[piece]["srs"][rotation] = allkicks

loadtable("kicks/tetrio180.properties")

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

def putpiece(piece, rotation, column, row, board = board, ghost = False):
    if(placeable(piece, rotation, column, row)):
        currentpieceboard = pieces[piece]["shape"].copy()

        for i in range(rotation):
            currentpieceboard = rotate(currentpieceboard)

        for piecerowindex, piecerow in enumerate(currentpieceboard):
            for piececolumnindex, piecevalue in enumerate(piecerow):
                if(piecevalue == 1):
                    if(ghost):
                        board[row + piecerowindex][column + piececolumnindex] = piece.lower()
                    else:
                        board[row + piecerowindex][column + piececolumnindex] = piece

def drawghostpiece():
    global currentpiece, currentpiecerotation, currentpiecex, currentpiecey, allboards, piecesplaced, bag
    ghosty = currentpiecey
    while placeable(currentpiece, currentpiecerotation, currentpiecex, ghosty):
        ghosty += 1

    ghosty -= 1
    putpiece(currentpiece, currentpiecerotation, currentpiecex, ghosty, board, True)

visualizeboard = ""
knownfumens = []
knownfumenboards = []

def drawvisualizer(loadfumen):
    global board
    if(loadfumen in knownfumens):
        fulllengthboard = knownfumenboards[knownfumens.index(loadfumen)]
    else:
        system(f"node decode.js {loadfumen} > ezsfinder.txt")
        tempboard = open("ezsfinder.txt").read()
        tempboard = tempboard.replace("_", defaultboardcharacter).replace("X", "G")
        tempboard = tempboard.splitlines()
        fulllengthboard = []
        for i in range(boardheight - len(tempboard)):
            fulllengthboard.append([defaultboardcharacter for j in range(boardlength)])
        for i in tempboard:
            fulllengthboard.append([char.lower() for char in i])

        knownfumens.append(loadfumen)
        knownfumenboards.append(fulllengthboard)

    board = deepcopy(fulllengthboard)

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
            facing = [[1, 0, 1],
                      [0, 0, 0],
                      [0, 0, 0]]

            for i in range(currentpiecerotation):
                facing = rotate(facing)

            corners = 0
            facingcorners = 0

            for xoffset in range(0, 3, 2):
                for yoffset in range(0, 3, 2):
                    if(currentpiecey + yoffset <= boardheight and currentpiecex + xoffset <= boardlength):
                        if(nopieceboard[currentpiecey + yoffset][currentpiecex + xoffset] != defaultboardcharacter):
                            corners += 1
                            if(facing[yoffset][xoffset] == 1):
                                facingcorners += 1
                    else:
                        if(nopieceboard[currentpiecey + yoffset][currentpiecex + xoffset] != defaultboardcharacter):
                            corners += 1

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

ogbag = [char for char in "ISZJLOT"]
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
    kicks = pieces[currentpiece]["srs"][str(currentpiecerotation) + str((currentpiecerotation + rotation) % 4)]
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
    global currentpiece, currentpiecerotation, currentpiecex, currentpiecey, allboards, piecesplaced, bag, visualizeboard
    visualizeboard = ""
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
    clearscreen(-3, -3, 6, 3)
    drawinfopieces(-3, -3, holdpiece)

running = True

def grid(startx, starty, boardlength, boardheight, blocksize, blockwidth):
    for i in range(startx, startx + (boardlength * blocksize), blocksize):
        for j in range(starty, starty + (boardheight * blocksize), blocksize):
            rect = pygame.Rect(i, j, blocksize, blocksize)
            pygame.draw.rect(s, (200, 200, 200), rect, blockwidth)

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

tetrominoes = f"IZSJLTOG{defaultboardcharacter}"
piece = 0
smaller = False
filledpieces = []
xlocation = 8

def createcolorsquares():
    for v, i in enumerate(tetrominoes):
        blockrenderer(boardlength + xlocation, v, pieces[i]["color"])

    blockrenderer(boardlength + xlocation, len(pieces) + 4, (0, 0, 255))

def createsettextboxes():
    for box in textvariables:
        settextbutton(box[0], str(eval(box[4])), box[1], box[2], box[3], 24)

def settextbutton(text, subtext, x, y, color, size):
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, j + y, color)

    font = pygame.font.SysFont(None, size)
    pytext = font.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def grayoutboard():
    for piecerowindex, piecerow in enumerate(nopieceboard):
        for piececolumnindex, piecevalue in enumerate(piecerow):
            if(piecevalue != defaultboardcharacter):
                nopieceboard[piecerowindex][piececolumnindex] = "G"

def truefalsebutton(text, x, y, value):
    for i in range(-3, 3, 1):
        blockrenderer(x + i, y - 1, RESET)
    font = pygame.font.SysFont(None, 24)
    pytext = font.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (1 * blocksize) - textwidth/2, starty + (y - 1 * blocksize)))

    blockrenderer(x + 1, y, RED)
    blockrenderer(x, y, GARBAGE)

    if(value == False or value == "False"):
        blockrenderer(x + 1, y, RED)
        blockrenderer(x, y, GARBAGE)
    else:
        blockrenderer(x, y, GREEN)
        blockrenderer(x + 1, y, GARBAGE)

def createsfinderboxes():
    for box in ezsfindervariables:
        setezsfinderbutton(box[0], "deprecated", box[1], box[2], box[3], 24)

def createtruefalse():
    for truefalse in truevariables:
        truefalsebutton(truefalse[0], truefalse[1], truefalse[2], truefalse[3])

def setezsfinderbutton(text, subtext, x, y, color, size):
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, j + y, color)

    font = pygame.font.SysFont(None, size)
    pytext = font.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def setqueuebutton():
    x = boardlength + 2
    y = -2
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, y + j, RESET)

    font = pygame.font.SysFont(None, 24)
    pytext = font.render("Set game queue", True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def setheldpiece():
    x = -4
    y = -5

    font = pygame.font.SysFont(None, 24)
    pytext = font.render("Set the held piece", True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def set_variable(variable_name):
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window

    # Create tkinter window with larger size
    window = tk.Toplevel()
    window.title("Set Variable")
    window.geometry("300x100")  # Set window size to 300x100

    # Create label
    label = tk.Label(window, text=f"Set the value of {variable_name}")
    label.pack()

    # Create textbox
    textbox = tk.Entry(window)
    textbox.insert(-1, eval(variable_name))
    textbox.pack()
    # Function to set the variable and close the window
    def set_value():
        global_dict = globals()  # Get the global dictionary
        global_dict[variable_name] = textbox.get()  # Set the variable in the global dictionary
        window.destroy()
        root.quit()

    # Bind Enter key to set_value function
    textbox.bind('<Return>', lambda event: set_value())

    # Protocol handler for window close event
    window.protocol("WM_DELETE_WINDOW", set_value)

    window.mainloop()  # Start the tkinter event loop

def set_queue():
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window

    # Create tkinter window with larger size
    window = tk.Toplevel()
    window.title("Set Variable")
    window.geometry("300x100")  # Set window size to 300x100

    # Create label
    label = tk.Label(window, text=f"Set the queue")
    label.pack()

    # Create textbox
    textbox = tk.Entry(window)
    textbox.insert(-1, ','.join(queue))
    textbox.pack()
    # Function to set the variable and close the window
    def set_value():
        global queue, currentpiece, bag
        try:
            allqueues = sfinder_all_permutations(textbox.get())
            queue = [char for char in choice(allqueues)]
            currentpiece = queue[0]
            queue.pop(0)
            bag = deepcopy(ogbag)
            while(len(queue) < 5):
                    queue.append(piecepick())
        except:
            pass
        window.destroy()
        root.quit()

    # Bind Enter key to set_value function
    textbox.bind('<Return>', lambda event: set_value())

    # Protocol handler for window close event
    window.protocol("WM_DELETE_WINDOW", set_value)

    window.mainloop()  # Start the tkinter event loop

def set_hold():
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window

    # Create tkinter window with larger size
    window = tk.Toplevel()
    window.title("Set Variable")
    window.geometry("300x100")  # Set window size to 300x100

    # Create label
    label = tk.Label(window, text=f"Set the held piece")
    label.pack()

    # Create textbox
    textbox = tk.Entry(window)
    textbox.insert(-1, holdpiece)
    textbox.pack()
    # Function to set the variable and close the window
    def set_value():
        global holdpiece
        clearscreen(-3, -3, 6, 3)
        if(textbox.get() == ""):
            holdpiece = ""
        else:
            holdpiece = textbox.get()[0].upper()
            drawinfopieces(-3, -3, holdpiece)
        window.destroy()
        root.quit()

    # Bind Enter key to set_value function
    textbox.bind('<Return>', lambda event: set_value())

    # Protocol handler for window close event
    window.protocol("WM_DELETE_WINDOW", set_value)

    window.mainloop()  # Start the tkinter event loop

lastcommand = "No command yet"

#submission box jumping point
ezsfinderboxx = -4
helpbuttonboxx = boardlength + 10
ezsfindervariables = [
["Chance", ezsfinderboxx, 0, RED, "chance"],
["Minimals", ezsfinderboxx, 2, BLUE, "minimals"],
["T-Spin Minimals", ezsfinderboxx, 4, RED, "t_spin_minimals"],
["Tetris Minimals", ezsfinderboxx, 6, BLUE, "tetris_minimals"],
["Score", ezsfinderboxx, 8, RED, "get_score"],
["PC finder", helpbuttonboxx, 10, RED, "pc_finder"]
]

textboxx = 20
textvariables = [
["Set fed queue", textboxx, 0, ORANGE, "sfinder_fed_queue"],
["Set clear", textboxx, 2, CYAN, "clear"],
["Initial Combo", textboxx, 4, ORANGE, "initial_combo"],
["B2B Bonus", textboxx, 6, CYAN, "b2b_end_bonus"]
]

truefalsex = 30
truevariables = [
["Initial b2b", truefalsex, 0, initial_b2b],
]

def drawlastcommand():
    global textboxx
    x = 14
    y = 13
    font = pygame.font.SysFont(None, 24)
    pytext = font.render(lastcommand, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    block = pygame.Rect(startx + (x * blocksize), starty + (y * blocksize), 20 * blocksize, 2 * blocksize)
    pygame.draw.rect(s, RESET, block)
    s.blit(pytext, (startx + (x * blocksize) + (1.5 * blocksize), starty + (y * blocksize) + (1 *  blocksize) - textheight/2 + 16, blocksize, blocksize))

def clearscreen(x, y, width, height):
    block = pygame.Rect(startx + (x * blocksize), starty + (y * blocksize), width * blocksize, height * blocksize)
    pygame.draw.rect(s, RESET, block)

def drawallpieces():
    global board, lastdrawn
    clearscreen(0, 0, boardlength + 6, boardheight)
    createtruefalse()
    drawlastcommand()
    drawghostpiece()

    if(visualizeboard != ""):
        drawvisualizer(visualizeboard)

    putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey, board)

    for boardcolumnindex, boardcolumn in enumerate(board):
        for boardrowindex, boardvalue in enumerate(boardcolumn):
            if(boardvalue != defaultboardcharacter):
                if(boardvalue == boardvalue.upper()):
                    blockrenderer(boardrowindex, boardcolumnindex, pieces[boardvalue]["color"])
                else:
                    blockrenderer(boardrowindex, boardcolumnindex, pieces[boardvalue.upper()]["color"], True)

    board = deepcopy(nopieceboard)

    if(len(queue) < 5):
        queue.append(piecepick())

    grid(startx, starty, boardlength, boardheight, blocksize, blockwidth)

    drawqueue()

def drawqueue():
    for pieceindex, piece in enumerate(queue[:5]):
        if(piece == "I"):
            drawinfopieces(pieceindex * 3 - 1, boardlength + 1 + (4 - len(pieces[piece]["shape"][0])), piece)
        else:
            drawinfopieces(pieceindex * 3, boardlength + 1 + (4 - len(pieces[piece]["shape"][0])), piece)

def reset():
    global holdpiece, currentpiece, queue, currentpiecerotation, currentpiecex, currentpiecey, nopieceboard, board, bag, score
    bag = deepcopy(ogbag)
    currentpiece = piecepick()
    queue = [piecepick() for i in range(5)]
    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    score = 0
    combocount = 0
    nopieceboard = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]
    board = deepcopy(nopieceboard)
    holdpiece = ""
    clearscreen(-3, -3, 6, 3)
    drawallpieces()

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

keyspressed = []

clock = pygame.time.Clock()

# Set the font for the fps display
font = pygame.font.SysFont('Arial', 30)

createsettextboxes()
createsfinderboxes()
createcolorsquares()
setqueuebutton()
setheldpiece()
drawvisualizer("v115@JhA8IeA8DeB8BeC8AeE8JeAgH")

while running:
    for key in controls:
        if(keyboard.is_pressed(key)):
            if(key in keyspressed):
                if(controls[key] in dohold):
                    if(eval(f"time.time() * 1000 > {dohold[controls[key]]['timer']} + {dohold[controls[key]]['delay']}")):
                        exec(f"{controls[key]}()")
                        drawallpieces()
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
            fumen = outputcode()
            pos = list(pygame.mouse.get_pos())
            pos[0] = (pos[0] - startx) // blocksize
            pos[1] = (pos[1] - starty) // blocksize

            if(pos[0] >= 0 and pos[0] < boardlength and pos[1] >= 0 and pos[1] < boardheight):
                nopieceboard[pos[1]][pos[0]] = tetrominoes[piece]

            if(pos[0] == boardlength + xlocation and pos[1] >= 0 and pos[1] < len(pieces)):
                piece = pos[1]

            if(pos[0] == boardlength + xlocation and pos[1] >= 0 and pos[1] == len(pieces) + 4):
                print(outputcode())

            for box in textvariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    set_variable(box[4])

            for box in ezsfindervariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    exec(f"{box[4]}()")

            for box in truevariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 1 and pos[1] == box[2]):
                    box[3] = not box[3]
                    createtruefalse()

            if(pos[0] >= boardlength + 2 and pos[0] <= boardlength + 5 and pos[1] >= -2 and pos[1] <= -1):
                set_queue()

            if(pos[0] >= -4 and pos[0] <= -1 and pos[1] >= -5 and pos[1] <= -4):
                set_hold()

            if(pos[0] >= boardlength + 6 and pos[0] <= boardlength + 9 and pos[1] >= len(tetrominoes) + 2 and pos[1] <= len(tetrominoes) + 3):
                grayoutboard()

        drawallpieces()

        if event.type == pygame.QUIT:
            running = False

    fps = int(clock.get_fps())

    # Render the fps text
    fps_text = font.render("FPS: {}".format(fps), True, (255, 255, 255))

    # Draw the fps text to the screen
    block = pygame.Rect(0, 0, 130, 40)
    pygame.draw.rect(s, RESET, block, blocksize - 1)
    s.blit(fps_text, (10, 10))

    # Tick the clock
    clock.tick(1000)
    pygame.display.update()
