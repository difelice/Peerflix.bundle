#!/usr/bin/env node

var GIFEncoder = require('gifencoder');
var Canvas = require('canvas');
var fs = require('fs');

var VIDEO_DURATION = 5*1000;
var VIDEO_HEIGHT = 300;
var VIDEO_WIDTH = 500;

var canvas = new Canvas(VIDEO_WIDTH, VIDEO_HEIGHT);
canvas.height = VIDEO_HEIGHT;
canvas.width = VIDEO_WIDTH;

var ctx = canvas.getContext('2d');
ctx.translate(VIDEO_WIDTH / 2, VIDEO_HEIGHT / 2);
ctx.rotate((-1 / 2) * Math.PI); // rotate -90 deg
ctx.antialias = 'subpixel';
ctx.fillStyle = "#FFFFFF";
ctx.filter = 'best';
ctx.opacity = 0.2;
ctx.patternQuality = 'best';
ctx.textDrawingMode = 'glyph';
ctx.fillRect(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT);

var addText = function(text) {
	ctx.rotate((1 / 2) * Math.PI);

	text += '%';

	var textDimensions = ctx.measureText(text);

	ctx.font = '48px Impact';
	ctx.fillStyle = "#FFFFFF";
	ctx.fillText(
		text,
		-1 * textDimensions.width / 2,
		0
	);

	ctx.rotate((-1 / 2) * Math.PI);
};

var clearCanvas = function() {
	// Store the current transformation matrix
	ctx.save();

	// Use the identity matrix while clearing the canvas
	ctx.setTransform(1, 0, 0, 1, 0, 0);
	ctx.clearRect(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT);

	// Restore the transform
	ctx.restore();
}

var getProgressFrame = function(options) {
	var radius = Math.floor((Math.min(VIDEO_WIDTH, VIDEO_HEIGHT) - options.lineWidth) / 2);

	var drawCircle = function(color, lineWidth, percent) {
		percent = Math.min(Math.max(0, percent || 100), 100);
		ctx.beginPath();
		ctx.arc(0, 0, radius, 0, Math.PI * 2 * percent / 100, false);
		ctx.strokeStyle = color;
		ctx.lineCap = 'round';
		ctx.lineWidth = lineWidth;
		ctx.stroke();
	};

	drawCircle('#EFEFEF', options.lineWidth, 100);
	drawCircle('#555555', options.lineWidth, options.percent);

	return ctx;
};

try {
	console.log('Writing images now...');

	for (var i = 0; i <= 100; i++) {
		var encoder = new GIFEncoder(VIDEO_WIDTH, VIDEO_HEIGHT);

		var imagePath = [
			__dirname,
			'/assets/progressbar-image-',
			i,
			'.gif'
		].join('');

		var step = 10;
		var numberOfSteps = 100 / step;
		var delay = VIDEO_DURATION / numberOfSteps;

		encoder.createReadStream().pipe(fs.createWriteStream(imagePath));

		encoder.start();
		encoder.setRepeat(-1);   // 0 for repeat, -1 for no-repeat
		encoder.setDelay(delay);
		encoder.setQuality(5000);

		clearCanvas();

		addText(i);

		for (var j = 0; j <= 100; j += step) {
			var frame = getProgressFrame({
				lineWidth: 5,
				percent: j
			});

			encoder.addFrame(frame);
		}

		console.log('Writing image', imagePath);

		encoder.finish();
	}

	console.log('Done!');
}
catch (e) {
	console.error(e);
}