# Set your Spotify app credentials (client ID and client secret)
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import auth.auth

client_id = auth.auth.SPOTIFY_ID
client_secret = auth.auth.SPOTIFY_SECRET
redirect_uri = 'http://localhost:3000/callback'  # my demo use http://localhost:3000/callback

# scopes for Remote control playback, Get Available Devices, Pause playback
SCOPEs = ['app-remote-control', 'user-read-playback-state', 'user-modify-playback-state']


def pause_spotify():
  devices = sp.devices()
  for device in devices['devices']:
    if device['is_active']:
      sp.pause_playback(device['id'])


def resume_spotify():
  devices = sp.devices()
  for device in devices['devices']:
    if device['is_active']:
      sp.start_playback(device['id'])


if __name__ == '__main__':
  auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=SCOPEs)
  sp = spotipy.Spotify(auth_manager=auth_manager)
  resume_spotify()
