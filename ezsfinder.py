from sys import argv
from os import system

help = """The options are:
ezsfinder.py chance <fumen> <queue> <clear=4>; This spits out the chance to solve this.
ezsfinder.py fail_queues <fumen> <queue> <clear=4>; This spits out all the fail queues.
ezsfinder.py minimals <fumen> <queue> <clear=4> <saves=all of them>; This spits out a tinyurl for the minimals. Saves is by default not considered.
ezsfinder.py score <fumen> <queue> <clear=4> <initial_b2b=false> <initial_combo=0> <b2b_bonus=0>; This gives you information and the average score for the setup.
ezsfinder.py help <command>; This gives you more specific help for specific commands.
ezsfinder.py help queue; This gives you more information on how the queue notation works."""

pargv = argv.copy()
if(len(argv) < 3):
    print(help)
    raise SystemExit(0)

if(not pargv[1] == "help"):
    argv = [pargv[0], pargv[1], pargv[2], pargv[3], 4, "I||O||J||L||T||S||Z", "false", 0, 0]
    commands = [0, 0, 0, 0, "clear", "saves", "initial_b2b", "initial_combo", "b2b_bonus"]
    for i in pargv:
        if("=" in i):
            arg = i.split("=")
            term = arg[0]
            value = arg[1]
            argv[commands.index(term)] = value

elif(argv[1].lower() == "chance"):
    system("java -jar sfinder.jar percent --tetfu %s --patterns %s --clear %s > ezsfinder.txt" % (argv[2], argv[3], argv[4]))
    output = open("ezsfinder.txt").read()
    print(output[output.find("success"):output.find("success") + 20].split()[2])

elif(argv[1].lower() == "fail_queues"):
    system("java -jar sfinder.jar percent --tetfu %s --patterns %s -fc -1 --clear %s > ezsfinder.txt" % (argv[2], argv[3], argv[4]))
    output = open("ezsfinder.txt").read().splitlines()
    doprint = False
    for i in output:
        if(i == ""):
            doprint = False
        if(doprint):
            print(i)
        if("Fail pattern" in i):
            doprint = True

elif(argv[1].lower() == "minimals"):
    system("java -jar sfinder.jar path -f csv -k pattern --tetfu %s --patterns %s --clear %s > ezsfinder.txt" % (argv[2], argv[3], argv[4]))
    system('py sfinder-saves.py filter -w "%s" -p "%s" > ezsfinder.txt' % (argv[5], argv[3]))

elif(argv[1].lower() == "score"):
    system("java -jar sfinder.jar path -t %s -p %s --clear %s --hold avoid -split yes -f csv -k pattern -o output/path.csv > ezsfinder.txt" % (argv[2], argv[3], argv[4]))
    system("node avg_score_ezsfinderversion.js queue=%s initialB2B=%s initialCombo=%s b2bEndBonus=%s > ezsfinder.txt" % (argv[3], argv[6], argv[7], argv[8]))
    score = open("ezsfinder.txt").read().splitlines()
    printingscores = True
    for v, i in enumerate(score):
        if(i == "{"):
            printingscores = False
        if(printingscores):
            print("There are %s queues that allow you to get %s" % (i.split(": ")[1], i.split(": ")[0]))
        if("average_covered_score" in i):
            print("On average, when the setup has a perfect clear, you would score %s points."% round(float(i.split(": ")[1][:-1]), 2))
            print("Factoring in pc chance, the average score is %s" % round(float(i.split(": ")[1][:-1]) / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]), 2))

elif(argv[1].lower() == "help"):
    if(argv[2].lower() == "chance"):
        print("""This uses sfinder's percent command to calculate the score.The command structure is sfinder chance <fumen> <queue>.
An example command is:
ezsfinder chance v115@9gA8IeB8CeA8DeF8DeF8NeAgH *p7. (Outputs 99.76%)""")
    if(argv[2].lower() == "queue"):
        print("""The standard queue notation is designed to simulate Tetris' bag system.
When you see the square brackets, it indicates a bag. [SZ] stands for a bag, composing of an S and a Z piece. * Stands in for a full bag of all the pieces, or [IOSZJLT].
When you see a p and then a number next to it, it indicates how many bags to draw out of that queue. [JLT]p2 indicates to draw 2 pieces out of the bag. This is fed into the program as all ways to draw 2 pieces out of the bag [JLT], so the program would get:
JL,JT,LT.""")

else:
    print(help)
    raise SystemExit(0)
