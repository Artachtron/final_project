import os, sys, pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.world import World


class TestWorld:
    def test_create_world(self):
        world = World(world_id=0)
        
        assert type(world) == World
        
    def test_world_fields(self):
        world = World(world_id=0,
                      dimensions=(35,21),
                      block_size=13,
                      sim_speed=100,
                      display_active=True)
        
        assert {'id', 'dimensions', 'block_size', 'grid',
                'sim_speed', 'display_active', 'simulation',
                'display'}.issubset(vars(world))
        
        assert world.id == 0
        assert world.dimensions == (35,21)
        assert world.block_size == 13
        assert world.sim_speed == 100
        assert world.display_active == True
        
    def test_init_world(self):
            world = World(world_id=0,
                      dimensions=(35,21),
                      block_size=13,
                      sim_speed=100,
                      display_active=True)
            
            # World table
            assert world.world_table.__class__.__name__ == 'WorldTable'
            assert world.world_table.id == world.id
            
            # Simulation
            assert world.simulation.__class__.__name__ == 'Simulation'
            assert world.simulation.id == world.id
           
            # Grid
            assert world.grid.__class__.__name__ == 'Grid'
            assert world.grid.id == world.id
            assert world.grid.dimensions == world.dimensions
           
            # Display
            assert world.display.__class__.__name__ == 'Display'
            assert world.display.id == world.id
            assert world.display.dimensions == world.dimensions
            assert world.display.block_size == world.block_size
            
        
    class TestWorldMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
 
            self.world = World( world_id=0,
                                dimensions=(35,21),
                                block_size=13,
                                sim_speed=100,
                                display_active=True)
            
            self.grid = self.world.grid
            self.table = self.world.world_table
            yield
        
        def test_create_entity(self):
            # Animal
            coordinates = (1,1)
            self.world.create_new_animal(coordinates=coordinates)
            
            animal = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert animal
            assert animal.__class__.__name__ == 'Animal'
            assert animal.id == 1
            assert animal.position == coordinates
            
            assert self.table.get_entity_id() == 2
            assert self.table.animals[1] == animal
            assert len(self.table.animals) == 1
            
            # Tree
            coordinates = (2, 4)
            self.world.create_new_tree(coordinates=coordinates)
            
            tree = self.grid.entity_grid.get_cell_value(coordinates=coordinates)
            assert tree
            assert tree.__class__.__name__ == 'Tree'
            assert tree.id == 2
            assert tree.position == coordinates
            
            assert self.table.get_entity_id() == 3
            assert self.table.trees[2] == tree
            assert len(self.table.trees) == 1
        

        
        
  