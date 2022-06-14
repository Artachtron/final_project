import pygame as pg
import sys

from typing import Tuple
from os.path import dirname, realpath, join
from pathlib import Path

grid = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class DisplayedObject(pg.sprite.Sprite):
    def __init__(self,
                 dis_obj_id: int,
                 size: int,
                 position: int,
                 appearance: str):
        
        self.id = dis_obj_id
        self.size = size
        self.position = position
        
        assets_path = join(
    Path(
        dirname(
            realpath(__file__))).parent.absolute(),
    "assets/")
        
        self.image: pg.Surface = pg.image.load(join(assets_path,
                                            appearance)).convert_alpha()
        
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x *grid.BLOCK_SIZE + grid.BLOCK_SIZE /2,
                pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE /2))
        


class Display:
    def __init__(self,
                 display_id: int,
                 sim_speed: int,
                 block_size: int,
                 dimensions: Tuple[int, int]):
        
        self.id = display_id
        self.sim_speed: int = sim_speed
        self.block_size: int = block_size
        self.dimensions: Tuple[int, int] = dimensions
        
        self.window_width: int = block_size * dimensions[0]
        self.window_height: int = block_size * dimensions[1]
        
        
        self.tick_counter = 0
        self.clock: pg.Clock
        self.screen: pg.Screen
        
        self._init_pygame()
        
    def _init_pygame(self) -> None:
        pg.init()
        
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        self.clock = pg.time.Clock() 
    
    def run(self) -> None:
        
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
        
        self.draw_world()
        pg.display.update()
        self.clock.tick(60)
        self.tick_counter += 1
        if self.tick_counter == self.sim_speed:
            self.tick_counter = 0

    def draw_world(self) -> None:
        """Draw the world, grid and entities"""
        self.draw_grid()
        self.draw_entities()
        self.draw_energies()
    
    def draw_grid(self) -> None:
        """Draw the grid"""
        #SCREEN.fill(WHITE)
        color_grid = grid.color_grid.subgrid
        for x in range(0, self.window_width, self.block_size):
            for y in range(0, self.window_height,  self.block_size):
                rect = pg.Rect(x, y,  self.block_size,  self.block_size)
                pg.draw.rect(self.screen, color_grid[int(x/ self.block_size),int(y/ self.block_size)], rect, 0)
                pg.draw.rect(self.screen, BLACK, rect, 1)
                
    def draw_entities(self) -> None:
        """Draw the entities"""
        
        grid.entity_group.draw(self.screen)

    def draw_energies(self) -> None:
        """Draw the energies"""
        grid.energy_group.draw(self.screen)
        
    def update_world(self) -> None:
        """Update the world"""
        """ if  self.tick_counter == 0:
            update_entities() """

    def update_entities(self) -> None:
        """Update the entities"""
        grid.entity_group.update()


class EntitySprite(pg.sprite.Sprite):
    def __init__(self,
                image_filename: str,
                position:Tuple[int,int],
                size: int):
        
        assets_path = join(
    Path(
        dirname(
            realpath(__file__))).parent.absolute(),
    "assets/models/entities")
        
        image: pg.Surface = pg.image.load(join(assets_path,
                                            image_filename)).convert_alpha()
        self.size: int = size
        self.image: pg.Surface = pg.transform.scale(image, (size, size))
        self.position = position
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x *grid.BLOCK_SIZE + grid.BLOCK_SIZE /2,
                pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE /2))
        
class SeedSprite(EntitySprite):
    def __init__(self,
                 position:Tuple[int,int],
                 size: int,
                 ):
        
        super(SeedSprite, self).__init__(image_filename="Seed.png",
                                        size=size,
                                        position=position)
        
class AnimalSprite(EntitySprite):
    def __init__(self,
                 position:Tuple[int,int],
                 size: int,):
        
        super(AnimalSprite,self).__init__(image_filename='Animal.png',
                                          size=size,
                                          position=position)
        
class TreeSprite(EntitySprite):
    def __init__(self,
                 position:Tuple[int,int],
                 size: int,):
        
        super(TreeSprite, self).__init__(image_filename='Plant.png',
                                         size=size,
                                         position=position)