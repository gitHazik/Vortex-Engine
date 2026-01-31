from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data, BitMask32, Vec3
from panda3d.core import WindowProperties
from panda3d.bullet import BulletWorld, BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape
import sys

from src.fps_controller import FPSController

class Game(ShowBase):
    """Main game application with FPS controller."""
    
    def __init__(self):
        # Configure window settings
        load_prc_file_data("", """
            win-size 1920 1080
            window-title Advanced FPS Controller Demo
            framebuffer-multisample 1
            multisamples 4
            cursor-hidden #t
            sync-video #t
        """)

        super().__init__()
        
        self._setup_window()
        self._setup_camera()
        self._setup_physics()
        self._setup_lighting()
        self._setup_arena()
        self._setup_player()
        self._setup_controls()
        self._setup_tasks()
        
        # Display instructions
        self._show_instructions()

    
    def _setup_window(self):
        """Configure window properties."""
        props = WindowProperties()
        props.set_mouse_mode(WindowProperties.M_relative)
        self.win.request_properties(props)
        self.set_background_color(0.53, 0.81, 0.92)  # Sky blue
        
    def _setup_camera(self):
        """Configure camera settings."""
        self.camLens.set_fov(90)
        self.camLens.set_near_far(0.1, 5000)
        self.disable_mouse()
    
    def _setup_physics(self):
        """Initialize physics world."""
        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
    
    def _setup_lighting(self):
        """Setup scene lighting."""
        try:
            from src import arena_lighting
            arena_lighting.lighting()
        except ImportError:
            # Fallback lighting if custom module not available
            from panda3d.core import AmbientLight, DirectionalLight
            
            # Ambient light
            ambient = AmbientLight('ambient')
            ambient.set_color((0.3, 0.3, 0.3, 1))
            ambient_np = self.render.attach_new_node(ambient)
            self.render.set_light(ambient_np)
            
            # Directional light (sun)
            sun = DirectionalLight('sun')
            sun.set_color((0.8, 0.8, 0.7, 1))
            sun_np = self.render.attach_new_node(sun)
            sun_np.set_hpr(-45, -60, 0)
            self.render.set_light(sun_np)
    
    def _setup_arena(self):
        """Load and setup the arena with collision."""
        # Load arena model
        try:
            self.arena = self.loader.load_model('models/arena_1.bam')
            self.arena.reparent_to(self.render)
            self.arena.set_pos(0, 0, 0)
            
            # Create collision mesh from model
            self._create_arena_collision()
        except:
            print("Warning: Could not load arena model. Creating fallback ground plane.")
            self._create_fallback_ground()
    
    def _create_arena_collision(self):
        """Create collision mesh from arena model."""
        geom_nodes = self.arena.find_all_matches('**/+GeomNode')
        
        if geom_nodes.get_num_paths() > 0:
            geom_node = geom_nodes.get_path(0).node()
            geom = geom_node.get_geom(0)
            
            # Create bullet mesh
            mesh = BulletTriangleMesh()
            mesh.add_geom(geom)
            shape = BulletTriangleMeshShape(mesh, dynamic=False)
            
            # Create rigid body
            body = BulletRigidBodyNode('arena_collision')
            body.add_shape(shape)
            body.set_mass(0)  # Static object
            body.set_friction(0.5)
            
            # Attach to scene
            arena_np = self.render.attach_new_node(body)
            arena_np.set_pos(self.arena.get_pos())
            arena_np.set_collide_mask(BitMask32.allOn())
            
            self.world.attach_rigid_body(body)
    
    def _create_fallback_ground(self):
        """Create a simple ground plane as fallback."""
        from panda3d.bullet import BulletPlaneShape
        
        # Create simple ground plane
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        body = BulletRigidBodyNode('ground')
        body.add_shape(shape)
        body.set_mass(0)
        body.set_friction(0.5)
        
        ground_np = self.render.attach_new_node(body)
        ground_np.set_pos(0, 0, 0)
        ground_np.set_collide_mask(BitMask32.allOn())
        
        self.world.attach_rigid_body(body)
        
        # Visual representation
        from panda3d.core import CardMaker
        cm = CardMaker('ground_card')
        cm.set_frame(-100, 100, -100, 100)
        ground_card = self.render.attach_new_node(cm.generate())
        ground_card.set_p(-90)
        ground_card.set_color(0.3, 0.6, 0.3, 1)
    
    def _setup_player(self):
        """Initialize the FPS controller."""
        self.fps_controller = FPSController(
            world=self.world,
            render=self.render,
            camera=self.camera,
            win=self.win,
            mouse_watcher=self.mouseWatcherNode,
            spawn_pos=Vec3(0, 0, 5),
            walk_speed=6.0,
            sprint_speed=12.0,
            strafe_speed=6.0,
            mouse_sensitivity=0.15,
            camera_smoothing=0.2,
            jump_height=6.0,
            pitch_limit_up=89,
            pitch_limit_down=-89
        )
        
        # Setup player controls
        self.fps_controller.setup_controls(self.accept)
    
    def _setup_controls(self):
        """Setup additional game controls."""
        self.accept("escape", self._exit_game)
        self.accept("f3", self.toggle_wireframe)
        self.accept("f1", self._toggle_instructions)
        self.accept("f2", self._toggle_debug_info)
        
        self.show_instructions = True
        self.show_debug = False
    
    def _setup_tasks(self):
        """Setup update tasks."""
        self.taskMgr.add(self._update_physics, "physics_update", sort=1)
        self.taskMgr.add(self._update_player, "player_update", sort=2)
        self.taskMgr.add(self._update_ui, "ui_update", sort=3)
    
    def _update_physics(self, task):
        """Update physics simulation."""
        dt = globalClock.get_dt()
        self.world.do_physics(dt, 10, 1.0/180.0)
        return task.cont
    
    def _update_player(self, task):
        """Update player controller."""
        dt = globalClock.get_dt()
        self.fps_controller.update(dt)
        return task.cont
    
    def _update_ui(self, task):
        """Update UI elements."""
        if self.show_debug:
            self._update_debug_text()
        return task.cont
    
    def _show_instructions(self):
        """Display on-screen instructions."""
        from panda3d.core import TextNode
        
        self.instruction_text = self.aspect2d.attach_new_node(
            TextNode('instructions')
        )
        text_node = self.instruction_text.node()
        text_node.set_text(
            "CONTROLS:\n"
            "WASD - Move\n"
            "Shift - Sprint\n"
            "Space - Jump\n"
            "Mouse - Look\n"
            "F1 - Toggle Help\n"
            "F2 - Toggle Debug\n"
            "F3 - Wireframe\n"
            "ESC - Exit"
        )
        text_node.set_align(TextNode.A_left)
        text_node.set_text_color(1, 1, 1, 1)
        text_node.set_shadow(0.05, 0.05)
        self.instruction_text.set_scale(0.06)
        self.instruction_text.set_pos(-1.5, 0, 0.9)
    
    def _toggle_instructions(self):
        """Toggle instruction display."""
        self.show_instructions = not self.show_instructions
        if self.show_instructions:
            self.instruction_text.show()
        else:
            self.instruction_text.hide()
    
    def _toggle_debug_info(self):
        """Toggle debug information display."""
        self.show_debug = not self.show_debug
        
        if self.show_debug and not hasattr(self, 'debug_text'):
            from panda3d.core import TextNode
            
            self.debug_text = self.aspect2d.attach_new_node(
                TextNode('debug')
            )
            text_node = self.debug_text.node()
            text_node.set_align(TextNode.A_left)
            text_node.set_text_color(0, 1, 0, 1)
            text_node.set_shadow(0.05, 0.05)
            self.debug_text.set_scale(0.05)
            self.debug_text.set_pos(-1.5, 0, -0.9)
        
        if self.show_debug:
            self.debug_text.show()
        else:
            self.debug_text.hide()
    
    def _update_debug_text(self):
        """Update debug information."""
        if hasattr(self, 'debug_text'):
            pos = self.fps_controller.get_position()
            heading = self.fps_controller.get_heading()
            on_ground = self.fps_controller.is_on_ground()
            fps = globalClock.get_average_frame_rate()
            
            debug_info = (
                f"FPS: {fps:.1f}\n"
                f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})\n"
                f"Heading: {heading:.1f}°\n"
                f"On Ground: {on_ground}\n"
                f"Sprint: {self.fps_controller.key_map['sprint']}"
            )
            
            self.debug_text.node().set_text(debug_info)
    
    def _exit_game(self):
        """Clean exit."""
        self.fps_controller.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    game = Game()
    game.run()