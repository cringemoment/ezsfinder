const {encoder, decoder} = require('tetris-fumen');

var pages = [];
var fumenCodes = process.argv.slice(2)

for(let code of fumenCodes){
    field = decoder.decode(code)[0].field;
    pages.push({field: field});
}
fumenLink = "https://fumen.zui.jp/?" + encoder.encode(pages);

console.log(fumenLink);