import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-modify-playback-state user-library-read user-read-currently-playing app-remote-control"
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

def getQueueList():
    playListStr = ""
    results = sp.featured_playlists()
    print(f"getQueueList results : {json.dumps(results)}")
    # for idx, item in enumerate(results['items']):
    #     track = item['track']
    #     playListStr += (idx, track['artists'][0]['name'], " – ", track['name'])

    return playListStr
