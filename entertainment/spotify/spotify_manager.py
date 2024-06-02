import spotipy
from spotipy import SpotifyClientCredentials

import config.auth

# Autenticación de Spotify
auth_manager = SpotifyClientCredentials(client_id=config.auth.SPOTIFY_ID, client_secret=config.auth.SPOTIFY_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


def play_pause():
    """Reproduce o pausa la reproducción en Spotify."""
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        sp.pause_playback()
        print("Reproducción pausada")
    else:
        sp.start_playback()
        print("Reproducción iniciada")


def next_track():
    """Pasa a la siguiente canción en Spotify."""
    sp.next_track()
    print("Siguiente canción")


def previous_track():
    """Vuelve a la canción anterior en Spotify."""
    sp.previous_track()
    print("Canción anterior")
