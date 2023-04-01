# coding=utf-8
import csv
import sys
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--csv-path", default=r".\output\cover.csv", help=r"Defaults to output\cover.csv.")
parser.add_argument("--unglued-fumen-script-path", default=r".\unglueFumen.js", help=r"Defaults to .\unglueFumen.js. Note this depends on Hillosanation/GluingFumens instead of Marfung37/GluingFumens.")
parser.add_argument("--output-file-path", default="", help="Appends '_to_path' to the input csv file by default. Note to keep the .csv extenstion.")
args = parser.parse_args(sys.argv[1:])

InputCSV = []
for row in csv.reader(open(args.csv_path, 'r')):
    InputCSV.append(row)
# print(InputCSV)

#write fumens to a file to prevent command length limits
open(r"output\temp_gluedfumens.txt", "w").write("\n".join(InputCSV[0][1:]))

os.system(fr'node {args.unglued_fumen_script_path} --fp ".\output\temp_gluedfumens.txt" --op ".\output\temp_ungluedfumens.txt"') #calls unglueFumen.js

ungluedRow = open(r"output\temp_ungluedfumens.txt", "r").read().split("\n")
# print(ungluedRow)

OutputCSV = []
OutputCSV.append(["pattern", "solutionCount", "solutions", "unusedMinos", "fumens"]) #QoL, not read by strict-minimal

for row in InputCSV[1:]: 
    sequence = row[0]
    SuccessFumens = []
    for element, fumen in zip(row[1:], ungluedRow):
        if (element == 'O'):
            SuccessFumens.append(fumen)
            # print(SuccessFumens)
    OutputCSV.append([sequence, len(SuccessFumens), '', '', ";".join(SuccessFumens)])
# print(OutputCSV)


OutputFilePath = ""
if (args.output_file_path != ""):
    OutputFilePath = args.output_file_path
else:
    extentionPos = args.csv_path.find(".csv")
    OutputFilePath = args.csv_path[:extentionPos] + "_to_path" + args.csv_path[extentionPos:]

print(f"writing to file: {OutputFilePath}")
OutputFileWriter = csv.writer(open(OutputFilePath, 'w', newline=''))
for row in OutputCSV:
    OutputFileWriter.writerow(row)
