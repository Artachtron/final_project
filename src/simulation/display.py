from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from grid import Grid
    from simulation import SimState
    from entities import Entity
    from energies import Resource
    from universal import SimulatedObject

import sys
from os.path import dirname, join, realpath
from pathlib import Path
from typing import Tuple

import pygame as pg

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class DisplayedObject(pg.sprite.Sprite):
    """Class:
        Object containing a sprite
        to be drawn on display

        Attributes:
            __Id (int):                 unique identifier
            size (int):                 sprite scaling factor
            position (Tuple[int, int]): coordinates to be drawn on
            appearance (str):           path of the sprite's image
            image (Surface):            sprite's image
            sprite (Surface):           sprite

        Methods:
            init:   initialize the displayed object
            update: update based on associated simulated object's state

        Static methods:
            create_display: create a display object
    """
    def __init__(self,
                 dis_obj_id: int,
                 size: int,
                 position: Tuple[int, int],
                 appearance: str):
        """Constructor:
            Initialize a displayed object

        Args:
            dis_obj_id (int):           unique identifier
            size (int):                 sprite scaling factor
            position (Tuple[int, int]): coordinates to be drawn on
            appearance (str):           path of the sprite's image
        """

        self.__id: int = dis_obj_id                 # unique identifier
        self.size: int = size                       # sprite scaling factor
        self.position: Tuple[int, int] = position   # coordinates to be drawn on

        self.appearance: str = appearance           # path of the sprite's image
        self.image: pg.surface.Surface              # sprite's image
        self.sprite: pg.surface.Surface             # sprite

    def init(self, block_size: int, assets_path: str, assets: Dict[str, pg.Image]):
        """Public method:
            Initialize a displayed object,
            loading the apearrance'path to create a sprite

        Args:
            block_size (int):               size of block cells
            assets_path (str):              path of the assets' directory
            assets (Dict[str, pg.Image]):   cache of sprites
        """
        super().__init__()

        if assets.get(self.appearance, None):
            self.sprite = assets[self.appearance]

        else:
            self.sprite = pg.image.load(join(assets_path,
                                        self.appearance)).convert_alpha()

            assets[self.appearance] = self.sprite

        # Display the object on the world
        self.update(block_size=block_size)

    @staticmethod
    def create_display(sim_obj: SimulatedObject, block_size: int, assets_path: str,
                       assets: Dict[str, pg.Image]) -> DisplayedObject:
        """Constructor:
            Create a displayed object associated to a simulated object

        Args:
            sim_obj (SimulatedObject):      simulated object to associate with
            block_size (int):               size of block cells
            assets_path (str):              path of the assets' directory
            assets (Dict[str, pg.Image]):   cache of sprites

        Returns:
            DisplayedObject: created displayed object
        """
        # Create the displayed object
        dis_obj = DisplayedObject(dis_obj_id=sim_obj.id,
                                  appearance=sim_obj.appearance,
                                  size=sim_obj.size,
                                  position=sim_obj.position)

        # Load the sprite and display it on the world
        dis_obj.init(block_size=block_size,
                     assets_path=assets_path,
                     assets=assets)

        return dis_obj

    def update(self, block_size: int, sim_state: Optional[SimState]=None):
        """Public method:
            Update the displayed object based on new simulated object state

        Args:
            block_size (int):                           size of block cells
            sim_state (Optional[SimState], optional):   current state of the simulation. Defaults to None.
        """
        # Retrieve information from current simulation state
        if sim_state:
            entity = sim_state.entities[self.__id]
            self.size = entity.size
            self.position = entity.position

        # Scale the image based on object's size
        self.image: pg.surface.Surface = pg.transform.scale(self.sprite, (self.size, self.size))

        # Place the sprite on the object's position
        pos_x, pos_y = self.position
        self.rect: pg.rect.Rect = self.image.get_rect(
            center=(pos_x * block_size + block_size /2,
                    pos_y * block_size + block_size /2))


class Display:
    """Class:
        Display of the simulation

        Attributes:
            __id (int):                             unique identifier
            block_size (int):                       size of the block cells
            dimensions (Tuple[int, int]):           dimensions of the world
            window_width (int):                     width of the window
            window_height (int):                    height of the window
            tick_counter (int):                     handle the display update rate
            sim_speed (int):                        simulation update rate
            clock (pg.Clock):                       handle frame per second
            screen (pg.Screen):                     main pygame surface to draw on
            show_grid (bool):                       grid's lines must be displayed
            assets (Dict[str, pg.Image]):           cache of sprites
            entities (Dict[int, DisplayedObject]):  register of displayed entities
            resources (Dict[int, DisplayedObject]): register of displayed resources
            assets_path (str):                      directory of assets
            entity_group (Group):                   group of entites' sprite
            resource_group (Group):                 group of resources' sprite
    """
    def __init__(self,
                 display_id: int,
                 block_size: int,
                 dimensions: Tuple[int, int],
                 sim_speed: int=1,
                 show_grid: bool=False):
        """Constructor:
            Initialize a display associated with a simulation

        Args:
            display_id (int):               unique identifier
            block_size (int):               size of the block cells
            dimensions (Tuple[int, int]):   dimensions of the world
            sim_speed (int, optional):      simulation update rate. Defaults to 1.
            show_grid (bool, optional):     grid's lines must be displayed. Defaults to False.
        """

        self.__id = display_id                                  # unique identifier
        self.block_size: int = block_size                       # size of the block cells
        self.dimensions: Tuple[int, int] = dimensions           # dimensions of the world
        self.window_width: int = block_size * dimensions[0]     # width of the window
        self.window_height: int = block_size * dimensions[1]    # height of the window

        self.tick_counter = 0                                   # handle the display update rate
        self.sim_speed: int = sim_speed                         # simulation update rate
        self.clock: pg.Clock                                    # handle frame per second
        self.screen: pg.Screen                                  # main pygame surface to draw on
        self.show_grid: bool = show_grid                        # grid's lines must be displayed

        self.assets: Dict[str, pg.Image] = {}                   # cache of sprites
        self.entities: Dict[int, DisplayedObject] = {}          # register of displayed entities
        self.resources: Dict[int, DisplayedObject] = {}         # register of displayed resources

        self.assets_path = join(                                # directory of assets
            Path(
                dirname(
                    realpath(__file__))).parent.parent.absolute(),
            "assets/")

        self.entity_group: pg.sprite.Group = pg.sprite.Group()  # group of entites' sprite
        self.resource_group: pg.sprite.Group = pg.sprite.Group()# group of resources' sprite

    def init(self, sim_state: Optional[SimState]=None) -> None:
        """Public method:
            Initialize a display

        Args:
            sim_state (Optional[SimState], optional): current state of the simulation. Defaults to None.
        """
        pg.init()

        self.screen = pg.display.set_mode((self.window_width, self.window_height))

        # Add entities and resources
        # from the simulation to the display
        if sim_state:
            for entity in sim_state.get_entities():
                self._add_entity(entity)

            for resource in sim_state.get_resources():
                self._add_resource(resource)

        self.clock = pg.time.Clock()

    def _add_entity(self, entity: Entity) -> None:
        """Private method:
            Create a new entity and add it to the display

        Args:
            entity (Entity): simulated entity to create display for
        """
        dis_entity = DisplayedObject.create_display(block_size=self.block_size,
                                                    assets_path=self.assets_path,
                                                    sim_obj=entity,
                                                    assets=self.assets)

        self.entities[entity.id] = dis_entity
        self.entity_group.add(dis_entity)

    def _remove_entity(self, entity: Entity) -> None:
        """Private method:
            Remove an entity from the display

        Args:
            entity (Entity): entity to remove
        """
        dis_entity = self.entities.pop(entity.id)
        self.entity_group.remove(dis_entity)

    def _add_resource(self, resource: Resource) -> None:
        """Private method:
            Create a new resource and add it to the display

        Args:
            resource (Resource): simulated resource to create display for
        """
        dis_resource = DisplayedObject.create_display(block_size=self.block_size,
                                                      assets_path=self.assets_path,
                                                      sim_obj=resource,
                                                      assets=self.assets)

        self.resources[resource.id] = dis_resource
        self.resource_group.add(dis_resource)

    def _remove_resource(self, resource: Resource):
        """Private method:
            Remove an resource from the display

        Args:
            resource (Resource): resource to remove
        """
        dis_resource = self.resources.pop(resource.id)
        self.resource_group.remove(dis_resource)


    def update(self, sim_state: SimState) -> None:
        """Public method:
            update the display and its components

        Args:
            sim_state (SimState): current state of the simulation
        """
        # update present entities
        self.entity_group.update(block_size=self.block_size,
                                 sim_state=sim_state)

        # Add the missing entities
        for entity in sim_state.added_entities.values():
            self._add_entity(entity)

        # Remove the extra entities
        for entity in sim_state.removed_entities.values():
            self._remove_entity(entity)

        # Add the missing resources
        for resource in sim_state.added_resources.values():
            self._add_resource(resource)

        # Remove the extra resources
        for resource in sim_state.removed_resources.values():
            self._remove_resource(resource)


        # self.resource_group.update(block_size=self.block_size,
        #                            sim_state=sim_state)

    def draw(self, grid: Grid) -> None:
        """Public method:
            Draw the display

        Args:
            grid (Grid): grid of the world
        """
        # Quit on close window
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

        # Draw the world
        self._draw_world(grid)
        # Update display
        pg.display.update()

        self.clock.tick(self.sim_speed)
        self.tick_counter += 1
        if self.tick_counter == self.sim_speed:
            self.tick_counter = 0

    def _draw_world(self, grid: Grid) -> None:
        """Private method:
            Draw the world, grid and entities

            Args:
                grid (Grid): grid of the world
        """
        self._draw_grid(grid)
        self._draw_entities()
        self._draw_resources()

    def _draw_grid(self, grid) -> None:
        """Private method:
            Draw the grid

           Args:
                grid (Grid): grid of the world
        """
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

    def _draw_entities(self) -> None:
        """Private method:
            Draw the entities"""
        self.entity_group.draw(self.screen)

    def _draw_resources(self) -> None:
        """Private method:
            Draw the energies"""
        self.resource_group.draw(self.screen)


    @property
    def id(self) -> int:
        """Property
            Return the display's id

        Returns:
            int: display's id
        """
        return self.__id


