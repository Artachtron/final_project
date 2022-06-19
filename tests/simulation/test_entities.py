import os, sys, pytest


sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.entities import Animal, Entity, Tree, Seed, Direction, Status
from project.src.simulation.energies import BlueEnergy, RedEnergy, EnergyType
from project.src.simulation.grid import Grid
from project.src.simulation.simulation import Environment

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
        assert entity.position == (20,10)
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
                self.env = Environment(env_id=0)
                self.grid = self.env.grid
                self.entity_grid = self.grid.entity_grid
                
                self.entity = self.env.create_animal(coordinates=(0,0))
                yield
            
            def test_drop_energy(self):
                assert self.entity._loose_energy(energy_type=EnergyType.BLUE,
                                                 quantity=5)
                assert self.entity.energies == {"blue energy": 5, "red energy": 10}
                assert self.entity.blue_energy == 5
                self.entity._action_cost = 0
                
                # Drop blue energy
                blue_cell = (1,1)
                assert self.grid.resource_grid.get_cell_value(coordinates=blue_cell) == None
                self.entity._drop_energy(environment=self.env,
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
                self.entity._drop_energy(environment=self.env,
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
                self.entity._drop_energy(environment=self.env,
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
                self.entity._drop_energy(environment=self.env,
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
        assert tree.position == (20,10)
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
            self.env = Environment(env_id=0)
            
            self.tree1 = self.env.create_tree(coordinates=(19,10))
            
          
            self.tree2 = self.env.create_tree(coordinates=(19,11))
           
            
            self.grid = self.env.grid
            self.grid.entity_grid._set_cell_value(coordinates=self.tree1.position,
                                                 value=self.tree1)
            
            yield
            
            self.tree = None
            
         
        def test_on_death(self):
            position = self.tree1.position
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            assert self.tree1.status.name == Status.ALIVE.name
            self.tree1._die() 
            assert self.tree1.status.name == Status.DEAD.name
            self.tree1.on_death(environment=self.env)
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
        
        assert {'_position', '_adult_size', '_age', 'organism',
                '_max_age', '_size', '_action_cost', '_is_adult',
                '_energies_stock', '_pocket'}.issubset(vars(animal))
        
        assert animal.id == 3
        assert animal.position == (20,10)
        assert animal._adult_size == 15
        assert animal._max_age == 100
        assert animal._age == 0
        assert animal._size == 13
        assert animal._action_cost == 1
        assert animal._energies_stock == {'blue energy': 12, 'red energy': 27}
        assert animal._is_adult == False
        assert animal._pocket == None
        
        # Organism
        org = animal.organism
        gen = org.genotype
        net = org.mind
        
        assert org.id == animal.id
        assert net.id == animal.id
        assert gen.id == animal.id
        
        assert org.entity_type == 'animal'
        assert len(net.inputs) == 96
        assert len(net.outputs) == 12
        
    class TestAnimalMethods:
        @pytest.fixture(autouse=True)
        def setup(self):

            """ self.entity_grid = SubGrid(dimensions=(20,20),
                                    data_type=Entity,
                                    initial_value=None) """
            
            self.env = Environment(env_id=0)
            
            self.animal = self.env.create_animal(coordinates=(3,3))
        
            
            self.grid: Grid = self.env.grid
            
            self.entity_grid = self.grid.entity_grid
            
            yield
            
            del self.animal
            del self.grid
            
            
            
        def test_move(self):
            animal = self.animal
            
            # Down
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == None
            animal._move(Direction.DOWN,
                            environment=self.env)
            assert animal.position == (3,4)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
            
            # Up
            animal._move(Direction.UP,
                            environment=self.env)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(2,3)) == None
            
            # Left
            animal._move(Direction.LEFT,
                            environment=self.env)
            assert animal.position == (2,3)
            assert self.entity_grid.get_cell_value(coordinates=(2,3)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
            
            # Right
            animal._move(Direction.RIGHT,
                            environment=self.env)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
            
        def test_move_occupied_cell(self):
            animal = Animal(position=(3,3))
            animal2 = Animal(position=(3,4))
            self.entity_grid._set_cell_value(coordinates=(3,4),
                                            value=animal2)
            
            # Move on already occupied cell
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
            animal._move(Direction.DOWN, 
                            environment=self.env)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
            
        def test_move_out_of_bounds_cell(self):
            animal = Animal(position=(0,0))
            self.entity_grid._set_cell_value(coordinates=(0,0),
                                            value=animal)
            # Left
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            animal._move(Direction.LEFT, 
                            environment=self.env)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            
            # Up
            animal._move(Direction.UP, 
                            environment=self.env)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            
            # Right
            animal2 = Animal(position=(19,19))
            self.entity_grid._set_cell_value(coordinates=(19,19),
                                            value=animal2)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
            animal2._move(Direction.RIGHT, 
                            environment=self.env)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
            
            #Down
            animal2._move(Direction.DOWN, 
                            environment=self.env)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
            
            
        def test_plant_tree(self):
            animal = self.env.create_animal(coordinates=(5,5))
            assert animal.red_energy == 10
            animal._plant_tree(environment=self.env)
            assert animal.red_energy == 0
            tree_cell = self.entity_grid._find_coordinates_baseclass(position=(5,5),
                                                                        target_class=Tree)[0]
            tree = self.grid.entity_grid.get_cell_value(coordinates=tree_cell)
            assert tree.__class__.__name__ == "Tree"
            
            # No free cells
    
            # env2 = Environment(env_id=2)
            # animal2 = env2.create_animal(coordinates=(0,0))
            # animal2._plant_tree(environment=env2)
            # assert len(env2.grid.entity_grid._find_coordinates_with_class(position=(0,0),
            #                                                           target_class=Tree)) == 0
        
        def test_pick_up_resource(self):
            position = (1,1)
            energy = self.env.create_energy(coordinates=position,
                                            quantity=10,
                                            energy_type=EnergyType.RED)
            
            assert self.grid.resource_grid.get_cell_value(position)
            
            blue_stock = self.animal.blue_energy
            red_stock = self.animal.red_energy
            self.animal._pick_up_resource(coordinates=position,
                                            environment=self.env)
            
            assert not self.grid.resource_grid.get_cell_value(position) 
            assert self.animal.blue_energy <= blue_stock 
            assert self.animal.red_energy == red_stock + energy.quantity 
            
        def test_pick_up_seed(self):
            tree = self.env.create_tree(coordinates=(3,2))
            seed = self.env.create_seed_from_tree(tree)
            
            
            position = seed.position
            
            self.grid.resource_grid._set_cell_value(coordinates=position,
                                                    value=seed)
            
            animal = self.env.create_animal(coordinates=(4,2))
            
            assert not animal._pocket
            assert self.grid.resource_grid.get_cell_value(coordinates=position) == seed
            
            animal._pick_up_resource(coordinates=position,
                                        environment=self.env)
            
            assert animal._pocket == seed
            assert not self.grid.resource_grid.get_cell_value(coordinates=position)
            
        def test_recycle_seed(self):
            tree = self.env.create_tree(coordinates=(3,2),
                                        blue_energy=5,
                                        red_energy=7)
            seed = self.env.create_seed_from_tree(tree)
            
            position = seed.position
            
            self.grid.resource_grid._set_cell_value(coordinates=position,
                                                    value=seed)
            
            animal = self.env.create_animal(coordinates=(3,2))
            # Pocket empty
            animal._recycle_seed(environment=self.env)
            assert len(self.grid.resource_grid._find_coordinates_baseclass(target_class=BlueEnergy,
                                                                            position=position)) == 0
            animal._pick_up_resource(coordinates=position,
                                        environment=self.env)
            
            animal._recycle_seed(environment=self.env)
            assert not animal._pocket 
            energie_cells = (self.grid.resource_grid._find_coordinates_baseclass(target_class=BlueEnergy,
                                                                            position=animal.position) + 
                                self.grid.resource_grid._find_coordinates_baseclass(target_class=RedEnergy,
                                                                            position=animal.position))
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
            tree = self.env.create_tree(coordinates=(3,2),
                                        max_age=32,
                                        blue_energy=12,
                                        red_energy=57)
            
            # Replant seed
            max_age, blue_energy, red_energy = tree._max_age, tree.blue_energy, tree.red_energy
            tree.on_death(environment=self.env)
            animal = self.env.create_animal(coordinates=(2,3))
            
            animal._pick_up_resource(coordinates=tree.position,
                                        environment=self.env)
            animal.red_energy == 10
            animal.blue_energy == 10
            animal._plant_tree(environment=self.env)
            animal.red_energy == 0
            animal.blue_energy == 9
            
            cell = self.entity_grid._find_coordinates_baseclass(position=(2,3),
                                                                    target_class=Tree)[0]
            tree = self.grid.entity_grid.get_cell_value(coordinates=cell)
            assert tree._max_age == max_age
            assert tree.blue_energy == blue_energy
            assert tree.red_energy == red_energy
            
            tree.on_death(environment=self.env)
            
            
            # New tree
            animal._gain_energy(energy_type=EnergyType.RED,
                                quantity=100)
            animal._plant_tree(environment=self.env)
            cell = self.entity_grid._find_coordinates_baseclass(position=(2,3),
                                                                    target_class=Tree)[0]
            tree = self.grid.entity_grid.get_cell_value(coordinates=cell)
            assert not tree._max_age == max_age
            assert not tree.blue_energy == blue_energy
            assert not tree.red_energy == red_energy
            
        def test_decompose(self):
            resource_grid = self.grid.resource_grid
            position = self.animal.position
            self.grid.place_entity(value=self.animal)
            assert not resource_grid._find_coordinates_baseclass(position=position,
                                                                    target_class=BlueEnergy)
            assert not resource_grid._find_coordinates_baseclass(position=position,
                                                                    target_class=RedEnergy)
            
            self.animal._decompose(entity=self.animal,
                                    environment=self.env)
            assert resource_grid._find_coordinates_baseclass(position=position,
                                                                target_class=BlueEnergy)
            assert resource_grid._find_coordinates_baseclass(position=position,
                                                                target_class=RedEnergy)
    
        
        def test_die(self):
            resource_grid = self.grid.resource_grid
            position = self.animal.position
            self.grid.place_entity(value=self.animal)
            
            assert self.animal.status.name == Status.ALIVE.name
            self.animal._die()
            assert self.animal.status.name == Status.DEAD.name
            
            assert not resource_grid._find_coordinates_baseclass(position=position,
                                                                    target_class=BlueEnergy)
            assert not resource_grid._find_coordinates_baseclass(position=position,
                                                                    target_class=RedEnergy)
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            self.animal.on_death(environment=self.env)
            assert resource_grid._find_coordinates_baseclass(position=position,
                                                                target_class=BlueEnergy)
            assert resource_grid._find_coordinates_baseclass(position=position,
                                                                target_class=RedEnergy)
            assert not self.grid.entity_grid.get_cell_value(coordinates=position)
        
        def test_modify_cell_color(self):
                cell_color = self.env.grid._color_grid.get_cell_value(coordinates=self.animal.position)
                assert tuple(cell_color) == (255,255,255)
                
                
                new_color = (177,125,234)
                
                self.animal._paint(color=new_color,
                                   environment=self.env)
                
                cell_color = self.env.grid._color_grid.get_cell_value(coordinates=self.animal.position)
                assert tuple(cell_color) == new_color
                
                new_color = (46,12,57)
                
                self.animal._paint(color=new_color,
                                   environment=self.env)
                
                cell_color = self.env.grid._color_grid.get_cell_value(coordinates=self.animal.position)
                assert tuple(cell_color) == new_color
        
                
        class TestAnimalMind:
            @pytest.fixture(autouse=True)
            def setup(self):
                self.env = Environment(env_id=0)
                self.animal = self.env.create_animal(coordinates=(5,5),
                                                     blue_energy=157,
                                                     red_energy=122,
                                                     max_age=24,
                                                     size=37)
                
                self.animal._increase_age(amount=12)
                
                
            def test_normalize_inputs(self):
                # Empty grid
                inputs = self.animal._normalize_inputs(environment=self.env)
                
                assert len(inputs) == 96
                assert inputs[0] == 0.5
                assert inputs[1] == 37/100
                assert round(inputs[2],5) == 157/100000
                assert round(inputs[3],5) == 122/100000
                assert sum(inputs[4:12]) == 0    
                assert sum(inputs[12:21]) == 0
                assert sum(inputs[21:]) == 75*0        
                
                # Non-empty grid
                self.env.create_tree(coordinates=(5,6))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(6,5))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(4,5))
                self.env.create_energy(energy_type=EnergyType.BLUE,
                                       quantity=15,
                                       coordinates=(5,4))
                
                inputs = self.animal._normalize_inputs(environment=self.env)
                
    
                assert sum(inputs[4:12]) == 1    
                assert sum(inputs[12:21]) == 3
                assert sum(inputs[21:]) == 75*0       
                          
                
            def test_activate_mind(self):
                for _ in range(100):
                    self.animal._activate_mind(environment=self.env)
                    
            
            
                
        
            

        
        