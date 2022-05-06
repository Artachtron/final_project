import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from collections import namedtuple
import world

Position = namedtuple('Position', ['x', 'y'])

class Animal(pg.sprite.Sprite):
    def __init__(self, size=10, pos_x=0, pos_y=0):
        super().__init__()
        self.size = size
        image = pg.image.load(join(Path(dirname(realpath(__file__))).parent.absolute(),r'assets\Fichier 1.png')).convert_alpha()
        self.image = pg.transform.scale(image, (size,size))
        self.position = Position(pos_x*world.BLOCK_SIZE, pos_y*world.BLOCK_SIZE)
        self.rect = self.image.get_rect(center= (self.position.x+world.BLOCK_SIZE/2,self.position.y+world.BLOCK_SIZE/2))
        
