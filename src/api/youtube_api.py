"""
YouTube Data API wrapper for enhanced functionality
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import List, Dict, Optional
from config import YOUTUBE_API_KEY

class YouTubeAPI:
    """YouTube Data API wrapper"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize YouTube API client
        
        Args:
            api_key: YouTube Data API key
        """
        self.api_key = api_key or YOUTUBE_API_KEY
        self.logger = logging.getLogger("YouTubeAPI")
        
        if not self.api_key:
            self.logger.warning("No YouTube API key provided. Some features may be limited.")
            self.youtube = None
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                self.logger.info("YouTube API client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize YouTube API: {e}")
                self.youtube = None
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for videos on YouTube
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of video information dictionaries
        """
        if not self.youtube:
            self.logger.warning("YouTube API not initialized")
            return []
        
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video'
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                video_info = {
                    'id': search_result['id']['videoId'],
                    'title': search_result['snippet']['title'],
                    'description': search_result['snippet']['description'],
                    'channel': search_result['snippet']['channelTitle'],
                    'published_at': search_result['snippet']['publishedAt'],
                    'thumbnail': search_result['snippet']['thumbnails']['default']['url'],
                    'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
                }
                videos.append(video_info)
            
            self.logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API search error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected search error: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video details dictionary or None
        """
        if not self.youtube:
            return None
        
        try:
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            video = video_response['items'][0]
            
            video_details = {
                'id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'channel': video['snippet']['channelTitle'],
                'channel_id': video['snippet']['channelId'],
                'published_at': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'thumbnail': video['snippet']['thumbnails']['high']['url'],
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
            return video_details
            
        except HttpError as e:
            self.logger.error(f"YouTube API video details error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected video details error: {e}")
            return None
    
    def get_trending_videos(self, region_code: str = 'US', max_results: int = 10) -> List[Dict]:
        """
        Get trending videos
        
        Args:
            region_code: Country code (e.g., 'US', 'GB', 'ID')
            max_results: Maximum number of results
            
        Returns:
            List of trending video dictionaries
        """
        if not self.youtube:
            return []
        
        try:
            trending_response = self.youtube.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=max_results
            ).execute()
            
            videos = []
            for video in trending_response.get('items', []):
                video_info = {
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'thumbnail': video['snippet']['thumbnails']['high']['url'],
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                videos.append(video_info)
            
            self.logger.info(f"Retrieved {len(videos)} trending videos")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API trending error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected trending error: {e}")
            return []
    
    def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get videos from a specific channel
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of results
            
        Returns:
            List of channel video dictionaries
        """
        if not self.youtube:
            return []
        
        try:

            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
      
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response.get('items', []):
                video_info = {
                    'id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                }
                videos.append(video_info)
            
            self.logger.info(f"Retrieved {len(videos)} videos from channel")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API channel videos error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected channel videos error: {e}")
            return []
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get videos from a playlist
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of results
            
        Returns:
            List of playlist video dictionaries
        """
        if not self.youtube:
            return []
        
        try:
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response.get('items', []):
                if item['snippet']['resourceId']['kind'] == 'youtube#video':
                    video_info = {
                        'id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'position': item['snippet']['position'],
                        'thumbnail': item['snippet']['thumbnails']['default']['url'],
                        'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    }
                    videos.append(video_info)
            
            self.logger.info(f"Retrieved {len(videos)} videos from playlist")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API playlist error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected playlist error: {e}")
            return []
    
    def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for YouTube channels
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of channel information dictionaries
        """
        if not self.youtube:
            return []
        
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='channel'
            ).execute()
            
            channels = []
            for search_result in search_response.get('items', []):
                channel_info = {
                    'id': search_result['id']['channelId'],
                    'title': search_result['snippet']['title'],
                    'description': search_result['snippet']['description'],
                    'published_at': search_result['snippet']['publishedAt'],
                    'thumbnail': search_result['snippet']['thumbnails']['default']['url'],
                    'url': f"https://www.youtube.com/channel/{search_result['id']['channelId']}"
                }
                channels.append(channel_info)
            
            self.logger.info(f"Found {len(channels)} channels for query: {query}")
            return channels
            
        except HttpError as e:
            self.logger.error(f"YouTube API channel search error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected channel search error: {e}")
            return []
    
    def get_video_comments(self, video_id: str, max_results: int = 20) -> List[Dict]:
        """
        Get comments for a video
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments
            
        Returns:
            List of comment dictionaries
        """
        if not self.youtube:
            return []
        
        try:
            comments_response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            ).execute()
            
            comments = []
            for item in comments_response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_info = {
                    'author': comment['authorDisplayName'],
                    'author_channel_id': comment.get('authorChannelId', {}).get('value', ''),
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'like_count': comment.get('likeCount', 0),
                    'reply_count': item['snippet'].get('totalReplyCount', 0)
                }
                comments.append(comment_info)
            
            self.logger.info(f"Retrieved {len(comments)} comments for video")
            return comments
            
        except HttpError as e:
            self.logger.error(f"YouTube API comments error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected comments error: {e}")
            return []
    
    def get_api_quota_info(self) -> Dict:
        """
        Get information about API quota usage (approximate)
        
        Returns:
            Dictionary with quota information
        """
        quota_costs = {
            'search': 100,
            'videos': 1,
            'channels': 1,
            'playlistItems': 1,
            'commentThreads': 1
        }
        
        return {
            'quota_costs': quota_costs,
            'note': 'Daily quota limit is typically 10,000 units',
            'documentation': 'https://developers.google.com/youtube/v3/getting-started#quota'
        }