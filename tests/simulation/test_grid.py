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
        
        assert {'dimensions', 'BLOCK_SIZE',
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
        @pytest.fixture(autouse=True)
        def setup(self):
            self.grid = Grid(grid_id=0,
                             dimensions=(20,25))
            self.entity_grid = self.grid.entity_grid
            self.energy_grid = self.grid.resource_grid     
            
        def test_creation_grid(self):
            assert self.grid
            assert type(self.grid) == Grid
            
        def test_dimensions_grid(self):
            assert self.grid.width == 20
            assert self.grid.height == 25
            assert self.grid.dimensions == (20,25)
            
        def test_set_cell(self):
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None
            self.entity_grid.set_cell_value(coordinates=(2,5), value=1)
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == 1
            self.entity_grid.set_cell_value(coordinates=(2,5), value=None)
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None
            
            assert self.energy_grid.get_cell_value(coordinates=(2,5)) == None
            self.energy_grid.set_cell_value(coordinates=(2,5), value=1)
            assert self.energy_grid.get_cell_value(coordinates=(2,5)) == 1
            self.energy_grid.set_cell_value(coordinates=(2,5), value=None)
            assert self.energy_grid.get_cell_value(coordinates=(2,5)) == None