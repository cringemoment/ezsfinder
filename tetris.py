from random import choice, randint, seed
import pygame
from copy import deepcopy
import time
from os import system as ossystem, getcwd
import tkinter as tk
import itertools
from bs4 import BeautifulSoup
from collections import OrderedDict

#if you're looking to modify something, it's probably here
das = 83
arr = 0
softdropdelay = 0
softdropspeed = 0
loadsetups = False #Loading setups take ages so disable this if you don't want it
boardlength = 10
boardheight = 15
defaultboardcharacter = "_"
board = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]
nopieceboard = deepcopy(board)
allboards = []
startx = 180
starty = 180
blocksize = 32
blockwidth = 1
pygame.font.init()
normalfont = pygame.font.Font(f'fonts\ComicMono.ttf', blocksize - 14)
statfont = pygame.font.Font(f'fonts\ComicMono.ttf', blocksize - 12)

startingseed = randint(-10000, 100000000)
piecesplaced = 0
controls = {}

configfile = open("settings.txt").read().splitlines()
if(configfile == []):
    controls = {
    pygame.K_LEFT : "move_left",
    pygame.K_RIGHT : "move_right",
    pygame.K_w : "reset",
    pygame.K_UP : "cw_rotate",
    pygame.K_s : "ccw_rotate",
    pygame.K_d : "full_rotate",
    pygame.K_x : "harddrop",
    pygame.K_DOWN : "softdrop",
    pygame.K_z : "hold",
    pygame.K_t : "undo",
    pygame.K_y : "redo"
    }

configfile = open("settings.txt").read().splitlines()
handlingfile = open("handling.txt").read().splitlines()
settingorder = open("defaultsettingorder.txt").read().splitlines()
configfile = sorted(configfile, key = lambda x: settingorder.index(x.split("-")[1]))

def savecontrols():
    writeto = open("settings.txt", "w")
    handlingto = open("handling.txt", "w")
    for control in controls:
        writeto.write(f"{control}-{controls[control]}\n")

    handlingto.write(str(das))
    handlingto.write("\n")
    handlingto.write(str(arr))
    handlingto.write("\n")
    handlingto.write(str(softdropdelay))
    handlingto.write("\n")
    handlingto.write(str(softdropspeed))
    handlingto.write("\n")
    handlingto.write(str(loadsetups))
    handlingto.write("\n")

def loadcontrols():
    global das, arr, softdropdelay, softdropspeed, loadsetups
    for i in configfile:
        controls[int(i.split("-")[0])] = i.split("-")[1]

    das = int(handlingfile[0])
    arr = int(handlingfile[1])
    softdropdelay = int(handlingfile[2])
    softdropspeed = int(handlingfile[3])
    loadsetups = handlingfile[4] == "True"

    print(das)

loadcontrols()
controlslist = [controls[i] for i in controls]

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

def countpieces(string):
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
        input_str = input_str.replace("^", "[^]").replace("!", "p" + str(countpieces(input_str)))
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
    if(not fumen == ""):
        system(f"node decode.js {fumen} > ezsfinder.txt")
        tempboard = open("ezsfinder.txt").read()
        tempboard = tempboard.replace("_", defaultboardcharacter).replace("X", "G")
        tempboard = tempboard.splitlines()
        fulllengthboard = []
        if(tempboard == ['']):
            for i in range(boardheight):
                fulllengthboard.append([defaultboardcharacter for j in range(boardlength)])
        else:
            for i in range(boardheight - len(tempboard)):
                fulllengthboard.append([defaultboardcharacter for j in range(boardlength)])
            for i in tempboard:
                fulllengthboard.append([char for char in i])

        nopieceboard = deepcopy(fulllengthboard)
        drawallpieces()

extrax = 22
extray = 10

pygame.init()
s = pygame.display.set_mode((boardlength * blocksize + extrax * blocksize, boardheight * blocksize + extray * blocksize))
s.fill((20, 20, 20))

debug = True
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

def evaluatesave(save):
    piecessaveindex = {
    "S" : 0,
    "Z" : 0,
    "O" : 3,
    "J" : 1,
    "L" : 1,
    "I" : 4,
    "T" : 6
    }

    score = 0
    for piece in save:
        score += piecessaveindex[piece]

    if(save.count("J") + save.count("L") % 2 == 0):
        score += 8

    return score

def evaluatedpcsave(save):
    piecessaveindex = {
    "T" : 0,
    "J" : 1,
    "L" : 1,
    "S" : 2,
    "Z" : 2,
    "I" : 3,
    "O" : 4
    }

    score = 0
    for piece in save:
        score += piecessaveindex[piece]

    return score

def pc_finder():
    global visualizeboard, lastcommand
    count = 0
    startingheight = boardheight - 2
    highestvalue = startingheight

    for rowindex, row in enumerate(nopieceboard):
        if(highestvalue != startingheight):
            break
        for value in row:
            if(value != defaultboardcharacter and rowindex <= startingheight):
                highestvalue = rowindex
                break

    count = 0

    for i in range(boardheight - 1, -1, -1):
        for j in range(boardlength):
            if nopieceboard[i][j] == defaultboardcharacter:
                count += 1

        if count % 4 == 0 and i <= highestvalue: # check if count is divisible by 4
            highestvalue = boardheight - i
            break

    allpieces = currentpiece + holdpiece + ''.join(queue)

    if(len(bag) == 1):
        allpieces += bag[0]

    system(f"java -jar sfinder.jar path -t {fumen} -p {allpieces} --clear {highestvalue} > ezsfinder.txt")

    with open('output/path_unique.html', 'r', encoding = "utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    solutions = []

    for link in soup.find_all('a')[1:]:
        href = link.get('href')
        if href.startswith('http://fumen.zui.jp/?'):
            pieces = ''.join([i[0] for i in link.get_text().split(' ')])
            solutions.append([href, pieces])

    saves = []

    if(solutions != []):
        for solution in solutions:
            solutionfumen = solution[0]
            piecesused = solution[1]

            solutionallpieces = [char for char in allpieces.replace(",", "")]
            solutionpiecesused = [char for char in piecesused]
            pieceuseddontremove = deepcopy(piecesused)

            for pieceused in pieceuseddontremove:
                solutionpiecesused.remove(pieceused)
                try:
                    solutionallpieces.remove(pieceused)
                except ValueError:
                    lastcommand = "Errored. Place more pieces"
                    return False

            leftover = solutionallpieces + bag
            saves.append([solutionfumen, leftover, evaluatesave(leftover)])

        saves.sort(key=lambda x: int(x[2]) * -1)
        visualizeboard = saves[0][0]

    else:
        lastcommand = "No solution, sorry"

def dpc_save_finder():
    global visualizeboard, lastcommand
    count = 0
    startingheight = boardheight - 2
    highestvalue = startingheight

    for rowindex, row in enumerate(nopieceboard):
        if(highestvalue != startingheight):
            break
        for value in row:
            if(value != defaultboardcharacter and rowindex <= startingheight):
                highestvalue = rowindex
                break

    count = 0

    for i in range(boardheight - 1, -1, -1):
        for j in range(boardlength):
            if nopieceboard[i][j] == defaultboardcharacter:
                count += 1

        if count % 4 == 0 and i <= highestvalue: # check if count is divisible by 4
            highestvalue = boardheight - i
            break

    allpieces = currentpiece + holdpiece + ''.join(queue)

    if(len(bag) == 1):
        allpieces += bag[0]

    system(f"java -jar sfinder.jar path -t {fumen} -p {allpieces} --clear {highestvalue} > ezsfinder.txt")

    with open('output/path_unique.html', 'r', encoding = "utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    solutions = []

    for link in soup.find_all('a')[1:]:
        href = link.get('href')
        if href.startswith('http://fumen.zui.jp/?'):
            pieces = ''.join([i[0] for i in link.get_text().split(' ')])
            solutions.append([href, pieces])

    saves = []

    if(solutions != []):
        for solution in solutions:
            solutionfumen = solution[0]
            piecesused = solution[1]

            solutionallpieces = [char for char in allpieces.replace(",", "")]
            solutionpiecesused = [char for char in piecesused]
            pieceuseddontremove = deepcopy(piecesused)

            for pieceused in pieceuseddontremove:
                solutionpiecesused.remove(pieceused)
                try:
                    solutionallpieces.remove(pieceused)
                except ValueError:
                    lastcommand = "Errored. Place more pieces"
                    return False

            leftover = solutionallpieces + bag
            saves.append([solutionfumen, leftover, evaluatedpcsave(leftover)])

        saves.sort(key=lambda x: int(x[2]) * -1)
        visualizeboard = saves[0][0]

    else:
        lastcommand = "No solution, sorry"

def hold_reorders(queue):
    if len(queue) <= 1:
        return set(queue)  # base case

    result = set()

    a = hold_reorders(queue[1:])  # use first piece, work on the 2nd-rest
    for part in a:
        result.add(queue[0] + part)

    b = hold_reorders(queue[0] + queue[2:])  # use second piece, work on 1st + 3rd-rest
    for part in b:
        result.add(queue[1] + part)

    return list(result)

def getscore(queue, clear, fumen):
    holdqueues = hold_reorders(queue.replace(",", ""))
    queuefeed = open("queuefeed.txt", "w")
    for i in holdqueues:
        queuefeed.write(i + "\n")
    queuefeed.close()

    system(f"java -jar sfinder.jar cover -t {fumen} -pp queuefeed.txt > ezsfinder.txt")
    system(f'node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_end_bonus} fileType=cover fileName="output/cover.csv" > ezsfinder.txt')
    score = open("ezsfinder.txt").read().splitlines()
    printingscores = True
    for v, i in enumerate(score):
        if("average_covered_score" in i):
            return(round(float(i.split(": ")[1][:-1]) / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]), 2))

def cat_finder():
    global visualizeboard, lastcommand
    count = 0
    startingheight = boardheight - 2
    highestvalue = startingheight

    for rowindex, row in enumerate(nopieceboard):
        if(highestvalue != startingheight):
            break
        for value in row:
            if(value != defaultboardcharacter and rowindex <= startingheight):
                highestvalue = rowindex
                break

    count = 0

    for i in range(boardheight - 1, -1, -1):
        for j in range(boardlength):
            if nopieceboard[i][j] == defaultboardcharacter:
                count += 1

        if count % 4 == 0 and i <= highestvalue: # check if count is divisible by 4
            highestvalue = boardheight - i
            break

    allpieces = currentpiece + holdpiece + ''.join(queue)

    if(len(bag) == 1):
        allpieces += bag[0]

    system(f"java -jar sfinder.jar path -t {fumen} -p {allpieces} --clear {highestvalue} > ezsfinder.txt")

    with open('output/path_unique.html', 'r', encoding = "utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    solutions = []

    for link in soup.find_all('a')[1:]:
        href = link.get('href')
        if href.startswith('http://fumen.zui.jp/?'):
            pieces = ''.join([i[0] for i in link.get_text().split(' ')])
            solutions.append([href, pieces])

    saves = []

    if(solutions != []):
        for solution in solutions:
            solutionfumen = solution[0]
            piecesused = solution[1]

            system(f"node glueFumens.js {solutionfumen} > ezsfinder.txt")
            glued = open("ezsfinder.txt").read().replace("\n", "")

            solutionpiecesused = ','.join([char for char in piecesused])

            saves.append([solutionfumen, getscore(solutionpiecesused, highestvalue, glued)])

        saves.sort(key=lambda x: int(x[1]) * -1)

        visualizeboard = saves[0][0]

    else:
        lastcommand = "No solution, sorry"

allsetups = {}

if(loadsetups):
    print("Loading konbini setups")
    firstsetups = open("konbini/first.txt").read().splitlines()
    firstsetupscover6 = eval(open("konbini/first-covered-6.json").read())
    firstsetupscover7 = eval(open("konbini/first-covered-7.json").read())
    print("PC number 1 loaded")

    for i in range(2, 8):
        allsetups[i] = {}
        allsetups[i]["setups"] = open(f"konbini/setups{i}.txt").read().splitlines()
        allsetups[i]["cover"] = eval(open(f"konbini/setups{i}cover.json").read())
        print(f"PC number {i} loaded")

if(loadsetups):
    dpcsetups = open("konbini/dpc.txt").read().splitlines()
    dpccover = eval(open("konbini/dpccover.json").read())
    print(f"DPC setups loaded")

def unglue(glued):
    system(f"node unglueFumen.js --fu {glued} > ezsfinder.txt")
    return(open("ezsfinder.txt").read().replace("\n", ""))

def setup_finder():
    global visualizeboard, lastcommand
    if(nopieceboard != [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]):
        lastcommand = "This only works for empty boards"
        return False

    allpieces = currentpiece + holdpiece + ''.join(queue)
    if(len(bag) == 1):
        allpieces += bag[0]
    pcnumber = (5 * piecesplaced % 7) + 1
    pcpieces = [3, 7, 7, 8, 5, 7, 6, 3]

    if(pcnumber != 1 and holdpiece == ""):
        allpieces += (choice(bag))

    if(pcnumber == 1):
        if(len(allpieces) == 6):
            visualizeboard = unglue(firstsetups[firstsetupscover6[allpieces][0]])
        else:
            visualizeboard = unglue(firstsetups[firstsetupscover7[allpieces][0]])

    elif(pcnumber == 2 or pcnumber == 3):
        allpieces = [char for char in allpieces]

        piecesinused = ""
        if(allpieces[1] in allpieces[2:]):
            allpieces[0], allpieces[1] = allpieces[1], allpieces[0]

        allpieces = ''.join(allpieces)

        piececount = pcpieces[pcnumber]
        pckeypieces = allpieces[:piececount]
        pcsetups = allsetups[pcnumber]["setups"]
        pcsetupcovers = allsetups[pcnumber]["cover"]

        try:
            if(len(pcsetupcovers[pckeypieces]) == 0):
                lastcommand = "No setup found in the database"
                return False
        except KeyError:
            lastcommand = "No setup found in the database"
            return False

        visualizeboard = unglue(pcsetups[pcsetupcovers[pckeypieces][0]])

    elif(pcnumber == 5):
        allpieces = ''.join(allpieces)
        piececount = pcpieces[pcnumber]
        pckeypieces = allpieces[:piececount]
        pcsetups = allsetups[pcnumber]["setups"]
        pcsetupcovers = allsetups[pcnumber]["cover"]

        if(len(pcsetupcovers[pckeypieces]) == 0):
            allpieces = [char for char in allpieces]

            piecesinused = ""
            if(allpieces[1] in allpieces[2:]):
                allpieces[0], allpieces[1] = allpieces[1], allpieces[0]

            allpieces = ''.join(allpieces)

        piececount = pcpieces[pcnumber]
        pckeypieces = allpieces[:piececount]
        pcsetups = allsetups[pcnumber]["setups"]
        pcsetupcovers = allsetups[pcnumber]["cover"]

        try:
            if(len(pcsetupcovers[pckeypieces]) == 0):
                lastcommand = "No setup found in the database"
                return False
        except KeyError:
            lastcommand = "No setup found in the database"
            return False

        visualizeboard = unglue(pcsetups[pcsetupcovers[pckeypieces][0]])

    else:
        piececount = pcpieces[pcnumber]
        pckeypieces = allpieces[:piececount]
        pcsetups = allsetups[pcnumber]["setups"]
        pcsetupcovers = allsetups[pcnumber]["cover"]

        try:
            if(len(pcsetupcovers[pckeypieces]) == 0):
                lastcommand = "No setup found in the database"
                return False
        except KeyError:
            lastcommand = "No setup found in the database"
            return False

        visualizeboard = unglue(pcsetups[pcsetupcovers[pckeypieces][0]])

def dpc_finder():
    global visualizeboard, lastcommand
    if(nopieceboard != [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]):
        lastcommand = "This only works for empty boards"
        return False

    allpieces = currentpiece + holdpiece + ''.join(queue)
    if(len(bag) == 1):
        allpieces += bag[0]

    pcnumber = (5 * piecesplaced % 7) + 1

    if(pcnumber != 3):
        lastcommand = "This only works for third pc"
        return False

    allpieces = [char for char in allpieces]

    piecesinused = ""
    if(allpieces[1] in allpieces[2:]):
        allpieces[0], allpieces[1] = allpieces[1], allpieces[0]

    allpieces = ''.join(allpieces)

    pckeypieces = allpieces
    pcsetups = dpcsetups
    pcsetupcovers = dpccover

    try:
        if(len(pcsetupcovers[pckeypieces]) == 0):
            lastcommand = "No setup found in the database"
            return False
    except KeyError:
        lastcommand = "No setup found in the database"
        return False

    visualizeboard = unglue(pcsetups[pcsetupcovers[pckeypieces][0]])

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
0 : 0,
1 : 100,
2 : 300,
3 : 500,
4 : 800,
"t0" : 400,
"t1" : 800,
"t2" : 1200,
"t3" : 1600,
"pc" : 3500
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

            if(type(allkicks[0]) != type([])):
                allkicks = [allkicks]

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
    for rowindex, row in enumerate(board):
        if all(square != defaultboardcharacter for square in row):
            filled_rows.append(rowindex)
    return filled_rows

def clear_filled_rows(board):
    global combo, score, combocount, b2b, gointob2b
    gointob2b = 0
    filled_rows = get_filled_rows(nopieceboard)

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
                if(currentpiecey + yoffset < boardheight and currentpiecex + xoffset < boardlength):
                    if(nopieceboard[currentpiecey + yoffset][currentpiecex + xoffset] != defaultboardcharacter):
                        corners += 1
                        if(facing[yoffset][xoffset] == 1):
                            facingcorners += 1
                else:
                    corners += 1
                    if(facing[yoffset][xoffset] == 1):
                        facingcorners += 1

        if(tspinkick):
            print(bigkick)
            if(corners >= 3):
                if(facingcorners == 2):
                    gointob2b = 2
                else:
                    gointob2b = 1
                    if(bigkick == True):
                        gointob2b = 2

    if(len(filled_rows) > 0):
        combo = True
        combo += 1

        for row in filled_rows:
            del board[row]
            board.insert(0, [defaultboardcharacter for _ in range(boardlength)])

    else:
        combo = False
        combocount = 0

    return(len(filled_rows))

combo = False
b2b = False
combocount = 0
score = 0
gointob2b = 0

lastpcpiececount = 0
consecutivepcs = 0
consecutiveb2bs = 0

def tabulatescore(linescleared, activateb2b):
    global combo, combocount, b2b, lastpcpiececount, consecutivepcs, consecutiveb2bs

    pced = False

    currentscore = 0

    if(activateb2b == 2):
        currentscore = scorevalues["t" + str(linescleared)]
        consecutiveb2bs += 1

    elif(activateb2b == 1):
        currentscore = scorevalues[linescleared] + 100
        consecutiveb2bs += 1

    else:
        currentscore = scorevalues[linescleared]

    if(nopieceboard == [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]):
        currentscore += scorevalues["pc"]
        pced = True
        consecutivepcs += 1
        lastpcpiececount = piecesplaced

    if(piecesplaced - lastpcpiececount > 10):
        consecutivepcs = 0

    if(b2b == True):
        if(activateb2b > 0 or linescleared == 4):
            currentscore *= 1.5

    currentscore += combocount * 50

    wordlines = ["", "Single", "Double", "Triple", "QwQ"]
    word = wordlines[linescleared]

    if(b2b):
        word = "B2B " + word

    if(activateb2b == 1):
        word = "Mini Tspin " + word
    elif(activateb2b == 2):
        word = "Tspin " + word

    if(pced):
        word += " PC"

    if(linescleared == 4 or activateb2b > 0):
        b2b = True

    elif(linescleared > 0):
        b2b = False
        consecutiveb2bs = 0

    if(combo == True):
        combocount += 1

    clearscreen(-5, 0, 6, 4)
    writetext(-5, 0, word, 30)

    return(int(currentscore))

ogbag = [char for char in "IOSZJLT"]
bag = deepcopy(ogbag)

def piecepick():
    global bag
    chosenseed = ((piecesplaced * startingseed) + startingseed * startingseed)
    seed(chosenseed)
    piecepicked = choice(bag)
    bag.remove(piecepicked)
    if(len(bag) == 0):
        bag = deepcopy(ogbag)
    return piecepicked

queue = [piecepick() for i in range(6)]
currentpiece = queue[0]
queue.pop(0)
holdpiece = ""
currentpiecerotation = 0
currentpiecex = pieces[currentpiece]["spawnposition"]
currentpiecey = 0

def kicksubtract(kicktable1, kicktable2):
    subtractedkicktable = []
    for kick1, kick2 in zip(kicktable1, kicktable2):
        subtractedkicktable.append([kick1[0] - kick2[0], kick1[1] - kick2[1]])
    return subtractedkicktable

tspinkick = False
bigkick = False
def rotatepiece(rotation):
    global currentpiecerotation, currentpiece, currentpiecex, currentpiecey, tspinkick, bigkick
    plsbreak = False
    kicks = pieces[currentpiece]["srs"][str(currentpiecerotation) + str((currentpiecerotation + rotation) % 4)]
    for kicknumber, offset in enumerate(kicks):
        if placeable(currentpiece, (currentpiecerotation + rotation) % 4, currentpiecex + offset[0], currentpiecey + (offset[1] * -1)):
            if(currentpiece == "T"):
                tspinkick = True
                print(kicknumber)
                if(kicknumber == 4):
                    bigkick = True
            else:
                tspinkick = False
                bigkick = False

            #print(f"offset of {offset[0]}x and {(offset[1] * -1)}y works")
            currentpiecex += offset[0]
            currentpiecey += (offset[1] * -1)
            currentpiecerotation = (currentpiecerotation + rotation) % 4
            break

def cw_rotate():
    rotatepiece(1)

def ccw_rotate():
    rotatepiece(-1)

def full_rotate():
    rotatepiece(2)

def move(distance):
    global currentpiecex
    if placeable(currentpiece, currentpiecerotation, currentpiecex + distance, currentpiecey):
        currentpiecex += distance

def move_left():
    move(-1)

def move_right():
    move(1)

def move_das(direction):
    global currentpiecex
    tempx = currentpiecex
    for distance in range(0, 10 * direction, direction):
        if placeable(currentpiece, currentpiecerotation, currentpiecex + distance, currentpiecey):
            tempx = distance
        else:
            currentpiecex += tempx
            break
    drawallpieces()

def move_left_das():
    move_das(-1)

def move_right_das():
    move_das(1)

def savestate():
    allboards.append([deepcopy(nopieceboard), deepcopy(queue), currentpiece, holdpiece, deepcopy(bag), piecesplaced, deepcopy(score)])

piecesplaced = 0

def harddrop():
    global currentpiece, currentpiecerotation, currentpiecex, currentpiecey, allboards, piecesplaced, bag, visualizeboard, score, gointob2b, piecesplaced, undooffset

    visualizeboard = ""

    counter = 0
    while placeable(currentpiece, currentpiecerotation, currentpiecex, currentpiecey):
        currentpiecey += 1
        score += 2
        counter += 1
    currentpiecey -= 1
    score -= 2

    if(counter != 1):
        bigkick = False
        tspinkick = False

    putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey, nopieceboard)

    filled_rows = clear_filled_rows(nopieceboard)
    score += tabulatescore(filled_rows, gointob2b)
    piecesplaced += 1
    currentpiece = queue[0]
    queue.pop(0)

    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    board = deepcopy(nopieceboard)

    drawallpieces()
    drawqueue()

    savestate()
    undooffset = 0

undooffset = 0

def loadboard():
    global nopieceboard, board, queue, currentpiece, holdpiece, bag, piecesplaced, currentpiecerotation, currentpiecex, currentpiecey, score, undooffset, visualizeboard
    visualizeboard = ""

    nopieceboard = deepcopy(allboards[-1 - undooffset][0])
    board = deepcopy(nopieceboard)

    queue = deepcopy(allboards[-1 - undooffset][1])
    currentpiece = deepcopy(allboards[-1 - undooffset][2])
    holdpiece = deepcopy(allboards[-1 - undooffset][3])
    bag = deepcopy(allboards[-1 - undooffset][4])
    piecesplaced = allboards[-1 - undooffset][5]
    score = allboards[-1 - undooffset][6]

    clearscreen(-6, -3, 6, 3)
    if(not holdpiece == ""):
        if(holdpiece == "I"):
            drawinfopieces(-5, -6, holdpiece)
        else:
            drawinfopieces(-3, -4, holdpiece)

    if bag == []:
        bag = deepcopy(ogbag)

    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0

    drawallpieces()

def undo():
    global undooffset
    if(len(allboards) > undooffset + 1):
        undooffset += 1
        loadboard()

def redo():
    global undooffset
    if(undooffset > 0):
        undooffset -= 1
        loadboard()

def softdrop():
    global currentpiecey, score
    if(placeable(currentpiece, currentpiecerotation, currentpiecex, currentpiecey + 1)):
        currentpiecey += 1
        score += 1

def softdrop_das():
    global currentpiecey, score
    counter = 0
    while placeable(currentpiece, currentpiecerotation, currentpiecex, currentpiecey):
        currentpiecey += 1
        score += 1
        counter += 1
    if(counter != 1):
        bigkick = False
        tspinkick = False
    currentpiecey -= 1
    score -= 1
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
    clearscreen(-6, -3, 6, 3)
    if(holdpiece == "I"):
        drawinfopieces(-5, -6, holdpiece)
    else:
        drawinfopieces(-3, -4, holdpiece)

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
    pytext = normalfont.render(text, True, (255, 255, 255))
    s.blit(pytext, (startx + (x * blocksize), starty + (y * blocksize), blocksize, blocksize))

def stattext(x, y, text, size):
    global startx, starty, blocksize, blockwidth
    pytext = statfont.render(text, True, (255, 255, 255))
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
xlocation = 6

def createcolorsquares():
    for v, i in enumerate(tetrominoes):
        blockrenderer(boardlength + xlocation, v, pieces[i]["color"])

def createsettextboxes():
    for box in textvariables:
        settextbutton(box[0], str(eval(box[4])), box[1], box[2], box[3])

def settextbutton(text, subtext, x, y, color):
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, j + y, color)

    pytext = normalfont.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def grayoutboard():
    for piecerowindex, piecerow in enumerate(nopieceboard):
        for piececolumnindex, piecevalue in enumerate(piecerow):
            if(piecevalue != defaultboardcharacter):
                nopieceboard[piecerowindex][piececolumnindex] = "G"

def truefalsebutton(text, x, y, value):
    clearscreen(x - 1, y - 1, 4, 3)

    pytext = normalfont.render(text, True, (255, 255, 255))

    textwidth = pytext.get_width()
    textheight = pytext.get_height()

    s.blit(pytext, (startx + (x * blocksize) + (1 * blocksize) - textwidth/2, starty + ((y - 1) * blocksize)))

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
        setezsfinderbutton(box[0], "deprecated", box[1], box[2], box[3])

def createmenuboxes():
    for box in menuvariables:
        setezsfinderbutton(box[0], "deprecated", box[1], box[2], box[3])

def createsettingboxes():
    for box in settingvariables:
        setezsfinderbutton(box[0], "deprecated", box[1], box[2], box[3])

controlcolors = [RED, BLUE]
def createcontrolboxes():
    for controlindex, control in enumerate(controls):
        setcontrolbutton(controls[control], "deprecated", 22, controlindex, controlcolors[controlindex % 2], 18)

def createhelpboxes():
    for box in helpvariables:
        setezsfinderbutton(box[0], "deprecated", box[1], box[2], box[3])

def createtruefalse():
    for truefalse in truevariables:
        truefalsebutton(truefalse[0], truefalse[1], truefalse[2], truefalse[3])

def settingtruefalse():
    for truefalse in settingtruevariables:
        truefalsebutton(truefalse[0], truefalse[1], truefalse[2], truefalse[3])

def setezsfinderbutton(text, subtext, x, y, color):
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, j + y, color)

    pytext = normalfont.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def setcontrolbutton(text, subtext, x, y, color, size):
    for i in range(4):
        for j in range(1):
            blockrenderer(x + i, j + y, color)

    font = pygame.font.Font(f'fonts\ComicMono.ttf',size)
    pytext = normalfont.render(text, True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (0.5 *  blocksize) - textheight/2, blocksize, blocksize))

def setqueuebutton():
    x = boardlength + 2
    y = -2
    for i in range(4):
        for j in range(2):
            blockrenderer(x + i, y + j, RESET)

    pytext = normalfont.render("Set game queue", True, (255, 255, 255))
    textwidth = pytext.get_width()
    textheight = pytext.get_height()
    s.blit(pytext, (startx + (x * blocksize) + (2 * blocksize) - textwidth/2, starty + (y * blocksize) + (1 *  blocksize) - textheight/2, blocksize, blocksize))

def setheldpiece():
    x = -5
    y = -5

    pytext = normalfont.render("Set held piece", True, (255, 255, 255))
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

    print("Window initialized")

    # Create label
    label = tk.Label(window, text=f"Set the value of {variable_name}")
    label.pack()

    print("Textbox inserted")

    # Create textbox
    textbox = tk.Entry(window)
    if(variable_name == "loadfumen"):
        textbox.insert(-1, outputcode())
    else:
        textbox.insert(-1, eval(variable_name))

    textbox.pack()
    print("Inserted value")
    # Function to set the variable and close the window
    def set_value():
        print("setting value")
        if(variable_name == "loadfumen"):
            loadfumen(textbox.get())
        else:
            global_dict = globals()  # Get the global dictionary
            global_dict[variable_name] = textbox.get()  # Set the variable in the global dictionary

        window.destroy()
        root.quit()
        print("done")

    # Bind Enter key to set_value function
    textbox.bind('<Return>', lambda event: set_value())

    # Protocol handler for window close event
    window.protocol("WM_DELETE_WINDOW", set_value)

    print("starting  the main loop")
    window.mainloop()  # Start the tkinter event loop
    root.destroy()

KEYSYM_TO_KEY = {
    "Alt_L": pygame.K_LALT,
    "Alt_R": pygame.K_RALT,
    "BackSpace": pygame.K_BACKSPACE,
    "Caps_Lock": pygame.K_CAPSLOCK,
    "Control_L": pygame.K_LCTRL,
    "Control_R": pygame.K_RCTRL,
    "Delete": pygame.K_DELETE,
    "Down": pygame.K_DOWN,
    "End": pygame.K_END,
    "Escape": pygame.K_ESCAPE,
    "F1": pygame.K_F1,
    "F2": pygame.K_F2,
    "F3": pygame.K_F3,
    "F4": pygame.K_F4,
    "F5": pygame.K_F5,
    "F6": pygame.K_F6,
    "F7": pygame.K_F7,
    "F8": pygame.K_F8,
    "F9": pygame.K_F9,
    "F10": pygame.K_F10,
    "F11": pygame.K_F11,
    "F12": pygame.K_F12,
    "Home": pygame.K_HOME,
    "Insert": pygame.K_INSERT,
    "KP_0": pygame.K_KP0,
    "KP_1": pygame.K_KP1,
    "KP_2": pygame.K_KP2,
    "KP_3": pygame.K_KP3,
    "KP_4": pygame.K_KP4,
    "KP_5": pygame.K_KP5,
    "KP_6": pygame.K_KP6,
    "KP_7": pygame.K_KP7,
    "KP_8": pygame.K_KP8,
    "KP_9": pygame.K_KP9,
    "KP_Add": pygame.K_KP_PLUS,
    "KP_Decimal": pygame.K_KP_PERIOD,
    "KP_Divide": pygame.K_KP_DIVIDE,
    "KP_Enter": pygame.K_KP_ENTER,
    "KP_Multiply": pygame.K_KP_MULTIPLY,
    "KP_Subtract": pygame.K_KP_MINUS,
    "Left": pygame.K_LEFT,
    "Menu": pygame.K_MENU,
    "Num_Lock": pygame.K_NUMLOCK,
    "Page_Down": pygame.K_PAGEDOWN,
    "Page_Up": pygame.K_PAGEUP,
    "Pause": pygame.K_PAUSE,
    "Print": pygame.K_PRINT,
    "Right": pygame.K_RIGHT,
    "Scroll_Lock": pygame.K_SCROLLLOCK,
    "Shift_L": pygame.K_LSHIFT,
    "Shift_R": pygame.K_RSHIFT,
    "space": pygame.K_SPACE,
    "Tab": pygame.K_TAB,
    "Up": pygame.K_UP,
    "quoteleft": pygame.K_BACKQUOTE
}


def save_key_input(key_name):
    global controls
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window

    # Create tkinter window with larger size
    window = tk.Toplevel()
    window.title("Save Key Input")
    window.geometry("300x100")  # Set window size to 300x100

    # Create label
    label = tk.Label(window, text=f"Set the value of {controls[key_name]}")
    label.pack()

    valuern = tk.Label(window, text=f"Currentvalue is {pygame.key.name(key_name).upper()}")
    valuern.pack()

    # Function to save the key input and close the window
    def save_input(event):
        global controls

        key = event.keysym
        if(key in KEYSYM_TO_KEY):
            key_input = KEYSYM_TO_KEY[key]
        else:
            key_input = eval(f"pygame.K_{event.keysym}")

        if(key_input in controls):
            error = tk.Label(window, text=f"This control is already in use, please dont do that")
            error.pack()
        else:
            controls[key_input] = controls.pop(key_name)
            window.destroy()
            root.quit()

    def quit():
        window.destroy()
        root.quit()

    # Bind key press event to save_input function
    window.bind('<KeyPress>', save_input)

    # Protocol handler for window close event
    window.protocol("WM_DELETE_WINDOW", lambda: quit())

    window.mainloop()  # Start the tkinter event loop

def set_queue():
    print("setting queue")
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
        allqueues = sfinder_all_permutations(textbox.get())
        queue = [char for char in choice(allqueues)]
        currentpiece = queue[0]
        queue.pop(0)
        bag = deepcopy(ogbag)
        while(len(queue) < 5):
                queue.append(piecepick())
        window.destroy()
        root.quit()
        drawallpieces()

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
        clearscreen(-6, -3, 6, 3)
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

lastcommand = "QwQtris - not a ripoff of anything QwQ"

#submission box jumping point
ezsfinderboxx = boardlength + 8
helpbuttonboxx = boardlength + 8
fumenbuttonboxx = boardlength + 40
ezsfindervariables = [
["Chance", ezsfinderboxx, 0, RED, "chance"],
["Minimals", ezsfinderboxx, 2, BLUE, "minimals"],
["T-Spin Minimals", ezsfinderboxx, 4, RED, "t_spin_minimals"],
["Tetris Minimals", ezsfinderboxx, 6, BLUE, "tetris_minimals"],
["Score", ezsfinderboxx, 8, RED, "get_score"]
]

helpvariables = [
["Pure PC save", helpbuttonboxx, 0, BLUE, "pc_finder"],
["DPC save", helpbuttonboxx, 2, BLUE, "dpc_save_finder"],
[":cat: solve", helpbuttonboxx, 4, BLUE, "cat_finder"]
]

if(loadsetups):
    helpvariables.append(["Setup Finder", helpbuttonboxx + 4, 0, MAGENTA, "setup_finder"])
    helpvariables.append(["DPC Finder", helpbuttonboxx + 4, 2, MAGENTA, "dpc_finder"])

textboxx = 22
textvariables = [
["Set fed queue", textboxx, 0, ORANGE, "sfinder_fed_queue"],
["Set clear", textboxx, 2, CYAN, "clear"],
["Initial Combo", textboxx, 4, ORANGE, "initial_combo"],
["B2B Bonus", textboxx, 6, CYAN, "b2b_end_bonus"],
["Load fumen", textboxx, 8, ORANGE, "loadfumen"]
]

settingvariables = [
["Set fed queue", textboxx, 0, ORANGE, "sfinder_fed_queue"]
]

truefalsex = 18
truevariables = [
["Initial b2b", truefalsex, -2, initial_b2b],
]

menubuttonx = 22
menuvariables = [
["Help Tools", menubuttonx, 12, RED],
["Research", menubuttonx, 14, BLUE],
["Settings", menubuttonx, 16, RED],
]

settingvariablesx = 18
settingvariables = [
["DAS", settingvariablesx, 0, ORANGE, "das"],
["ARR", settingvariablesx, 2, BLUE, "arr"],
["SDL", settingvariablesx, 4, ORANGE, "softdropdelay"],
["SDS", settingvariablesx, 6, BLUE, "softdropspeed"],
]

settingtruevariables = [
["Setup Finder", settingvariablesx + 1, 10, loadsetups],
]

def drawlastcommand():
    global textboxx
    x = -5
    y = 16
    pytext = normalfont.render(lastcommand, True, (255, 255, 255))
    block = pygame.Rect(startx + (x * blocksize), starty + (y * blocksize), 20 * blocksize, 2 * blocksize)
    pygame.draw.rect(s, RESET, block)
    s.blit(pytext, (startx + (x * blocksize), starty + (y * blocksize), blocksize, blocksize))

def clearscreen(x, y, width, height):
    block = pygame.Rect(startx + (x * blocksize), starty + (y * blocksize), width * blocksize, height * blocksize)
    pygame.draw.rect(s, RESET, block)

def drawallpieces():
    global board, lastdrawn
    clearscreen(0, 0, boardlength + 6, boardheight + 2)
    clearscreen(0, -1, 2, 1)
    drawghostpiece()
    drawlastcommand()

    statx = -5
    staty = 5
    statincrement = 0.8
    statsize = blocksize//4

    clearscreen(statx, 5, staty, 10)
    stattext(statx, staty + statincrement, f"Score", statsize)
    stattext(statx, staty + statincrement * 2, "0" * max(8 - len(str(score)), 0) + str(score), statsize)

    stattext(statx, staty + statincrement * 3, f"PPB", statsize)
    if(piecesplaced == 0):
        stattext(statx, staty + statincrement * 4, "0", statsize)
    else:
        stattext(statx, staty + statincrement * 4, str(round(score/piecesplaced, 2)) + "0" * max(8 - len(str(round(score/piecesplaced, 2))), 0), statsize)
    stattext(statx, staty + statincrement * 5, f"Pieces Placed", statsize)
    stattext(statx, staty + statincrement * 6, "0" * max(8 - len(str(piecesplaced)), 0) + str(piecesplaced), statsize)
    stattext(statx, staty + statincrement * 7, f"Chain PCs", statsize)
    stattext(statx, staty + statincrement * 8, "0" * max(8 - len(str(consecutivepcs)), 0) + str(consecutivepcs), statsize)
    stattext(statx, staty + statincrement * 9, f"Chain B2B", statsize)
    stattext(statx, staty + statincrement * 10, "0" * max(8 - len(str(consecutiveb2bs)), 0) + str(consecutiveb2bs), statsize)
    #stattext(statx, staty + statincrement * 8, "0" * max(8 -len(str((piecesplaced * 5 % 7) + 1)), 0) + str((piecesplaced * 5 % 7) + 1), statsize)

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
    global holdpiece, currentpiece, queue, currentpiecerotation, currentpiecex, currentpiecey, nopieceboard, board, bag, score, piecesplaced, startingseed, visualizeboard, consecutivepcs, consecutiveb2bs

    startingseed = randint(0, 100000)

    bag = deepcopy(ogbag)
    currentpiece = piecepick()
    queue = [piecepick() for i in range(5)]
    currentpiecerotation = 0
    currentpiecex = pieces[currentpiece]["spawnposition"]
    currentpiecey = 0
    score = 0
    combocount = 0
    piecesplaced = 0
    nopieceboard = [[defaultboardcharacter for idea in range(boardlength)] for i in range(boardheight)]
    board = deepcopy(nopieceboard)
    holdpiece = ""
    clearscreen(-6, -3, 6, 3)
    drawallpieces()
    savestate()
    visualizeboard = ""
    undooffset = 0
    consecutivepcs = 0
    consecutiveb2bs = 0

putpiece(currentpiece, currentpiecerotation, currentpiecex, currentpiecey)
drawallpieces()

dastimer = 0
softdroptimer = 0

dohold = {
"move_left" : {
    "timer" : "dastimer",
    "delay" : "das",
    "between" : "arr",
    "lastmove" : 0
},
"move_right" : {
    "timer" : "dastimer",
    "delay" : "das",
    "between" : "arr",
    "lastmove" : 0
},
"softdrop" : {
    "timer" : "softdroptimer",
    "delay" : "softdropdelay",
    "between" : "softdropspeed",
    "lastmove" : 0
},
}

piece = 1

def outputcode():
    temp = ""
    for row in board:
        for piece in row:
            if(piece == defaultboardcharacter):
                temp += "_"
            elif(piece == "G"):
                temp += "X"
            else:
                temp += piece
    system(f"node encode.js {temp} > ezsfinder.txt")
    outputfumen = open("ezsfinder.txt").read()[:-1]
    return(outputfumen)

keyspressed = []

clock = pygame.time.Clock()

# Set the font for the fps display
font = pygame.font.Font(f'fonts\ComicMono.ttf',30)
menu = 0

def createmenu():
    clearscreen(17.5, -4, 8.5, 16)
    if(menu == 1):
        createsfinderboxes()
        createsettextboxes()
        createtruefalse()

    elif(menu == 0):
        createhelpboxes()

    elif(menu == 2):
        createsettingboxes()
        createcontrolboxes()
        settingtruefalse()

createmenu()

createcolorsquares()
createmenuboxes()
setqueuebutton()
setheldpiece()
savestate()

tap = False

while running:
    presseddown = pygame.key.get_pressed()
    for key in controls:
        if(presseddown[key]):
            if(key in keyspressed):
                if(controls[key] in dohold):
                    if(eval(f"time.time() * 1000 > int({dohold[controls[key]]['timer']}) + int({dohold[controls[key]]['delay']})")):
                        if(eval(dohold[controls[key]]['between']) == 0):
                            exec(f"{controls[key]}_das()")
                        else:
                            if(eval(f"time.time() * 1000 > int({dohold[controls[key]]['lastmove']}) + int({dohold[controls[key]]['between']})")):
                                dohold[controls[key]]['lastmove'] = time.time() * 1000
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

    if pygame.mouse.get_pressed()[0]:
        pos = list(pygame.mouse.get_pos())
        pos[0] = (pos[0] - startx) // blocksize
        pos[1] = (pos[1] - starty) // blocksize

        if(pos[0] >= 0 and pos[0] < boardlength and pos[1] >= 0 and pos[1] < boardheight):
            nopieceboard[pos[1]][pos[0]] = tetrominoes[piece]

        if(pos[0] == boardlength + xlocation and pos[1] >= 0 and pos[1] < len(pieces)):
            piece = pos[1]

        if(menu == 1):
            for box in textvariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    set_variable(box[4])

            for box in ezsfindervariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    fumen = outputcode()
                    exec(f"{box[4]}()")

            if(not tap):
                for box in truevariables:
                    if(pos[0] >= box[1] and pos[0] <= box[1] + 1 and pos[1] == box[2]):
                        box[3] = not box[3]
                        initial_b2b = not initial_b2b
                        createtruefalse()

        for boxindex, box in enumerate(menuvariables):
            if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                menu = boxindex
                createmenu()

        if(menu == 0):
            for box in helpvariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    fumen = outputcode()
                    exec(f"{box[4]}()")

        if(pos[0] >= boardlength + 2 and pos[0] <= boardlength + 5 and pos[1] >= -2 and pos[1] <= -1):
            set_queue()

        if(pos[0] >= -4 and pos[0] <= -1 and pos[1] >= -5 and pos[1] <= -4):
            set_hold()

        if(menu == 2):
            for box in settingvariables:
                if(pos[0] >= box[1] and pos[0] <= box[1] + 3 and pos[1] >= box[2] and pos[1] <= box[2] + 1):
                    set_variable(box[4])

            if(pos[0] >= 22 and pos[0] <= 26 and pos[1] >= 0 and pos[1] < boardheight):
                for iindex, i in enumerate(controls):
                    if(controls[i] == controlslist[pos[1]]):
                        save_key_input(i)
                        break

            if(not tap):
                for box in settingtruevariables:
                    if(pos[0] >= box[1] and pos[0] <= box[1] + 1 and pos[1] == box[2]):
                        loadsetups = not loadsetups
                        box[3] = not box[3]
                        settingtruefalse()

        drawallpieces()
        tap = True

    else:
        tap = False

    if pygame.mouse.get_pressed()[2]:
        pos = list(pygame.mouse.get_pos())
        pos[0] = (pos[0] - startx) // blocksize
        pos[1] = (pos[1] - starty) // blocksize

        if(pos[0] >= 0 and pos[0] < boardlength and pos[1] >= 0 and pos[1] < boardheight):
            nopieceboard[pos[1]][pos[0]] = defaultboardcharacter

        drawallpieces()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            savecontrols()
            running = False

    # Tick the clock
    pygame.display.update()
