import pytest
import sys, os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world

class TestGrid:
    def setup_class(self):
        self.grid = world.Grid()      
        
    def test_creation_grid(self):
        assert self.grid
        assert type(self.grid) == world.Grid
        
    def test_dimensions_grid(self):
        grid = world.Grid(width=5, height=10)
        assert grid._width == 5
        assert grid._height == 10
        assert grid.dimensions == (5,10)
        
    def test_update_cell(self):
        assert self.grid.get_position_value(position=(5,5)) == 0
        self.grid.update_grid_cell_value(position=(5,5), value=1)
        assert self.grid.get_position_value(position=(5,5)) == 1
        self.grid.update_grid_cell_value(position=(5,5), value=0)
        assert self.grid.get_position_value(position=(5,5)) == 0
        
    