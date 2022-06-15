import os, sys, pytest
import numpy as np

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.grid import Grid, SubGrid
from project.src.simulation.entities import Animal, Tree, EntityType
from project.src.simulation.energies import BlueEnergy

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
        
        
    class TestGridMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
 
            self.grid = Grid(grid_id=0,
                                dimensions=(20,20))
            
            yield
            
                       
        def test_place_on_grid(self):
            position = (2,3)
            tree = Tree(position=position)
            assert not self.grid.entity_grid.get_cell_value(coordinates=position)
            self.grid.place_on_entity(element=tree)
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            
            energy = BlueEnergy(energy_id=0,
                                position=position)
            
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            self.grid.place_on_resource(element=energy)
            assert self.grid.resource_grid.get_cell_value(coordinates=position)
        
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
            
            self.animal = Animal(position=(2,5))    
            
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
            
        def test_cell_out_of_bounds_handled(self):
            array = np.zeros(self.grid.dimensions, dtype=int)
            pos_1 = (20,0)
            pos_2 = (0,25)
            pos_3 = (-1,0)
            pos_4 = (0,-1)
            
            with pytest.raises(IndexError):
                array[pos_1]
            try:
                self.entity_grid.set_cell_value(coordinates=pos_1, value=1)
            except IndexError:
                pytest.fail("Unexpected IndexError")
            
            with pytest.raises(IndexError):
                array[pos_2]
            try:
                self.entity_grid.set_cell_value(coordinates=pos_2, value=1)
            except IndexError:
                pytest.fail("Unexpected IndexError")
                        
            assert not self.entity_grid.get_cell_value(coordinates=pos_1)
            assert not self.entity_grid.get_cell_value(coordinates=pos_2)
            assert not self.entity_grid.get_cell_value(coordinates=pos_3)
            assert not self.entity_grid.get_cell_value(coordinates=pos_4)
          
        def test_get_cell(self):
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None 
            
            self.entity_grid.set_cell_value(coordinates=(2,5),
                                            value=self.animal)
            
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == self.animal
            
        
        def test_are_coordinates_in_bounds(self):
            pos_1 = (20,0)
            pos_2 = (0,25)
            pos_3 = (-1,0)
            pos_4 = (0,-1)
            
            assert not self.entity_grid.are_coordinates_in_bounds(coordinates=pos_1)
            assert not self.entity_grid.are_coordinates_in_bounds(coordinates=pos_2)
            assert not self.entity_grid.are_coordinates_in_bounds(coordinates=pos_3)
            assert not self.entity_grid.are_coordinates_in_bounds(coordinates=pos_4)
            
            pos_5 = (10,0)
            pos_6 = (0,15)
            pos_7 = (3,0)
            pos_8 = (0,4)
            
            assert self.entity_grid.are_coordinates_in_bounds(coordinates=pos_5)
            assert self.entity_grid.are_coordinates_in_bounds(coordinates=pos_6)
            assert self.entity_grid.are_coordinates_in_bounds(coordinates=pos_7)
            assert self.entity_grid.are_coordinates_in_bounds(coordinates=pos_8)
            
        def test_are_vacant_coordinates(self):
            # Free cell
            free = self.entity_grid.are_vacant_coordinates(coordinates=(12,15))
            
            assert free
            
            # Occupied cell
            self.entity_grid.set_cell_value(coordinates=(12,15),
                                            value=self.animal)
            
            free = self.entity_grid.are_vacant_coordinates(coordinates=(12,15))
            
            assert not free
            
        def test_find_coordinates_with_class(self):
            tree1 = self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(1,1))
            
            assert len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                                     target_class=Tree)) == 1
            
            tree2 = self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(2,1))
            
            len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                              target_class=Tree))  == 2
            
            
            
            # Does not detect animal
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value,
                                             position=(1,2))
            
            len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                              target_class=Tree))  == 2
            
        
        def test_find_free_coordinates(self):
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 9
            
            self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(1,1))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 8
            
            self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(0,1))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 7
            
            self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(0,0))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 6
            
            # Out of search range, no change
            self.grid.create_entity(entity_type=EntityType.Tree.value,
                                            position=(3,3))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 6
        
        def test_select_free_coordinates(self):
            cells = []
            position = self.animal.position()
            radius = 1
            for x in range(-radius,radius+1):
                for y in range(-radius,radius+1):
                    cells.append(tuple(np.add(position,(x,y))))
            
            for _ in range(100):
                free_cell = self.entity_grid.select_free_coordinates(position=position,
                                                                    radius=radius)
                assert free_cell in cells
                
            position = (3,5)
            self.animal.position = position
            radius = 2
            cells = []
            for x in range(-radius,radius+1):
                for y in range(-radius,radius+1):
                    cells.append(tuple(np.add(position,(x,y))))
            
            for _ in range(100):
                free_cell = self.entity_grid.select_free_coordinates(position=position,
                                                                    radius=radius)
                assert free_cell 
                assert free_cell in cells
                
        
        