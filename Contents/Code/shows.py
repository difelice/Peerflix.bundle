import re

################################################################################

SUBPREFIX = 'shows'
RE_MAGNET = re.compile('\?magnet=(.+)$')

################################################################################

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
			show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
			object_container.add(show_object)

	if (page_index + 1) <= 10:
		object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
def favorites_menu(title):
	trakt_slugs = Dict['shows_favorites'] if 'shows_favorites' in Dict else []

	object_container = ObjectContainer(title2=title)

	json_url = Prefs['SCRAPYARD_URL'] + '/api/shows/favorites?'
	json_post = { 'shows_favorites': JSON.StringFromObject(trakt_slugs) }
	json_data = JSON.ObjectFromURL(json_url, values=json_post, cacheTime=CACHE_1HOUR)

	if json_data and 'shows' in json_data:
		for json_item in json_data['shows']:
			show_object = TVShowObject()
			SharedCodeService.common.fill_show_object(show_object, json_item)
			show_object.rating_key = json_item['trakt_slug']
			show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
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
			show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
			object_container.add(show_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def show_menu(title, trakt_slug):
	object_container = ObjectContainer(title2=title)

	if 'shows_favorites' in Dict and trakt_slug in Dict['shows_favorites']:
		object_container.add(DirectoryObject(key=Callback(remove_from_favorites, title='Remove from Favorites', show_title=title, trakt_slug=trakt_slug), title='Remove from Favorites', summary='Remove TV show from Favorites', thumb=R('favorites.png')))
	else:
		object_container.add(DirectoryObject(key=Callback(add_to_favorites, title='Add to Favorites', show_title=title, trakt_slug=trakt_slug), title='Add to Favorites', summary='Add TV show to Favorites', thumb=R('favorites.png')))

	json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'seasons' in json_data:
		for json_item in json_data['seasons']:
			season_object = SeasonObject()
			SharedCodeService.common.fill_season_object(season_object, json_item)
			season_object.rating_key    = '{0}-{1}'.format(trakt_slug, season_object.index)
			season_object.key           = Callback(season_menu, title=season_object.title, show_title=title, trakt_slug=trakt_slug, season_index=season_object.index)
			object_container.add(season_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
def add_to_favorites(title, show_title, trakt_slug):
	if 'shows_favorites' not in Dict:
		Dict['shows_favorites'] = []

	if trakt_slug not in Dict['shows_favorites']:
		Dict['shows_favorites'].append(trakt_slug)
		Dict.Save()

	object_container = ObjectContainer(title2=title)
	object_container.header  = 'Add to Favorites'
	object_container.message = '{0} added to Favorites'.format(show_title)
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
def remove_from_favorites(title, show_title, trakt_slug):
	if 'shows_favorites' in Dict and trakt_slug in Dict['shows_favorites']:
		Dict['shows_favorites'].remove(trakt_slug)
		Dict.Save()

	object_container = ObjectContainer(title2=title)
	object_container.header  = 'Remove from Favorites'
	object_container.message = '{0} removed from Favorites'.format(show_title)
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season_menu(title, show_title, trakt_slug, season_index):
	object_container = ObjectContainer(title2=title)

	json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug + '/season/' + str(season_index)
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	if json_data and 'episodes' in json_data:
		for json_item in json_data['episodes']:
			episodeTitle = '{0}. {1}'.format(json_item['episode_index'], json_item['title'])

			directory_object = DirectoryObject()
			directory_object.title   = episodeTitle
			directory_object.summary = json_item['overview']
			directory_object.thumb   = json_item['thumb']
			directory_object.art     = json_item['art']
			# directory_object.key     = Callback(episode_menu, episodeTitle=episodeTitle, trakt_slug=trakt_slug, season_index=season_index, episode_index=json_item['episode_index'])

			object_container.add(
				PeerflixEpisodeObject(
					episodeTitle,
					trakt_slug,
					season_index,
					json_item['episode_index']
				)
			)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def PeerflixEpisodeObject(episodeTitle, trakt_slug, season_index, episode_index):
	json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug + '/season/' + str(season_index) + '/episode/' + str(episode_index)
	json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

	magnetSeeds = 0
	magnetIndex = 0

	if json_data and 'magnets' in json_data:
		for index, json_item in enumerate(json_data['magnets']):
			if (json_item['seeds'] > magnetSeeds):
				magnetIndex = index
				magnetSeeds = json_item['seeds']

	try:
		json_item = json_data['magnets'][magnetIndex]

		magnet = json_item['link']

		return CreatePlayableObject(
			title = episodeTitle,
			thumb = None,
			art = None,
			type = 'hls',
			url = 'http://peerflix/play' + '?magnet=' + String.Quote(magnet)
		)
	except:
		Log.Debug('Could Parse Magnet {0} in {1}'.format(magnetIndex, json_url))

	return None

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
	object_container = ObjectContainer(title2='Empty')
	return object_container

@route(SharedCodeService.common.PREFIX + '/PlayHLS.m3u8')
@indirect
def PlayHLS(url, magnet):
	Log.Debug('host --> ' + SharedCodeService.utils.get_local_host())

	# url = 'http://' + SharedCodeService.utils.get_local_host() + ':8077/'
	url = 'http://localhost:8077/'

	SharedCodeService.peerflix.start(magnet)

	Log.Info('Playing ' + url)

	# Fix for Plex Web
	if Client.Product in ['Plex Web'] and Client.Platform not in ['Safari']:
		return Redirect(url)

	return IndirectResponse(
		VideoClipObject,
		key = HTTPLiveStreamURL(url = url)
	)

@route(SharedCodeService.common.PREFIX + '/CreatePlayableObject', include_container = bool)
def CreatePlayableObject(title, thumb, art, type, url, include_container = False):
	magnet = String.Unquote(RE_MAGNET.search(url).group(1))

	Log.Debug('This is the magnet ' + magnet)

	items = []

	codec = 'aac'
	container = 'flv'
	bitrate = 320
	key = HTTPLiveStreamURL(
		Callback(
			PlayHLS, url = url, magnet = magnet
		)
	)

	streams = [
		AudioStreamObject(
			codec = codec,
			channels = 2
		)
	]

	# if title_contains_pattern(magnet_data['title'], ['avi']):
	# 	container = 'avi'
	# elif title_contains_pattern(magnet_data['title'], ['flv']):
	# 	container = 'flv'
	# elif title_contains_pattern(magnet_data['title'], ['mkv']):
	# 	container = 'mkv'
	# elif title_contains_pattern(magnet_data['title'], ['mov']):
	# 	container = 'mov'
	# elif title_contains_pattern(magnet_data['title'], ['mp4']):
	# 	container = 'mp4'

	# if title_contains_pattern(magnet_data['title'], ['5.1', '5 1']):
	# 	media_object.audio_channels = 6

	# if title_contains_pattern(magnet_data['title'], ['aac']):
	# 	codec = 'aac'
	# elif title_contains_pattern(magnet_data['title'], ['ac3']):
	# 	codec = 'ac3'
	# elif title_contains_pattern(magnet_data['title'], ['dts']):
	# 	codec = 'dts'
	# elif title_contains_pattern(magnet_data['title'], ['mp3']):
	# 	codec = 'mp3'

	# if title_contains_pattern(magnet_data['title'], ['x264', 'h264']):
	# 	video_codec = 'h264'
	# elif title_contains_pattern(magnet_data['title'], ['divx']):
	# 	video_codec = 'divx'
	# elif title_contains_pattern(magnet_data['title'], ['xvid']):
	# 	video_codec = 'xvid'

	items.append(
		MediaObject(
			bitrate = bitrate,
			container = container,
			audio_codec = codec,
			audio_channels = 2,
			optimized_for_streaming = True,
			parts = [
				PartObject(
					key = key,
					streams = streams
				)
			]
		)
	)
	obj = VideoClipObject(  # NOTE! Need to set VCO here instead of TO because of PHT
		key =
			Callback(
				CreatePlayableObject,
				title = title,
				thumb = thumb,
				type = type,
				art = art,
				url = url,
				include_container = True
			),
		rating_key = title,
		title = title,
		items = items,
		thumb = thumb,
		art = art
	)

	if include_container:
		return ObjectContainer(objects = [obj])
	else:
		return obj