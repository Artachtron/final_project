import os, sys, pytest
import tarfile

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.entities import Animal, Entity, Tree, Seed, Direction, EntityType
from project.src.simulation.energies import BlueEnergy, RedEnergy, EnergyType
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
        
        assert {'_position', '_adult_size', '_age',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock'}.issubset(vars(entity))
        
        assert entity.id == 3
        assert entity._position.vect == (20,10)
        assert entity._adult_size == 15
        assert entity._max_age == 100
        assert entity._age == 0
        assert entity._size == 13
        assert entity._action_cost == 1
        assert entity._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert entity._is_adult == False
        
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
            assert self.entity._size == 13
            self.entity._grow()
            assert self.entity._size == 14
            
        def test_reached_adulthood(self):
            for _ in range(10):
                if self.entity._size < self.entity._adult_size:
                    assert not self.entity._is_adult
                else:
                    assert self.entity._is_adult

                self.entity._grow()
                    
            assert self.entity._is_adult
        
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
        
        assert {'_position', '_adult_size', '_age',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock', '_production_type'}.issubset(vars(tree))
        
        assert tree.id == 3
        assert tree._position.vect == (20,10)
        assert tree._adult_size == 15
        assert tree._max_age == 100
        assert tree._age == 0
        assert tree._size == 13
        assert tree._action_cost == 1
        assert tree._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert tree._is_adult == False
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
            
            self.tree2 = Tree(position=(20,11),
                                tree_id=3,
                                adult_size=15,
                                max_age=100,
                                size=13,
                                action_cost=1,
                                blue_energy=1000,
                                red_energy=2000,
                                production_type=EnergyType.BLUE)
            
            self.grid = Grid(0, (30,30))
            self.grid.entity_grid.set_cell_value(coordinates=self.tree1.position(),
                                                 value=self.tree1)
            
            yield
            
            self.tree = None
            
         
        def test_on_death(self):
            position = self.tree1.position()
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            self.tree1._die(grid=self.grid) 
            assert not self.grid.entity_grid.get_cell_value(coordinates=position)
            seed = self.grid.resource_grid.get_cell_value(coordinates=position)
            assert seed
            assert seed.__class__.__name__ == 'Seed'
            
       
        
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
        
        assert {'_position', '_adult_size', '_age',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock', '_pocket'}.issubset(vars(animal))
        
        assert animal.id == 3
        assert animal.position.vect == (20,10)
        assert animal._adult_size == 15
        assert animal._max_age == 100
        assert animal._age == 0
        assert animal._size == 13
        assert animal._action_cost == 1
        assert animal._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert animal._is_adult == False
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
                
                
            def test_move(self):
                animal = self.animal
              
                # Down
                assert animal.position() == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == None
                animal._move(Direction.DOWN,
                             grid=self.grid)
                assert animal.position() == (3,4)
                assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
                
                # Up
                animal._move(Direction.UP,
                             grid=self.grid)
                assert animal.position() == (3,3)
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(2,3)) == None
                
                # Left
                animal._move(Direction.LEFT,
                             grid=self.grid)
                assert animal.position() == (2,3)
                assert self.entity_grid.get_cell_value(coordinates=(2,3)) == animal
                assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
                
                # Right
                animal._move(Direction.RIGHT,
                             grid=self.grid)
                assert animal.position() == (3,3)
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
                
                
            def test_plant_tree(self):
                animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=10)
                assert animal.red_energy == 10
                animal._plant_tree(grid=self.grid)
                assert animal.red_energy == 0
                tree_cell = self.entity_grid._find_coordinates_with_class(position=(3,3),
                                                                          target_class=Tree)[0]
                tree = self.grid.entity_grid.get_cell_value(coordinates=tree_cell)
                assert tree.__class__.__name__ == "Tree"
                
                # No free cells
                grid2 = Grid(grid_id=0,
                             dimensions=(1,1))
                animal2 = grid2.create_entity(entity_type=EntityType.Animal.value, position=(0,0), size=10, blue_energy=10, red_energy=10)
                animal2._plant_tree(grid=self.grid)
                assert len(grid2.entity_grid._find_coordinates_with_class(position=(0,0),
                                                                          target_class=Tree)) == 0
                
            def test_pick_up_seed(self):
                seed = Seed(seed_id=0,
                            position=(3,2),
                            genetic_data={})
                
                position = seed.position()
                
                self.grid.resource_grid.set_cell_value(coordinates=position,
                                                      value=seed)
                
                animal = self.grid.create_entity(entity_type=EntityType.Animal.value,
                                                 position=(3,3),
                                                 size=10,
                                                 blue_energy=10,
                                                 red_energy=10)
                
                assert not animal._pocket
                assert self.grid.resource_grid.get_cell_value(coordinates=position) == seed
                
                animal._pick_up_resource(coordinates=position,
                                         grid=self.grid)
                
                assert animal._pocket == seed
                assert not self.grid.resource_grid.get_cell_value(coordinates=position)
                
            def test_recycle_seed(self):
                seed = Seed(seed_id=0,
                            position=(3,2),
                            genetic_data={'position':(1,2),
                                          'blue_energy':5,
                                          'red_energy':7})
                
                position = seed.position()
                
                self.grid.resource_grid.set_cell_value(coordinates=position,
                                                      value=seed)
                
                animal = self.grid.create_entity(entity_type=EntityType.Animal.value,
                                                 position=(3,3),
                                                 size=10,
                                                 blue_energy=10,
                                                 red_energy=10)
                
                animal._recycle_seed(grid=self.grid)
                assert len(self.grid.resource_grid._find_coordinates_with_class(target_class=BlueEnergy,
                                                                                position=position)) == 0
                animal._pick_up_resource(coordinates=position,
                                         grid=self.grid)
                
                animal._recycle_seed(grid=self.grid)
                assert not animal._pocket 
                energie_cells = (self.grid.resource_grid._find_coordinates_with_class(target_class=BlueEnergy,
                                                                                position=animal.position()) + 
                                 self.grid.resource_grid._find_coordinates_with_class(target_class=RedEnergy,
                                                                                position=animal.position()))
                energies =  [self.grid.resource_grid.get_cell_value(coordinates=energy) for energy in energie_cells]
                assert len(energies) == 2
                
                blue, red = 0, 0
                for energy in energies:
                    if energy.type.value == EnergyType.BLUE.value:
                        assert energy.quantity == 5 
                        blue += 1
                    elif energy.type.value == EnergyType.RED.value:
                        assert energy.quantity == 7  
                        red += 1
                assert (blue,red) == (1,1)
                
            def test_replant_seed(self):
                tree = Tree(position=(3,2),
                            blue_energy=12,
                            red_energy=27,
                            max_age=30,
                            size=2)
                
                max_age, blue_energy, red_energy = tree._max_age, tree.blue_energy, tree.red_energy
                tree._die(grid=self.grid)
                animal = self.grid.create_entity(entity_type=EntityType.Animal.value,
                                                 position=(3,3),
                                                 size=10,
                                                 blue_energy=10,
                                                 red_energy=20)
                
                animal._pick_up_resource(coordinates=tree.position(),
                                         grid=self.grid)
                animal.red_energy == 10
                animal.blue_energy == 10
                animal._plant_tree(grid=self.grid)
                animal.red_energy == 0
                animal.blue_energy == 9
                
                cell = self.entity_grid._find_coordinates_with_class(position=(3,3),
                                                                     target_class=Tree)[0]
                tree = self.grid.entity_grid.get_cell_value(coordinates=cell)
                assert tree._max_age == max_age
                assert tree.blue_energy == blue_energy
                assert tree.red_energy == red_energy
                
                tree._die(grid=self.grid)
                animal._plant_tree(grid=self.grid)
                cell = self.entity_grid._find_coordinates_with_class(position=(3,3),
                                                                      target_class=Tree)[0]
                tree = self.grid.entity_grid.get_cell_value(coordinates=cell)
                assert not tree._max_age == max_age
                assert not tree.blue_energy == blue_energy
                assert not tree.red_energy == red_energy
            
        
            

        
        