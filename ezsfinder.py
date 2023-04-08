from sys import argv
from os import system as ossystem
from bs4 import BeautifulSoup

debug = False
def system(command):
    if(debug):
        print(command)
    ossystem(command)

commands = ["chance", "fail_queues", "fail-queues", "minimals", "score", "special_minimals", "special-minimals", "second_stats", "setup_stats", "all_setups", "help"]
for i in commands:
    f = open(i, "w")
    f.close()

dpcscores = {
  "O": 4726.38,
  "I": 4495.70,
  "S": 4454.71,
  "Z": 4454.71,
  "L": 4255.94,
  "J": 4255.94,
  "T": 4135.55
}

def ezhelp():
    if(len(argv) < 3):
        defaulthelp = """The options are:
ezsfinder.py chance <fumen> <queue> <clear=4>; This spits out the chance to solve this.
ezsfinder.py fail_queues <fumen> <queue> <clear=4>; This spits out all the fail queues.
ezsfinder.py minimals <fumen> <queue> <clear=4> <saves=all of them>; This spits out a tinyurl for the minimals. Saves is by default not considered.
ezsfinder.py score <fumen> <queue> <clear=4> <initial_b2b=false> <initial_combo=0> <b2b_bonus=0>; This gives you information and the average score for the setup.
ezsfinder.py special_minimals <fumen> <queue> <clear=4> <saves=all of them>; This gets you minimal sets for t-spin and tetris solves.
ezsfinder.py second_stats <fumen> <queue> <clear=4>; This prints out the standard set of statistics for 2nd.
ezsfinder.py setup_stats <fumen> <queue> <clear=4> <fill=I> <margin=O> <exclude=none> <second_queue=>; This runs setup on a setup, and then runs cover on each of those.
ezsfinder.py all_setups <queue=> <max_setup_height=4> <fill=I> <margin=O> <exclude=none> <second_queue=> <pieces_used=3>; This will take a queue and find every setup for it, and then check the pc chance and cover. Useful for bruteforcing pc setups.
ezsfinder.py help <command or parameter>; This gives you more specific help for a command or parameter. eg ezsfinder.py help chance or ezsfinder.py help queue"""
        print(defaulthelp)
        return False

    arg = argv[2]
    helpcommand = arg.lower()
    helpcommands = {
    "chance" : """This uses sfinder's percent command to calculate the score.The command structure is sfinder chance <fumen> <queue>.
An example command is:
ezsfinder chance v115@9gA8IeB8CeA8DeF8DeF8NeAgH *p7. (Outputs 99.76%)""",
    "queue" : """The standard queue notation is designed to simulate Tetris' bag system.
When you see the square brackets, it indicates a bag. [SZ] stands for a bag, composing of an S and a Z piece. * Stands in for a full bag of all the pieces, or [IOSZJLT].
When you see a p and then a number next to it, it indicates how many bags to draw out of that queue. [JLT]p2 indicates to draw 2 pieces out of the bag. This is fed into the program as all ways to draw 2 pieces out of the bag [JLT], so the program would get:
JL,JT,LT.""" ,
    "special_minimals" : """This hooks together like 5 different programs to get the minimals. Your options for minimal_type are the same as sfinder's cover --mode parameters, which are:
tsm: This includes all tspins
tss: This includes tss and up
tsd: This includes all tsd and up
tst: This includes only tst
tetris: Looks for tetris anywhere in the solve
tetris-end: Looks for the last 4 lines cleared being a tetris""",
    "minimals" : """This uses Marfung's sfinder-saves.py to generate the minimals + saves, so use that notation.
For example, if you wanted to find save O solutions, you would put O.
If you wanted to find save T or O solutions, you would seperate it with ||, so T||O.""",
    "fumen" : """A fumen, or a tetfu, is how Tetris boards are shared. You can make them at https://harddrop.com/fumen/ or https://fumen.zui.jp/.
When you draw a board and then hit output data, you get a long encoded string, which represents the board and any comments. You can then use this to send tetris boards through text."""
    }

    if(not arg in helpcommands):
        print("Woops, looks like something went wrong. Either I haven't added a help for this yet, so annoy me till I do, or you've typoed, in which case shame on you.")
        return False
    print(helpcommands[arg])
    return True

if(len(argv) < 3):
    ezhelp()
    raise SystemExit(0)

pargv = argv.copy()
pargv = [argv[i] if i < len(argv) else "s=s" for i in range(len(pargv))]

if(not argv[1] == "help"):
    parameters = [
    ["ezsfinder", pargv[0]],
    ["command", pargv[1]],
    ["fumen", "t", "tetfu", pargv[2]],
    ["queue", "p", pargv[3]],
    ["clear", "c", 4],
    ['saves', 'I||O||J||L||T||S||Z'],
    ['initial_b2b', "i_b2b", 'false'],
    ['initial_combo', "i_cb", 0],
    ['b2b_bonus', 0],
    ['minimal_type', 'tss'],
    ['fill', 'I'],
    ['margin', 'O'],
    ['exclude', 'none'],
    ['second_queue', False],
    ['pieces_used', 3],
    ["cover_fumens", False],
    ["kicktable", "kicks/jstris180.properties"],
    ["mode", "normal"]
    ]

    argv = [i[1] for i in parameters.copy()]
    terms = [i[0] for i in parameters.copy()]

    for i in parameters[2:]:
        exec("%s='%s'" % (i[0], i[-1]))

    for i in pargv:
        if("=" in i):
            exec("%s='%s'" % (i.split("=")[0], i.split("=")[1]))
            for commandpair in parameters:
                for command in commandpair:
                    if(i.split("=")[0] == command):
                        exec("%s='%s'" % (commandpair[0], i.split("=")[1]))

def chance():
    system(f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    output = open("ezsfinder.txt").read()
    print(output[output.find("success"):output.find("success") + 20].split()[2])

def fail_queues():
    system(f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {queue} -fc -1 --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    output = open("ezsfinder.txt").read().splitlines()
    doprint = False
    for i in output:
        if(i == ""):
            doprint = False
        if(doprint):
            print(i)
        if("Fail pattern" in i):
            doprint = True

def minimals():
    system("java -jar sfinder.jar path -f csv -k pattern --tetfu %s --patterns %s --clear %s -K kicks/jstris180.properties -d 180> ezsfinder.txt" % (fumen, queue, clear))
    system('py sfinder-saves.py filter -w "%s" -p "%s"' % (saves, queue))

def score():
    system(f"java -jar sfinder.jar path -t {fumen} -p {queue} --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
    system(f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} > ezsfinder.txt")
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
    #system(f"java -jar sfinder.jar path -f csv -k pattern --tetfu {fumen} --patterns {queue} --clear {clear} > ezsfinder.txt")
    #system('py sfinder-saves.py percent -k "2nd Saves" -pc 2 > ezsfinder.txt')
    #saves = [i.split() for i in open("ezsfinder.txt").read().splitlines()]
    #savechances = [float(i[1][:-1])/100 for i in saves]
    #print(savechances)

def special_minimals():
    system("java -jar sfinder.jar path -t %s -p %s --clear %s -K kicks/jstris180.properties -d 180> ezsfinder.txt" % (fumen, queue, clear))
    with open('output/path_unique.html', encoding = "utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    allfumen = soup.find('a')['href']
    system(f"node glueFumens.js --fu {allfumen} > input/field.txt")
    system(f"java -jar sfinder.jar cover -p {queue} -M {minimal_type} -K kicks/jstris180.properties -d 180> ezsfinder.txt")
    system("cover-to-path.py > ezsfinder.txt")
    system("sfinder-minimal output/cover_to_path.csv> ezsfinder.txt")
    system("true_minimal.py")

def second_stats():
    system("java -jar sfinder.jar path -f csv -k pattern --tetfu %s --patterns %s --clear %s -K kicks/jstris180.properties -d 180 > ezsfinder.txt" % (fumen, queue, clear))
    system('py sfinder-saves.py percent -k "2nd alge Saves" -pc 2')

def setup_stats():
    if(cover_fumens == "False"):
        system(f"java -jar sfinder.jar setup --fill {fill} --margin {margin} -fo csv -e {exclude} --tetfu {fumen} -p {queue} -K kicks/jstris180.properties -d 180 > ezsfinder.txt --split yes")
        fumens = [i.split("http://fumen.zui.jp/?")[1].split(",")[0] for i in open("output/setup.csv").read().splitlines()[1:]]

    else:
        fumens = cover_fumens.split()
        for v, i in enumerate(fumens):
            system(f"node glueFumens.js --fu {i} > ezsfinder.txt")
            fumens[v] = open("ezsfinder.txt").read()[:-1]

    covers = []
    fumenandscores = []
    allfumens = ""
    for indfumen in fumens:
        allfumens += indfumen + " "
        system(f"java -jar sfinder.jar cover --hold use -t {indfumen} -p {queue} -K kicks/jstris180.properties -d 180 -M {mode}> ezsfinder.txt")
        coveredfumen = open("ezsfinder.txt").read().splitlines()
        for line in coveredfumen:
            if("OR") in line:
                fumencoverage = line.split("OR  = ")[1]
                system(f"node unglueFumen.js --fu {indfumen} > ezsfinder.txt")
                unglued = open("ezsfinder.txt").read()[:-1]
                print(f"{unglued} has {fumencoverage} coverage", end="")
                if(second_queue):
                    system(f"java -jar sfinder.jar percent --tetfu {unglued} --patterns {second_queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
                    output = open("ezsfinder.txt").read()
                    ungluedchance = output[output.find('success'):output.find('success') + 20].split()[2]
                    print(f", and a pc chance of {ungluedchance}")
                    ungluedchance = float(ungluedchance[:-1])/100
                    system(f"java -jar sfinder.jar path -t {unglued} -p {second_queue} --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
                    system(f"node avg_score_ezsfinderversion.js queue={second_queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} > ezsfinder.txt")
                    score = open("ezsfinder.txt").read().splitlines()
                    printingscores = True
                    for v, i in enumerate(score):
                        if("average_covered_score" in i):
                            score = int(score[v + 1].split(": ")[1][:-1]) / int(score[-1]) * 100, round(float(i.split(": ")[1][:-1]) / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]), 2)
                            print("Factoring in pc chance (%s%%), the average score is %s" % score, end = "")
                    fumenandscores.append([unglued, list(score)[1]])
                print("")

    system(f"java -jar sfinder.jar cover -t {allfumens} -p {queue} > ezsfinder.txt -K kicks/jstris180.properties -d 180 -M {mode}> ezsfinder.txt")
    coveredfumens = open("ezsfinder.txt").read().splitlines()
    for line in coveredfumens:
        if("OR") in line:
            fumencoverage = line.split("OR  = ")[1]
            print(f"Combined, they have {fumencoverage} coverage")

    useable = [0 for i in range(len(fumenandscores))]
    nocover = 0
    slist = fumenandscores.copy()
    slist.sort(key=lambda x: int(x[1]) * -1)
    scoreindex = [fumenandscores.index(i) for i in slist]
    allcover = [i.split(",")[1:] for i in open("output/cover.csv").read().splitlines()[1:]]
    for covervalue in allcover:
        for coverindex in scoreindex:
            if(covervalue[coverindex] == "O"):
                useable[coverindex] += 1
                break
        else:
            nocover += 1

    totalaveragescore = 0

    print("For max score:")
    queuelength = sum(useable) + nocover
    for useableindex, useablecount in enumerate(useable):
        currentfumen = fumenandscores[useableindex]
        fumenscore = currentfumen[1]
        averagescore = fumenscore * useablecount / queuelength
        print(f"{fumenandscores[useableindex][0]} is used {useablecount} of the time, and adds {averagescore} to the average score")
        totalaveragescore += averagescore
    print(f"The average score of this setup is {totalaveragescore}")


def all_setups():
    for i in range(1, 11):
        system(f"java -jar sfinder.jar setup -H use -t v115@9gtpwhYpJeAglbhglgWReAAechglgWQeAAedhglgWP?eAAeehglgWOeAAefhglgWNeAAeghglgWMeAAehhglgWLeAA?eihglgWKeAAejhglgWJeAAe -f {fill} -m {margin} --line 4 -np {pieces_used} -fo csv -o output/{i} --page {i} -p {queue} --split yes -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
        fumens = [i.split("http://fumen.zui.jp/?")[1].split(",")[0] for i in open(f"output/{i}.csv").read().splitlines()[1:]]
        allfumens = ""
        for indfumen in fumens:
            allfumens += indfumen + " "
            system(f"java -jar sfinder.jar cover -t {indfumen} -p {queue} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
            coveredfumen = open("ezsfinder.txt").read().splitlines()
            for line in coveredfumen:
                if("OR") in line:
                    fumencoverage = line.split("OR  = ")[1]
                    print(f"{indfumen} has {fumencoverage} coverage", end="")
                    system(f"node unglueFumen.js --fu {indfumen} > ezsfinder.txt")
                    unglued = open("ezsfinder.txt").read()[:-1]
                    system(f"java -jar sfinder.jar percent --tetfu {unglued} --patterns {second_queue} --clear {clear} -K kicks/jstris180.properties -d 180 > ezsfinder.txt")
                    output = open("ezsfinder.txt").read()
                    print(f", and a pc chance of {output[output.find('success'):output.find('success') + 20].split()[2]}", end = "")
                    print("")

exec(f"{argv[1]}()")
