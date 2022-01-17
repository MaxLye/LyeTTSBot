import json
import spotipy
from pydash import py_
from spotipy.oauth2 import SpotifyOAuth

# SCOPE = "user-modify-playback-state user-library-read user-read-currently-playing app-remote-control"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private user-read-email user-follow-modify user-follow-read user-library-modify user-library-read streaming app-remote-control user-read-playback-position user-top-read user-read-recently-played playlist-modify-private playlist-read-collaborative playlist-read-private playlist-modify-public"
USERNAME = '1291026324'
CLIENT_ID = 'dc6d6e7a310444f3bf9adcf2449b515b'
CLIENT_SECRET = 'e3aa3ab58a5045038295b1d98db9af92'
REDIRECT_URI = 'https://md.ahlye.com/'

sp = None

def init():
    refresh_spotify()
    sp.user_playlists('spotify')

def refresh_spotify():
    global sp
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE,
        username=USERNAME,
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET))

def addSong(url):
    try:
        sp.add_to_queue(url)
    except:
        refresh_spotify()

def getCurrentPlayingSong():
    result = sp.current_user_playing_track()
    return f"{py_.get(result, 'item.name', 'Error')} by {py_.get(result, 'item.artists.0.name', 'Unknown')}"