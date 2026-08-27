"""Merge videos and apply quality filters"""
import subprocess
from pathlib import Path

class VideoProcessor:
    def __init__(self, location_name, country):
        self.location = location_name
        self.country = country
        self.videos = []
    
    def add_videos(self, video_paths):
        """Add videos to merge"""
        self.videos = video_paths
        print(f"📹 Added {len(video_paths)} videos")
    
    def create_concat_file(self):
        """Create FFmpeg concat file"""
        concat_file = Path("/tmp/concat_list.txt")
        with open(concat_file, 'w') as f:
            for video in self.videos:
                f.write(f"file '{video}'\n")
        return concat_file
    
    def merge_videos(self, output_path):
        """Merge all videos"""
        print(f"\n🎬 Merging {len(self.videos)} videos...")
        
        concat_file = self.create_concat_file()
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",  # No re-encoding for speed
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Merged successfully: {output_path}")
            return True
        else:
            print(f"❌ Merge failed")
            return False
    
    def apply_filters(self, input_video, output_video):
        """Apply quality enhancement filters"""
        print(f"\n✨ Applying quality filters...")
        
        filter_chain = (
            "eq=contrast=1.1:saturation=1.15,"  # Boost contrast & saturation
            "unsharp=5:5:0.8,"  # Sharpen
            "nlmeans=h=1.5,"  # Denoise
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", filter_chain,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Filters applied: {output_video}")
            return True
        else:
            print(f"⚠️  Filter application issue")
            return False
    
    def add_text_overlay(self, input_video, output_video):
        """Add location text overlay"""
        print(f"\n📝 Adding text overlay...")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", f"""
            drawtext=text='{self.location}':fontsize=70:fontcolor=white:x=(w-text_w)/2:y=h/3:borderw=3:bordercolor=black,
            drawtext=text='{self.country}':fontsize=50:fontcolor=gold:x=(w-text_w)/2:y=h/3+120:borderw=2:bordercolor=black
            """,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Text overlay added: {output_video}")
            return True
        else:
            print(f"⚠️  Text overlay issue")
            return False
    
    def process_complete(self, output_path):
        """Complete processing pipeline"""
        print(f"\n{'='*60}")
        print(f"  Processing: {self.location}, {self.country}")
        print(f"{'='*60}\n")
        
        if not self.videos:
            print("❌ No videos to process")
            return False
        
        # Step 1: Merge
        merged = "/tmp/merged.mp4"
        if not self.merge_videos(merged):
            return False
        
        # Step 2: Apply filters
        filtered = "/tmp/filtered.mp4"
        if not self.apply_filters(merged, filtered):
            return False
        
        # Step 3: Add text
        if not self.add_text_overlay(filtered, output_path):
            return False
        
        print(f"\n✅ Final video ready: {output_path}")
        return True

if __name__ == "__main__":
    print("Video processor initialized")
