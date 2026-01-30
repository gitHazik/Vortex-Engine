from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data, BitMask32, Vec3, Point3, LVecBase3f
from panda3d.core import WindowProperties
import sys
from panda3d.bullet import BulletWorld, BulletCharacterControllerNode
from panda3d.bullet import ZUp, BulletCapsuleShape, BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode

class app(ShowBase):
    def __init__(self):
        load_prc_file_data("", """
            win-size 1280 720
            window-title Simple Player Controller
            framebuffer-multisample 1
            multisamples 4
            cursor-hidden #t
        """)

        super().__init__()
        
        # Window properties
        props = WindowProperties()
        props.set_mouse_mode(WindowProperties.M_relative)
        base.win.request_properties(props)
        base.set_background_color(0.5, 0.5, 0.8)
        
        self.camLens.set_fov(90)
        self.camLens.set_near_far(0.1, 5000)

        self.accept("f3", self.toggle_wireframe)
        self.accept("escape", sys.exit, [0])
        
        # Physics setup


        # Lighting setup
        from src import arena_lighting
        arena_lighting.lighting()
        
        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
        
        # Load the arena model
        arena_1 = self.loader.load_model('models/arena_1.bam')
        arena_1.reparent_to(self.render)
        arena_1.set_pos(0, 0, 0)
        
        # Create collision from arena model
        from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape
        from panda3d.core import TransformState
        
        def make_collision_from_model(input_model, node_number, mass, world, target_pos):
            geom_nodes = input_model.find_all_matches('**/+GeomNode')
            geom_nodes = geom_nodes.get_path(node_number).node()
            geom_target = geom_nodes.get_geom(0)
            output_bullet_mesh = BulletTriangleMesh()
            output_bullet_mesh.add_geom(geom_target)
            tri_shape = BulletTriangleMeshShape(output_bullet_mesh, dynamic=False)

            body = BulletRigidBodyNode('arena_collision')
            np = self.render.attach_new_node(body)
            np.node().add_shape(tri_shape)
            np.node().set_mass(mass)
            np.node().set_friction(0.5)
            np.set_pos(target_pos)
            np.set_collide_mask(BitMask32.allOn())
            world.attach_rigid_body(np.node())
        
        make_collision_from_model(arena_1, 0, 0, self.world, arena_1.get_pos())
        
        # Player character controller
        shape = BulletCapsuleShape(0.75, 0.5, ZUp)
        player_node = BulletCharacterControllerNode(shape, 0.1, 'Player')
        player_np = self.render.attach_new_node(player_node)
        player_np.set_pos(0, 0, 5)
        player_np.set_collide_mask(BitMask32.allOn())
        self.world.attach_character(player_np.node())
        self.player = player_np

        # Camera setup
        self.camera.reparent_to(self.player)
        self.camera.set_y(self.player, 0)
        self.camera.set_z(self.player, 0.55)
        
        # Jump function
        def jump():
            self.player.node().do_jump()

        self.accept('space', jump)
        self.accept('mouse3', jump)

        # Movement system
        self.keyMap = {"left": 0, "right": 0, "forward": 0, "backward": 0}

        def setKey(key, value):
            self.keyMap[key] = value

        self.accept("a", setKey, ["left", 1])
        self.accept("a-up", setKey, ["left", 0])
        self.accept("d", setKey, ["right", 1])
        self.accept("d-up", setKey, ["right", 0])
        self.accept("w", setKey, ["forward", 1])
        self.accept("w-up", setKey, ["forward", 0])
        self.accept("s", setKey, ["backward", 1])
        self.accept("s-up", setKey, ["backward", 0])
        
        self.disable_mouse()

        # Movement speeds
        self.movementSpeed = 5
        self.striveSpeed = 5

        def move(Task):
            # Mouse look
            pointer = base.win.get_pointer(0)
            mouse_watch = base.mouseWatcherNode
            
            if pointer.in_window and mouse_watch.has_mouse():
                mouseX = pointer.get_x()
                mouseY = pointer.get_y()
                
                window_Xcoord_halved = base.win.get_x_size() // 2
                window_Ycoord_halved = base.win.get_y_size() // 2
                
                mouseSpeedX = 0.2
                mouseSpeedY = 0.2
                maxPitch = 90
                minPitch = -50

                if base.win.movePointer(0, window_Xcoord_halved, window_Ycoord_halved):
                    # Calculate pitch
                    p = self.camera.get_p() - (mouseY - window_Ycoord_halved) * mouseSpeedY
                    p = max(minPitch, min(maxPitch, p))
                    self.camera.set_p(p)

                    # Calculate heading
                    h = self.player.get_h() - (mouseX - window_Xcoord_halved) * mouseSpeedX
                    if h < -360:
                        h += 360
                    elif h > 360:
                        h -= 360
                    self.player.set_h(h)

            # Movement
            dt = globalClock.get_dt()
            
            if self.keyMap["left"]:
                self.player.set_x(self.player, -self.striveSpeed * dt)
                        
            if self.keyMap["right"]:
                self.player.set_x(self.player, self.striveSpeed * dt)

            if self.keyMap["forward"]:
                self.player.set_y(self.player, self.movementSpeed * dt)
                    
            if self.keyMap["backward"]:
                self.player.set_y(self.player, -self.movementSpeed * dt)
                
            return Task.cont

        def physics_update(Task):
            dt = globalClock.get_dt()
            self.world.do_physics(dt)
            return Task.cont
            
        self.task_mgr.add(move)
        self.task_mgr.add(physics_update)

app().run()