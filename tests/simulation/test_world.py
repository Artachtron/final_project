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
        
        assert {'dimensions', 'block_size', 'sim_speed',
                'display_active', 'simulation',
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
            
            
            # Simulation
            assert world.simulation.__class__.__name__ == 'Simulation'
            assert world.simulation.id == world.id
           
           
           
            # Display
            assert world.display.__class__.__name__ == 'Display'
            assert world.display.id == world.id
            assert world.display.dimensions == world.dimensions
            assert world.display.block_size == world.block_size
            
