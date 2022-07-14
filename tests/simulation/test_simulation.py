import os
import sys

import pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'platform')))
from project.src.platform.energies import EnergyType
from project.src.platform.entities import Direction, Tree
from project.src.platform.grid import Grid
from project.src.platform.simulation import Environment, Simulation
from project.src.platform.universal import SimulatedObject


class TestSimulation:
    def test_create_simulation(self):
        env = Environment(env_id=1)
        sim = Simulation(sim_id=0)
        assert type(sim) == Simulation


class TestEnvironment:
    def test_create_environment(self):
        env = Environment(env_id=1)
      
        assert type(env) == Environment
    
    def test_init_env(self):
            env = Environment(env_id=1)
            env.init()
            
            # Sim state
            assert env.state.__class__.__name__ == 'SimState'
            assert env.state.id == env.id
            # Grid
            assert env.grid.__class__.__name__ == 'Grid'
            assert env.grid.id == env.id
        
    class TestEnvMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
 
            self.env = Environment(env_id=1)
            self.env.init()
            
            self.grid = self.env.grid
            self.state = self.env.state
            yield
        
        def test_create_entity(self):
            # Animal
            coordinates = (1,1)
            self.env.spawn_animal(coordinates=coordinates)
            
            animal = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert animal
            assert animal.__class__.__name__ == 'Animal'
            assert animal.id == 1
            assert animal.position == coordinates
            
            assert self.state.get_entity_id() == 2
            assert self.state.animals[1] == animal
            assert len(self.state.animals) == 1
            
            # Tree
            coordinates = (2, 4)
            self.env.spawn_tree(coordinates=coordinates)
            
            tree = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert tree
            assert tree.__class__.__name__ == 'Tree'
            assert tree.id == 2
            assert tree.position == coordinates
            
            assert self.state.get_entity_id() == 3
            assert self.state.trees[2] == tree
            assert len(self.state.trees) == 1
            
            # Already used
            animal = self.env.spawn_animal(coordinates=coordinates)
            assert not animal
            
            tree2 = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert tree2 == tree
            assert tree2.__class__.__name__ == 'Tree'
            assert tree2.id == 2
            
            assert self.state.get_entity_id() == 3
            assert self.state.trees[2] == tree2
            assert len(self.state.trees) == 1
            assert len(self.state.animals) == 1
            
        def test_create_energy(self):
            coordinates = (1,1)
            energy = self.env.create_energy(energy_type=EnergyType.BLUE,
                                            quantity=12,
                                            coordinates=coordinates)
            
            assert self.grid.resource_grid.get_cell_value(coordinates=coordinates)
            assert energy.__class__.__name__ == 'BlueEnergy'
            assert energy.id == 1
            assert energy.position == coordinates
            assert energy.quantity == 12
            
            assert self.state.get_energy_id() == 2
            assert self.state.energies[1] == energy
            assert len(self.state.energies) == 1 
            
            # Already used
            coordinates = (1,1)
            assert not self.env.create_energy(energy_type=EnergyType.BLUE,
                                              quantity=12,
                                              coordinates=coordinates)
            
            energy2 = self.grid.resource_grid.get_cell_value(coordinates=coordinates)
            assert energy2 == energy
            assert energy2.__class__.__name__ == 'BlueEnergy'
            assert energy2.id == 1
            assert energy2.position == coordinates
            
            assert self.state.get_energy_id() == 2
            assert self.state.energies[1] == energy2
            assert len(self.state.energies) == 1
            
        def test_create_seed_from_tree(self):
            position = (1,1)
            tree = self.env.spawn_tree(coordinates=position,
                                        blue_energy=32,
                                        red_energy=13,
                                        size=27,
                                        adult_size=16,
                                        max_age=30) 
            
            assert self.grid.entity_grid.get_cell_value(coordinates=position)
            seed = self.env.create_seed_from_tree(tree=tree)
            assert not self.grid.entity_grid.get_cell_value(coordinates=position)
            assert self.grid.resource_grid.get_cell_value(coordinates=position) == seed
            
            assert seed.id == tree.id
            assert seed.genetic_data['blue_energy'] == 32
            assert seed.genetic_data['red_energy'] == 13
            assert seed.genetic_data['adult_size'] == 16
            assert seed.genetic_data['max_age'] == 30
            
        def test_spawn_tree(self):
            position = (1,1)
            tree = self.env.spawn_tree(coordinates=position)
            seed = self.env.create_seed_from_tree(tree=tree)
            assert len(self.state.seeds) == 1
            tree2 = self.env.sprout_tree(seed=seed,
                                        position=position)
            
            assert tree.id == tree2.id
            assert tree.position == tree2.position
            assert tree.blue_energy == tree2.blue_energy
            assert tree.red_energy == tree2.red_energy
            assert tree._max_age == tree2._max_age
            
            assert self.grid.resource_grid.get_cell_value(coordinates=position)

            
        def test_remove_entity(self):
           # Animal
            coordinates = (1,1)
            animal = self.env.spawn_animal(coordinates=coordinates)
            
            assert self.grid.entity_grid.get_cell_value(coordinates=coordinates) == animal
    
            assert self.state.animals[1] == animal
            assert len(self.state.animals) == 1 
            
            self.env.remove_entity(entity=animal)
            assert not self.grid.entity_grid.get_cell_value(coordinates=coordinates)
    
            assert len(self.state.animals) == 0
            
        def test_remove_resource(self):
           # Animal
            coordinates = (1,1)
            energy = self.env.create_energy(coordinates=coordinates,
                                            energy_type=EnergyType.BLUE,
                                            quantity=10)
            
            assert self.grid.resource_grid.get_cell_value(coordinates=coordinates) == energy
    
            assert self.state.energies[1] == energy
            assert len(self.state.energies) == 1 
            
            self.env.remove_resource(resource=energy)
            assert not self.grid.resource_grid.get_cell_value(coordinates=coordinates)
    
            assert len(self.state.energies) == 0
            
        def test_find_entities_around(self):
            coordinates = (1,1)
            animal = self.env.spawn_animal(coordinates=coordinates)
            entities = self.env.find_if_entities_around(coordinates=coordinates,
                                                        include_self=True,
                                                        radius=1)
            assert sum(list(entities)) == 1
            
            entities = self.env.find_if_entities_around(coordinates=coordinates,
                                                        include_self=False,
                                                        radius=1)
            assert sum(list(entities)) == 0

            self.env.spawn_animal(coordinates=(2,2))
            self.env.spawn_animal(coordinates=(2,1))
            
            entities = self.env.find_if_entities_around(coordinates=coordinates,
                                                        include_self=True,
                                                        radius=1)
            assert sum(list(entities)) == 3
            
        def test_find_resources_around(self):
            coordinates = (1,1)
            animal = self.env.spawn_animal(coordinates=coordinates)
            resources = self.env.find_if_resources_around(coordinates=coordinates,
                                                        include_self=True,
                                                        radius=1)
            assert sum(list(resources)) == 0
            
            self.env.create_energy(energy_type=EnergyType.BLUE,
                                   quantity=10,
                                   coordinates=(1,2))
            
            tree = self.env.spawn_tree(coordinates=(2,2))
            
            resources = self.env.find_if_resources_around(coordinates=coordinates,
                                                        include_self=True,
                                                        radius=1)
            assert sum(list(resources)) == 1
            
            self.env.create_energy(energy_type=EnergyType.RED,
                                   quantity=10,
                                   coordinates=(2,1))
            
            self.env.create_seed_from_tree(tree=tree)
            
            resources = self.env.find_if_resources_around(coordinates=coordinates,
                                                        include_self=True,
                                                        radius=4)
            assert sum(list(resources)) == 3
            
        def test_get_colors_around(self):
            coordinates = (2,2)
            colors = self.env.get_colors_around(coordinates=coordinates,
                                                radius=2)
            
            assert colors.shape == (5,5,3)
            
            # Padding working
            coordinates = (0,2)
            colors = self.env.get_colors_around(coordinates=coordinates,
                                                radius=2)
            
            assert colors.shape == (5,5,3)
            
            coordinates = (2,0)
            colors = self.env.get_colors_around(coordinates=coordinates,
                                                radius=2)
            
            assert colors.shape == (5,5,3)

    class TestAnimalActions:
        @pytest.fixture(autouse=True)
        def setup(self):
            
            self.env = Environment(env_id=0)
            self.env.init()
            
            self.animal = self.env.spawn_animal(coordinates=(3,3))

            self.grid: Grid = self.env.grid
            
            self.entity_grid = self.grid.entity_grid
            
            yield
            
            del self.animal
            del self.grid
            
        def test_move_action(self):
            animal = self.animal
            
            # Down
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == None
            animal._decide_move(Direction.DOWN)
            self.env._event_on_action(entity=animal)
            
            assert animal.position == (3,4)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
            
            # Up
            animal._decide_move(Direction.UP)
            self.env._event_on_action(entity=animal)
            
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(2,3)) == None
            
            # Left
            animal._decide_move(Direction.LEFT)
            self.env._event_on_action(entity=animal)
            
            assert animal.position == (2,3)
            assert self.entity_grid.get_cell_value(coordinates=(2,3)) == animal
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == None
            
            # Right
            animal._decide_move(Direction.RIGHT)
            self.env._event_on_action(entity=animal)
            
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,3)) == animal
        
        def test_move_occupied_cell(self):
            animal = self.animal
            animal2 = self.env.spawn_animal(coordinates=(3,4))
            self.entity_grid._set_cell_value(coordinates=(3,4),
                                            value=animal2)
            
            # Move on already occupied cell
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
            animal._decide_move(Direction.DOWN)
            
            self.env._event_on_action(entity=animal)
            
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
          
        def test_move_out_of_bounds_cell(self):
            animal = self.env.spawn_animal(coordinates=(0,0))
            self.entity_grid._set_cell_value(coordinates=(0,0),
                                            value=animal)
            # Left
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            animal._decide_move(Direction.LEFT)
            self.env._event_on_action(entity=animal)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            
            # Up
            animal._decide_move(Direction.UP)
            self.env._event_on_action(entity=animal)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(coordinates=(0,0)) == animal
            
            # Right
            animal2 = self.env.spawn_animal(coordinates=(19,19))
            self.entity_grid._set_cell_value(coordinates=(19,19),
                                            value=animal2)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
            animal2._decide_move(Direction.RIGHT)
            self.env._event_on_action(entity=animal2)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2
            
            #Down
            animal2._decide_move(Direction.DOWN)
            self.env._event_on_action(entity=animal2)
            assert animal2.position == (19,19)
            assert self.entity_grid.get_cell_value(coordinates=(19,19)) == animal2  

        def test_plant_tree(self):
            animal = self.env.spawn_animal(coordinates=(5,5))
            assert animal.red_energy == 10
            animal._decide_plant_tree()
            self.env._event_on_action(entity=animal)
            assert animal.red_energy == 0
            tree_cell, = self.entity_grid._find_coordinates_baseclass(coordinates=(5,5),
                                                                      base_class=Tree)
            tree = self.grid.entity_grid.get_cell_value(coordinates=tree_cell)
            assert tree.__class__.__name__ == "Tree"

        
class TestSimulatedObject:
    def test_create_simulated_object(self):
        sim = SimulatedObject(sim_obj_id=0,
                              size=10,
                              position=(20,10),
                              appearance="")
        


      
        
        