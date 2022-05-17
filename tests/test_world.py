import pytest
import sys, os
import numpy as np
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world

class TestGrid:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        self.energy_grid = self.grid.resource_grid     
        
    def test_creation_grid(self):
        assert self.grid
        assert type(self.grid) == world.Grid
        
    def test_dimensions_grid(self):
        assert self.grid._width == 5
        assert self.grid._height == 10
        assert self.grid.dimensions == (5,10)
        
    def test_update_cell(self):
        assert self.entity_grid.get_cell_value(cell_coordinates=(2,5)) == None
        self.entity_grid.set_cell_value(cell_coordinates=(2,5), value=1)
        assert self.entity_grid.get_cell_value(cell_coordinates=(2,5)) == 1
        self.entity_grid.set_cell_value(cell_coordinates=(2,5), value=None)
        assert self.entity_grid.get_cell_value(cell_coordinates=(2,5)) == None
        
        assert self.energy_grid.get_cell_value(cell_coordinates=(2,5)) == None
        self.energy_grid.set_cell_value(cell_coordinates=(2,5), value=1)
        assert self.energy_grid.get_cell_value(cell_coordinates=(2,5)) == 1
        self.energy_grid.set_cell_value(cell_coordinates=(2,5), value=None)
        assert self.energy_grid.get_cell_value(cell_coordinates=(2,5)) == None
        
    def test_cell_out_of_bounds_handled(self):
        array = np.zeros(self.grid.dimensions, dtype=int)
        pos_1 = (5,0)
        pos_2 = (0,11)
        pos_3 = (-1,0)
        pos_4 = (0,-1)
        
        with pytest.raises(IndexError):
            array[pos_1]
        try:
            self.entity_grid.set_cell_value(cell_coordinates=pos_1, value=1)
        except IndexError:
            pytest.fail("Unexpected IndexError")
        
        with pytest.raises(IndexError):
            array[pos_2]
        try:
            self.entity_grid.set_cell_value(cell_coordinates=pos_2, value=1)
        except IndexError:
            pytest.fail("Unexpected IndexError")
                    
        assert not self.entity_grid.get_cell_value(cell_coordinates=pos_1)
        assert not self.entity_grid.get_cell_value(cell_coordinates=pos_2)
        assert not self.entity_grid.get_cell_value(cell_coordinates=pos_3)
        assert not self.entity_grid.get_cell_value(cell_coordinates=pos_4)
        
        
class TestWorld:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        world.init_pygame()
        yield
        
    def test_initialization_pygame(self):
        assert world.CLOCK
        assert type(world.CLOCK) == type(pg.time.Clock())
        assert world.SCREEN
        assert type(world.SCREEN) == pg.Surface
    
    # def test_initialization_worlds(self):
    
    def test_initialization_population(self):
        world.init_grid()
        world.init_population(counts=(3, 2))
        
        assert world.grid
                
        assert len(world.grid.entity_group) == 3 + 2
     
    #def test_world_update(self):
        
    def test_entities_update(self):
        world.init_grid()
        world.init_population(counts=(1,0))
        
        before_update_position = world.grid.entity_group.sprites()[0].position
        world.update_entities()
        world.update_entities()
        world.update_entities()
        after_update_position = world.grid.entity_group.sprites()[0].position
                
        assert before_update_position != after_update_position
    
    def test_world_drawing(self):
        world.init_grid()
        world.init_population(counts=(3,2))
        world.init_energies()
        
        world.draw_world()