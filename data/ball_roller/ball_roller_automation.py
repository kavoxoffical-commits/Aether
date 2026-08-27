"""Ball Roller - Daily Automation System"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

class BallRollerAutomation:
    def __init__(self):
        self.blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"  # macOS
        # For Linux: /usr/bin/blender
        # For Windows: "C:\\Program Files\\Blender Foundation\\Blender 3.x\\blender.exe"
        
        self.project_dir = Path("./ball_roller_project")
        self.output_dir = self.project_dir / "output"
        self.script_dir = self.project_dir / "scripts"
    
    def generate_scene(self):
        """Step 1: Generate random scene"""
        print("🎬 Step 1: Generating random scene...")
        
        config = {
            "ball_color": self._random_neon_color(),
            "track_complexity": self._random_complexity(),
            "lighting_style": self._random_lighting(),
            "camera_speed": self._random_camera_speed(),
            "timestamp": datetime.now().isoformat()
        }
        
        config_file = self.project_dir / f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        print(f"   ✅ Scene config: {config}")
        return config
    
    def render_in_blender(self, scene_config):
        """Step 2: Render in Blender"""
        print("\n🎥 Step 2: Rendering in Blender...")
        
        # Run Blender with Python script
        cmd = [
            self.blender_path,
            "--background",
            "--python", str(self.script_dir / "blender_script.py"),
            "--",
            json.dumps(scene_config)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print("   ✅ Blender rendering complete")
                return True
            else:
                print(f"   ❌ Blender error: {result.stderr}")
                return False
        except FileNotFoundError:
            print("   ⚠️  Blender not found. Please install Blender.")
            return False
    
    def mix_audio(self, video_path):
        """Step 3: Mix audio with video"""
        print("\n🔊 Step 3: Adding sound effects...")
        
        audio_dir = self.project_dir / "audio"
        output_video = self.output_dir / f"ball_roller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        # FFmpeg command to add audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_dir / "rolling.wav"),
            "-i", str(audio_dir / "collision.wav"),
            "-filter_complex",
            "[1:a]atrim=0:3[a1];[2:a]atrim=0:0.4[a2];[a1][a2]concat=n=2:v=0:a=1[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            str(output_video)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            if result.returncode == 0:
                print(f"   ✅ Video with audio: {output_video}")
                return output_video
            else:
                print(f"   ❌ FFmpeg error")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def upload_to_youtube(self, video_path):
        """Step 4: Upload to YouTube Shorts"""
        print("\n📤 Step 4: Uploading to YouTube...")
        
        title = "Ball Roller - Physics Simulation"
        description = """3D Ball Rolling Physics Simulation
        
Pure physics-based animation with realistic collisions and camera tracking.

#Physics #3D #Animation #Blender #Shorts"""
        
        tags = ["physics", "3d", "animation", "blender", "shorts", "viral"]
        
        print(f"   Title: {title}")
        print(f"   Ready for YouTube upload")
        print(f"   Video: {video_path}")
        
        # YouTube API integration would go here
        return True
    
    def run_daily(self):
        """Run complete daily pipeline"""
        print("\n" + "="*60)
        print("🎬 BALL ROLLER - DAILY GENERATION")
        print("="*60 + "\n")
        
        # Step 1
        scene_config = self.generate_scene()
        
        # Step 2
        if not self.render_in_blender(scene_config):
            print("❌ Rendering failed")
            return False
        
        # Find rendered video
        render_dir = self.output_dir / "renders"
        videos = list(render_dir.glob("*.mp4")) if render_dir.exists() else []
        
        if not videos:
            print("❌ No rendered video found")
            return False
        
        video_path = videos[-1]  # Latest
        
        # Step 3
        final_video = self.mix_audio(video_path)
        
        if not final_video:
            print("❌ Audio mixing failed")
            return False
        
        # Step 4
        self.upload_to_youtube(final_video)
        
        print("\n" + "="*60)
        print("✅ DAILY GENERATION COMPLETE!")
        print("="*60 + "\n")
        return True
    
    def _random_neon_color(self):
        colors = ["#FF3366", "#00FFFF", "#9933FF", "#FFCC00", "#FF00FF"]
        import random
        return random.choice(colors)
    
    def _random_complexity(self):
        import random
        return random.randint(5, 12)  # Number of track pieces
    
    def _random_lighting(self):
        styles = ["neon_blue", "neon_pink", "neon_purple", "cyberpunk"]
        import random
        return random.choice(styles)
    
    def _random_camera_speed(self):
        import random
        return round(random.uniform(1.0, 2.5), 1)

if __name__ == "__main__":
    automation = BallRollerAutomation()
    
    # Test run
    print("🚀 Running daily generation...\n")
    automation.run_daily()
