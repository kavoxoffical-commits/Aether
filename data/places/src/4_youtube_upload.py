"""Upload videos to YouTube Shorts"""
import os
import json
from pathlib import Path
from datetime import datetime

class YouTubeUploader:
    def __init__(self, channel_name="Places"):
        self.channel_name = channel_name
        self.credentials_file = Path.home() / ".places_youtube_creds.json"
    
    def get_youtube_client(self):
        """Initialize YouTube API client"""
        # This requires google-auth-oauthlib
        # For now, return setup instructions
        return None
    
    def upload_video(self, video_path, title, description, tags):
        """Upload video to YouTube Shorts"""
        
        print(f"\n{'='*60}")
        print(f"📹 Preparing YouTube Upload")
        print(f"{'='*60}\n")
        
        print(f"📌 Title: {title}")
        print(f"📝 Description: {description}")
        print(f"🏷️  Tags: {', '.join(tags)}")
        print(f"📂 Video: {video_path}")
        
        file_size = Path(video_path).stat().st_size / (1024*1024)
        print(f"💾 Size: {file_size:.1f} MB")
        
        # Prepare metadata
        metadata = {
            "title": title,
            "description": description,
            "tags": tags,
            "category_id": "22",  # People & Blogs
            "privacy_status": "public",
            "made_for_kids": False,
            "shorts": True
        }
        
        print(f"\n✅ Ready for upload!")
        print(f"\n📋 Metadata: {json.dumps(metadata, indent=2)}")
        
        return metadata
    
    def create_description(self, location_name, country):
        """Generate description"""
        description = f"""🌍 {location_name}, {country}

Beautiful location footage from around the world.

#Places #Travel #Shorts #{location_name.replace(' ', '')} #YouTube #{country.replace(' ', '')}"""
        
        return description
    
    def setup_instructions(self):
        """Print setup instructions"""
        print("\n" + "="*60)
        print("🔑 YOUTUBE API SETUP REQUIRED")
        print("="*60 + "\n")
        
        print("1️⃣  Create YouTube Channel:")
        print("   • Go to youtube.com")
        print("   • Create new channel: 'Places'")
        print("   • Enable Shorts (automatic)")
        
        print("\n2️⃣  Create OAuth Credentials:")
        print("   • Go to console.cloud.google.com")
        print("   • Create new project: 'Places'")
        print("   • Enable YouTube Data API v3")
        print("   • Create OAuth 2.0 credentials (Desktop app)")
        print("   • Download JSON file")
        
        print("\n3️⃣  Install Python libraries:")
        print("   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
        print("\n4️⃣  Save credentials:")
        print("   Save to: ~/.places_youtube_creds.json")
        
        print("\n" + "="*60)
        print("Then system will auto-upload daily! 🚀")
        print("="*60 + "\n")

if __name__ == "__main__":
    uploader = YouTubeUploader()
    uploader.setup_instructions()
