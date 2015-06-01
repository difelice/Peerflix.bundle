#!/usr/bin/env node

var WaterMarker = require('watermark-video');

var escapeSpaces = function(str) {
	return str.replace(/ /ig, '\\ ');
};

var videoFilePath = 'Build/assets/5seconds.avi';

for (var i = 0; i <= 100; i++) {
	var outputFilePath = [
		'Build/assets/progressbar-video-',
		i,
		'.avi'
	].join('');

	var watermarkFilePath = [
		'Build/assets/progressbar-image-',
		i,
		'.gif'
	].join('');

	new WaterMarker(
		{
			outputFilePath: outputFilePath,
			videoFilePath: videoFilePath,
			watermarkFilePath: watermarkFilePath
		}
	);
}

