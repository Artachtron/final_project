import os, sys, pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.grid import Grid, SubGrid

class TestGrid:
    def test_create_grid(self):
        grid = Grid(grid_id=0,
                    dimensions=(20,20))
        
        assert type(grid) == Grid
        
    def test_grid_fields(self):
        grid = Grid(grid_id=0,
                    dimensions=(20,20),
                    block_size=20)
        
        assert {'id', 'dimensions', 'BLOCK_SIZE',
                '_resource_grid', '_entity_grid',
                '_color_grid'}.issubset(vars(grid))
        
        assert grid.id == 0
        assert grid.dimensions == (20,20)
        assert grid.BLOCK_SIZE == 20
        
class TestSubGrid:
    def test_create_subgrid(self):
        subgrid = SubGrid(dimensions=(20,20),
                          data_type=SubGrid,
                          initial_value=None)
        
        assert type(subgrid) == SubGrid
        
    def test_subgrid_fields(self):
        subgrid = SubGrid(dimensions=(20,20),
                          data_type=SubGrid,
                          initial_value=None)
        
        {'dimensions', 'data_type', 'initial_value', 'array'}.issubset(vars(subgrid))
        
        assert subgrid.dimensions == (20,20)
        assert subgrid.data_type == SubGrid
        assert subgrid.initial_value == None
        
    class TestSubGridMethods:
        pass