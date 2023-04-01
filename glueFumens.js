const fs = require('fs');
const {decoder, encoder, Field} = require('tetris-fumen');

const rowLen = 10;

const pieceMappings = {
    "T": [
        [[0, -1], [0, 0], [-1, -1], [1, -1]],
        [[0, -1], [0, 0], [-1, -1], [0, -2]],
        [[1, 0], [0, 0], [2, 0], [1, -1]],
        [[0, -1], [0, 0], [1, -1], [0, -2]]
        ],
    "I": [
        [[1, 0], [0, 0], [2, 0], [3, 0]],
        [[0, -2], [0, 0], [0, -1], [0, -3]]
        ],
    "L": [
        [[-1, -1], [0, 0], [-2, -1], [0, -1]],
        [[1, -1], [0, 0], [1, 0], [1, -2]],
        [[1, 0], [0, 0], [2, 0], [0, -1]],
        [[0, -1], [0, 0], [0, -2], [1, -2]]
        ],
    "J": [
        [[1, -1], [0, 0], [0, -1], [2, -1]],
        [[0, -1], [0, 0], [-1, -2], [0, -2]],
        [[1, 0], [0, 0], [2, 0], [2, -1]],
        [[0, -1], [0, 0], [1, 0], [0, -2]]
        ],
    "S": [
        [[0, -1], [0, 0], [1, 0], [-1, -1]],
        [[1, -1], [0, 0], [0, -1], [1, -2]]
        ],
    "Z": [
        [[1, -1], [0, 0], [1, 0], [2, -1]],
        [[0, -1], [0, 0], [-1, -1], [-1, -2]]
        ],
    "O": [
        [[0, -1], [0, 0], [1, 0], [1, -1]]
        ]
}

const rotationDict = {
    0: "spawn",
    1: "left",
    2: "reverse",
    3: "right"
}

function checkRotation(x, y, field, piecesArr, allPiecesArr, removeLineClearBool, depth=0){
    const piece = field.at(x, y);

    const rotationStates = pieceMappings[piece];

    let found = false;
    let leftoverPieces = null;

    for(let state = 0; state < rotationStates.length; state++){
        let minoPositions = [];
        let newPiecesArr = piecesArr.slice();
        for(let pos of rotationStates[state]){
            let posX = x + pos[0];
            let posY = y + pos[1];

            // checks for position is in bounds
            if(posX < 0 || posX >= rowLen){
                break;
            }
            if(posY < 0){
                break;
            }

            if(field.at(posX, posY) == piece){
                minoPositions.push([posX, posY]);
            }
            else{
                break;
            }
        }
        // if there's 4 minos
        if(minoPositions.length == 4){
            // a rotation is found
            let foundBefore = found;

            found = true;

            // a rotation that works
            let operPiece = {
                type: piece,
                rotation: rotationDict[state],
                x: minoPositions[0][0],
                y: minoPositions[0][1]
            }
            newPiecesArr.push(operPiece)

            let newField = field.copy()
            for(let pos of minoPositions){
                let posX = pos[0];
                let posY = pos[1];
                // change the field to be the piece to be replaced by gray
                newField.set(posX, posY, "X");
            }
            let oldHeight = newField.str().split("\n").length - 1;
            if(removeLineClearBool){
                newField = removeLineClears(newField);
            }
            

            const height = newField.str().split("\n").length - 1;

            // check if a line clear occurred
            let startx = x;
            let starty = y
            if(oldHeight > height){
                // start position to 0 otherwise it's where we left off scanning the field
                startx = 0;
                starty = height - 1
            }

            let oldLen = allPiecesArr.length;

            let data = scanField(startx, starty, newField, newPiecesArr, allPiecesArr, removeLineClearBool, depth + 1)
            let possPiecesArr = data[0];
            leftoverPieces = data[1];

            if(leftoverPieces == null){
                leftoverPieces = findRemainingPieces(newField)
            }
            
            // if the field doesn't have any more pieces it's good
            if(possPiecesArr != null && leftoverPieces.length == 0){
                allPiecesArr.push(possPiecesArr);
            } else if(oldLen == allPiecesArr.length){
                // the piece didn't result into a correct glued fumen
                if(!leftoverPieces.includes(piece)){
                    return [found, leftoverPieces]
                } else {
                    found = foundBefore
                }
            }
        }
    }
    return [found, leftoverPieces]
}

function scanField(x, y, field, piecesArr, allPiecesArr, removeLineClearBool, depth=0){
    var newX = x;
    for(let newY = y; newY >= 0; newY--){
        for(; newX < rowLen; newX++){
            // if it is a piece
            if(field.at(newX, newY) != "X" && field.at(newX, newY) != "_"){
                let [rotationWorked, leftover] = checkRotation(newX, newY, field, piecesArr, allPiecesArr, removeLineClearBool, depth)
                if(rotationWorked){
                    // a rotation works for the piece so just end the function as the scan finished
                    return [null, leftover];
                }
                // skips this one that meets no rotation as it might be a cut piece
            }
        }
        newX = 0
    }
    return [piecesArr, null];
}

function makeEmptyField(field, height){
    var emptyField = field.copy();
    for(let y = height-1; y >= 0; y--){
        for(let x = 0; x < rowLen; x++){
            let piece = emptyField.at(x, y);
            if(piece.match(/[TILJSZO]/)){
                emptyField.set(x, y, "_");
            }
        }
    }
    return emptyField;
}

function removeLineClears(field){
    var lines = field.str().split("\n");
    for(let i = lines.length-1; i >= 0; i--){
        if(lines[i].match(/X{10}/)){
            lines.splice(i, 1);
        }
    }
    const newField = Field.create(lines.slice(0, -1).join(""), lines[-1]);
    return newField;
}

function findRemainingPieces(field){
    let lines = field.str().split("\n").slice(0, -1);
    let piecesFound = [];
    for(let line of lines){
        let pieces = line.match(/[TILJSZO]/g)
        if(pieces != null){
            for(let piece of pieces){
                if(!piecesFound.includes(piece)){
                    piecesFound.push(piece);
                }
            }
            
        }
    }
    return piecesFound;
}

function parseArgs(sliced_argv){
    return require('yargs')(sliced_argv)
    .option({
      'so': {
          alias: 'single-output',
          default: false,
          describe: 'Option to only add one glued fumen per fumen inputted. Useful for cover in sfinder.',
          type: 'boolean',
      },
      's': {
          alias: 'silence',
          default: false,
          describe: 'Does not report when multiple fumens were available.',
          type: 'boolean',
      },
      'fu': {
          alias: 'fumen',
          default: '',
          describe: 'The input to be glued. If multiple fumens are to be glued, then put them in a space-separated string.',
          type: 'string',
      },
      'fp': {
          alias: 'file-path',
          default: '',
          type: 'string',
          describe: 'File path for a utf8-encoded file containing whitespace-separated fumens. This overrides --fu.',
      },
      'op': {
          alias: 'output-path',
          default: '',
          type: 'string',
          describe: 'File path for the output file.'
      },
    })
    .check((argv, options) => {
      const filePaths = argv
      if ((filePaths.fu == '') && (filePaths.fp == '')) {
        throw new Error("Neither fp nor fu was provided.");
      } else {
        return true; // tell Yargs that the arguments passed the check
      }
    })
    .hide('version') // i dont need version control
    .help()
    .alias('help', 'h').argv;
}

function glueFumen(sliced_argv=process.argv.slice(2),removeLineClearBool=true,exportResults=true){
    const argv = parseArgs(sliced_argv);

    let fumenData = (argv.fp != "" ? fs.readFileSync(argv.fp, "utf8") : argv.fu);
    const fumenCodes = fumenData.split(/\s+/);

    var allPiecesArr = [];
    var allFumens = [];
    var fumenIssues = 0;
    for(let code of fumenCodes){
        let inputPages = decoder.decode(code);
        let thisGlueFumens = []; // holds the glue fumens for this fumenCode
        for(let pageNum = 0; pageNum < inputPages.length; pageNum++){
            let field = inputPages[pageNum].field;
            field = removeLineClears(field);
            const height = field.str().split("\n").length - 1;
            let emptyField = makeEmptyField(field, height);
            allPiecesArr = []

            scanField(0, height - 1, field, [], allPiecesArr, removeLineClearBool);
            
            if(allPiecesArr.length == 0){
                console.log("Warning: " + code + " couldn't be glued");
                fumenIssues++;
            }
            
            for(let piecesArr of allPiecesArr){
                let pages = [];
                pages.push({
                    field: emptyField,
                    operation: piecesArr[0]
                })
                for(let i = 1; i < piecesArr.length; i++){
                    pages.push({
                        operation: piecesArr[i]
                    })
                }
                let pieceFumen = encoder.encode(pages);
                thisGlueFumens.push(pieceFumen);
            }

            if(allPiecesArr.length > 1){
                // multiple outputs warning
                if (argv.so) {
                    thisGlueFumens = [thisGlueFumens[0]];
                }
                if (!argv.s) console.log("Warning: " + code + " led to " + allPiecesArr.length + " outputs" + (argv.so ? ", inserting only 1" : "") + ": " + thisGlueFumens.join(" "));
            }

            // add the glue fumens for this code to all the fumens
            allFumens.push(...thisGlueFumens)
        }
    }

    if(fumenIssues != 0){
        console.log("Warning: " + fumenIssues + " fumens couldn't be glued");
    }

    if (exportResults) return allFumens;

    allFumensString = allFumens.join("\n");
    if (argv.op == '') {
        console.log(allFumensString);
        return;
    }
    fs.writeFile(argv.op, allFumensString, (err) => {
        if (err) console.log(err);
        else console.log("File written successfully to " + argv.op + "\n");
    });
    return;

}

exports.glueFumen = glueFumen;

if(require.main == module){
    glueFumen(process.argv.slice(2),true,false);
}

