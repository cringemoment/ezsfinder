// Import the fs module
const fs = require('fs');

// Define the path to the CSV file
const filePath = 'output/path.csv';

// Read the CSV file
fs.readFile(filePath, 'utf-8', (err, data) => {
  if (err) {
    console.error(err);
    return;
  }

  // Split the CSV data into an array of rows
  const rows = data.split('\n');

  // Get the second row (index 1)
  const secondRow = rows[1];

  // Split the row into an array of values
  const values = secondRow.split(',');

  // Get the length of the first value
  const length = values[0].length;

  // Log the length to the console
  console.log(length);
});
