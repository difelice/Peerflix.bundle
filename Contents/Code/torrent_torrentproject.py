import re

from torrent_base import BaseAPI, ShowNotFound, EpisodeNotFound, QualityNotFound, MovieNotFound

class TorrentProjectAPI(BaseAPI):

    URL = 'http://torrentproject.com/'

    LANGUAGES = [                  # Common language keywords found in torrents, so we can filter them. Sorry, only English supported for now.
        'GERMAN',
        'FRENCH',
        'DUTCH',
        'NL',
        'ITALIAN',
        'SPANISH',
        'LATINO',
        'RUS',
        'HEBREW',
    ]

    UNWANTED_MOVIE_KEYWORDS = [          # Torrents with these keywords found will be ignored (unless the keyword is in the movie title)
        'TRILOGY',
        'DUOLOGY',
    ]

    UNWANTED_TV_KEYWORDS = [
        'SEASON',
        'COMPLETE',
    ]

    def query_tvshow(self, show, season, episode, quality):
        query_string = show.replace(' ', '+')
        specifier = 's%02d' % season + 'e%02d' % episode

        query = query_string + '+' + specifier

        # Before searching with specified quality, do a search without, to see if the show exists
        if self.get_json(query=query_string, quality=quality)['total_found'] == '0':
            raise ShowNotFound('No results were found for show: ' + show)

        result = self.get_magnet_tv(query=query, quality=quality)

        if len(result) == 0:   # No quality of any kind was found, most likely the episode does not exist.          # TODO never used?
            raise EpisodeNotFound('Could not find episode ' + str(episode) + ' of season ' + str(season) + ' of ' + show)

        return result

    def query_movie(self, movie, year, quality):
        query = movie.replace(' ', '+')
        if year is not None: query += '+' + str(year)

        # Before searching with specified quality, do a search without, to see if the movie exists
        if self.get_json(query=query, quality=quality)['total_found'] == '0':
            raise MovieNotFound('No results found for movie: ' + movie)

        search_terms = self.wanted_movie.split(' ')            # Get the words in the movie
        for s in search_terms:
            for lan in self.LANGUAGES:                         # This removes languages that are in the search terms. Otherwise movies with search terms equal to a langauge would always be skipped
                if re.match(s, lan, re.IGNORECASE):
                    self.LANGUAGES.remove(lan)

        result = self.get_magnet_movie(query=query, quality=quality)

        if len(result) == 0:   # No quality of any kind was found, most likely the movie  does not exist.
            raise MovieNotFound('No results found for movie: ' + self.wanted_movie)

        return result

    def get_json(self, query, quality):
        # Allow None so a search can be performed without any quality string
        if quality is not None:
            query += '+' + quality

        json = {}

        try:
            json = JSON.ObjectFromURL(self.URL + '?s=' + query + '&out=json', cacheTime=CACHE_1HOUR)
        except Exception as e:
            raise e

        return json

    def get_magnet(self, torrent_hash):
        torrent_url = self.URL + torrent_hash

        try:
            html = HTML.ElementFromURL(torrent_url)
        except:
            raise LookupError('Could not reach host')

        links = html.xpath('.//a[contains(text(),"Magnet Link")]')

        if len(links) is 0:
            raise ValueError('Could not find the magnet link, did the website change?')

        return links[0].get('href')

    def get_magnet_tv(self, query, quality):
        """ Returns the URL to a torrent/magnet link of specified quality or raise error if not found """

        json = self.get_json(query, quality)

        best = None
        num_seeds = 0
        num_leechs = 0

        for n in json:
            entry = json[n]

            if n == 'total_found': continue

            title = entry['title']

            # Perform some checks
            if entry['category'] != 'tv': continue
            if self.contains(title=title, container=self.UNWANTED_TV_KEYWORDS): continue

            for s in self.TV_INDEX_SPECIFIERS:
                regex_result = re.search(s, entry['title'], re.IGNORECASE)
                if regex_result is not None:
                    if int(regex_result.group(1)) == self.wanted_season and int(regex_result.group(2)) == self.wanted_episode:
                        # Take link with most seeds, if the same amount, take the one with most leechs
                        if entry['seeds'] > num_seeds or (entry['seeds'] == num_seeds and entry['leechs'] > num_leechs):
                            best = entry
                            num_seeds = entry['seeds']
                            num_leechs = entry['leechs']

        if best is None:
            raise QualityNotFound()

        return self.get_magnet(torrent_hash=best['torrent_hash'])

    def get_magnet_movie(self, query, quality):
        """ Returns the URL to a torrent/magnet link of specified quality or raise error if not found """

        json = self.get_json(query=query, quality=quality)

        movie = self.wanted_movie
        terms_removed = re.findall(r'-\w+', self.wanted_movie, re.IGNORECASE) # Terms such -foo should be ignored when searching the titles
        for t in terms_removed: movie = movie.replace(t, '')

        movie = movie.strip()   # Remove start and trailing whitespaces
        movie_regex = movie.replace(' ', '\D?')      # e.g. Movie?Name?5

        if quality is None: quality = ''

        best = None
        num_seeds = 0
        num_leechs = 0

        for n in json:
            entry = json[n]

            if n == 'total_found': continue                                                                     # TorrentProject adds a total_found that we must ignore

            title = entry['title']

            # Perform some checks
            if self.contains(title=title, container=self.LANGUAGES): continue                                 # Check if movie title contains language terms that we dont want
            if self.contains(title=title, container=self.TV_INDEX_SPECIFIERS): continue                       # Check if the torrent is really a movie and not a tv show
            if re.search(quality, title, re.IGNORECASE) is None: continue                                       # Check that the quality string is in the title
            if self.contains_unwanted_quality_specifier(title=title, wanted_quality=quality): continue         # Skip files that contains wrong quality identifiers
            if self.contains(title=title, container=self.UNWANTED_MOVIE_KEYWORDS): continue                   # Check the title for unwanted keywords
            if re.search(movie_regex, title, re.IGNORECASE) is None: continue                                   # The movie name was not found in the title, wrong search result so ignore it

            if entry['seeds'] > num_seeds or (entry['seeds'] == num_seeds and entry['leechs'] > num_leechs):  # Take link with most seeds, if the same amount, take the one with most leechs
                best = entry
                num_seeds = entry['seeds']
                num_leechs = entry['leechs']

        if best is None:
            raise QualityNotFound('Could not find anything matching the quality: ' + quality)

        return self.get_magnet(torrent_hash=best['torrent_hash'])










