import pygame as pg
import sys

from typing import Final

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SIMULATION_SPEED: Final[int] = 20


GRID_HEIGHT: Final[int] = 20
GRID_WIDTH: Final[int] = 20
BLOCK_SIZE: Final[int] = 20

WINDOW_HEIGHT: Final[int] = BLOCK_SIZE * GRID_HEIGHT
WINDOW_WIDTH: Final[int] = BLOCK_SIZE * GRID_WIDTH

def init_pygame() -> None:
    """Initialize pygame"""
    global SCREEN, CLOCK
    global tick_counter
    
    tick_counter = 0
    
    pg.init()
    
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
    
def main() -> None:
    
    for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
    
    draw_world()
    pg.display.update()
    CLOCK.tick(60)
    tick_counter += 1
    if tick_counter == SIMULATION_SPEED:
        tick_counter = 0

def draw_world() -> None:
    """Draw the world, grid and entities"""
    draw_grid()
    draw_entities()
    draw_energies()
    
def draw_grid() -> None:
    """Draw the grid"""
    #SCREEN.fill(WHITE)
    color_grid = grid.color_grid.subgrid
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pg.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pg.draw.rect(SCREEN, color_grid[int(x/BLOCK_SIZE),int(y/BLOCK_SIZE)], rect, 0)
            pg.draw.rect(SCREEN, BLACK, rect, 1)
            
def draw_entities() -> None:
    """Draw the entities"""
    grid.entity_group.draw(SCREEN)

def draw_energies() -> None:
    """Draw the energies"""
    grid.energy_group.draw(SCREEN)
    
def update_world() -> None:
    """Update the world"""
    if tick_counter == 0:
        update_entities()

def update_entities() -> None:
    """Update the entities"""
    grid.entity_group.update()
    
class EntitySprite(pg.sprite.Sprite):
    def __init__(self,
                image_filename: str):
        image: pg.Surface = pg.image.load(join(assets_path,
                                            image_filename)).convert_alpha()
        self.size: int = size
        self.image: pg.Surface = pg.transform.scale(image, (size, size))
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x *grid.BLOCK_SIZE + grid.BLOCK_SIZE /2,
                pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE /2))
        
class SeedSprite(EntitySprite):
    def __init__(self):
        super(SeedSprite, self).__init__(image_filename="Seed.png",
                                        size=size,
                                        position=position)
        
class AnimalSprite(EntitySprite):
    def __init__(self):
        super(AnimalSprite,self).__init__(image_filename='Animal.png')
        
class TreeSprite(EntitySprite):
    def __init__(self, *args, **kwargs):
        super(TreeSprite, self).__init__(image_filename='Plant.png')