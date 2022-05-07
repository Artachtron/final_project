import pytest
import sys, os
import numpy as np
import pygame as pg


sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world

class TestGrid:
    def setup_class(self):
        self.grid = world.Grid(width=5, height=10)      
        
    def test_creation_grid(self):
        assert self.grid
        assert type(self.grid) == world.Grid
        
    def test_dimensions_grid(self):
        assert self.grid._width == 5
        assert self.grid._height == 10
        assert self.grid.dimensions == (5,10)
        
    def test_update_cell(self):
        assert self.grid.get_position_value(position=(2,5)) == 0
        self.grid.update_grid_cell_value(position=(2,5), value=1)
        assert self.grid.get_position_value(position=(2,5)) == 1
        self.grid.update_grid_cell_value(position=(2,5), value=0)
        assert self.grid.get_position_value(position=(2,5)) == 0
        
    def test_cell_out_of_bounds_handled(self):
        array = np.zeros(self.grid.dimensions, dtype=int)
        pos_1 = (5,0)
        pos_2 = (0,11)
        
        with pytest.raises(IndexError):
            array[pos_1]
        try:
            self.grid.update_grid_cell_value(position=pos_1, value=1)
        except IndexError:
            pytest.fail("Unexpected IndexError")
        
        with pytest.raises(IndexError):
            array[pos_2]
        try:
            self.grid.update_grid_cell_value(position=pos_2, value=1)
        except IndexError:
            pytest.fail("Unexpected IndexError")
                
        assert self.grid.get_position_value(position=pos_1) == None
        assert self.grid.get_position_value(position=pos_2) == None
        
class TestWorld:
    
    def setup_class(self):
        world.init_pygame()
        
    def test_initialization_pygame(self):
        assert world.CLOCK
        assert type(world.CLOCK) == type(pg.time.Clock())
        assert world.SCREEN
        assert type(world.SCREEN) == pg.Surface
    
    def test_initialization_population(self):
        grid = world.Grid(height=10,width=10)
        world.init_population(grid=grid, counts=(3, 2))
        
        assert world.animal_group
        assert world.tree_group
        
        assert len(world.animal_group) == 3
        assert len(world.tree_group) == 2