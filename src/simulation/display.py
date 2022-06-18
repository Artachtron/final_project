from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid
    from simulation import SimState

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
        
        self.appearance = appearance
        
    def init(self, block_size: int, assets_path: str):
        super(DisplayedObject, self).__init__()
        self.image: pg.Surface = pg.image.load(join(assets_path,
                                                    self.appearance)).convert_alpha()    
        
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x *block_size + block_size /2,
                pos_y * block_size + block_size /2))
        
        

class Display:
    def __init__(self,
                 display_id: int,
                 block_size: int,
                 dimensions: Tuple[int, int],
                 sim_speed: int=1):
        
        self.__id = display_id
        self.block_size: int = block_size
        self.dimensions: Tuple[int, int] = dimensions
        
        self.window_width: int = block_size * dimensions[0]
        self.window_height: int = block_size * dimensions[1]
        
        
        self.tick_counter = 0
        self.sim_speed: int = sim_speed
        self.clock: pg.Clock
        self.screen: pg.Screen
        
        self.assets_path = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.absolute(),
            "assets/")
        
        self.entity_group = pg.sprite.Group()
        self.resource_group = pg.sprite.Group()
     
        
    def init(self, sim_state: SimState) -> None:
        pg.init()
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        
        for entity in sim_state.entities:
            entity.dis_obj.init(block_size=self.block_size,
                                assets_path=self.assets_path)
            
            self.entity_group.add(entity.dis_obj)
        
        
        self.clock = pg.time.Clock() 
    
    def draw(self, grid) -> None:
        
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
        
        self.draw_world(grid)
        pg.display.update()
        self.clock.tick(60)
        self.tick_counter += 1
        if self.tick_counter == self.sim_speed:
            self.tick_counter = 0

    def draw_world(self, grid) -> None:
        """Draw the world, grid and entities"""
        self.draw_grid(grid)
        self.draw_entities(grid)
        # self.draw_energies(grid)
    
    def draw_grid(self, grid) -> None:
        """Draw the grid"""
        #SCREEN.fill(WHITE)
        color_grid = grid.color_grid.array
        for x in range(0, self.window_width, self.block_size):
            for y in range(0, self.window_height,  self.block_size):
                rect = pg.Rect(x, y,  self.block_size,  self.block_size)
                pg.draw.rect(self.screen,
                             color_grid[int(x / self.block_size),
                                        int(y / self.block_size)],
                             rect, 0)
                
                pg.draw.rect(self.screen, BLACK, rect, 1)
                
    def draw_entities(self, grid) -> None:
        """Draw the entities"""
        
        self.entity_group.draw(self.screen)

    def draw_energies(self, grid) -> None:
        """Draw the energies"""
        grid.energy_group.draw(self.screen)
        
    def update_world(self) -> None:
        """Update the world"""
        """ if  self.tick_counter == 0:
            update_entities() """

    def update_entities(self) -> None:
        """Update the entities"""
        grid.entity_group.update()
        
    @property
    def id(self):
        return self.__id

        
