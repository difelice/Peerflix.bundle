import re
import time
import sys
import urllib

from torrent import TorrentMediaSearcher
from torrent_base import MovieNotFound, EpisodeNotFound, ShowNotFound, QualityNotFound

################################################################################

SUBPREFIX = 'shows'
RE_MAGNET = re.compile('\?magnet=(.+)$')

################################################################################

TorrentMediaSearcher()

@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='TV Shows')
	object_container.add(DirectoryObject(key=Callback(shows_menu, title='Trending', page='/api/shows/trending', page_index=1), title='Trending', summary='Browse TV shows currently being watched.'))
	object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/api/shows/popular', page_index=1), title='Popular', summary='Browse most popular TV shows.'))
	object_container.add(DirectoryObject(key=Callback(favorites_menu, title='Favorites'), title='Favorites', summary='Browse your favorite TV shows', thumb=R('favorites.png')))
	object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))
	return object_container

################################################################################

@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', page_index=int)
def shows_menu(title, page, page_index):
	object_container = ObjectContainer(title2=title)

	json_url  = Prefs['SCRAPYARD_URL'] + page + '?page={0}'.format(page_index)
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'shows' in json_data:
		for json_item in json_data['shows']:
			show_object = TVShowObject()
			SharedCodeService.common.fill_show_object(show_object, json_item)
			show_object.rating_key = json_item['trakt_slug']
			show_object.key        = Callback(show_menu, title=show_object.title, traktSlug=json_item['trakt_slug'])
			object_container.add(show_object)

	if (page_index + 1) <= 10:
		object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
def favorites_menu(title):
	traktSlugs = Dict['shows_favorites'] if 'shows_favorites' in Dict else []

	object_container = ObjectContainer(title2=title)

	json_url = Prefs['SCRAPYARD_URL'] + '/api/shows/favorites?'
	json_post = { 'shows_favorites': JSON.StringFromObject(traktSlugs) }
	json_data = JSON.ObjectFromURL(json_url, values=json_post, cacheTime=CACHE_1HOUR)

	if json_data and 'shows' in json_data:
		for json_item in json_data['shows']:
			show_object = TVShowObject()
			SharedCodeService.common.fill_show_object(show_object, json_item)
			show_object.rating_key = json_item['trakt_slug']
			show_object.key        = Callback(show_menu, title=show_object.title, traktSlug=json_item['trakt_slug'])
			object_container.add(show_object)

	object_container.objects.sort(key=lambda tvshow_object: show_object.title)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
	object_container = ObjectContainer(title2=title)

	json_url  = Prefs['SCRAPYARD_URL'] + '/api/shows/search?query=' + String.Quote(query)
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'shows' in json_data:
		for json_item in json_data['shows']:
			show_object = TVShowObject()
			SharedCodeService.common.fill_show_object(show_object, json_item)
			show_object.rating_key = json_item['trakt_slug']
			show_object.key        = Callback(show_menu, title=show_object.title, traktSlug=json_item['trakt_slug'])
			object_container.add(show_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def show_menu(title, traktSlug):
	object_container = ObjectContainer(title2=title)

	if 'shows_favorites' in Dict and traktSlug in Dict['shows_favorites']:
		object_container.add(DirectoryObject(key=Callback(remove_from_favorites, title='Remove from Favorites', showTitle=title, traktSlug=traktSlug), title='Remove from Favorites', summary='Remove TV show from Favorites', thumb=R('favorites.png')))
	else:
		object_container.add(DirectoryObject(key=Callback(add_to_favorites, title='Add to Favorites', showTitle=title, traktSlug=traktSlug), title='Add to Favorites', summary='Add TV show to Favorites', thumb=R('favorites.png')))

	json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + traktSlug
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'seasons' in json_data:
		for json_item in json_data['seasons']:
			season_object = SeasonObject()
			SharedCodeService.common.fill_season_object(season_object, json_item)
			season_object.rating_key    = '{0}-{1}'.format(traktSlug, season_object.index)
			season_object.key           = Callback(ShowSeason, title=season_object.title, showTitle=title, traktSlug=traktSlug, seasonIndex=season_object.index)
			object_container.add(season_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
def add_to_favorites(title, showTitle, traktSlug):
	if 'shows_favorites' not in Dict:
		Dict['shows_favorites'] = []

	if traktSlug not in Dict['shows_favorites']:
		Dict['shows_favorites'].append(traktSlug)
		Dict.Save()

	object_container = ObjectContainer(title2=title)
	object_container.header  = 'Add to Favorites'
	object_container.message = '{0} added to Favorites'.format(showTitle)
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
def remove_from_favorites(title, showTitle, traktSlug):
	if 'shows_favorites' in Dict and traktSlug in Dict['shows_favorites']:
		Dict['shows_favorites'].remove(traktSlug)
		Dict.Save()

	object_container = ObjectContainer(title2=title)
	object_container.header  = 'Remove from Favorites'
	object_container.message = '{0} removed from Favorites'.format(showTitle)
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', seasonIndex = int)
def ShowSeason(title, showTitle, traktSlug, seasonIndex):
	object_container = ObjectContainer(title2=title)

	json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + traktSlug + '/season/' + str(seasonIndex)
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'episodes' in json_data:
		for json_item in json_data['episodes']:
			episodeIndex = json_item['episode_index']
			episodeTitle = '{0}. {1}'.format(episodeIndex, json_item['title'])

			episodeObject = EpisodeObject()
			episodeObject.art     = json_item['art']
			episodeObject.summary = json_item['overview']
			episodeObject.thumb   = json_item['thumb']
			episodeObject.title   = episodeTitle

			episodeObject.rating_key = Callback(
				ShowEpisode,
				episodeIndex = episodeIndex,
				episodeTitle = episodeTitle,
				seasonIndex = seasonIndex,
				showTitle = showTitle,
				traktSlug = traktSlug
			)

			episodeObject.key = Callback(
				ShowEpisode,
				episodeIndex = episodeIndex,
				episodeTitle = episodeTitle,
				seasonIndex = seasonIndex,
				showTitle = showTitle,
				traktSlug = traktSlug
			)

			object_container.add(episodeObject)

	return object_container

def getBestMagnet(magnets):
	seedsAndPeers = 0
	indexOfBest = 0

	for index, curMagnet in enumerate(magnets):
		curSeeds = curMagnet['seeds']
		curSeedsAndPeers = curSeeds + curMagnet['peers']

		if (curSeeds > 0) and (curSeedsAndPeers > seedsAndPeers):
			seedsAndPeers = curSeedsAndPeers
			indexOfBest = index

	Log.Info('Best magnet was at position {0}'.format(indexOfBest))

	return magnets[indexOfBest]['link']

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', seasonIndex = int, episodeIndex = int)
def ShowEpisode(episodeIndex, episodeTitle, seasonIndex, showTitle, traktSlug, includeRelated = False, includeRelatedCount = 0):
	try:
		magnet = TorrentMediaSearcher().request_tv_magnet(provider='eztv', show=showTitle, season=seasonIndex, episode=episodeIndex, quality='hd')

		# magnet = TorrentMediaSearcher().request_tv_magnet(provider='torrentproject', show=showTitle, season=seasonIndex, episode=episodeIndex, quality='hd')
	except QualityNotFound:
		magnet = TorrentMediaSearcher().request_tv_magnet(provider='scrapyard', show=showTitle, season=seasonIndex, episode=episodeIndex, quality='hd')

	return CreatePlayableObject(
		art = None,
		include_container = True,
		thumb = None,
		magnet = magnet,
		title = episodeTitle
	)

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
	object_container = ObjectContainer(title2='Empty')
	return object_container

def getMagnetMediaContainer(fileJSON):
	# Default container
	container = 'flv'

	fileName = fileJSON['name']

	def matchPatterns(string, patterns):
		for pattern in patterns:
			if pattern.lower() in string.lower():
				return True

	if matchPatterns(fileName, ['avi']):
		container = 'avi'
	elif matchPatterns(fileName, ['flv']):
		container = 'flv'
	elif matchPatterns(fileName, ['mkv']):
		container = 'mkv'
	elif matchPatterns(fileName, ['mov']):
		container = 'mov'
	elif matchPatterns(fileName, ['mp4']):
		container = 'mp4'

	return container

@route(SharedCodeService.common.PREFIX + '/CreatePlayableObject', include_container = bool)
@indirect
def CreatePlayableObject(title, thumb, art, magnet, include_container = False):
	peerflixFiles = []

	# try:
	# 	peerflixJSON = JSON.ObjectFromURL(streamURL + '.json', cacheTime=0, sleep = 3)
	# 	peerflixFiles = peerflixJSON['files']
	# except:
	# 	Log.Exception('Failed get get Peerflix JSON')
	# 	raise Ex.MediaNotAvailable

	# if (len(peerflixFiles) is 0):
	# 	raise Ex.MediaNotAvailable

	bitrate = 2500
	codec = 'aac'
	# container = getMagnetMediaContainer(peerflixFiles[0])
	items = []

	# Log.Info('Detected container {0}'.format(container))

	obj = VideoClipObject(
		art = art,
		title = title,
		items = [
			MediaObject(
				audio_channels = 2,
				audio_codec = codec,
				bitrate = bitrate,
				# container = container,
				optimized_for_streaming = False,
				parts = [
					PartObject(
						key = HTTPLiveStreamURL(
							Callback(
								PlayHLS,
								magnet = magnet
							)
						),
						streams = [
							AudioStreamObject(
								channels = 2,
								codec = codec
							)
						]
					)
				]
			)
		],
		key =
			Callback(
				CreatePlayableObject,
				title = title,
				thumb = thumb,
				art = art,
				magnet = magnet,
				include_container = True
			),
		rating_key = title,
		thumb = thumb
	)

	if include_container:
		return ObjectContainer(objects = [obj])
	else:
		return obj

@route(SharedCodeService.common.PREFIX + '/PlayHLS.m3u8')
@indirect
def PlayHLS(magnet, streamURL = '', startedAt = -1):
	startedAt = int(startedAt)

	streamURL = SharedCodeService.peerflix.start(magnet)

	try:
		Log.Debug('Checking if server {0} is ready...'.format(streamURL))

		# Play file on index 0
		headers = HTTP.Request(streamURL + '0', cacheTime=0, sleep = 2).headers

		Log.Debug(headers)
	except:
		Log.Debug('Video is not ready yet, redirecting...')

		time.sleep(2)

		if startedAt is -1:
			startedAt = int(time.time())
		elif (int(time.time()) - startedAt) > 120:
			Log.Debug('Taking too long.. Killing peerflix...')

			SharedCodeService.peerflix.stop(magnet)

			raise Ex.MediaNotAvailable
		else:
			Log.Debug(int(time.time()) - startedAt)

		return IndirectResponse(
			VideoClipObject,
			key = Callback(
				PlayHLS,
				magnet = magnet,
				startedAt = startedAt
			)
		)

	Log.Info('Video Ready! Playing it now.. (' + streamURL + ')')

	return IndirectResponse(
		VideoClipObject,
		key = HTTPLiveStreamURL(url = streamURL)
	)