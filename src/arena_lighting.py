from panda3d.core import PointLight, Spotlight, AmbientLight, PerspectiveLens
from panda3d.core import LPoint3f, Point3, Vec3, Vec4, LVecBase3f, VBase4, LPoint2f


def lighting():
    # Ambient light - provides base illumination
    amb_light = AmbientLight('amblight')
    amb_light.set_color(Vec4(0.3, 0.3, 0.35, 1))  # Reduced from Vec3(1)
    amb_light_node = base.render.attach_new_node(amb_light)
    base.render.set_light(amb_light_node)

    # Main spotlight - reduced intensity
    slight_1 = Spotlight('slight_1')
    slight_1.set_color(Vec4(2.5, 2.5, 2.0, 1))  # Reduced from 8 to 2.5
    slight_1.set_shadow_caster(True, 4096, 4096)
    lens = PerspectiveLens()
    slight_1.set_lens(lens)
    slight_1.get_lens().set_fov(120)
    slight_1_node = base.render.attach_new_node(slight_1)
    slight_1_node.set_pos(69, -49, 90)
    slight_1_node.look_at(0, 0, 0.5)
    base.render.set_light(slight_1_node)
    
    # Secondary spotlight - fill light
    slight_2 = Spotlight('slight_2')
    slight_2.set_color(Vec4(0.8, 0.8, 1.0, 1))  # Slightly blue tint
    lens = PerspectiveLens()
    slight_2.set_lens(lens)
    slight_2.get_lens().set_fov(40)
    slight_2_node = base.render.attach_new_node(slight_2)
    slight_2_node.set_pos(-69, -49, 90)
    slight_2_node.look_at(0, 0, 20)
    base.render.set_light(slight_2_node)

    # Environment point light for skybox
    env_light_1 = PointLight('env_light_1')
    env_light_1.set_color(Vec4(1.2, 1.2, 1.0, 1))  # Reduced from 6
    env_light_1_node = base.render.attach_new_node(env_light_1)
    env_light_1_node.set_pos(0, 0, 0)

    # Load skybox
    base_env = base.loader.load_model('models/daytime_skybox.bam')
    base_env.name = 'basic_skybox'
    base_env.reparent_to(base.render)
    base_env.set_scale(1)
    base_env.set_pos(0, 0, 0)
    base_env.set_light(env_light_1_node)
    base_env.set_light_off(base.render.find('**/slight_1'))


def init_flashlight():
    """Optional flashlight attached to camera"""
    base.slight = Spotlight('flashlight')
    base.slight.set_color(VBase4(3.5, 3.6, 3.8, 1))  # Cool white
    lens = PerspectiveLens()
    lens.set_near_far(0.5, 500)
    base.slight.set_lens(lens)
    base.slight.set_attenuation((0.5, 0, 0.0005))
    base.slight.get_lens().set_fov(35)
    base.slight_node = base.render.attach_new_node(base.slight)
    base.slight_node.reparent_to(base.cam)
    base.slight_node.set_pos(0, 0.4, 0.2)
    base.render.find('**/basic_skybox').set_light_off(base.slight_node)


def toggle_flashlight():
    """Toggle flashlight on/off"""
    if base.render.has_light(base.slight_node):
        base.render.set_light_off(base.slight_node)
    else:
        base.render.set_light(base.slight_node)