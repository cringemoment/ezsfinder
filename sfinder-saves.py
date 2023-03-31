from collections import Counter
import argparse
import os
import re
import json
import subprocess

class Saves():
    # constants
    PIECES = ["T", "I", "L", "J", "S", "Z", "O"]

    # files
    pathFile = "output/path.csv"
    percentOutput = "output/savesPercent.txt"

    filteredPath = "resources/filteredPath.csv"
    filterOutput = "output/filteredSolves.txt"

    wantedSavesJSON = "resources/wantedSavesMap.json"
    fumenLabels = "resources/fumenLabels.js"
    fumenCombine = "resources/fumenCombine.js"
    fumenComment = "resources/fumenAddComment.js"
    fumenFirsts = "resources/fumenTakeFirstPage.js"
    bestSave = "bestSaves/"

    def __init__(self):
        self.__setupParser()

    def __setupParser(self):
        self.__parser = argparse.ArgumentParser(usage="<cmd> [options]", description="A tool for further expansion of the saves from path.csv")
        subparsers = self.__parser.add_subparsers()

        self.__setupPercentParser(subparsers)
        self.__setupFilterParser(subparsers)

    def __setupPercentParser(self, parser):
        percentParser = parser.add_parser("percent", help="Give the percents of saves using the path.csv file with wanted save expression")
        percentParser.set_defaults(func=self.__percentParse)
        percentParser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
        percentParser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
        percentParser.add_argument("-a", "--all", help="output all of the saves and corresponding percents (alternative to not having -k nor -w)", action="store_true")
        percentParser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
        percentParser.add_argument("-p", "--pieces", help="pieces used on the setup (required unless there's -pc)", metavar="<string>", nargs='+')
        percentParser.add_argument("-pc", "--pc-num", help="pc num for the setup & solve (required unless there's -p)", metavar="<int>", type=int)
        percentParser.add_argument("-td", "--tree-depth", help="set the tree depth of pieces in percent (default: 0)", metavar="<int>", type=int, default=0)
        percentParser.add_argument("-f", "--path", help="path file directory (default: output/path.csv)", metavar="<directory>", default=self.pathFile, type=str)
        percentParser.add_argument("-o", "--output", help="output file directory (default: output/saves.txt)", metavar="<directory>", default=self.percentOutput, type=str)
        percentParser.add_argument("-pr", "--print", help="log to terminal (default: True)", action="store_false")
        percentParser.add_argument("-fr", "--fraction", help="include the fraction along with the percent (default: True)", action="store_false")
        percentParser.add_argument("-fa", "--fails", help="include the fail queues for saves in output (default: False)", action="store_true")
        percentParser.add_argument("-os", "--over-solves", help="have the percents be saves/solves (default: False)", action="store_true")

    def __setupFilterParser(self, parser):
        filterParser = parser.add_parser("filter", help="filter path.csv of fumens that doesn't meet the wanted saves")
        filterParser.set_defaults(func=self.__filterParse)
        filterParser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
        filterParser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
        filterParser.add_argument("-bs", "--best-save", help="instead of listing each wanted save separately, it prioritizes the first then second and so on (requires a -w or -k default: false)", action="store_true")
        filterParser.add_argument("-i", "--index", help="index of -k or -w to pick which expression to filter by (default='')", default=None, metavar="<string>", nargs='*')
        filterParser.add_argument("-p", "--pieces", help="pieces used on the setup (required unless there's -pc)", metavar="<string>", nargs='+')
        filterParser.add_argument("-pc", "--pc-num", help="pc num for the setup & solve (required unless there's -p)", metavar="<int>", type=int)
        filterParser.add_argument("-c", "--cumulative", help="gives percents cumulatively in fumens of a minimal set (default: False)", action="store_true")
        filterParser.add_argument("-f", "--path", help="path file directory (default: output/path.csv)", metavar="<directory>", default=self.pathFile, type=str)
        filterParser.add_argument("-o", "--output", help="output file directory (default: output/filteredSolves)", metavar="<directory>", default=self.filterOutput, type=str)
        filterParser.add_argument("-pr", "--print", help="log to terminal (default: True)", action="store_false")
        filterParser.add_argument("-s", "--solve", help="setting for how to output solve (minimal, unique, none)(default: minimal)", choices={"minimal", "unique", "none"}, metavar="<string>", default="minimal", type=str)
        filterParser.add_argument("-t", "--tinyurl", help="output the link with tinyurl if possible (default: True)", action="store_false")
        filterParser.add_argument("-fc", "--fumen-code", help="include the fumen code in the output (default: False)", action="store_true")

    def handleParse(self, customInput=os.sys.argv[1:]):
        args = self.__parser.parse_args(customInput)
        if vars(args):
            args.func(args)
        else:
            print("No Command Inputted")

    def __percentParse(self, args):
        percentFuncArgs = {}

        # semi-required options
        wantedSaves = []
        if args.wanted_saves is not None:
            # add all wanted saves
            wantedSaves.extend(args.wanted_saves)
        if args.key is not None:
            with open(self.wantedSavesJSON, "r", encoding = "utf-8") as outfile:
                wantedSaveDict = json.loads(outfile.read())
            wantedSaves.extend([",".join(wantedSaveDict[k]) for k in args.key])
        wantedSaves = ",".join(wantedSaves)
        percentFuncArgs["All Saves"] = args.all

        if not wantedSaves and not args.all:
            # didn't have the wanted-saves nor a key
            print("Syntax Error: The options --wanted-saves (-w), --key (-k) nor --all (-a) was found")
            return
        if not wantedSaves and args.best_save:
            # didn't have -w or -k but have -bs true
            print("Syntax Error: The options --wanted-saves (-w) nor --key (-k) was found when --best-save (-bs) is true")
            return

        pieces = ""
        pcNum = -1
        if args.pieces is not None:
            pieces = "".join(args.pieces).upper()
        elif args.pc_num is not None:
            pcNum = args.pc_num
        else:
            # didn't have the pieces nor a pc num
            print("Syntax Error: The options --pieces (-p) nor --pc-num (-pc) was found")
            return

        # options
        percentFuncArgs["Best Save"] = args.best_save
        percentFuncArgs["Tree Depth"] = args.tree_depth
        percentFuncArgs["Path File"] = args.path
        percentFuncArgs["Output File"] = args.output
        percentFuncArgs["Print"] = args.print
        percentFuncArgs["Fraction"] = args.fraction
        percentFuncArgs["Fails"] = args.fails
        percentFuncArgs["Over Solves"] = args.over_solves

        self.percent(wantedSaves, pieces, pcNum, percentFuncArgs)

    # return an dictionary including all the wantedSaves over the path file
    def percent(self, wantedSaves, pieces="", pcNum=-1, args={}):
        defaultArgs = {
            "Path File": self.pathFile,
            "Output File": self.percentOutput,
            "Print": True,
            "All Saves": False,
            "Best Save": False,
            "Tree Depth": 0,
            "Fraction": True,
            "Fails": False,
            "Over Solves": False
        }
        defaultArgs.update(args)
        args = defaultArgs

        if not os.path.exists(args["Path File"]):
            print(f'The path to "{args["Path File"]}" could not be found!')
            return

        # holds a tree where each node is a dictionary with a percent and
        # next key where next is a list holding the next node depth
        wantedTree = {}
        wantedSavesFails = {}
        wantedStacks = []
        countAll = None
        storeAllPreviousQs = None
        treeDepth = args["Tree Depth"]
        if args["All Saves"]:
            countAll = {}
            if args["Fails"]:
                storeAllPreviousQs = []

        if wantedSaves:
            for wantedSave in wantedSaves.split(","):
                if "#" in wantedSave:
                    wantedSave =  wantedSave.split("#")
                    alias = wantedSave[1]
                    wantedSave =  wantedSave[0]
                else:
                    alias = wantedSave

                wantedTree[alias] = {"count": 0, "next": None}
                wantedStacks.append(self.__makeStack(wantedSave))

        # from pieces get the pieces given for the possible pieces in the last bag of the pc and it's length
        lastBag, newBagNumUsed = self.__findLastBag(pieces, pcNum)

        totalCases = self.__getPercentData(lastBag, newBagNumUsed, wantedStacks, wantedTree, treeDepth, countAll, storeAllPreviousQs, wantedSavesFails, args)

        allStr = self.__formatPercentData(totalCases, wantedTree, treeDepth, countAll, wantedSavesFails, args)
        with open(args["Output File"], "w", encoding = "utf-8") as infile:
            infile.write(allStr)

        if args["Print"]:
            print(allStr)

    def __getPercentData(self, lastBag, newBagNumUsed, wantedStacks, wantedTree, treeDepth, countAll, storeAllPreviousQs, wantedSavesFails, args):
        totalCases = 0
        outfile = open(args["Path File"], "r", encoding = "utf-8")
        outfile.readline() # skip header row

        for line in outfile:
            line = line.split(",")
            # has solve?
            if line[1] != "0":
                bagSavePieces = lastBag - set(line[0][-newBagNumUsed:])
                savePieces = set(line[3].strip().split(";"))
                if '' in savePieces:
                    savePieces = set()

                allSaves = self.__createAllSavesQ(savePieces, bagSavePieces)
                if args["All Saves"]:
                    for save in allSaves:
                        if save in countAll:
                            countAll[save] += 1
                        else:
                            countAll[save] = 1
                            if args["Fails"]:
                                wantedSavesFails[save] = storeAllPreviousQs.copy()

                    if args["Fails"]:
                        storeAllPreviousQs.append(line[0])
                        for nonsave in set(wantedSavesFails.keys()) - set(allSaves):
                            wantedSavesFails[nonsave].append(line[0])

                for stack, wantedSave in zip(wantedStacks, wantedTree):
                    canSave = bool(self.parseStack(allSaves, stack))
                    currDepthNode = wantedTree[wantedSave]

                    currDepth = 0
                    node = {"count": 0, "next": None}

                    # add to count of overall
                    currDepthNode["count"] += canSave
                    while currDepth < treeDepth:
                        # if a node has not been created for the next piece
                        if currDepthNode["next"] is None:
                            currDepthNode["next"] = {}
                        if line[0][currDepth] not in currDepthNode["next"]:
                            # create a new node for the next piece
                            currDepthNode["next"][line[0][currDepth]] = node.copy()

                        currDepthNode = currDepthNode["next"][line[0][currDepth]]

                        currDepthNode["count"] += canSave

                        currDepth += 1

                    if canSave:
                        if args["Best Save"]:
                            # best save will not consider any further stack
                            break
                    else:
                        if args["Fails"]:
                            if wantedSave not in wantedSavesFails:
                                wantedSavesFails[wantedSave] = [line[0]]
                            else:
                                wantedSavesFails[wantedSave].append(line[0])
                totalCases += args["Over Solves"]

            totalCases += not args["Over Solves"]

        outfile.close()

        return totalCases

    def __formatPercentData(self, totalCases, wantedTree, treeDepth, countAll, wantedSavesFails, args):
        allStr = []
        for key, value in wantedTree.items():
            if totalCases:
                percent = value["count"] / totalCases * 100
                percentStr = f'{key}: {percent:.2f}%'
                if args["Fraction"]:
                    percentStr += f' ({value["count"]}/{totalCases})'

                if treeDepth > 0:
                    percentStr += f"\nTree (depth: {treeDepth})"
                    def helper(pieces, currNode, divisor=1, currDepth=0):
                        additionStr = ""

                        percent = currNode["count"] / (totalCases // divisor) * 100
                        if currDepth == 0:
                            additionStr += f"\n* -> {percent:.2f}%"
                        else:
                            additionStr += '\n' + '  ' * (currDepth - 1) + f'∟ {pieces} -> {percent:.2f}%'
                        if args["Fraction"]:
                            additionStr += f' ({currNode["count"]}/{totalCases // divisor})'

                        if currDepth < treeDepth:
                            for piece in self.PIECES:
                                if piece in currNode["next"]:
                                    additionStr += helper(pieces + piece, currNode["next"][piece], divisor*len(currNode["next"]), currDepth+1)
                        return additionStr

                    percentStr += helper("", value)
            else:
                percentStr = f'{key}: {value}'

            if args["Fails"] and key in wantedSavesFails:
                percentStr += "\nFail Queues:\n"
                percentStr += ",".join(wantedSavesFails[key])
            allStr.append(percentStr)
        if args["All Saves"]:
            # format countAll to be tetris sorted
            sortedCountAll = {}
            for key in sorted(map(lambda x: self.getOrderValue(x)+x, countAll.keys())):
                sortedCountAll[key[len(key)//2:]] = countAll[key[len(key)//2:]]

            for key, value in sortedCountAll.items():
                if totalCases:
                    percent = value / totalCases * 100
                    percentStr = f'{key}: {percent:.2f}%'
                    if args["Fraction"]:
                        percentStr += f' ({value}/{totalCases})'
                else:
                    percentStr = f'{key}: {value}'

                if args["Fails"] and key in wantedSavesFails:
                    percentStr += "\nFail Queues:\n"
                    percentStr += ",".join(wantedSavesFails[key])
                allStr.append(percentStr)

        return "\n".join(allStr)

    def __filterParse(self, args):
        filterFuncArgs = {}

        if args.wanted_saves and args.key:
            # both -w and -k is inputted which doesn't make sense
            print("Syntax Error: Both options --wanted-saves (-w) and --key (-k) was found for filter")
            return

        # handle index parameter
        if args.index is None:
            indexRanges = []
        else:
            indexRanges = (','.join(args.index)).split(',')

        newIndexRanges = []
        for part in indexRanges:
            part = part.split("-")
            if len(part) <= 2:
                newIndexRanges.append((part[0], part[0] if len(part) == 1 else part[1]))
            else:
                print("Syntax Error: incorrect format in --index (-i)")
                return

        # handle wanted saves input
        if args.wanted_saves is not None:
            wantedSaves = ",".join(args.wanted_saves).split(",")
        elif args.key is not None:
            with open(self.wantedSavesJSON, "r", encoding = "utf-8") as outfile:
                wantedSaveDict = json.loads(outfile.read())
            wantedSaves = ",".join(wantedSaveDict[args.key]).split(",")

        if not wantedSaves:
            # didn't have the wanted-saves nor a key
            print("Syntax Error: The options --wanted-saves (-w) nor --key (-k) was found")
            return

        if not args.best_save:
            wantedSaves = [wantedSaves[0]]

        # apply index ranges to wanted saves
        newWantedSaves = [] if newIndexRanges else wantedSaves
        for start, end in newIndexRanges:
            if 0 <= start < len(wantedSaves) and 0 <= end < len(wantedSaves) and start <= end:
                newWantedSaves.extend[wantedSaves[start, end]]
            else:
                # index given was out of range
                print("OutOfBounds: The option index is out of bounds of possible wantedsaves expressions")
                return

        pieces = ""
        pcNum = -1
        if args.pieces is not None:
            pieces = "".join(args.pieces).upper()
        elif args.pc_num is not None:
            pcNum = args.pc_num
        else:
            # didn't have the pieces nor a pc num
            print("Syntax Error: The options --pieces (-p) nor --pc-num (-pc) was found")
            return

        # options
        filterFuncArgs["Cumulative"] = args.cumulative
        filterFuncArgs["Path File"] = args.path
        filterFuncArgs["Output File"] = args.output
        filterFuncArgs["Print"] = args.print
        filterFuncArgs["Solve"] = args.solve
        filterFuncArgs["Tinyurl"] = args.tinyurl
        filterFuncArgs["Fumen Code"] = args.fumen_code

        self.filter(newWantedSaves, pieces, pcNum, filterFuncArgs)

    # filter the path fumen's for the particular save
    def filter(self, wantedSaves, pieces="", pcNum=-1, args={}):
        defaultArgs = {
            "Cumulative": False,
            "Path File": self.pathFile,
            "Output File": self.filterOutput,
            "Solve": "minimal",
            "Tinyurl": True,
            "Fumen Code": False,
            "Print": True
        }
        defaultArgs.update(args)
        args = defaultArgs

        if not os.path.exists(args["Path File"]):
            print(f'The path to "{args["Path File"]}" could not be found!')
            return

        pathFileLines = []
        linesMatched = []
        fumenSet = set()
        fumenAndQueue = {}

        self.__filterGetData(args["Path File"], pathFileLines, fumenSet, fumenAndQueue, linesMatched)

        # from pieces get the pieces given for the possible pieces in the last bag of the pc and it's length
        lastBag, newBagNumUsed = self.__findLastBag(pieces, pcNum)

        # main section
        aliases = []
        wantedStacks = []
        for wantedSave in wantedSaves:
            if "#" in wantedSave:
                aliases.append(wantedSave.split("#")[1])
                wantedSave = wantedSave.split("#")[0]
            else:
                aliases.append(wantedSave)
            wantedStacks.append(self.__makeStack(wantedSave))

        self.__filterFumensInPath(wantedStacks, pathFileLines, fumenAndQueue, lastBag, newBagNumUsed)

        with open(self.filteredPath, "w", encoding = "utf-8") as infile:
            for line in pathFileLines:
                infile.write(",".join(line) + "\n")

        if args["Solve"] != "None":
            if args["Solve"] == "minimal":
                self.true_minimal(self.filteredPath, args["Output File"], args["Tinyurl"], args["Fumen Code"], args["Cumulative"], aliases, )
            elif args["Solve"] == "unique":
                self.uniqueFromPath(self.filteredPath, args["Output File"], args["Tinyurl"], args["Fumen Code"], aliases)

            if args["Print"]:
                with open(args["Output File"], "r", encoding = "utf-8") as outfile:
                    print(outfile.read())

    def __filterGetData(self, pathFile, pathFileLines, fumenSet, fumenAndQueue, linesMatched):
        with open(pathFile, "r", encoding = "utf-8") as outfile:
            headerLine = outfile.readline().rstrip().split(",")
            pathFileLines.append(headerLine)
            for line in outfile:
                line = line.rstrip().split(",")
                pathFileLines.append(line)
                linesMatched.append(False)
                if line[4]:
                    fumens = line[4].split(";")
                else:
                    continue
                fumenSet.update(set(fumens))

        labelP = subprocess.Popen(["node", self.fumenLabels] + list(fumenSet), stdout=subprocess.PIPE)
        labels = labelP.stdout.read().decode().rstrip().split("\n")

        for label, fumen in zip(labels, fumenSet):
            fumenAndQueue[fumen] = label

    def __filterFumensInPath(self, stacks, pathFileLines, fumenAndQueue, lastBag, newBagNumUsed):
        for line in pathFileLines[1:]:
            queue = Counter(line[0])
            if line[4]:
                fumens = line[4].split(";")
            else:
                continue
            matchedFumens = []
            for stack in stacks:
                for fumen in fumens:
                    savePiece = queue - Counter(fumenAndQueue[fumen])

                    bagSavePieces = lastBag - set(line[0][-newBagNumUsed:])
                    allSaves = [self.tetrisSort("".join(savePiece) + "".join(bagSavePieces))]
                    if self.parseStack(allSaves, stack):
                        matchedFumens.append(fumen)
                if matchedFumens:
                    break

            # reformat the line with new filtered data
            line[4] = ";".join(matchedFumens)
            line[1] = str(len(matchedFumens))

    def true_minimal(self, pathFile="", output="", tinyurl=True, fumenCode=False, cumulative=False, aliases=[]):
        if not pathFile:
            pathFile = self.pathFile
        if not output:
            output = self.filterOutput

        os.system(f'sfinder-minimal {pathFile}')

        with open("path_minimal_strict.md", "r", encoding = "utf-8") as trueMinFile:
            trueMinLines = trueMinFile.readlines()

        fumenLst = re.findall("(v115@[a-zA-Z0-9?/+]*)", trueMinLines[6])

        # only get the first page in case multipage fumens in minimals
        firstsP = subprocess.Popen(["node", self.fumenFirsts] + fumenLst, stdout=subprocess.PIPE)
        fumenLst = firstsP.stdout.read().decode().rstrip().split()

        totalCases = int(re.search("/ (\d+)\)", trueMinLines[2]).group(1))
        percents = []
        if cumulative:
            # count from path the number of each solve cumulatively
            orderedCumulative = []
            cumPercents = []

            with open(pathFile, "r", encoding = "utf-8") as outfile:
                lines = outfile.readlines()

            while fumenLst:
                countSolve = {minFumen: 0 for minFumen in fumenLst}
                for line in lines:
                    fumens = line.rstrip().split(",")[-1]
                    if fumens:
                        for fumen in fumens.split(";"):
                            if fumen in countSolve:
                                countSolve[fumen] += 1

                maxCover = max(countSolve.values())
                maxIndex = list(countSolve.values()).index(maxCover)

                if maxCover == 0:
                    break

                maxFumen = list(countSolve.keys())[maxIndex]

                if cumPercents:
                    cumPercents.append(cumPercents[-1] + maxCover / totalCases)
                else:
                    cumPercents.append(maxCover / totalCases)

                # remove the lines with queues already covered
                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i]
                    fumens = line.rstrip().split(",")[-1]
                    if fumens:
                        if maxFumen in fumens.split(";"):
                            lines.pop(i)
                orderedCumulative.append(fumenLst.pop(maxIndex))

            percents = list(map(lambda x: f'Cumulative Cover: {x*100:.2f}%', cumPercents))
            fumenLst = orderedCumulative
        else:
            for line in trueMinLines[13::9]:
                numCoverCases = int(re.match("(\d+)", line).group(1))
                percent = numCoverCases / totalCases * 100
                percent = f'{percent:.2f}% ({numCoverCases}/{totalCases})'
                percents.append(percent)

        combineP = subprocess.Popen(["node", self.fumenCombine] + fumenLst, stdout=subprocess.PIPE)
        fumenCombineOut = combineP.stdout.read().decode().rstrip()
        commentP = subprocess.Popen(["node", self.fumenComment, fumenCombineOut] + percents, stdout=subprocess.PIPE)
        line = commentP.stdout.read().decode().rstrip()

        if fumenCode:
            fumenCode = line[22:]

        if tinyurl:
            try:
                line = self.make_tiny(line)
            except:
                line = "Tinyurl did not accept fumen due to url length"

        with open(output, "w", encoding = "utf-8") as infile:
            infile.write(f"True minimal for {','.join(aliases)}: \n")
            infile.write(line)
            if fumenCode:
                infile.write("\n" + fumenCode)

    def uniqueFromPath(self, pathFile="", output="", tinyurl=True, fumenCode=False, aliases=[]):
        if not pathFile:
            pathFile = self.pathFile
        if not output:
            output = self.filterOutput

        countSolve = {}
        with open(pathFile, "r", encoding = "utf-8") as outfile:
            outfile.readline()
            for totalCases, line in enumerate(outfile):
                fumens = line.rstrip().split(",")[-1]
                if fumens:
                    for fumen in fumens.split(";"):
                        if fumen not in countSolve:
                            countSolve[fumen] = 1
                        else:
                            countSolve[fumen] += 1

        totalCases += 1
        countSolve = sorted(countSolve.items(), key=lambda x:x[1], reverse=True)
        solves = []
        percents = []
        for fumen, count in countSolve:
            # add the fumen codes and percents to separate lists
            percent = count / totalCases * 100
            percents.append(f"{percent:.2f}% ({count}/{totalCases})")
            solves.append(fumen)

        # combine the fumen codes of the solves
        combineP = subprocess.Popen(["node", self.fumenCombine] + solves, stdout=subprocess.PIPE)
        fumenCombineOut = combineP.stdout.read().decode().rstrip()
        # add the comments to each page of the coverage of that solve
        commentP = subprocess.Popen(["node", self.fumenComment, fumenCombineOut] + percents, stdout=subprocess.PIPE)
        line = commentP.stdout.read().decode().rstrip()

        if fumenCode or len(countSolve) > 128:
            fumenCode = line[21:]

        if tinyurl:
            try:
                line = self.make_tiny(line)
            except:
                line = "Tinyurl did not accept fumen due to url length"

        with open(output, "w", encoding = "utf-8") as infile:
            infile.write(f"Unique Solves Filtered for {','.join(aliases)}: \n")
            infile.write(line)
            if fumenCode:
                infile.write("\n" + fumenCode)

    # determine the length of the last bag based on queue
    def __findLastBag(self, pieces, pcNum):
        if not pieces:
            if pcNum != -1:
                lastBag = set(self.PIECES)
                newBagNumUsed = (pcNum * 3) % 7 + 1
                return set(lastBag), newBagNumUsed
            else:
                raise SyntaxError("One of pieces or pcNum must be filled out")

        if not re.match("[!1-7*]", pieces[-1]):
            raise SyntaxError("The pieces inputted doesn't end with a bag")

        # what kind of bag is the last part
        lastPartPieces = re.findall("\[?([\^tiljszoTILJSZO*]+)\]?P?[1-7!]?", pieces.split(",")[-1])[0]
        if not lastPartPieces:
            raise SyntaxError("The pieces inputted doesn't end with a bag")

        # number of pieces used in the next bag
        newBagNumUsed = pieces[-1]

        # turn the piece input into data for determining saves
        if lastPartPieces[0] == "*":
                # all pieces used
                lastBag = self.PIECES
        elif lastPartPieces[0] == "^":
                # remove the pieces from the bag
                lastBag = set(self.PIECES) - set([piece.upper() for piece in lastPartPieces[1:]])
        else:
                # only these pieces in the bag
                lastBag = set([piece.upper() for piece in lastPartPieces])

        # determine the number of pieces the last bag has
        if newBagNumUsed.isnumeric():
            newBagNumUsed = int(newBagNumUsed)
        elif newBagNumUsed == "!":
            # it must be !
            newBagNumUsed = len(lastBag)
        else:
            # case without a number or ! (just *)
            newBagNumUsed = 1

        return set(lastBag), newBagNumUsed

    def make_tiny(self, url):
        import contextlib

        try:
            from urllib.parse import urlencode

        except ImportError:
            from urllib import urlencode
        from urllib.request import urlopen

        request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
        with contextlib.closing(urlopen(request_url)) as response:
            return response.read().decode('utf-8 ')

    # finds all the saves and adds them to a list
    def __createAllSavesQ(self, savePieces, bagSavePieces, solveable=True):
        allSaves = []
        if solveable and not savePieces:
            lstSaves = list(bagSavePieces)
            saves = [self.tetrisSort("".join(lstSaves))]
            return saves
        for p in savePieces:
            lstSaves = list(bagSavePieces)
            lstSaves.append(p)
            saves = self.tetrisSort("".join(lstSaves))
            allSaves.append(saves)
        return allSaves

    # turn the wantedPieces into a multi-depth stack to easily parse through
    def __makeStack(self, wantedPieces, index=0, depth=0):
        stack = []

        queue = ""
        operatorHold = ""
        justAddedHold = False
        while index < len(wantedPieces):
            char = wantedPieces[index]

            # finish for normal queue
            if queue and not re.match("[TILJSZO]", char):
                stack.append(self.tetrisSort(queue))
                queue = ""

            # regex queue
            if char == "/":
                queue = re.search("(/.*?/)", wantedPieces[index:])
                if queue:
                    queue = queue.group(1)
                else:
                    raise SyntaxError("Wanted Saves: Missing ending '/' in regex queue")
                stack.append(queue)
                index += len(queue) - 1
                queue = ""

            # normal queue
            elif re.match("[TILJSZO]", char):
                queue += char

            # negator
            elif char == "!":
                stack.append("!")
            # avoider
            elif char =="^":
                stack.append("^")

            # operator
            elif char == "&" or char == "|":
                if operatorHold == char:
                    stack.append(operatorHold*2)
                    operatorHold = ""
                else:
                    operatorHold += char
                    justAddedHold = True

            # parentheses
            elif char == "(":
                lst, i = self.__makeStack(wantedPieces, index+1, depth+1)
                stack.append(lst)
                index = i
            elif char == ")":
                if depth != 0:
                    return stack, index
                else:
                    raise SyntaxError("Wanted Saves: Missing opening parentheses")
            # error
            else:
                raise SyntaxError(f"Wanted Saves: Input has unknown character '{char}'")

            if justAddedHold:
                justAddedHold = False
            elif operatorHold:
                raise SyntaxError("Wanted Saves: Operator inputted incorrectly should be && or ||")

            index += 1

        if queue:
            stack.append(self.tetrisSort(queue))
            queue = ""

        # check if back to the top layer
        if depth == 0:
            return stack
        else:
            raise SyntaxError("Wanted Saves: Missing closing parentheses")

    def __compareQueues(self, allSaves, queue):
        # hold all queues that match
        matchedSaves = set()

        # check regex queue
        if re.match("/.*/", queue):
            for save in allSaves:
                if re.search(queue[1:-1], save):
                    matchedSaves.add(save)

        # normal queue
        else:
            for save in allSaves:
                index = 0
                for piece in save:
                    if index == len(queue):
                        break
                    if piece == queue[index]:
                        index += 1
                if index == len(queue):
                    matchedSaves.add(save)

        return matchedSaves

    def parseStack(self, allSaves, stack):
        negate = False
        avoid = False
        operator = ""
        currMatches = set()
        for ele in stack:
            if ele == "!":
                negate = not negate
            elif ele == "^":
                avoid = not avoid

            elif self.isOperator(ele):
                operator = ele

            elif self.isQueue(ele) or type(ele) == type([]):
                if self.isQueue(ele):
                    matchedSaves = self.__compareQueues(allSaves, ele)
                else:
                    matchedSaves = self.parseStack(allSaves, ele)

                # if avoid then match with all queues that previously not matched
                if avoid:
                    matchedSaves = set(allSaves) - matchedSaves
                # if negate then didn't match or if matched then match with all
                if negate:
                    if matchedSaves:
                        matchedSaves = set()
                    else:
                        matchedSaves = set(allSaves)

                if operator:
                    if operator == "&&":
                        if currMatches and matchedSaves:
                            currMatches = currMatches | matchedSaves
                        else:
                            currMatches = set()
                    elif operator == "||":
                        currMatches = currMatches | matchedSaves
                    else:
                        raise RuntimeError("WantedParse: Operator variable got a non-operator (please contact dev)")
                else:
                    currMatches = matchedSaves

            else:
                raise RuntimeError("WantedParse: Stack includes string that's not a queue nor operator (please contact dev)")
        return currMatches

    # sorts the pieces inputted
    def tetrisSort(self, queue):
        # order of the pieces TILJSZO
        PIECEORDER = {
            "T":"1", "1":"T",
            "I":"2", "2":"I",
            "L":"3", "3":"L",
            "J":"4", "4":"J",
            "S":"5", "5":"S",
            "Z":"6", "6":"Z",
            "O":"7", "7":"O"
        }

        numQ = ""
        for p in queue:
            numQ += PIECEORDER[p]

        numQ = "".join(sorted(list(numQ)))
        queue = ""

        for c in numQ:
            queue += PIECEORDER[c]

        return queue

    def getOrderValue(self, queue):
        PIECEORDER = {
            "T":"1",
            "I":"2",
            "L":"3",
            "J":"4",
            "S":"5",
            "Z":"6",
            "O":"7"
        }

        val = ""
        for p in queue:
            val += PIECEORDER[p]

        return val

    def isOperator(self, operator):
        return operator == "&&" or operator == "||"

    def isQueue(self, queue):
        if queue[0] == "/":
            return True
        return re.match("[TILJSZO]+", str(queue))

def runTestCases():
    s = Saves()

    tests = open("resources/testOutputs.txt", "r", encoding = "utf-8")

    s.handleParse(customInput=["percent", "-w", "/[OSZ]/#O/S/Z", "-k", "2nd Saves", "-a", "-pc", "2", "-f", "resources/testPath2.csv"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile:
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 1")

    tests.readline()
    s.handleParse(customInput=["percent", "-w", "/[ILJO]/", "-p", "*p7", "-fa", "-os", "-f", "resources/testPath2.csv"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile:
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 2")

    tests.readline()
    s.handleParse(customInput=["percent", "-k", "1st Saves", "-p", "*p7", "-fr", "-os", "-f", "resources/testPath1.csv"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile:
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 3")

    tests.readline()
    s.handleParse(customInput=["filter", "-w", "/T.*[LJ].*$/", "-pc", "1", "-f", "resources/testPath1.csv", "-t"])
    with open(s.filterOutput, "r") as outfile:
        for out in outfile:
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 4")

    tests.close()

    # clean up
    open(s.filterOutput, "w").close()
    open(s.percentOutput, "w").close()
    os.remove("resources/filteredPath.csv")
    os.remove("path_minimal_strict.md")

if __name__ == "__main__":
    s = Saves()
    s.handleParse()
    #runTestCases()
