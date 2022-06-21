from __future__ import annotations
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from grid import Grid
    from simulation import SimState, SimulatedObject
    from entities import Entity
    from energies import Resource

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
                 position: Tuple[int, int],
                 appearance: str):
        
        self.id = dis_obj_id
        self.size = size
        self.position = position
        
        self.appearance = appearance
        
    def init(self, block_size: int, assets_path: str, assets: Dict[str, pg.Image]):
        super(DisplayedObject, self).__init__()
      
        if assets.get(self.appearance, None):
            self.sprite = assets[self.appearance]
            
        else:
            self.sprite = pg.image.load(join(assets_path,
                                        self.appearance)).convert_alpha()  
            
            assets[self.appearance] = self.sprite  

        self.update(block_size=block_size)

    @staticmethod
    def create_display(sim_obj: SimulatedObject, block_size: int, assets_path: str,
                       assets: Dict[str, pg.Image]) -> DisplayedObject:
        
        dis_obj = DisplayedObject(dis_obj_id=sim_obj.id,
                                  appearance=sim_obj.appearance,
                                  size=sim_obj.size,
                                  position=sim_obj.position)
        
        dis_obj.init(block_size=block_size,
                     assets_path=assets_path,
                     assets=assets)
        
        return dis_obj
        
    def update(self, block_size, sim_state: SimState=None):
        if sim_state:
            entity = sim_state.entities[self.id]
            self.size = entity.size
            self.position = entity.position
        
        self.image: pg.Surface = pg.transform.scale(self.sprite, (self.size, self.size))
           
        pos_x, pos_y = self.position    
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x * block_size + block_size /2,
                    pos_y * block_size + block_size /2))
        
        

class Display:
    def __init__(self,
                 display_id: int,
                 block_size: int,
                 dimensions: Tuple[int, int],
                 sim_speed: int=1,
                 show_grid: bool=False):
        
        self.__id = display_id
        self.block_size: int = block_size
        self.dimensions: Tuple[int, int] = dimensions
        self.window_width: int = block_size * dimensions[0]
        self.window_height: int = block_size * dimensions[1]
        
        self.tick_counter = 0
        self.sim_speed: int = sim_speed
        self.clock: pg.Clock
        self.screen: pg.Screen
        self.show_grid = show_grid
        
        self.assets: Dict[str, pg.Image] = {}
        self.entities: Dict[int, DisplayedObject] = {}
        self.resources: Dict[int, DisplayedObject] = {}
        
        self.assets_path = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.absolute(),
            "assets/")
        
        self.entity_group = pg.sprite.Group()
        self.resource_group = pg.sprite.Group()
           
    def init(self, sim_state: SimState=None) -> None:
        pg.init()
        
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        
        if sim_state:
            for entity in sim_state.get_entities():
                self.add_entity(entity)
        
        self.clock = pg.time.Clock() 
        
    def add_entity(self, entity: Entity):
        dis_entity = DisplayedObject.create_display(block_size=self.block_size,
                                                    assets_path=self.assets_path,
                                                    sim_obj=entity,
                                                    assets=self.assets)    
            
        self.entities[entity.id] = dis_entity
        self.entity_group.add(dis_entity)
        
    def remove_entity(self, entity: Entity):
        dis_entity = self.entities.pop(entity.id)
        self.entity_group.remove(dis_entity)
        
    def add_resource(self, resource: Resource):
        dis_resource = DisplayedObject.create_display(block_size=self.block_size,
                                                      assets_path=self.assets_path,
                                                      sim_obj=resource,
                                                      assets=self.assets)    
            
        self.resources[resource.id] = dis_resource
        self.resource_group.add(dis_resource)
        
    def remove_resource(self, resource: Resource):
        dis_resource = self.resources.pop(resource.id)
        self.resource_group.remove(dis_resource)    
    
        
    def update(self, sim_state: SimState):
        for entity in sim_state.added_entities.values():
            self.add_entity(entity)
            
        for entity in sim_state.removed_entities.values():
            self.remove_entity(entity)
            
        for resource in sim_state.added_resources.values():
            self.add_resource(resource)
            
        for resource in sim_state.removed_resources.values():
            self.remove_resource(resource)
        
        self.entity_group.update(block_size=self.block_size,
                                 sim_state=sim_state)
        
        # self.resource_group.update(block_size=self.block_size,
        #                            sim_state=sim_state)
    
    def draw(self, grid) -> None:
        
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
        
        self.draw_world(grid)
        pg.display.update()
        self.clock.tick(self.sim_speed)
        self.tick_counter += 1
        if self.tick_counter == self.sim_speed:
            self.tick_counter = 0

    def draw_world(self, grid) -> None:
        """Draw the world, grid and entities"""
        self.draw_grid(grid)
        self.draw_entities()
        self.draw_resources()
    
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
                if self.show_grid:
                    pg.draw.rect(self.screen, BLACK, rect, 1)
                
    def draw_entities(self) -> None:
        """Draw the entities"""
        self.entity_group.draw(self.screen)

    def draw_resources(self) -> None:
        """Draw the energies"""
        self.resource_group.draw(self.screen)
        
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

        
