import re


class BaseAPI():

    URL = None

    QUALITY_SPECIFIERS = {
        'normal tv' : 'HDTV',
        'normal movie' : 'XVID',
        'hd' : '720p',
        'fullhd' : '1080p',
    }

    TV_INDEX_SPECIFIERS = [
        r'S(\d+)E(\d+)',            # Regex for S??E??
        r'(\D+\d{2})x(\d{2}\D+)',   # Regex for ??x?? and makes sure before and after are no numbers or it could match a resolution (1024x768)
    ]

    wanted_movie = None
    wanted_year = None
    wanted_show = None
    wanted_season = None
    wanted_episode = None
    wanted_quality = None


    def __init__(self):
        if self.URL is None:
            raise ValueError('URL has not been set')

    def create_tvshow_request(self, show, season, episode, quality):
        self.wanted_show = show
        self.wanted_season = season
        self.wanted_episode = episode

        # Check if quality string is correct
        if quality == 'normal': quality = self.QUALITY_SPECIFIERS['normal tv']
        elif quality not in self.QUALITY_SPECIFIERS.keys() and quality not in self.QUALITY_SPECIFIERS.values():
            raise ValueError('Invalid quality selected')

        for n in self.QUALITY_SPECIFIERS:  # Change quality types into the search string
            if quality == n: quality = self.QUALITY_SPECIFIERS[n]

        self.wanted_quality = quality
        return self.query_tvshow(show=self.wanted_show, season=self.wanted_season, episode=self.wanted_episode, quality=quality)

    def create_movie_request(self, movie, year, quality):
        self.wanted_movie = movie
        self.wanted_year = year

        # Check if quality string is correct
        if quality == 'normal': quality = self.QUALITY_SPECIFIERS['normal movie']
        elif quality not in self.QUALITY_SPECIFIERS.keys() and quality not in self.QUALITY_SPECIFIERS.values() and quality is not None:
            raise ValueError('Invalid quality selected')

        for n in self.QUALITY_SPECIFIERS:  # Change quality types into the search string
            if quality == n: quality = self.QUALITY_SPECIFIERS[n]

        self.wanted_quality = quality
        return self.query_movie(movie=movie, year=year, quality=quality)

    def query_tvshow(self, show, season, episode):
        raise NotImplementedError('This method must be implemented')

    def query_movie(self, movie):
        raise NotImplementedError('This method must be implemented')

    def contains(self, title, container):
        for c in container:
            if re.search(c, title, re.IGNORECASE) is not None:      # If found
                return True
        return False

    def contains_unwanted_quality_specifier(self, title, wanted_quality):
        for q in self.QUALITY_SPECIFIERS:
            if self.QUALITY_SPECIFIERS[q] == wanted_quality: continue         # Don't check the wanted quality
            if re.search(self.QUALITY_SPECIFIERS[q], title, re.IGNORECASE) is not None:    # If found
                return True
        return False

"""
    Exceptions
"""


class ProviderException(Exception):

    def __init__(self, message=None, errors=None):

        Exception.__init__(self, message)
        self.errors = errors


class ShowNotFound(ProviderException):
    """
        Raised when the specified show is not found
    """


class EpisodeNotFound(ProviderException):
    """
        Raised when the specified episode is not found
    """


class QualityNotFound(ProviderException):
    """
        Raised when the specified quality is not found
    """


class MovieNotFound(ProviderException):
    """
        Raised when the specified movie is not found
    """
