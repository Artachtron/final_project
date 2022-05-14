from contextlib import redirect_stderr
from tkinter import E
import pytest
import sys, os
import pygame as pg


sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, entities
from project.src.energies import EnergyType
from project.src.grid import Grid

class TestTree:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = Grid(width=5, height=10)
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
    
class TestEntityEnergy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        world.init_pygame()
        self.entity = self.grid.create_entity(size=1, position=(0,0), blue_energy=5, red_energy=10, entity_type="animal")
        yield
    
    def test_loose_energy(self):
        # Loose blue energy
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        self.entity.loose_energy(energy_type=EnergyType.BLUE, quantity=5)
        assert self.entity.energies_stock == {"blue energy": 0, "red energy": 10}
        assert self.entity.get_blue_energy() == 0
        
        # Loose red energy
        self.entity.loose_energy(energy_type=EnergyType.RED, quantity=5)
        assert self.entity.energies_stock == {"blue energy": 0, "red energy": 5}
        assert self.entity.get_red_energy() == 5
        
    def test_drop_energy(self):
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        self.entity.action_cost = 0
        
        # Drop blue energy
        blue_cell = (1,1)
        assert self.grid.energy_grid.get_position_value(position=blue_cell) == None
        self.entity.drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell_coordinates=blue_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 10}
        assert self.entity.get_blue_energy() == 4
        blue_energy = self.grid.energy_grid.get_position_value(position=blue_cell)
        assert blue_energy != None
        assert self.grid.energy_group.has(blue_energy)
        assert type(blue_energy).__name__ == 'BlueEnergy'
        assert blue_energy.quantity == 1
        
        # Drop red energy
        red_cell = (3,2)
        assert self.grid.energy_grid.get_position_value(position=red_cell) == None
        assert self.entity.get_red_energy() == 10
        self.entity.drop_energy(energy_type=EnergyType.RED, quantity=3, cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 7}
        assert self.entity.get_red_energy() == 7
        red_energy = self.grid.energy_grid.get_position_value(position=red_cell)
        assert red_energy != None
        assert self.grid.energy_group.has(red_energy)
        assert type(red_energy).__name__ == 'RedEnergy'
        assert red_energy.quantity == 3
        
        # Drop energy on occupied cell
        self.entity.drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 7}
        assert self.entity.get_blue_energy() == 4
        red_energy2 = self.grid.energy_grid.get_position_value(position=red_cell)
        assert red_energy2 != None
        assert self.grid.energy_group.has(red_energy2)
        assert type(red_energy2).__name__ == 'RedEnergy' 
        assert red_energy.quantity == 3
        
        # Drop too much energy
        red_cell2 = (3,3)
        assert self.grid.energy_grid.get_position_value(position=red_cell2) == None
        assert self.entity.get_red_energy() == 7
        self.entity.drop_energy(energy_type=EnergyType.RED, quantity=10, cell_coordinates=red_cell2)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 0}
        assert self.entity.get_red_energy() == 0
        red_energy2 = self.grid.energy_grid.get_position_value(position=red_cell2)
        assert red_energy2.quantity == 7
        
    def test_actions_cost(self):
        entity = self.entity
        entity.energies_stock['blue energy'] = 10
        
        assert self.entity.get_blue_energy() == 10
        
        entity.move(entities.Direction.LEFT)
        assert self.entity.get_blue_energy() == 9
        
        entity.increase_age()
        assert self.entity.get_blue_energy() == 8
        
        entity.grow()
        assert self.entity.get_blue_energy() == 7
                
        entity.drop_energy(energy_type=EnergyType.RED, quantity=1, cell_coordinates=(1,1))
        assert self.entity.get_blue_energy() == 5
        
        entity.pick_up_energy(cell_coordinates=(1,1))
        assert self.entity.get_blue_energy() == 3

    def test_pick_up_energy(self):
        self.entity.action_cost = 0
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        
        # Blue energy
        blue_cell = (1,1)
        assert self.grid.energy_grid.get_position_value(position=blue_cell) == None
        self.grid.create_energy(energy_type=EnergyType.BLUE, quantity=10, cell_coordinates=blue_cell)
        blue_energy = self.grid.energy_grid.get_position_value(position=blue_cell)
        assert  blue_energy != None
        assert self.grid.energy_group.has(blue_energy)
        
        # Energy picked up
        self.entity.pick_up_energy(cell_coordinates=blue_cell)
        assert self.grid.energy_grid.get_position_value(position=blue_cell) == None
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 10}
        assert self.entity.get_blue_energy() == 15
        assert not self.grid.energy_group.has(blue_energy)
        
        # Red energy
        red_cell = (2,2)
        self.entity.get_red_energy() == 10
        assert self.grid.energy_grid.get_position_value(position=red_cell) == None
        self.grid.create_energy(energy_type=EnergyType.RED, quantity=5, cell_coordinates=red_cell)
        red_energy = self.grid.energy_grid.get_position_value(position=red_cell)
        assert red_energy != None
        assert self.grid.energy_group.has(red_energy)
        
        # Energy picked up
        self.entity.pick_up_energy(cell_coordinates=red_cell)
        assert self.grid.energy_grid.get_position_value(position=red_cell) == None
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 15}
        assert self.entity.get_red_energy() == 15
        assert not self.grid.energy_group.has(red_energy)
        
        # Pick up empty cell
        self.entity.pick_up_energy(cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 15}
        
    def test_grow(self):
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_red_energy() == 10
        assert self.entity.size == 1
        assert self.entity.max_age == self.entity.size*5
        assert self.entity.action_cost == 1
        
        # Grow
        self.entity.grow()
        assert self.entity.get_red_energy() == 0
        assert self.entity.size == 2
        assert self.entity.max_age == 10
        assert self.entity.action_cost == 2
        
    def test_age(self):
        assert self.entity.age == 0
        self.entity.increase_age()
        
        # +1
        assert self.entity.age == 1
        
        # +5
        self.entity.increase_age(amount=4)
        assert self.entity.age == 5
        
        # Above max age
        self.entity.increase_age()
        assert self.grid.entity_grid.get_position_value(position=self.entity.position) == None
        
    def test_die(self):
        assert self.entity
        position = self.entity.position
        assert self.grid.entity_grid.get_position_value(position=position) == self.entity
        assert self.grid.entity_group.has(self.entity)
        
        # Die
        self.entity.die()
        assert self.grid.entity_grid.get_position_value(position=position) == None
        assert not self.grid.entity_group.has(self.entity)
        
    def test_run_out_of_energy(self):
        assert self.grid.entity_group.has(self.entity)
        self.entity.loose_energy(energy_type=EnergyType.BLUE, quantity=5)
        assert not self.grid.entity_group.has(self.entity)