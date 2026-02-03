from panda3d.core import PointLight, Spotlight, AmbientLight, PerspectiveLens
from panda3d.core import LPoint3f, Point3, Vec3, Vec4, LVecBase3f, VBase4, LPoint2f


def lighting():
    # Ambient light - provides base illumination
    amb_light = AmbientLight('amblight')
    amb_light.set_color(Vec4(0.5, 0.5, 0.55, 2)) 
    amb_light_node = base.render.attach_new_node(amb_light)
    base.render.set_light(amb_light_node)

    # Main spotlight
    slight_1 = Spotlight('slight_1')
    slight_1.set_color(Vec4(0.3, 0.3, 0.25, 1))  # Very low intensity
    slight_1.set_shadow_caster(True, 4096, 4096) 
    slight_1.set_lens(PerspectiveLens())
    slight_1.get_lens().set_fov(180)
    slight_1.get_lens().set_near_far(1, 400)  # Limit range
    slight_1_node = base.render.attach_new_node(slight_1)
    slight_1_node.set_pos(69, -49, 90)
    slight_1_node.look_at(0, 0, 0.5)
    base.render.set_light(slight_1_node)
    
    # Secondary spotlight
    slight_2 = Spotlight('slight_2')
    slight_2.set_color(Vec4(0.2, 0.2, 0.25, 1))  # Very low, slightly blue
    slight_2.set_lens(PerspectiveLens())
    slight_2.get_lens().set_fov(70)
    slight_2.get_lens().set_near_far(1, 200)
    slight_2_node = base.render.attach_new_node(slight_2)
    slight_2_node.set_pos(-69, -49, 90)
    slight_2_node.look_at(0, 0, 20)
    base.render.set_light(slight_2_node)

    # Environment point light for skybox only
    env_light_1 = PointLight('env_light_1')
    env_light_1.set_color(Vec4(1.5, 1.5, 1.3, 1))
    env_light_1_node = base.render.attach_new_node(env_light_1)
    env_light_1_node.set_pos(0, 0, 100)  # Move up so it doesn't brighten ground

    # Load skybox
    base_env = base.loader.load_model('models/daytime_skybox.bam')
    base_env.name = 'basic_skybox'
    base_env.reparent_to(base.render)
    base_env.set_scale(1)
    base_env.set_pos(0, 0, 0)
    base_env.set_light(env_light_1_node)
    # base_env.set_light_off(base.render.find('**/slight_1'))
    base_env.set_light_off(base.render.find('**/slight_2'))  