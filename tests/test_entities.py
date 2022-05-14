from contextlib import redirect_stderr
import pytest
import sys, os
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, entities, energies
from project.src.energies import EnergyType, BlueEnergy, RedEnergy

class TestTree:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        world.init_pygame()
        yield
        
    def test_create_tree(self):
        tree = entities.Tree(grid=self.grid, position=(3,3))
        
        assert type(tree) == entities.Tree
        assert tree.__class__.__base__ == entities.Entity
        
    def test_fields(self):
        tree = entities.Tree(grid=self.grid, position=(3,3), size=10)
        
        assert set(['size', 'position', 'image', 'rect', 'grid']).issubset(vars(tree))
               
        assert tree.size == 10
        assert tree.position == (3,3)
        assert tree.entity_grid == self.entity_grid
        assert type(tree.image) == pg.Surface
        assert type(tree.rect) == pg.Rect
        
    def test_tree_on_grid(self):
        assert self.entity_grid.get_position_value(position=(3,3)) == None
        
        tree = entities.Tree(grid=self.grid, position=(3,3))

        assert self.entity_grid.get_position_value(position=(3,4)) == None
        assert self.entity_grid.get_position_value(position=(3,3)) == tree

class TestAnimal:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        world.init_pygame()
        yield
        
    def test_create_animal(self):
        animal = entities.Animal(grid=self.grid, position=(3,3))
        
        assert type(animal) == entities.Animal
        assert animal.__class__.__base__ == entities.Entity
        
    def test_fields(self):
        animal = entities.Animal(grid=self.grid, position=(3,3), size=10)
        
        assert set(['size', 'position', 'image', 'rect', 'grid']).issubset(vars(animal))
               
        assert animal.size == 10
        assert animal.position == (3,3)
        assert animal.entity_grid == self.entity_grid
        assert type(animal.image) == pg.Surface
        assert type(animal.rect) == pg.Rect
        
    def test_animal_on_grid(self):
        assert self.entity_grid.get_position_value(position=(3,3)) == None
        
        animal = entities.Animal(grid=self.grid, position=(3,3))

        assert self.entity_grid.get_position_value(position=(3,4)) == None
        assert self.entity_grid.get_position_value(position=(3,3)) == animal
        
    def test_move(self):
        animal = entities.Animal(grid=self.grid, position=(3,3))
        
        # Down
        assert animal.position == (3,3)
        assert self.entity_grid.get_position_value(position=(3,4)) == None
        animal.move(entities.Direction.DOWN)
        assert animal.position == (3,4)
        assert self.entity_grid.get_position_value(position=(3,4)) == animal
        assert self.entity_grid.get_position_value(position=(3,3)) == None
        
           # Up
        animal.move(entities.Direction.UP)
        assert animal.position == (3,3)
        assert self.entity_grid.get_position_value(position=(3,3)) == animal
        assert self.entity_grid.get_position_value(position=(2,3)) == None
        
         # Left
        animal.move(entities.Direction.LEFT)
        assert animal.position == (2,3)
        assert self.entity_grid.get_position_value(position=(2,3)) == animal
        assert self.entity_grid.get_position_value(position=(3,3)) == None
        
        # Right
        animal.move(entities.Direction.RIGHT)
        assert animal.position == (3,3)
        assert self.entity_grid.get_position_value(position=(3,3)) == animal
        
    def test_move_occupied_cell(self):
        animal = entities.Animal(grid=self.grid, position=(3,3))
        animal2 = entities.Animal(grid=self.grid, position=(3,4))
        
        # Move on already occupied cell
        assert animal.position == (3,3)
        assert self.entity_grid.get_position_value(position=(3,4)) == animal2
        assert animal2.position == (3,4)
        animal.move(entities.Direction.DOWN)
        assert animal.position == (3,3)
        assert self.entity_grid.get_position_value(position=(3,4)) == animal2
        assert animal2.position == (3,4)
        
    def test_move_out_of_bounds_cell(self):
        animal = entities.Animal(grid=self.grid, position=(0,0))
        
        # Left
        assert animal.position == (0,0)
        assert self.entity_grid.get_position_value(position=(0,0)) == animal
        animal.move(entities.Direction.LEFT)
        assert animal.position == (0,0)
        assert self.entity_grid.get_position_value(position=(0,0)) == animal
        
        # Up
        animal.move(entities.Direction.UP)
        assert animal.position == (0,0)
        assert self.entity_grid.get_position_value(position=(0,0)) == animal
        
        # Right
        animal2 = entities.Animal(grid=self.grid, position=(4,9))
        assert animal2.position == (4,9)
        assert self.entity_grid.get_position_value(position=(4,9)) == animal2
        animal2.move(entities.Direction.RIGHT)
        assert animal2.position == (4,9)
        assert self.entity_grid.get_position_value(position=(4,9)) == animal2
        
        #Down
        animal2.move(entities.Direction.DOWN)
        assert animal2.position == (4,9)
        assert self.entity_grid.get_position_value(position=(4,9)) == animal2
        
    def test_drop_energy(self):
        animal = entities.Animal(grid=self.grid, position=(0,0), blue_energy=5, red_energy=10)
        assert animal.energies_stock == {"blue energy": 5, "red energy": 10}
        assert animal.get_blue_energy() == 5
        
        # Drop blue energy
        blue_cell = (1,1)
        assert self.grid.energy_grid.get_position_value(position=blue_cell) == None
        animal.drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell=blue_cell)
        assert animal.energies_stock == {"blue energy": 4, "red energy": 10}
        assert animal.get_blue_energy() == 4
        blue_energy = self.grid.energy_grid.get_position_value(position=blue_cell)
        assert blue_energy != None
        assert self.grid.energy_group.has(blue_energy)
        assert type(blue_energy).__name__ == 'BlueEnergy'
        
        # Drop red energy
        red_cell = (3,2)
        assert self.grid.energy_grid.get_position_value(position=red_cell) == None
        assert animal.get_red_energy() == 10
        animal.drop_energy(energy_type=EnergyType.RED, quantity=3, cell=red_cell)
        assert animal.energies_stock == {"blue energy": 4, "red energy": 7}
        assert animal.get_red_energy() == 7
        red_energy = self.grid.energy_grid.get_position_value(position=red_cell)
        assert red_energy != None
        assert self.grid.energy_group.has(red_energy)
        assert type(red_energy).__name__ == 'RedEnergy'
        
        # Do not drop energy if cell already contains energy
        animal.drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell=red_cell)
        assert animal.energies_stock == {"blue energy": 4, "red energy": 7}
        assert animal.get_blue_energy() == 4
        red_energy2 = self.grid.energy_grid.get_position_value(position=red_cell)
        assert red_energy2 != None
        assert self.grid.energy_group.has(red_energy2)
        assert type(red_energy2).__name__ == 'RedEnergy' 