# __author__ = "Christiaan Maks (christiaanmaks@mylittlesky.net)"
# __version__ = "1.0"
# __copyright__ = "Copyright (c) 2014 Christiaan Maks"
# __license__ = "GPLv2"

from torrent_eztv import EZTVAPI
from torrent_scrapyard import ScrapYardAPI
from torrent_torrentproject import TorrentProjectAPI

class TorrentMediaSearcher():

	PROVIDERS = {
		'eztv': EZTVAPI,
		'scrapyard' : ScrapYardAPI,
		'torrentproject' : TorrentProjectAPI
	}

	@staticmethod
	def request_movie_magnet(provider, movie, year=None, quality=None):
		if provider in TorrentMediaSearcher.PROVIDERS:
			provider_class = TorrentMediaSearcher.PROVIDERS[provider]
		else:
			raise ValueError('No valid search provider selected, choose from: ' + str(TorrentMediaSearcher.PROVIDERS.keys()))

		if year is not None and 1000 > year > 9999:
			raise ValueError('Invalid year input, please use the yyyy format or do not use the year parameter (results will be less accurate)')

		search = provider_class()
		return search.create_movie_request(movie=movie, year=year, quality=quality)

	@staticmethod
	def request_tv_magnet(provider, show, season, episode, quality=None):
		if provider in TorrentMediaSearcher.PROVIDERS:
			provider_class = TorrentMediaSearcher.PROVIDERS[provider]
		else:
			raise ValueError('No valid search provider selected, choose from: ' + str(TorrentMediaSearcher.PROVIDERS.keys()))

		search = provider_class()
		return search.create_tvshow_request(show=show, season=season, episode=episode, quality=quality)