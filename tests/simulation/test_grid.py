import os, sys, pytest
import numpy as np

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.grid import Grid, SubGrid
from project.src.simulation.entities import Animal, Tree, Entity
from project.src.simulation.energies import BlueEnergy, RedEnergy, Energy, Resource, EnergyType
from project.src.simulation.simulation import Environment

class TestGrid:
    def test_create_grid(self):
        grid = Grid(grid_id=0,
                    dimensions=(20,20))
        
        assert type(grid) == Grid
        
    def test_grid_fields(self):
        grid = Grid(grid_id=0,
                    dimensions=(20,20))
        
        assert {'dimensions','_resource_grid',
                '_entity_grid', '_color_grid'}.issubset(vars(grid))
        
        assert grid.id == 0
        assert grid.dimensions == (20,20)
         
        
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
            self.grid.place_entity(value=tree)
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            
            energy = BlueEnergy(energy_id=0,
                                position=position)
            
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            self.grid.place_resource(value=energy)
            assert self.grid.resource_grid.get_cell_value(coordinates=position)
            
        def test_is_subclass(self):
            animal = Animal(position=(1,1))
            tree = Tree(position=(2,2))
            blue_energy = BlueEnergy(position=(1,1))
            red_energy = RedEnergy(position=(2,2))
            
            # Animal
            assert self.grid.is_subclass(derived=animal,
                                         base_class=Animal)
            
            assert self.grid.is_subclass(derived=animal,
                                         base_class=Entity)
            
            assert not self.grid.is_subclass(derived=animal,
                                             base_class=Tree)
            
            assert not self.grid.is_subclass(derived=animal,
                                             base_class=Energy)
            
            # Tree
            assert self.grid.is_subclass(derived=tree,
                                         base_class=Tree)
            
            assert self.grid.is_subclass(derived=tree,
                                         base_class=Entity)
            
            assert not self.grid.is_subclass(derived=tree,
                                             base_class=Animal)
            
            assert not self.grid.is_subclass(derived=tree,
                                             base_class=Energy)
            
            # Blue Energy
            assert self.grid.is_subclass(derived=blue_energy,
                                         base_class=BlueEnergy)
            
            assert self.grid.is_subclass(derived=blue_energy,
                                         base_class=Energy)
            
            assert self.grid.is_subclass(derived=blue_energy,
                                         base_class=Resource)
            
            assert not self.grid.is_subclass(derived=blue_energy,
                                             base_class=Entity)
            
            assert not self.grid.is_subclass(derived=blue_energy,
                                             base_class=RedEnergy)
            
            # Red Energy
            assert self.grid.is_subclass(derived=red_energy,
                                         base_class=RedEnergy)
            
            assert self.grid.is_subclass(derived=red_energy,
                                         base_class=Energy)
            
            assert self.grid.is_subclass(derived=red_energy,
                                         base_class=Resource)
            
            assert not self.grid.is_subclass(derived=red_energy,
                                             base_class=Entity)
            
            assert not self.grid.is_subclass(derived=red_energy,
                                             base_class=BlueEnergy)
        
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
            self.env = Environment(env_id=0)
            self.grid =  self.env.grid
            
            self.entity_grid = self.grid.entity_grid
            self.energy_grid = self.grid.resource_grid 
            
            self.animal = Animal(position=(2,5))    
            
        def test_creation_grid(self):
            assert self.grid
            assert self.grid.__class__.__name__ == 'Grid'
            
        def test_dimensions_grid(self):
            assert self.grid.width == 20
            assert self.grid.height == 20
            assert self.grid.dimensions == (20,20)
            
        def test_empty_cell(self):
            animal = Animal(animal_id=0,
                            position=(2,5))
            self.grid.place_entity(animal)
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == animal
            self.entity_grid._empty_cell(coordinates=(2,5))
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None
        
        def test_set_cell(self):
            animal = Animal(animal_id=0,
                            position=(2,5))
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None
            self.entity_grid._set_cell_value(coordinates=(2,5), value=animal)
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == animal
            self.entity_grid._empty_cell(coordinates=(2,5))
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None
            
            energy = BlueEnergy(energy_id=0,
                                position=(2,5))
            
            assert self.energy_grid.get_cell_value(coordinates=(2,5)) == None
            self.energy_grid._set_cell_value(coordinates=(2,5), value=energy)
            assert self.energy_grid.get_cell_value(coordinates=(2,5)) == energy
            self.energy_grid._empty_cell(coordinates=(2,5))
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
                self.entity_grid._set_cell_value(coordinates=pos_1, value=1)
            except IndexError:
                pytest.fail("Unexpected IndexError")
            
            with pytest.raises(IndexError):
                array[pos_2]
            try:
                self.entity_grid._set_cell_value(coordinates=pos_2, value=1)
            except IndexError:
                pytest.fail("Unexpected IndexError")
                        
            assert not self.entity_grid.get_cell_value(coordinates=pos_1)
            assert not self.entity_grid.get_cell_value(coordinates=pos_2)
            assert not self.entity_grid.get_cell_value(coordinates=pos_3)
            assert not self.entity_grid.get_cell_value(coordinates=pos_4)
          
        def test_get_cell(self):
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == None 
            
            self.entity_grid._set_cell_value(coordinates=(2,5),
                                            value=self.animal)
            
            assert self.entity_grid.get_cell_value(coordinates=(2,5)) == self.animal
            
        
        def test_are_coordinates_in_bounds(self):
            pos_1 = (20,0)
            pos_2 = (0,25)
            pos_3 = (-1,0)
            pos_4 = (0,-1)
            
            assert not self.entity_grid._are_coordinates_in_bounds(coordinates=pos_1)
            assert not self.entity_grid._are_coordinates_in_bounds(coordinates=pos_2)
            assert not self.entity_grid._are_coordinates_in_bounds(coordinates=pos_3)
            assert not self.entity_grid._are_coordinates_in_bounds(coordinates=pos_4)
            
            pos_5 = (10,0)
            pos_6 = (0,15)
            pos_7 = (3,0)
            pos_8 = (0,4)
            
            assert self.entity_grid._are_coordinates_in_bounds(coordinates=pos_5)
            assert self.entity_grid._are_coordinates_in_bounds(coordinates=pos_6)
            assert self.entity_grid._are_coordinates_in_bounds(coordinates=pos_7)
            assert self.entity_grid._are_coordinates_in_bounds(coordinates=pos_8)
            
        def test_are_vacant_coordinates(self):
            # Free cell
            free = self.entity_grid.are_vacant_coordinates(coordinates=(12,15))
            
            assert free
            
            # Occupied cell
            self.entity_grid._set_cell_value(coordinates=(12,15),
                                            value=self.animal)
            
            free = self.entity_grid.are_vacant_coordinates(coordinates=(12,15))
            
            assert not free
            
        def test_is_data_valid(self):       
            assert not self.grid.resource_grid._set_cell_value(coordinates=(2,5),
                                                               value=self.animal)
            
            assert self.grid.entity_grid._set_cell_value(coordinates=(2,5),
                                                         value=self.animal)
            
        def test_find_coordinates_with_class(self):
            tree1 = self.env.create_tree(coordinates=(1,1))
            
            assert len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                                     target_class=Tree)) == 1
            
            tree2 = self.env.create_tree(coordinates=(2,1))
            
            len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                              target_class=Tree))  == 2
            
            
            
            # Does not detect animal
            animal = self.env.create_animal(coordinates=(1,2))
            
            len(self.entity_grid._find_coordinates_with_class(position=(1,1),
                                                              target_class=Tree))  == 2
            
        
        def test_find_free_coordinates(self):
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 9
            
            self.env.create_tree(coordinates=(1,1))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 8
            
            self.env.create_tree(coordinates=(0,1))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 7
            
            self.env.create_tree(coordinates=(0,0))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 6
            
            # Out of search range, no change
            self.env.create_tree(coordinates=(3,3))
            
            assert len(self.entity_grid.find_free_coordinates(position=(1,1))) == 6
        
        def test_select_free_coordinates(self):
            cells = []
            position = self.animal.position
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
                
            # Multiple free cells
            free_cells = self.entity_grid.select_free_coordinates(position=position,
                                                                  radius=radius,
                                                                  num_cells=2)
            
            assert len(free_cells) == 2
            
            free_cells = self.entity_grid.select_free_coordinates(position=position,
                                                                  radius=radius,
                                                                  num_cells=3)
            
            assert len(free_cells) == 3
            
        def test_update_cell(self):
            self.grid.place_entity(value=self.animal)
            position = self.animal.position
            assert self.grid.entity_grid.get_cell_value(coordinates=position) == self.animal
            assert not self.grid.entity_grid.get_cell_value(coordinates=(5,5))
            
            new_position = (5,5)
            self.grid.entity_grid.update_cell(new_coordinates=new_position,
                                              value=self.animal)
                
            assert self.grid.entity_grid.get_cell_value(coordinates=new_position) == self.animal
            assert not self.grid.entity_grid.get_cell_value(coordinates=(3,5))
            
        def test_sub_region(self):
            grid = Grid(grid_id=0,
                        dimensions=(5,10))
            
            positions = [(1,2), (4,2), (3,7), (0,3)]
            for pos in positions:
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                        quantity=10,
                                        coordinates=pos)
                
            def not_none(arr):
                return sum(x is not None for x in arr)
            
            for i in range(1,4):
                subregion = self.grid.resource_grid.get_sub_region(initial_pos=(3,3),
                                                                    radius=i).flatten()
                
                assert not_none(subregion) == i
        
        