import os, sys, pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.entities import Animal, Entity, Tree, Direction
from project.src.simulation.energies import EnergyType
from project.src.simulation.grid import Grid

class TestEntity:
    def test_create_entity(self):
        entity = Entity(position=(20,20))
        
        assert type(entity) == Entity
        
    def test_entity_fields(self):
        entity = Entity(position=(20,10),
                        entity_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27)
        
        assert {'id', 'position', '_adult_size', '_age',
                '_max_age', 'size', '_action_cost', 'is_adult',
                '_energies_stock'}.issubset(vars(entity))
        
        assert entity.id == 3
        assert entity.position.vect == (20,10)
        assert entity._adult_size == 15
        assert entity._max_age == 100
        assert entity._age == 0
        assert entity.size == 13
        assert entity._action_cost == 1
        assert entity._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert entity.is_adult == False
        
    class TestEntityMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.entity = Entity(position=(20,10),
                                entity_id=3,
                                adult_size=15,
                                max_age=100,
                                size=13,
                                action_cost=1,
                                blue_energy=1000,
                                red_energy=2000)
            
            yield
            
            self.entity = None
          
        def test_increase_age(self):
            assert self.entity._age == 0
            self.entity._increase_age()
            assert self.entity._age == 1 
            
        def test_grow(self):
            assert self.entity.size == 13
            self.entity._grow()
            assert self.entity.size == 14
            
        def test_reached_adulthood(self):
            for _ in range(10):
                if self.entity.size < self.entity._adult_size:
                    assert not self.entity.is_adult
                else:
                    assert self.entity.is_adult

                self.entity._grow()
                    
            assert self.entity.is_adult
        
        def test_gain_energy(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000
            
            # Add Blue energy
            self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                     quantity=3) 
            assert self.entity.blue_energy == 1003
            assert self.entity.red_energy == 2000
            
            # Add Red energy
            self.entity._gain_energy(energy_type=EnergyType.RED,
                                     quantity=23) 
            assert self.entity.blue_energy == 1003
            assert self.entity.red_energy == 2023
            
             # ValueError if negative
            with pytest.raises(ValueError):
                self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                         quantity=-5)      
           
        def test_loose_energy(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000
            
            # Add Blue energy
            quantity = self.entity._loose_energy(energy_type=EnergyType.BLUE,
                                                 quantity=3) 
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 2000
            assert quantity == 3
            
            # Add Red energy
            quantity =self.entity._loose_energy(energy_type=EnergyType.RED,
                                                quantity=23) 
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 2000 - 23 
            assert quantity == 23
            
            # Energy stock should be 0 if loose more than pocessed
            quantity = self.entity._loose_energy(energy_type=EnergyType.RED,
                                                 quantity=2300) 
            assert self.entity.blue_energy == 997
            assert self.entity.red_energy == 0
            assert quantity == 2000 - 23
            
             # ValueError if negative
            with pytest.raises(ValueError):
                self.entity._gain_energy(energy_type=EnergyType.BLUE,
                                         quantity=-5)
                
        def test_perform_action(self):
            #Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000
            
            self.entity._perform_action()
            assert self.entity.blue_energy == 1000 - self.entity._action_cost    
            
        def test_can_perform_action(self):
            # Initial values
            assert self.entity.blue_energy == 1000
            assert self.entity.red_energy == 2000
            
            #Can perform action
            can = self.entity._can_perform_action(energy_type=EnergyType.RED,
                                                  quantity=2)
            assert can == True
            assert self.entity.red_energy == 1998
             
            # Cannot perform action  
            can = self.entity._can_perform_action(energy_type=EnergyType.RED,
                                                    quantity=3000)
            assert can == False
            assert self.entity.red_energy == 1998
         
        class TestEntityGridMethods:
            @pytest.fixture(autouse=True)
            def setup(self):
                self.grid = Grid(grid_id=0,
                                 dimensions=(20,20))
                self.entity_grid = self.grid.entity_grid
                
                self.entity = self.grid.create_entity(size=1,
                                                    position=(0,0),
                                                    blue_energy=5,
                                                    red_energy=10,
                                                    entity_type="animal")
                yield
            
            def test_drop_energy(self):

                assert self.entity.energies == {"blue energy": 5, "red energy": 10}
                assert self.entity.blue_energy == 5
                self.entity._action_cost = 0
                
                # Drop blue energy
                blue_cell = (1,1)
                assert self.grid.resource_grid.get_cell_value(coordinates=blue_cell) == None
                self.entity._drop_energy(grid=self.grid,
                                         energy_type=EnergyType.BLUE,
                                        quantity=1,
                                        coordinates=blue_cell)
                assert self.entity.energies == {"blue energy": 4, "red energy": 10}
                assert self.entity.blue_energy == 4
                blue_energy = self.grid.resource_grid.get_cell_value(coordinates=blue_cell)
                assert blue_energy != None
                assert type(blue_energy).__name__ == 'BlueEnergy'
                assert blue_energy.quantity == 1
                
                # Drop red energy
                red_cell = (3,2)
                assert self.grid.resource_grid.get_cell_value(coordinates=red_cell) == None
                assert self.entity.red_energy == 10
                self.entity._drop_energy(grid=self.grid,
                                         energy_type=EnergyType.RED,
                                        quantity=3,
                                        coordinates=red_cell)
                
                assert self.entity.energies == {"blue energy": 4, "red energy": 7}
                assert self.entity.red_energy == 7
                red_energy = self.grid.resource_grid.get_cell_value(coordinates=red_cell)
                assert red_energy != None
                assert type(red_energy).__name__ == 'RedEnergy'
                assert red_energy.quantity == 3
                
                # Drop energy on occupied cell
                self.entity._drop_energy(grid=self.grid,
                                         energy_type=EnergyType.BLUE,
                                        quantity=1,
                                        coordinates=red_cell)
                assert self.entity.energies == {"blue energy": 4, "red energy": 7}
                assert self.entity.blue_energy == 4
                red_energy2 = self.grid.resource_grid.get_cell_value(coordinates=red_cell)
                assert red_energy2 != None
                assert type(red_energy2).__name__ == 'RedEnergy' 
                assert red_energy.quantity == 3
                
                # Drop too much energy
                red_cell2 = (3,3)
                assert self.grid.resource_grid.get_cell_value(coordinates=red_cell2) == None
                assert self.entity.red_energy == 7
                self.entity._drop_energy(grid=self.grid,
                                         energy_type=EnergyType.RED,
                                        quantity=10,
                                        coordinates=red_cell2)
                
                assert self.entity.energies == {"blue energy": 4, "red energy": 0}
                assert self.entity.red_energy == 0
                red_energy2 = self.grid.resource_grid.get_cell_value(coordinates=red_cell2)
                assert red_energy2.quantity == 7
            
class TestTree:
    def test_create_tree(self):
        tree = Tree(position=(20,20)) 
        
        assert type(tree) == Tree
        assert tree.__class__.__base__ == Entity     
        
    def test_tree_fields(self):
        tree = Tree(position=(20,10),
                        tree_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27,
                        production_type=EnergyType.BLUE) 
        
        assert {'id', 'position', '_adult_size', '_age',
                '_max_age', 'size', '_action_cost', 'is_adult',
                '_energies_stock', '_production_type'}.issubset(vars(tree))
        
        assert tree.id == 3
        assert tree.position.vect == (20,10)
        assert tree._adult_size == 15
        assert tree._max_age == 100
        assert tree._age == 0
        assert tree.size == 13
        assert tree._action_cost == 1
        assert tree._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert tree.is_adult == False
        assert tree._production_type == EnergyType.BLUE
        
    class TestTreeMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.tree1 = Tree(position=(20,10),
                                tree_id=3,
                                adult_size=15,
                                max_age=100,
                                size=13,
                                action_cost=1,
                                blue_energy=1000,
                                red_energy=2000,
                                production_type=EnergyType.RED)
            
            self.tree1 = Tree(position=(20,11),
                                tree_id=3,
                                adult_size=15,
                                max_age=100,
                                size=13,
                                action_cost=1,
                                blue_energy=1000,
                                red_energy=2000,
                                production_type=EnergyType.BLUE)
            
            yield
            
            self.tree = None
            
            
        def test_produce_energy(self):
           pass 

class TestAnimal:
    def test_create_animal(self):
        animal = Animal(position=(20,20))
        
        assert type(animal) == Animal
        assert animal.__class__.__base__ == Entity
        
    def test_animal_fields(self):
        animal = Animal(position=(20,10),
                        animal_id=3,
                        adult_size=15,
                        max_age=100,
                        size=13,
                        action_cost=1,
                        blue_energy=12,
                        red_energy=27)
        
        assert {'id', 'position', '_adult_size', '_age',
                '_max_age', 'size', '_action_cost', 'is_adult',
                '_energies_stock', '_pocket'}.issubset(vars(animal))
        
        assert animal.id == 3
        assert animal.position.vect.vect == (20,10)
        assert animal._adult_size == 15
        assert animal._max_age == 100
        assert animal._age == 0
        assert animal.size == 13
        assert animal._action_cost == 1
        assert animal._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert animal.is_adult == False
        assert animal._pocket == None
        
    class TestAnimalMethods:
            @pytest.fixture(autouse=True)
            def setup(self):
                self.animal = Animal(position=(3,3),
                                    animal_id=3,
                                    adult_size=15,
                                    max_age=100,
                                    size=13,
                                    action_cost=1,
                                    blue_energy=12,
                                    red_energy=27)
                
                """ self.entity_grid = SubGrid(dimensions=(20,20),
                                       data_type=Entity,
                                       initial_value=None) """
                
                self.grid = Grid(grid_id=0,
                                 dimensions=(20,20))
                
                self.entity_grid = self.grid.entity_grid
                
                yield
                
                self.entity = None
                
            def test_available_coordinates(self):
                # Free cell
                free = self.animal._is_available_coordinates(coordinates=(12,15),
                                                             subgrid=self.entity_grid)
                
                assert free
                
                # Occupied cell
                self.entity_grid.set_cell_value(coordinates=(12,15),
                                            value=self.animal)
                
                free = self.animal._is_available_coordinates(coordinates=(12,15),
                                                             subgrid=self.entity_grid)
                
                assert not free
                
            def test_move(self):
                animal = self.animal
              
                # Down
                assert animal.position.vect.vect == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == None
                animal._move(Direction.DOWN,
                             grid=self.grid)
                assert animal.position.vect.vect == (3,4)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
                
                # Up
                animal._move(Direction.UP,
                             grid=self.grid)
                assert animal.position.vect.vect == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(2,3)) == None
                
                # Left
                animal._move(Direction.LEFT,
                             grid=self.grid)
                assert animal.position.vect.vect == (2,3)
                assert self.entity_grid.get_cell_value(coordinates=(2,3)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
                
                # Right
                animal._move(Direction.RIGHT,
                             grid=self.grid)
                assert animal.position.vect.vect == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
                
            def test_move_occupied_cell(self):
                animal = Animal(position=(3,3))
                animal2 = Animal(position=(3,4))
                self.entity_grid.set_cell_value(coordinates=(3,4),
                                                value=animal2)
                
                # Move on already occupied cell
                assert animal.position.vect == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
                assert animal2.position.vect == (3,4)
                animal._move(Direction.DOWN, 
                             grid=self.grid)
                assert animal.position.vect == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
                assert animal2.position.vect == (3,4)
                
            def test_move_out_of_bounds_cell(self):
                animal = Animal(position=(0,0))
                self.entity_grid.set_cell_value(coordinates=(0,0),
                                                value=animal)
                # Left
                assert animal.position.vect == (0,0)
                assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
                animal._move(Direction.LEFT, 
                             grid=self.grid)
                assert animal.position.vect == (0,0)
                assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
                
                # Up
                animal._move(Direction.UP, 
                             grid=self.grid)
                assert animal.position.vect == (0,0)
                assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
                
                # Right
                animal2 = Animal(position=(19,19))
                self.entity_grid.set_cell_value(coordinates=(19,19),
                                                value=animal2)
                assert animal2.position.vect == (19,19)
                assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
                animal2._move(Direction.RIGHT, 
                             grid=self.grid)
                assert animal2.position.vect == (19,19)
                assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
                
                #Down
                animal2._move(Direction.DOWN, 
                             grid=self.grid)
                assert animal2.position.vect == (19,19)
                assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
        
            

        
        