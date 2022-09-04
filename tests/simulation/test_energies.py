import os
import sys

import pytest
from project.src.platform.energies import (BlueEnergy, Energy, EnergyType,
                                           RedEnergy)


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
        
        assert {'_type', 'size', 'quantity',
                'appearance', '_position'}.issubset(vars(energy))
        
        assert energy.id == 0
        assert energy.type == EnergyType.BLUE
        assert energy._position.vect == (20,20)
        assert 3 < energy.size < 10 
        assert energy.quantity > 0
        