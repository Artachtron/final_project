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
        
    def test_tree_fields(self):
        tree = entities.Tree(grid=self.grid, position=(3,3), size=10)
        
        assert set(['size', 'position', 'image', 'rect', 'grid']).issubset(vars(tree))
               
        assert tree.size == 10
        assert tree.position == (3,3)
        assert tree.grid == self.grid
        assert type(tree.image) == pg.Surface
        assert type(tree.rect) == pg.Rect
        
    def test_tree_on_grid(self):
        assert self.grid.get_position_value(position=(3,3)) == 0
        
        tree = entities.Tree(grid=self.grid, position=(3,3))

        assert self.grid.get_position_value(position=(3,4)) == 0
        assert self.grid.get_position_value(position=(3,3)) == 1
