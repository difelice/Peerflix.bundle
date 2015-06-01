import re

from torrent_base import BaseAPI, QualityNotFound, ShowNotFound, EpisodeNotFound

try:
	all
except NameError:
	def all(iterable):
		for i in iterable:
			if not i:
				return False
		return True

class EZTVAPI(BaseAPI):

	URL = "http://eztv.it"

	def query_tvshow(self, show, season, episode, quality):
		show_id = self.get_show_id(show=show)

		return self.get_magnet_tv(show_id=show_id, show=show, season=season, episode=episode, quality=quality)

	def query_movie(self, *args):
		raise RuntimeError('Movies are not supported in the EZTV provider')

	def get_show_id(self, show):
		# all strings are in lowercase
		show = show.lower()
		terms = show.split(' ')

		try:
			html = HTML.ElementFromURL(self.URL)
		except requests.ConnectionError:
			raise LookupError('Could not reach host')

		tvShows = html.iterfind('.//select[@name="SearchString"]//option')

		for tvShow in tvShows:
			tvShowTitle = tvShow.text.lower()
			if all(x in tvShowTitle for x in terms):
				show_id = tvShow.get('value')
				break
		else:
			raise ShowNotFound()

		return show_id


	def get_magnet_tv(self, show_id, show, season, episode, quality):
		show_url = self.URL + '/shows/' + show_id + '/'

		try:
			html = HTML.ElementFromURL(show_url)
		except:
			raise LookupError('Could not reach host')

		episodes = html.xpath('.//a[contains(@class,"epinfo")]')

		parent_map = dict((c, p) for p in html for c in p)

		wanted_episode = None

		for e in episodes:
			if re.search(show, e.text, re.IGNORECASE) is None: continue

			for s in self.TV_INDEX_SPECIFIERS:
				regex_result = re.search(s, e.text, re.IGNORECASE)

				if  regex_result is not None:
					curSeason = int(regex_result.group(1))
					curEpisode = int(regex_result.group(2))

					if curSeason == season and curEpisode == episode:
						wanted_episode = e
						break

			if wanted_episode is not None:
				break

		if wanted_episode is None:
			raise QualityNotFound('Could not find anything matching the quality: ' + quality)

		magnetLink = wanted_episode.find('..').find('..').xpath('.//a[contains(@class, "magnet")]')

		return magnetLink[0].get('href')


