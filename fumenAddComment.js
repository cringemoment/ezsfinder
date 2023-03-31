const {encoder, decoder} = require('tetris-fumen');

var cmdInput = process.argv.slice(2);
var pages = decoder.decode(cmdInput[0]);
var comments = cmdInput.slice(1);

for(var i = 0; i < comments.length; i++){
    pages[i].comment = comments[i];
}
var fumenLink = "https://fumen.zui.jp/?" + encoder.encode(pages);

console.log(fumenLink);