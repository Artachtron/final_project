import pytest
import sys, os
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, energies


class TestEnergies:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=10, height=10)
        self.energy_grid = self.grid.energy_grid
        world.init_pygame()
  
    def test_create_energies(self):
        blue_energy = energies.BlueEnergy(grid=self.grid, position=(5,5), quantity=5)
        red_energy = energies.RedEnergy(grid=self.grid, position=(5,6), quantity=10)
        
        assert type(blue_energy) == energies.BlueEnergy
        assert type(red_energy) == energies.RedEnergy
        assert blue_energy.__class__.__base__ == energies.Energy
        assert red_energy.__class__.__base__ == energies.Energy
        #{'_Sprite__g': {}, 'type': <EnergyType.BLUE: 0>, 'quantity': 10, 'position': (4, 5), 'image': <Surface(10x10x32 SW)>, 'rect': <rect(85, 105, 10, 10)>, 'grid': <__main__.Grid object at 0x000001751E453A90>}
        
    def test_energies_fields(self):
        blue_energy = energies.BlueEnergy(grid=self.grid, position=(5,5), quantity=5)
        red_energy = energies.RedEnergy(grid=self.grid, position=(5,6), quantity=10)
        
        assert set(['type','quantity', 'position', 'image', 'rect', 'energy_grid']).issubset(vars(blue_energy))
        assert set(['type','quantity', 'position', 'image', 'rect', 'energy_grid']).issubset(vars(red_energy))
        
        assert blue_energy.type == energies.EnergyType.BLUE
        assert red_energy.type == energies.EnergyType.RED
        assert blue_energy.position == (5,5)
        assert red_energy.position == (5,6)
        assert blue_energy.quantity == 5
        assert red_energy.quantity == 10
        assert blue_energy.energy_grid == self.energy_grid
        assert red_energy.energy_grid == self.energy_grid
        assert type(blue_energy.image) == pg.Surface
        assert type(red_energy.image) == pg.Surface
        assert type(blue_energy.rect) == pg.Rect
        assert type(red_energy.rect) == pg.Rect
        
    def test_energies_on_grid(self):
        assert self.energy_grid.get_position_value(position=(5,5)) == None
        assert self.energy_grid.get_position_value(position=(5,6)) == None
        
        energies.BlueEnergy(grid=self.grid, position=(5,5), quantity=5)
        energies.RedEnergy(grid=self.grid, position=(5,6), quantity=10)
        
        assert self.energy_grid.get_position_value(position=(5,4)) == None
        assert self.energy_grid.get_position_value(position=(5,5)) == 1
        assert self.energy_grid.get_position_value(position=(5,6)) == 1