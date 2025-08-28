"""
Spotify Web API wrapper for enhanced functionality
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import logging
from typing import List, Dict, Optional
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

class SpotifyAPI:
    """Spotify Web API wrapper"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, redirect_uri: str = None, scope: str = None):
        """
        Initialize Spotify API client
        
        Args:
            client_id: Spotify app client ID
            client_secret: Spotify app client secret
            redirect_uri: Redirect URI for OAuth
            scope: Spotify API scopes (permissions)
        """
        self.client_id = client_id or SPOTIFY_CLIENT_ID
        self.client_secret = client_secret or SPOTIFY_CLIENT_SECRET
        self.redirect_uri = redirect_uri or SPOTIFY_REDIRECT_URI
        self.logger = logging.getLogger("SpotifyAPI")
        
        default_scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private user-library-read user-library-modify"
        self.scope = scope or default_scope
        
        self.spotify = None
        self.auth_manager = None
        
        if not self.client_id or not self.client_secret:
            self.logger.warning("Spotify API credentials not provided. Some features may be limited.")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Spotify client with OAuth"""
        try:

            self.auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_token_cache"
            )
            
            self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
            
            try:
                self.spotify.current_user()
                self.logger.info("Spotify API initialized with user authentication")
            except SpotifyException:

                self._initialize_client_credentials()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify OAuth: {e}")
            self._initialize_client_credentials()
    
    def _initialize_client_credentials(self):
        """Initialize Spotify client with client credentials (no user auth)"""
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
            self.logger.info("Spotify API initialized with client credentials (limited functionality)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify client credentials: {e}")
            self.spotify = None
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks on Spotify
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track information dictionaries
        """
        if not self.spotify:
            self.logger.warning("Spotify API not initialized")
            return []
        
        try:
            results = self.spotify.search(q=query, type='track', limit=limit)
            
            tracks = []
            for track in results['tracks']['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'uri': track['uri']
                }
                tracks.append(track_info)
            
            self.logger.info(f"Found {len(tracks)} tracks for query: {query}")
            return tracks
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API search error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected search error: {e}")
            return []
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for artists on Spotify
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of artist information dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.search(q=query, type='artist', limit=limit)
            
            artists = []
            for artist in results['artists']['items']:
                artist_info = {
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist['genres'],
                    'popularity': artist['popularity'],
                    'followers': artist['followers']['total'],
                    'external_url': artist['external_urls']['spotify'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else None,
                    'uri': artist['uri']
                }
                artists.append(artist_info)
            
            self.logger.info(f"Found {len(artists)} artists for query: {query}")
            return artists
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API artist search error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected artist search error: {e}")
            return []
    
    def search_playlists(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for playlists on Spotify
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of playlist information dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.search(q=query, type='playlist', limit=limit)
            
            playlists = []
            for playlist in results['playlists']['items']:
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist['description'],
                    'owner': playlist['owner']['display_name'],
                    'tracks_total': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'external_url': playlist['external_urls']['spotify'],
                    'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
                    'uri': playlist['uri']
                }
                playlists.append(playlist_info)
            
            self.logger.info(f"Found {len(playlists)} playlists for query: {query}")
            return playlists
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API playlist search error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected playlist search error: {e}")
            return []
    
    def get_current_playback(self) -> Optional[Dict]:
        """
        Get current playback information
        
        Returns:
            Current playback information or None
        """
        if not self.spotify:
            return None
        
        try:
            playback = self.spotify.current_playback()
            
            if not playback:
                return None
            
            current_track = playback.get('item')
            if not current_track:
                return None
            
            playback_info = {
                'is_playing': playback['is_playing'],
                'progress_ms': playback['progress_ms'],
                'volume_percent': playback['device']['volume_percent'],
                'device_name': playback['device']['name'],
                'device_type': playback['device']['type'],
                'shuffle_state': playback['shuffle_state'],
                'repeat_state': playback['repeat_state'],
                'track': {
                    'id': current_track['id'],
                    'name': current_track['name'],
                    'artist': ', '.join([artist['name'] for artist in current_track['artists']]),
                    'album': current_track['album']['name'],
                    'duration_ms': current_track['duration_ms'],
                    'external_url': current_track['external_urls']['spotify'],
                    'uri': current_track['uri']
                }
            }
            
            return playback_info
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API current playback error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected current playback error: {e}")
            return None
    
    def get_user_playlists(self, limit: int = 50) -> List[Dict]:
        """
        Get current user's playlists
        
        Args:
            limit: Maximum number of playlists
            
        Returns:
            List of user playlist dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            playlists = self.spotify.current_user_playlists(limit=limit)
            
            playlist_list = []
            for playlist in playlists['items']:
                playlist_info = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist['description'],
                    'tracks_total': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'collaborative': playlist['collaborative'],
                    'external_url': playlist['external_urls']['spotify'],
                    'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
                    'uri': playlist['uri']
                }
                playlist_list.append(playlist_info)
            
            self.logger.info(f"Retrieved {len(playlist_list)} user playlists")
            return playlist_list
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API user playlists error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected user playlists error: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100) -> List[Dict]:
        """
        Get tracks from a playlist
        
        Args:
            playlist_id: Spotify playlist ID
            limit: Maximum number of tracks
            
        Returns:
            List of track dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.playlist_tracks(playlist_id, limit=limit)
            
            tracks = []
            for item in results['items']:
                if item['track'] and item['track']['type'] == 'track':
                    track = item['track']
                    track_info = {
                        'id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'popularity': track['popularity'],
                        'added_at': item['added_at'],
                        'external_url': track['external_urls']['spotify'],
                        'uri': track['uri']
                    }
                    tracks.append(track_info)
            
            self.logger.info(f"Retrieved {len(tracks)} tracks from playlist")
            return tracks
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API playlist tracks error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected playlist tracks error: {e}")
            return []
    
    def get_user_saved_tracks(self, limit: int = 50) -> List[Dict]:
        """
        Get user's saved (liked) tracks
        
        Args:
            limit: Maximum number of tracks
            
        Returns:
            List of saved track dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.current_user_saved_tracks(limit=limit)
            
            tracks = []
            for item in results['items']:
                track = item['track']
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'added_at': item['added_at'],
                    'external_url': track['external_urls']['spotify'],
                    'uri': track['uri']
                }
                tracks.append(track_info)
            
            self.logger.info(f"Retrieved {len(tracks)} saved tracks")
            return tracks
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API saved tracks error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected saved tracks error: {e}")
            return []
    
    def get_recommendations(self, seed_tracks: List[str] = None, seed_artists: List[str] = None, 
                          seed_genres: List[str] = None, limit: int = 20) -> List[Dict]:
        """
        Get track recommendations
        
        Args:
            seed_tracks: List of track IDs for recommendations
            seed_artists: List of artist IDs for recommendations
            seed_genres: List of genres for recommendations
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended track dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            recommendations = self.spotify.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                limit=limit
            )
            
            tracks = []
            for track in recommendations['tracks']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'uri': track['uri']
                }
                tracks.append(track_info)
            
            self.logger.info(f"Retrieved {len(tracks)} recommendations")
            return tracks
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API recommendations error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected recommendations error: {e}")
            return []
    
    def get_top_tracks(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict]:
        """
        Get user's top tracks
        
        Args:
            time_range: 'short_term', 'medium_term', or 'long_term'
            limit: Maximum number of tracks
            
        Returns:
            List of top track dictionaries
        """
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.current_user_top_tracks(time_range=time_range, limit=limit)
            
            tracks = []
            for track in results['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'external_url': track['external_urls']['spotify'],
                    'uri': track['uri']
                }
                tracks.append(track_info)
            
            self.logger.info(f"Retrieved {len(tracks)} top tracks")
            return tracks
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API top tracks error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected top tracks error: {e}")
            return []
    
    def get_available_genres(self) -> List[str]:
        """
        Get available genre seeds for recommendations
        
        Returns:
            List of available genres
        """
        if not self.spotify:
            return []
        
        try:
            genres = self.spotify.recommendation_genre_seeds()
            return genres['genres']
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API genres error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected genres error: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = "", public: bool = True) -> Optional[str]:
        """
        Create a new playlist
        
        Args:
            name: Playlist name
            description: Playlist description
            public: Whether playlist is public
            
        Returns:
            Playlist ID if successful, None otherwise
        """
        if not self.spotify:
            return None
        
        try:
            user_id = self.spotify.current_user()['id']
            playlist = self.spotify.user_playlist_create(
                user=user_id,
                name=name,
                description=description,
                public=public
            )
            
            self.logger.info(f"Created playlist: {name}")
            return playlist['id']
            
        except SpotifyException as e:
            self.logger.error(f"Spotify API create playlist error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected create playlist error: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self.spotify or not self.auth_manager:
            return False
        
        try:
            self.spotify.current_user()
            return True
        except:
            return False