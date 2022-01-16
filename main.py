from re import M
from bs4 import BeautifulSoup
from os import getenv
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#Constants
URL = 'https://www.billboard.com/charts/hot-100/'
SCOPE = 'user-library-modify playlist-modify-private playlist-modify-public'
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')


def get_playlist_Id(user_id, playlist_name, sp):
    playlist_id = ''
    playlists = sp.user_playlists(user_id)
    
    # iterate through playlists I follow
    for playlist in playlists['items']:  
        # filter for newly created playlist
        if playlist['name'] == playlist_name:  
            playlist_id = playlist['id']
            return playlist_id
    
    return  sp.user_playlist_create(user=user_id, name=playlist_name)['id']

def get_song_titles(date):
    # Getting page data to scrape
    response = requests.get(URL + date)
    website_data = response.text
    soup = BeautifulSoup(website_data, 'html.parser')

    titles = [titles.getText().strip() for titles in soup.find_all(name='h3', id='title-of-a-story') if titles.parent.name == 'li']

    return titles

def create_playlist(titles, date):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='http://localhost/callback/'))

    user_id = sp.current_user()['id']
    song_uris = []
    year = date.split('-')[0]
    num_titles_added = 0

    for song in titles:
        result = sp.search(q=f'track:{song} year:{year}', type='track')
        try:
            uri = result['tracks']['items'][0]['uri']
            song_uris.append(uri)
            num_titles_added += 1
        # When the song does not exist on spotify
        except IndexError:
            pass 

    playlist_id = get_playlist_Id(user_id, f'{date} Billboard 100', sp)

    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=song_uris)
    print(f'Successfully found and added {num_titles_added} songs to the playlist {date} Billboard 100')


def main() :
    date = input('Which year do you want to travel to? Type the date in this format YYYY-MM-DD:')
    titles = get_song_titles(date)
    create_playlist(titles, date)

if __name__ == '__main__':
    main()
