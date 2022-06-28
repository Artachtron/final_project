import os
import sys

import pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.energies import EnergyType
from project.src.simulation.simulation import Environment, Simulation
from project.src.simulation.universal import SimulatedObject


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

        
class TestSimulatedObject:
    def test_create_simulated_object(self):
        sim = SimulatedObject(sim_obj_id=0,
                              size=10,
                              position=(20,10),
                              appearance="")
        


      
        
        