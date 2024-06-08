import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config.auth

# Configuración de autenticación de Spotify
client_id = config.auth.SPOTIFY_ID
client_secret = config.auth.SPOTIFY_SECRET
redirect_uri = 'http://localhost:3000/callback'  # URL de redirección
scopes = ['app-remote-control', 'user-read-playback-state', 'user-modify-playback-state']

# Autenticación de Spotify
auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)
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


if __name__ == '__main__':
    # Llama a las funciones de control de reproducción según sea necesario
    play_pause()
    # next_track()
    # previous_track()
