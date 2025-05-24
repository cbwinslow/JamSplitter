from langchain.tools import BaseTool
from spotipy import Spotify, SpotifyOAuth
from typing import Dict, Any
import os

class SpotifyTool(BaseTool):
    name = "spotify"
    description = "Use this tool to get artist information and album details from Spotify"

    def __init__(self):
        super().__init__()
        self.spotify = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                scope='user-read-private user-read-email'
            )
        )

    def _run(self, query: str) -> Dict[str, Any]:
        """Search Spotify for artist information"""
        try:
            results = self.spotify.search(q=query, type='artist', limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                return {
                    'name': artist['name'],
                    'popularity': artist['popularity'],
                    'followers': artist['followers']['total'],
                    'genres': artist['genres'],
                    'images': artist['images'],
                    'external_urls': artist['external_urls']
                }
            return {'error': 'Artist not found'}
        except Exception as e:
            return {'error': str(e)}

    async def _arun(self, query: str) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(query)
