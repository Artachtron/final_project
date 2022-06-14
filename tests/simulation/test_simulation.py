import sys, os, pygame

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.simulation import SimulatedObject, Simulation, Position


class TestSimulation:
    def test_create_simulation(self):
        sim = Simulation(sim_id=0)
        assert type(sim) == Simulation
        
""" class TestPosition:
    def test_test(self):
        p = Position(1,2) """
  
        
class TestSimulatedObject:
    def test_create_simulated_object(self):
        sim = SimulatedObject(sim_obj_id=0,
                              size=10,
                              position=(20,10),
                              appearance="")
      
        
        