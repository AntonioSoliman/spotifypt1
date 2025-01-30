from flask import Flask, redirect, request, url_for, render_template, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "d74cb805ae4f4e9c87c5d361d8adade3"
SPOTIFY_CLIENT_SECRET = "3a61d65da5914d1789080bccbc68e0fd"
SPOTIFY_REDIRECT_URI = "https://turbo-guide-wr7jqjp4vp6xh9pqq-5000.app.github.dev/callback"

app = Flask(__name__)
app.secret_key = 'chiave_per_session'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-private playlist-read-private",
    show_dialog=True
)

@app.route('/')
def home():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    playlists = sp.current_user_playlists()['items']
    
    playlist_id = request.args.get('playlist_id')
    tracks = []
    if playlist_id:
        tracks_data = sp.playlist_items(playlist_id)['items']
        tracks = [
            {
                'name': track['track']['name'],
                'artist': track['track']['artists'][0]['name'],
                'album': track['track']['album']['name'],
                'cover': track['track']['album']['images'][0]['url'] if track['track']['album']['images'] else None
            } 
            for track in tracks_data
        ]
    
    return render_template('home.html', user_info=user_info, playlists=playlists, tracks=tracks)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
