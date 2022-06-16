import sys, os, pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.simulation import Simulation, Environment
from project.src.simulation.extra_classes import SimulatedObject 


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
            self.env.create_animal(coordinates=coordinates)
            
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
            self.env.create_tree(coordinates=coordinates)
            
            tree = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert tree
            assert tree.__class__.__name__ == 'Tree'
            assert tree.id == 2
            assert tree.position == coordinates
            
            assert self.state.get_entity_id() == 3
            assert self.state.trees[2] == tree
            assert len(self.state.trees) == 1
  
        
class TestSimulatedObject:
    def test_create_simulated_object(self):
        sim = SimulatedObject(sim_obj_id=0,
                              size=10,
                              position=(20,10),
                              appearance="")
        


      
        
        