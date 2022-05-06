import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from collections import namedtuple
import world

assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets")

class Animal(pg.sprite.Sprite):
    def __init__(self, size=10, pos_x=0, pos_y=0):
        super().__init__()
        self.size = size
        image = pg.image.load(join(assets_path,'Fichier 1.png')).convert_alpha()
        self.image = pg.transform.scale(image, (size,size))
        position_x = pos_x * world.BLOCK_SIZE
        position_y = pos_y * world.BLOCK_SIZE
        self.rect = self.image.get_rect(center= (position_x + world.BLOCK_SIZE/2, position_y + world.BLOCK_SIZE/2))
        
    def tmp_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            pass
        
    def update(self):
        self.rect.x += 1*world.BLOCK_SIZE

