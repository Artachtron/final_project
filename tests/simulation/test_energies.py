import os, sys, pytest

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'simulation')))
from project.src.simulation.energies import Energy, BlueEnergy, RedEnergy, EnergyType

class TestEnergy:
    def test_create_energy(self):
       energy = Energy(energy_id=0,
                       energy_type=EnergyType.BLUE,
                       position=(20,20)) 
       
       assert type(energy) == Energy
       
    def test_energy_fields(self):
        energy = Energy(energy_id=0,
                        energy_type=EnergyType.BLUE,
                        position=(20,20)) 
        
        assert {'_type', '_size', 'quantity',
                '_appearance', '_position'}.issubset(vars(energy))
        
        assert energy.id == 0
        assert energy.type == EnergyType.BLUE
        assert energy._position.vect == (20,20)
        assert 5 < energy._size < 10 
        assert energy.quantity > 0
        