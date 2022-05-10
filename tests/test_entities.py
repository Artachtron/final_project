import pytest
import sys, os
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, entities

class TestTree:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
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
        assert tree.grid == self.grid
        assert type(tree.image) == pg.Surface
        assert type(tree.rect) == pg.Rect
        
    def test_tree_on_grid(self):
        assert self.grid.get_position_value(position=(3,3)) == 0
        
        entities.Tree(grid=self.grid, position=(3,3))

        assert self.grid.get_position_value(position=(3,4)) == 0
        assert self.grid.get_position_value(position=(3,3)) == 1

class TestAnimal:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
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
        assert animal.grid == self.grid
        assert type(animal.image) == pg.Surface
        assert type(animal.rect) == pg.Rect
        
    def test_animal_on_grid(self):
        assert self.grid.get_position_value(position=(3,3)) == 0
        
        animal = entities.Animal(grid=self.grid, position=(3,3))

        assert self.grid.get_position_value(position=(3,4)) == 0
        assert self.grid.get_position_value(position=(3,3)) == 1
        
    def test_move(self):
        animal = entities.Animal(grid=self.grid, position=(3,3))
        
        assert animal.position == (3,3)
        assert self.grid.get_position_value(position=(3,4)) == 0
        animal.move(entities.Direction.DOWN)
        assert animal.position == (3,4)
        assert self.grid.get_position_value(position=(3,4)) == 1
        assert self.grid.get_position_value(position=(3,3)) == 0
        animal.move(entities.Direction.UP)
        assert animal.position == (3,3)
        assert self.grid.get_position_value(position=(3,3)) == 1
        assert self.grid.get_position_value(position=(2,3)) == 0
        animal.move(entities.Direction.LEFT)
        assert animal.position == (2,3)
        assert self.grid.get_position_value(position=(2,3)) == 1
        assert self.grid.get_position_value(position=(3,3)) == 0
        animal.move(entities.Direction.RIGHT)
        assert animal.position == (3,3)
        assert self.grid.get_position_value(position=(3,3)) == 1
        
    def test_move_occupied_cell(self):
        animal = entities.Animal(grid=self.grid, position=(3,3))
        animal2 = entities.Animal(grid=self.grid, position=(3,4))
        
        assert animal.position == (3,3)
        assert self.grid.get_position_value(position=(3,4)) == 1
        assert animal2.position == (3,4)
        animal.move(entities.Direction.DOWN)
        assert animal.position == (3,3)
        assert self.grid.get_position_value(position=(3,4)) == 1
        assert animal2.position == (3,4)
        
    def test_move_out_of_bounds_cell(self):
        animal = entities.Animal(grid=self.grid, position=(0,0))
        
        assert animal.position == (0,0)
        assert self.grid.get_position_value(position=(0,0)) == 1
        animal.move(entities.Direction.LEFT)
        assert animal.position == (0,0)
        assert self.grid.get_position_value(position=(0,0)) == 1
        
        animal.move(entities.Direction.UP)
        assert animal.position == (0,0)
        assert self.grid.get_position_value(position=(0,0)) == 1
        
        animal2 = entities.Animal(grid=self.grid, position=(4,9))
        assert animal2.position == (4,9)
        assert self.grid.get_position_value(position=(4,9)) == 1
        animal2.move(entities.Direction.RIGHT)
        assert animal2.position == (4,9)
        assert self.grid.get_position_value(position=(4,9)) == 1
        animal2.move(entities.Direction.DOWN)
        assert animal2.position == (4,9)
        assert self.grid.get_position_value(position=(4,9)) == 1