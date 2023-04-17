// encode.js

const { encoder, Field } = require('tetris-fumen');

// Get Tetris board from command line argument
const tetrisBoard = process.argv[2];

// Create a Field object from the Tetris board
const field = Field.create(tetrisBoard);

// Create a page with the Field object
const page = {
  field: field,
};

// Encode the page to Fumen
const fumen = encoder.encode([page]);

console.log(fumen);
