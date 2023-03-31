import subprocess
import re

def make_tiny(url):
    import contextlib

    try:
        from urllib.parse import urlencode

    except ImportError:
        from urllib import urlencode
    from urllib.request import urlopen

    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8 ')

fumenCombine = "fumenCombine.js"
fumenComment = "fumenAddComment.js"

with open("path_minimal_strict.md", "r") as trueMinFile:
    trueMinLines = trueMinFile.readlines()

totalCases = int(re.search("/ (\d+)\)", trueMinLines[2]).group(1))
percents = []
for line in trueMinLines[13::9]:
    numCoverCases = int(re.match("(\d+)", line).group(1))
    percent = numCoverCases / totalCases * 100
    percent = f'{percent:.2f}% ({numCoverCases}/{totalCases})'
    percents.append(percent)
fumenLst = re.findall("(v115@[a-zA-Z0-9?/+]*)", trueMinLines[6])

combineP = subprocess.Popen(["node", fumenCombine] + fumenLst, stdout=subprocess.PIPE)
fumenCombineOut = combineP.stdout.read().decode().rstrip()
commentP = subprocess.Popen(["node", fumenComment, fumenCombineOut] + percents, stdout=subprocess.PIPE)
line = commentP.stdout.read().decode().rstrip()

try:
    line = make_tiny(line)
except:
    pass

trueminimaloutput = open("trueminimaloutput.txt", "w")
print("True minimal:")
print(line)
trueminimaloutput.write(line)
