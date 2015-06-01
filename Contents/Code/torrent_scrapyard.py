import re

from torrent_base import BaseAPI, ShowNotFound, EpisodeNotFound, QualityNotFound, MovieNotFound

class ScrapYardAPI(BaseAPI):

	URL = Prefs['SCRAPYARD_URL']

	def query_tvshow(self, show, season, episode, quality):
		show = re.sub(' ', '-', show.rstrip()).lower()

		try:
			jsonURL  = self.URL + '/api/show/' + show + '/season/' + str(season) + '/episode/' + str(episode)
			episodeJSON = JSON.ObjectFromURL(jsonURL, cacheTime=CACHE_1HOUR)

			return getBestMagnet(episodeJSON['magnets'])
		except:
			raise EpisodeNotFound('Could not find episode ' + str(episode) + ' of season ' + str(season) + ' of ' + show)

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