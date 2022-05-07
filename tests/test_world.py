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
        
