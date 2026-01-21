from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

class Game(ShowBase):
    def __init__(self):
        super().__init__()
    
game= Game()
game.run()