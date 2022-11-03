from typing import List
import dotenv
import os
import spotipy
import sys
import threading

class Spotify:
    def __init__(self) -> None:
        token = self.get_credentials()
        self.refresh_token(token)
    
    def refresh_token(self, token: str):
        self.spotify = spotipy.Spotify(auth=token)
        return self
    
    def get_credentials(self) -> str:
        dotenv.load_dotenv(".env")
        scopes = [
            "playlist-read-private",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-email"
        ]
        
        kwargs = {
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "redirect_uri": "http://localhost:8888/callback",
            "scope": " ".join(scopes),
            "username": os.getenv("USERNAME")
        }

        access_token = spotipy.prompt_for_user_token(**kwargs, cache_path=".spotify_cache")
        
        return access_token
    
    def get_playlists(self):
        return self.spotify.current_user_playlists()
    
    def search_query(self, q: str):
        query = self.spotify.search(q)
        return query
    
    def get_playlists_songs(self):
        playlists = self.get_playlists()
        PLAYLISTS = {}
        
        def _threaded(_playlist: dict):
            PLAYLISTS[_playlist['id']] = {}
            PLAYLISTS[_playlist['id']]['name'] = _playlist["name"]
            PLAYLISTS[_playlist['id']]['length'] = _playlist["tracks"]["total"]        
            PLAYLISTS[_playlist['id']]['snapshot'] = _playlist['snapshot_id']
            PLAYLISTS[_playlist['id']]['tracks'] = []
            
            songs = []
            offset = 0
            
            while True:
                for _track in self.spotify.playlist_items(_playlist["id"], limit=100, offset=offset)["items"]:
                    songs.append((_track["track"]["id"], _track["track"]["name"]))
                
                PLAYLISTS[_playlist['id']]['tracks'].extend(songs)
                sys.stdout.write("imported %s\n" % _playlist['name'])
                
                if not len(songs) == 100:
                    break
                
                songs.clear()
                offset += 100
        
        TASKS: List[threading.Thread] = []
        
        for _playlist in playlists["items"]:
            t = threading.Thread(
                target=_threaded, args=(_playlist,), daemon=True
            )
            TASKS.append(t)
        
        for i in TASKS:
            i.start()
        
        for i in TASKS:
            i.join()
        
        return PLAYLISTS
