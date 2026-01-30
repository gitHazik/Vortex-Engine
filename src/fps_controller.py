from panda3d.core import Vec3, Point3, BitMask32
from panda3d.bullet import BulletCharacterControllerNode, BulletCapsuleShape, ZUp
from direct.task import Task


class FPSController:
    """
    A smooth first-person shooter controller for Panda3D with Bullet physics.
    
    Features:
    - Smooth camera movement with configurable sensitivity
    - WASD movement with sprint capability
    - Jump mechanics
    - Configurable movement speeds and physics
    """
    
    def __init__(self, world, render, camera, win, mouse_watcher, 
                 spawn_pos=Vec3(0, 0, 5),
                 walk_speed=5.0,
                 sprint_speed=10.0,
                 strafe_speed=5.0,
                 mouse_sensitivity=0.2,
                 camera_smoothing=0.15,
                 jump_height=5.0,
                 pitch_limit_up=89.0,
                 pitch_limit_down=-89.0,
                 capsule_radius=0.75,
                 capsule_height=0.5,
                 step_height=0.4):
        """
        Initialize the FPS controller.
        
        Args:
            world: BulletWorld instance
            render: ShowBase render node
            camera: ShowBase camera node
            win: ShowBase window
            mouse_watcher: ShowBase mouseWatcherNode
            spawn_pos: Starting position (default: Vec3(0, 0, 5))
            walk_speed: Normal movement speed (default: 5.0)
            sprint_speed: Sprint movement speed (default: 10.0)
            strafe_speed: Strafing speed (default: 5.0)
            mouse_sensitivity: Mouse look sensitivity (default: 0.2)
            camera_smoothing: Camera interpolation factor 0-1 (default: 0.15)
            jump_height: Jump force (default: 5.0)
            pitch_limit_up: Max upward pitch in degrees (default: 89.0)
            pitch_limit_down: Max downward pitch in degrees (default: -89.0)
            capsule_radius: Player capsule radius (default: 0.75)
            capsule_height: Player capsule height (default: 0.5)
            step_height: Maximum step height (default: 0.4)
        """
        self.world = world
        self.render = render
        self.camera = camera
        self.win = win
        self.mouse_watcher = mouse_watcher
        
        # Movement parameters
        self.walk_speed = walk_speed
        self.sprint_speed = sprint_speed
        self.strafe_speed = strafe_speed
        self.current_speed = walk_speed
        
        # Camera parameters
        self.mouse_sensitivity = mouse_sensitivity
        self.camera_smoothing = camera_smoothing
        self.pitch_limit_up = pitch_limit_up
        self.pitch_limit_down = pitch_limit_down
        
        # Target rotation values for smooth interpolation
        self.target_pitch = 0
        self.target_heading = 0
        self.current_pitch = 0
        self.current_heading = 0
        
        # Jump parameters
        self.jump_height = jump_height
        
        # Input state
        self.key_map = {
            "left": False,
            "right": False,
            "forward": False,
            "backward": False,
            "sprint": False
        }
        
        # Create player character controller
        shape = BulletCapsuleShape(capsule_radius, capsule_height, ZUp)
        self.player_node = BulletCharacterControllerNode(shape, step_height, 'Player')
        self.player_node.set_jump_speed(jump_height)
        self.player_node.set_max_jump_height(jump_height * 2)
        self.player_node.set_gravity(9.81)
        
        self.player = self.render.attach_new_node(self.player_node)
        self.player.set_pos(spawn_pos)
        self.player.set_collide_mask(BitMask32.allOn())
        
        self.world.attach_character(self.player_node)
        
        # Setup camera
        self.camera.reparent_to(self.player)
        self.camera.set_pos(0, 0, 0.55)
        
        # Center mouse initially
        self._center_mouse()
    
    def _center_mouse(self):
        """Center the mouse pointer in the window."""
        if self.win.has_pointer(0):
            window_center_x = self.win.get_x_size() // 2
            window_center_y = self.win.get_y_size() // 2
            self.win.move_pointer(0, window_center_x, window_center_y)
    
    def setup_controls(self, accept_func):
        """
        Setup input controls using the ShowBase accept function.
        
        Args:
            accept_func: The ShowBase.accept function
        """
        # Movement keys
        accept_func("w", self._set_key, ["forward", True])
        accept_func("w-up", self._set_key, ["forward", False])
        accept_func("s", self._set_key, ["backward", True])
        accept_func("s-up", self._set_key, ["backward", False])
        accept_func("a", self._set_key, ["left", True])
        accept_func("a-up", self._set_key, ["left", False])
        accept_func("d", self._set_key, ["right", True])
        accept_func("d-up", self._set_key, ["right", False])
        
        # Sprint
        accept_func("shift", self._set_key, ["sprint", True])
        accept_func("shift-up", self._set_key, ["sprint", False])
        
        # Jump
        accept_func("space", self.jump)
    
    def _set_key(self, key, value):
        """Set key state in the key map."""
        self.key_map[key] = value
    
    def jump(self):
        """Make the player jump."""
        self.player_node.do_jump()
    
    def update_camera(self, dt):
        """
        Update camera rotation with smooth interpolation.
        
        Args:
            dt: Delta time
        """
        pointer = self.win.get_pointer(0)
        
        if not pointer.in_window or not self.mouse_watcher.has_mouse():
            return
        
        mouse_x = pointer.get_x()
        mouse_y = pointer.get_y()
        
        window_center_x = self.win.get_x_size() // 2
        window_center_y = self.win.get_y_size() // 2
        
        # Calculate mouse delta from center
        delta_x = mouse_x - window_center_x
        delta_y = mouse_y - window_center_y
        
        # Update target rotations
        self.target_pitch -= delta_y * self.mouse_sensitivity
        self.target_pitch = max(self.pitch_limit_down, min(self.pitch_limit_up, self.target_pitch))
        
        self.target_heading -= delta_x * self.mouse_sensitivity
        
        # Normalize heading
        if self.target_heading < -180:
            self.target_heading += 360
        elif self.target_heading > 180:
            self.target_heading -= 360
        
        # Smooth interpolation
        smoothing_factor = 1.0 - pow(self.camera_smoothing, dt * 60)
        
        self.current_pitch += (self.target_pitch - self.current_pitch) * smoothing_factor
        self.current_heading += (self.target_heading - self.current_heading) * smoothing_factor
        
        # Apply rotations
        self.camera.set_p(self.current_pitch)
        self.player.set_h(self.current_heading)
        
        # Recenter mouse
        self.win.move_pointer(0, window_center_x, window_center_y)
    
    def update_movement(self, dt):
        """
        Update player movement based on input.
        
        Args:
            dt: Delta time
        """
        # Determine current speed (sprint or walk)
        if self.key_map["sprint"]:
            self.current_speed = self.sprint_speed
        else:
            self.current_speed = self.walk_speed
        
        # Calculate movement direction
        move_vec = Vec3(0, 0, 0)
        
        if self.key_map["forward"]:
            move_vec.y += self.current_speed
        
        if self.key_map["backward"]:
            move_vec.y -= self.current_speed
        
        if self.key_map["left"]:
            move_vec.x -= self.strafe_speed
        
        if self.key_map["right"]:
            move_vec.x += self.strafe_speed
        
        # Apply movement relative to player orientation
        if move_vec.length() > 0:
            self.player.set_pos(self.player, move_vec * dt)
    
    def update(self, dt):
        """
        Main update method - call this every frame.
        
        Args:
            dt: Delta time
        """
        self.update_camera(dt)
        self.update_movement(dt)
    
    def get_position(self):
        """Get the player's current position."""
        return self.player.get_pos()
    
    def set_position(self, pos):
        """
        Set the player's position.
        
        Args:
            pos: Vec3 position
        """
        self.player.set_pos(pos)
    
    def get_heading(self):
        """Get the player's current heading."""
        return self.player.get_h()
    
    def is_on_ground(self):
        """Check if the player is on the ground."""
        return self.player_node.is_on_ground()
    
    def set_walk_speed(self, speed):
        """Set the walking speed."""
        self.walk_speed = speed
    
    def set_sprint_speed(self, speed):
        """Set the sprinting speed."""
        self.sprint_speed = speed
    
    def set_mouse_sensitivity(self, sensitivity):
        """Set the mouse sensitivity."""
        self.mouse_sensitivity = sensitivity
    
    def cleanup(self):
        """Clean up the controller."""
        self.world.remove_character(self.player_node)
        self.player.remove_node()