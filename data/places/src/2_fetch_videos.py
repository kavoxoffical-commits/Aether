"""Fetch videos from multiple sources"""
import requests
import json
from pathlib import Path
from datetime import datetime

class VideoFetcher:
    def __init__(self, location_name, search_queries):
        self.location = location_name
        self.queries = search_queries
        self.videos = []
    
    def fetch_pexels(self):
        """Fetch from Pexels"""
        # Note: Needs PEXELS_API_KEY
        print(f"🔍 Fetching from Pexels for: {self.location}")
        # Would require API key - for demo, simulated
        print("   ⏳ Searching...")
        # In production: use requests to Pexels API
        return []
    
    def fetch_mixkit(self):
        """Fetch from Mixkit (No auth required)"""
        print(f"🔍 Fetching from Mixkit for: {self.location}")
        all_videos = []
        
        for query in self.queries:
            try:
                # Mixkit API doesn't require auth
                url = f"https://api.mixkit.co/v1/videos?q={query}&limit=10"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        for video in data['data'][:5]:  # Take top 5
                            all_videos.append({
                                'source': 'mixkit',
                                'id': video['id'],
                                'url': video['attributes']['media_attributes']['preview_url'],
                                'duration': video['attributes']['duration'],
                                'quality': 'high'
                            })
                        print(f"   ✅ Found {len(video)} videos for '{query}'")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        
        return all_videos
    
    def fetch_pixabay(self):
        """Fetch from Pixabay"""
        print(f"🔍 Fetching from Pixabay for: {self.location}")
        # Pixabay requires API key
        print("   ⏳ Searching...")
        return []
    
    def fetch_coverr(self):
        """Fetch from Coverr"""
        print(f"🔍 Fetching from Coverr for: {self.location}")
        print("   ⏳ Searching...")
        return []
    
    def fetch_all(self):
        """Fetch from all sources"""
        print(f"\n🎬 Fetching videos for: {self.location}\n")
        
        self.videos.extend(self.fetch_mixkit())
        # self.videos.extend(self.fetch_pexels())
        # self.videos.extend(self.fetch_pixabay())
        # self.videos.extend(self.fetch_coverr())
        
        print(f"\n✅ Total videos found: {len(self.videos)}")
        return self.videos

if __name__ == "__main__":
    # Test
    fetcher = VideoFetcher("Sahara Desert", ["desert", "sand dunes"])
    fetcher.fetch_all()
