from panda3d.core import *
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletBoxShape
from direct.showbase.ShowBase import ShowBase

# -------------------------------
# PRC CONFIGURATION (BEFORE ShowBase)
# -------------------------------
loadPrcFileData(
    "",
    """
    win-size 1280 720
    window-title Vortex
    framebuffer-multisample 1
    multisamples 4
    hardware-animated-vertices true
    cursor-hidden true
    """
)


class Game(ShowBase):
    def __init__(self):
        super().__init__()  # Must be after loadPrcFileData

        # Background
        self.setBackgroundColor(0, 0, 0)

        # -------------------------------
        # BULLET PHYSICS WORLD SETUP
        # -------------------------------
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))

        # -------------------------------
        # CREATE TEST PLATFORM
        # -------------------------------
        self.platform_size = Vec3(10, 10, 1)
        self.platform_pos = Vec3(0, 0, -1)
        self.create_platform(self.platform_size, self.platform_pos)

        # -------------------------------
        # BASIC LIGHTING
        # -------------------------------
        self.setup_lights()

        # -------------------------------
        # CAMERA POSITION
        # -------------------------------
        self.camera.setPos(0, -20, 8)
        self.camera.setP(-20)

        # -------------------------------
        # PHYSICS UPDATE TASK
        # -------------------------------
        self.taskMgr.add(self.update_physics, "update_physics")

    # -------------------------------
    # PLATFORM CREATION
    # -------------------------------
    def create_platform(self, size, pos):
        shape = BulletBoxShape(size * 0.5)
        body = BulletRigidBodyNode("PlatformBody")
        body.addShape(shape)
        body.setMass(0.0)
        body_np = render.attachNewNode(body)
        body_np.setPos(pos)
        self.physics_world.attachRigidBody(body)

        cm = CardMaker("PlatformVisual")
        cm.setFrame(-size.x / 2, size.x / 2, -size.y / 2, size.y / 2)
        visual_np = render.attachNewNode(cm.generate())
        visual_np.setP(-90)
        visual_np.setPos(pos)
        visual_np.setColor(0.6, 0.6, 0.6, 1)

    # -------------------------------
    # LIGHTING SETUP
    # -------------------------------
    def setup_lights(self):
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor(Vec4(0.3, 0.3, 0.3, 1))
        ambient_np = render.attachNewNode(ambient_light)
        render.setLight(ambient_np)

        directional_light = DirectionalLight("directional_light")
        directional_light.setColor(Vec4(1, 1, 1, 1))
        directional_np = render.attachNewNode(directional_light)
        directional_np.setHpr(45, -60, 0)
        render.setLight(directional_np)

    # -------------------------------
    # PHYSICS UPDATE LOOP
    # -------------------------------
    def update_physics(self, task):
        dt = globalClock.getDt()
        self.physics_world.doPhysics(dt)
        return task.cont


if __name__ == "__main__":
    game = Game()
    game.run()
