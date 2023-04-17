const { decoder } = require('tetris-fumen');
const fumen = process.argv[2];
const pages = decoder.decode(fumen);
const page = pages[0];
var field = page.field.str();
const fieldRows = field.split('\n');
fieldRows.pop();
field = fieldRows.join('\n');
console.log(field);
