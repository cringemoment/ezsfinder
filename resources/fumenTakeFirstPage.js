const fs = require("fs");
const {encoder, decoder} = require('tetris-fumen');

var fumenCodes = process.argv.slice(2);
fumenCodes = fumenCodes.join(" ").split(" ");
fumenCodes = fumenCodes.join("\n").split("\n");
var newFumenCodes = [];
for(let code of fumenCodes){
    let page = decoder.decode(code)[0];
    let pages = [];
    pages.push({field: page.field, comment: page.comment});
    newFumenCodes.push(encoder.encode(pages));
}

console.log(newFumenCodes.join(" "));