################################################################################
import shows

################################################################################
TITLE  = 'Peerflix'
ART    = 'art-default.jpg'
ICON   = 'popcorn.png'

################################################################################
def Start():
	DirectoryObject.thumb  = R(ICON)

	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE

	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)

################################################################################

@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():

	Log.Info(SharedCodeService.common.TMDB_API_KEY)

	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(shows.menu), title='TV Shows', summary="Browse TV shows."))
	object_container.add(PrefsObject(title='Preferences', summary='Preferences for Peerflix channel.'))

	return object_container