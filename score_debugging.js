const { encoder, decoder, Field } = require('tetris-fumen');

function toPage(in_field, i) {
	let field = in_field.copy();
	flags = {
		rise: false,
		mirror: false,
		colorize: true,
		comment: '',
		lock: true,
		piece: undefined,
	};
	page = {
		comment: '',
		field,
		flags: flags,
		index: i,
	};
	return page;
}

function occupiedCorner(field, corner) {
	if (corner[1] < 0 || corner[0] < 0 || corner[0] > 9) return true;
	return field.at(corner[0], corner[1]) != '_';
}

function clearedOffset(rowsCleared, yIndex) {
	for (let row of rowsCleared) {
		if (yIndex >= row) yIndex++;
	}
	return yIndex;
}

function inverse_clearedOffset(rowsCleared, yIndex) {
	offset = 0;
	for (let row of rowsCleared) {
		if (yIndex > row) offset++;
	}
	return offset;
}

function get_score(
	queue,
	solution_pages,
	base_b2b = true,
	base_combo = 1,
	b2b_end_bonus = 0,
	base_field = undefined,
	cumulative_rowsCleared = undefined,
	base_viz = undefined,
	base_rowsCleared = undefined
) {
	// compute line clear orders in the source solution pages
	if (cumulative_rowsCleared == undefined) {
		let rowsCleared = [];
		let testing_field = solution_pages[0].field.copy(); // a copy of it so we don't disturb the original field
		cumulative_rowsCleared = [[]];
		for (let page of solution_pages) {
			testing_field.fill(page.operation);
			let positions = page.operation.positions();

			// check for line clears
			let y_positions = new Set();
			for (position of positions) {
				y_positions.add(position.y);
			}
			let temp_rowsCleared = new Set();
			for (let y of y_positions) {
				let line_cleared = true;
				for (let x = 0; x < 10; x++) {
					if (testing_field.at(x, y) == '_') line_cleared = false;
				}
				if (line_cleared) temp_rowsCleared.add(clearedOffset(rowsCleared, y));
			}
			for (let row of temp_rowsCleared) rowsCleared.push(row);
			testing_field.clearLine();
			rowsCleared.sort();
			cumulative_rowsCleared.push(rowsCleared.slice());

			// console.log(cumulative_rowsCleared)
		}
	}

	if (base_field == undefined) base_field = solution_pages[0].field.copy();

	if (base_viz == undefined) {
		var base_viz = []; // vizualizer fumen for debugging purposes
		base_viz.push(toPage(base_field, 0));
	}

	if (base_rowsCleared == undefined) base_rowsCleared = [];

	// let score = 0;
	let results = [];

	let piece = queue[0];
	for (let page of solution_pages) {
		let op = page.operation.copy();
		// assuming the queue matches the pieces in the solution and there's exactly one of each piece, no error handling here :sunglasses:
		if (piece == op.type) {
			global_y = clearedOffset(cumulative_rowsCleared[page.index], op.y);
			op.y = global_y - inverse_clearedOffset(base_rowsCleared, global_y);

			if (base_field.canLock(op)) {
				let field = base_field.copy();
				let score = 0;
				let b2b = base_b2b;
				let combo = base_combo;
				let viz = [...base_viz];
				let rowsCleared = [...base_rowsCleared];
				let log = piece + ": ";
				field.put(op);

				viz.push(toPage(field, viz.length));

				let positions = op.positions();

				// check for line clears
				let y_positions = new Set();
				for (position of positions) {
					y_positions.add(position.y);
				}
				temp_rowsCleared = new Set();
				for (let y of y_positions) {
					let line_cleared = true;
					for (let x = 0; x < 10; x++) {
						if (field.at(x, y) == '_') line_cleared = false;
					}
					if (line_cleared) temp_rowsCleared.add(clearedOffset(rowsCleared, y));
				}
				for (let row of temp_rowsCleared) rowsCleared.push(row);
				rowsCleared.sort();
				let lines_cleared = temp_rowsCleared.size;

				// console.log(lines_cleared);
				let tspin = false;
				let mini = true;
				if (op.type == 'T') {
					let four_corners = [
						[op.x - 1, op.y + 1], // northwest
						[op.x + 1, op.y + 1], // northeast
						[op.x + 1, op.y - 1], // southeast
						[op.x - 1, op.y - 1], // southwest
					];
					let num_corners = 0;
					for (let corner of four_corners) {
						if (occupiedCorner(field, corner)) num_corners++;
					}
					if (num_corners >= 3) {
						tspin = true;
						let two_corners;
						switch (op.rotation) {
							case 'spawn':
								two_corners = [four_corners[0], four_corners[1]];
								break;
							case 'right':
								two_corners = [four_corners[1], four_corners[2]];
								break;
							case 'reverse':
								two_corners = [four_corners[2], four_corners[3]];
								break;
							case 'left':
								two_corners = [four_corners[3], four_corners[0]];
								break;
						}
						let num_corners = 0;
						for (let corner of two_corners) {
							if (occupiedCorner(field, corner)) num_corners++;
							if (num_corners == 2) mini = false;
						}
					}
				}

				if (tspin) {
					if (mini) {
						switch (lines_cleared) {
							case 0:
								log += 't spin mini 0: ' + 100;
								score += 100;
								break;
							case 1:
								if (b2b) {
									log += 'b2b t spin mini single: ' + 300;
									score += 300;
								} else {
									log += 't spin mini single: ' + 200;
									score += 200;
								}
								break;
							case 2:
								if (b2b) {
									log += 'b2b t spin mini double: ' + 600; // ultra counts these as normal tsds tho... change to 1800?
									score += 600;
								} else {
									log += 't spin mini double: ' + 400; // ultra counts these as normal tsds tho... change to 1200?
									score += 400;
								}
								break;
							default:
								throw 'bruh something went wrong';
						}
					} else {
						switch (lines_cleared) {
							case 0:
								log += 't spin 0: ' + 400;
								score += 400;
								break;
							case 1:
								if (b2b) {
									log += 'b2b t spin single: ' + 1200;
									score += 1200;
								} else {
									log += 't spin single: ' + 800;
									score += 800;
								}
								break;
							case 2:
								if (b2b) {
									log += 'b2b t spin double: ' + 1800;
									score += 1800;
								} else {
									log += 't spin double: ' + 1200;
									score += 1200;
								}
								break;
							case 3:
								if (b2b) {
									log += 'b2b t spin triple: ' + 2400;
									score += 2400;
								} else {
									log += 't spin triple: ' + 1600;
									score += 1600;
								}
								break;
							default:
								throw 'bruh something went wrong';
						}
					}
					if (lines_cleared > 0) b2b = true;
				} else {
					switch (lines_cleared) {
						case 0:
							// break the combo
							break;
						case 1:
							log += 'single: ' + 100;
							score += 100;
							break;
						case 2:
							log += 'double: ' + 300;
							score += 300;
							break;
						case 3:
							log += 'triple: ' + 500;
							score += 500;
							break;
						case 4:
							if (b2b) {
								log += 'b2b quad: ' + 1200;
								score += 1200;
							} else {
								log += 'quad: ' + 800;
								score += 800;
							}
							b2b = true;
							break;
						default:
							throw 'bruh something went wrong';
					}
				}

				if (!tspin && lines_cleared > 0 && lines_cleared < 4) b2b = false;

				if (lines_cleared == 0) combo = 0;
				else {
					if (combo > 0) {
						log += ' combo ' + combo + ' : ' + 50 * combo;
						score += 50 * combo;
					}
					combo++;
				}

				field.clearLine();

				// check if board is cleared
				let pc = true;
				for (let x = 0; x < 10; x++) {
					if (field.at(x, 0) != '_') pc = false; // just gonna check the bottom row
				}
				if (pc) {
					// console.log('PC:', 3000);
					// score += 3000;
					if (b2b) score += b2b_end_bonus;
					// return score;
				}

				if (queue.length <= 1 && !pc) score = -3000;

				if (queue.length <= 1) results.push([score, log]);
				else {
					temp = get_score(
						queue.substring(1),
						solution_pages,
						b2b,
						combo,
						b2b_end_bonus,
						field,
						cumulative_rowsCleared,
						viz,
						rowsCleared
                    );
                    results.push([score + temp[0], log + ", " + temp[1]])
				}

				// console.log(encoder.encode(viz));
			} else {
				// throwing an error for debugging purposes, but may want to remove this if working on non *p7 solution queues with dupes
				// console.log(queue, encoder.encode(solution_pages));
				// console.log(encoder.encode(viz));
				// console.log(field.str(), op, global_y, rowsCleared);
				// throw "ummmmmmmmm";
				// return 0; // piece could not lock, solution and queue were incompatible
			}
		}
	}

	if (results.length < 1) {
		return [-3000, ""];
		// console.log(queue, encoder.encode(base_viz));
		// console.log(base_field.str())
		// throw results;
    }
    result_score = results[0][0];
    result_log = results[0][1];
    for (result of results) {
        if (result[0] > result_score) {
            result_score = result[0];
            result_log = result[1];
        }
    }
    return [result_score, result_log];

	// if (queue.length <= 1) {
	// 	// if the last piece placement didn't result in a PC, something went wrong
	// 	throw ('uhhhhhhhhhh', encoder.encode(viz));
	// 	return -3000;
	// }

	// return (
	// 	score +
	// 	get_score(
	// 		queue.substring(1),
	// 		solution_pages,
	// 		b2b,
	// 		combo,
	// 		b2b_end_bonus,
	// 		field.copy(),
	// 		cumulative_rowsCleared, // this should be global and unchanged so doesn't need copying
	// 		[...viz], // um figure out how to deep copy this
	// 		[...rowsCleared] // shallow array copy
	// 	)
	// );
}

fumen = 'v115@vhJT/I0hBxiBllBGoBipBXrBVxBUtBXqB';
pages = decoder.decode(fumen);

let queue = 'SZTZJLOTSI';
console.log(get_score(queue, pages, false, 0, 0));
