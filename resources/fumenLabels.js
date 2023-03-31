const fs = require("fs");
const {decoder} = require('tetris-fumen');

var fumenCodes = process.argv.slice(2)
var labels = [];
for(let code of fumenCodes){
    page = decoder.decode(code)[0];
    labels.push(page.comment);
}

console.log(labels.join("\n"));