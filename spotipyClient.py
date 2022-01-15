import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
sp.user_playlists('spotify')

def addSong(url):
    sp.add_to_queue(url)