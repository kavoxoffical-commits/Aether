"""Blender Python Script - 3D Ball Rolling Track"""
import bpy
import random
import math
from mathutils import Vector

class BallRollerGenerator:
    def __init__(self):
        self.scene = bpy.context.scene
        self.fps = 30
        self.duration = 15  # 15 seconds
        self.total_frames = self.fps * self.duration
        
    def clear_scene(self):
        """Delete all objects"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        print("✅ Scene cleared")
    
    def create_ball(self):
        """Create 3D ball with neon color"""
        colors = [
            (1.0, 0.2, 0.2),    # Red neon
            (0.2, 1.0, 0.8),    # Cyan neon
            (0.5, 0.2, 1.0),    # Purple neon
            (1.0, 0.8, 0.2),    # Yellow neon
            (1.0, 0.2, 0.8),    # Pink neon
        ]
        
        color = random.choice(colors)
        
        # Create sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 10, 0))
        ball = bpy.context.active_object
        ball.name = "Ball"
        
        # Add material (neon)
        mat = bpy.data.materials.new("NeonMaterial")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission"].default_value = (*color, 0.8)
        bsdf.inputs["Emission Strength"].default_value = 2.0
        
        ball.data.materials.append(mat)
        
        # Add physics
        bpy.context.view_layer.objects.active = ball
        bpy.ops.rigidbody.object_add()
        ball.rigid_body.type = 'DYNAMIC'
        ball.rigid_body.mass = 1.0
        ball.rigid_body.friction = 0.5
        ball.rigid_body.restitution = 0.3
        
        print(f"✅ Ball created - Color: {color}")
        return ball
    
    def create_random_track(self):
        """Generate random track with platforms, tubes, ramps"""
        track_objects = []
        x, y, z = 0, 10, 0
        
        track_types = ['platform', 'ramp', 'tube', 'spiral']
        
        for i in range(8):
            track_type = random.choice(track_types)
            
            if track_type == 'platform':
                bpy.ops.mesh.primitive_cube_add(
                    size=2,
                    location=(x, y, z)
                )
                platform = bpy.context.active_object
                platform.scale = (2, 0.2, 2)
                
            elif track_type == 'ramp':
                bpy.ops.mesh.primitive_cube_add(
                    size=2,
                    location=(x, y, z)
                )
                platform = bpy.context.active_object
                platform.scale = (2, 0.2, 2)
                platform.rotation_euler[0] = math.radians(30)
                
            elif track_type == 'tube':
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.6,
                    depth=3,
                    location=(x, y, z)
                )
                platform = bpy.context.active_object
                platform.rotation_euler[0] = math.radians(90)
                
            elif track_type == 'spiral':
                bpy.ops.mesh.primitive_torus_add(
                    major_radius=2,
                    minor_radius=0.3,
                    location=(x, y, z)
                )
                platform = bpy.context.active_object
            
            # Add physics (static)
            bpy.context.view_layer.objects.active = platform
            bpy.ops.rigidbody.object_add()
            platform.rigid_body.type = 'PASSIVE'
            
            # Material (dark)
            mat = bpy.data.materials.new(f"Track_{i}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
            bsdf.inputs["Metallic"].default_value = 0.8
            bsdf.inputs["Roughness"].default_value = 0.3
            
            platform.data.materials.append(mat)
            track_objects.append(platform)
            
            # Random next position
            x += random.uniform(-1, 1)
            y -= random.uniform(2, 3)
            z += random.uniform(-1, 1)
        
        print(f"✅ Track created - {len(track_objects)} pieces")
        return track_objects
    
    def setup_lighting(self):
        """Create neon lighting"""
        # Ambient light
        bpy.ops.object.light_add(type='SUN', location=(10, 20, 10))
        sun = bpy.context.active_object
        sun.data.energy = 2.0
        sun.data.color = (1.0, 0.9, 0.8)
        
        # Key light (neon blue)
        bpy.ops.object.light_add(type='POINT', location=(5, 10, 5))
        key_light = bpy.context.active_object
        key_light.data.energy = 3.0
        key_light.data.color = (0.2, 0.9, 1.0)
        
        # Fill light (neon pink)
        bpy.ops.object.light_add(type='POINT', location=(-5, 10, -5))
        fill_light = bpy.context.active_object
        fill_light.data.energy = 2.0
        fill_light.data.color = (1.0, 0.2, 0.8)
        
        print("✅ Lighting setup complete")
    
    def setup_camera_tracking(self, ball):
        """Setup camera to track ball"""
        bpy.ops.object.camera_add(location=(5, 5, 15))
        camera = bpy.context.active_object
        camera.name = "TrackingCamera"
        
        self.scene.camera = camera
        
        # Add tracking constraint
        track_constraint = camera.constraints.new(type='TRACK_TO')
        track_constraint.target = ball
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        track_constraint.up_axis = 'UP_Y'
        
        print("✅ Camera tracking setup")
        return camera
    
    def setup_rendering(self):
        """Configure rendering settings"""
        self.scene.render.resolution_x = 1080
        self.scene.render.resolution_y = 1920
        self.scene.render.fps = self.fps
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.ffmpeg.codec = 'H264'
        self.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
        
        print("✅ Rendering configured")
    
    def render_video(self, output_path):
        """Render final video"""
        self.scene.render.filepath = output_path
        bpy.ops.render.render(animation=True)
        print(f"✅ Video rendered: {output_path}")

# Run the generator
print("\n" + "="*60)
print("🎬 BALL ROLLER - BLENDER GENERATION")
print("="*60 + "\n")

generator = BallRollerGenerator()
generator.clear_scene()
ball = generator.create_ball()
track = generator.create_random_track()
generator.setup_lighting()
camera = generator.setup_camera_tracking(ball)
generator.setup_rendering()

# Note: Render would run in Blender environment
print("\n✅ Scene setup complete!")
print("   Ready for rendering in Blender")

