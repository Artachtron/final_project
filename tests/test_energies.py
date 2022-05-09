import pytest
import sys, os
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, energies


class TestEnergies:
    def setup_class(self):
        self.grid = world.Grid(width=5, height=10)
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
        
        assert set(['type','quantity', 'position', 'image', 'rect', 'grid']).issubset(vars(blue_energy))
        assert set(['type','quantity', 'position', 'image', 'rect', 'grid']).issubset(vars(red_energy))
        
        assert blue_energy.type == energies.EnergyType.BLUE
        assert red_energy.type == energies.EnergyType.RED
        assert blue_energy.position == (5,5)
        assert red_energy.position == (5,6)
        assert blue_energy.quantity == 5
        assert red_energy.quantity == 10
        assert blue_energy.grid == self.grid
        assert red_energy.grid == self.grid
        assert type(blue_energy.image) == pg.Surface
        assert type(red_energy.image) == pg.Surface
        
    def test_energies_on_grid(self):
        assert self.grid.get_position_value(position=(5,5)) == 0
        assert self.grid.get_position_value(position=(5,6)) == 0
        
        blue_energy = energies.BlueEnergy(grid=self.grid, position=(5,5), quantity=5)
        red_energy = energies.RedEnergy(grid=self.grid, position=(5,6), quantity=10)
        
        assert self.grid.get_position_value(position=(5,4)) == 0
        assert self.grid.get_position_value(position=(5,5)) == 1
        assert self.grid.get_position_value(position=(5,6)) == 1