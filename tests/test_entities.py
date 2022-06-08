from hashlib import new
import numpy as np
import pytest
import sys, os
import pygame as pg

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from project.src import world, entities
from project.src.energies import EnergyType
from project.src.entities import EntityType, Entity
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
        tree = entities.Tree(grid=self.grid, position=(3,3), size=10, blue_energy=7, red_energy=3, production_type=EnergyType.BLUE)
        
        assert set(['size', 'position', 'image', 'rect', 'grid', '_energies_stock', 'production_type']).issubset(vars(tree))
               
        assert tree.size == 10
        assert tree.position == (3,3)
        assert tree.entity_grid == self.entity_grid
        assert tree._energies_stock == {EnergyType.BLUE.value: 7, EnergyType.RED.value: 3}
        assert tree.production_type == EnergyType.BLUE
        assert type(tree.image) == pg.Surface
        assert type(tree.rect) == pg.Rect
        
    def test_tree_on_grid(self):
        assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == None
        
        tree = entities.Tree(grid=self.grid, position=(3,3))

        assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == None
        assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == tree
    
    class TestEnergyMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.grid = Grid(width=5, height=10)
            self.entity_grid = self.grid.entity_grid
            world.init_pygame()
            yield
            
        def test_energy_production(self):
            # Red energy
            tree = entities.Tree(grid=self.grid, production_type=EnergyType.RED, position=(0,0), size=1, red_energy=5, blue_energy=5)
            assert tree.get_red_energy() == 5
            assert tree.get_blue_energy() == 5
            tree.produce_energy()
            assert tree.get_red_energy() == 10
            assert tree.get_blue_energy() == 4
            tree.size = 2
            tree.produce_energy()
            assert tree.get_red_energy() == 20
            assert tree.get_blue_energy() == 3
            
            # Blue energy
            tree2 = entities.Tree(grid=self.grid, production_type=EnergyType.BLUE, position=(0,0), size=1, blue_energy=5, red_energy=5, action_cost=0)
            assert tree2.get_blue_energy() == 5
            assert tree2.get_red_energy() == 5
            tree2.produce_energy()
            assert tree2.get_blue_energy() == 10
            assert tree2.get_red_energy() == 5
            tree2.size = 2
            tree2.produce_energy()
            assert tree2.get_blue_energy() == 20
            assert tree2.get_red_energy() == 5
            
            tree3 = entities.Tree(grid=self.grid, production_type=EnergyType.BLUE, position=(1,1), size=1, blue_energy=5, action_cost=0)
            tree2.produce_energy()
            assert tree2.get_blue_energy() == 25
            assert tree2.get_red_energy() == 5
            
            tree4 = entities.Tree(grid=self.grid, production_type=EnergyType.BLUE, position=(0,1), size=1, blue_energy=5, action_cost=0)
            tree2.produce_energy()
            assert tree2.get_blue_energy() == 27
            assert tree2.get_red_energy() == 5
        
        def test_create_seed_on_death(self):
            position = (0,0)
            tree = entities.Tree(grid=self.grid, position=position)
            cell = self.entity_grid.get_cell_value(cell_coordinates=position)
            assert cell.__class__.__name__ == "Tree"
            tree._die()
            cell = self.grid.resource_grid.get_cell_value(cell_coordinates=position)
            assert cell.__class__.__name__ == "Seed"
 
        
class TestSeed:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        world.init_pygame()
        yield
        
    def test_create_seed(self):
        seed = entities.Seed(grid=self.grid, position=(0,0), production_type=EnergyType.BLUE)
        assert type(seed) == entities.Seed
        assert seed.__class__.__base__ == entities.EntitySprite
        
    def test_fields(self):
        seed = entities.Seed(grid=self.grid, position=(3,2), blue_energy=5 ,red_energy=7, production_type=EnergyType.BLUE)
        
        assert set(['size', 'position', 'image', 'rect', 'grid', '_energies_stock']).issubset(vars(seed)) 
        
        assert seed.size == 15
        assert seed.position == (3,2)
        assert seed.entity_grid == self.entity_grid
        assert seed._energies_stock == {EnergyType.BLUE.value: 5, EnergyType.RED.value: 7}   
        assert type(seed.image) == pg.Surface
        assert type(seed.rect) == pg.Rect
        assert type(seed.rect) == pg.Rect
        

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
        animal = entities.Animal(grid=self.grid, position=(3,3), size=10, blue_energy=1, red_energy=8)
        
        assert set(['size', 'position', 'image', 'rect', 'grid', '_energies_stock']).issubset(vars(animal))
               
        assert animal.size == 10
        assert animal.position == (3,3)
        assert animal.entity_grid == self.entity_grid
        assert animal._energies_stock == {EnergyType.BLUE.value: 1, EnergyType.RED.value: 8} 
        assert type(animal.image) == pg.Surface
        assert type(animal.rect) == pg.Rect
        
    def test_animal_on_grid(self):
        assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == None
        
        animal = entities.Animal(grid=self.grid, position=(3,3))

        assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == None
        assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == animal
    
    class TestAnimalMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.grid = world.Grid(width=5, height=10)
            self.entity_grid = self.grid.entity_grid
            world.init_pygame()
            yield   
            
        def test_move(self):
            animal = entities.Animal(grid=self.grid, position=(3,3))
            
            # Down
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == None
            animal.move(entities.Direction.DOWN)
            assert animal.position == (3,4)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == animal
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == None
            
            # Up
            animal.move(entities.Direction.UP)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == animal
            assert self.entity_grid.get_cell_value(cell_coordinates=(2,3)) == None
            
            # Left
            animal.move(entities.Direction.LEFT)
            assert animal.position == (2,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(2,3)) == animal
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == None
            
            # Right
            animal.move(entities.Direction.RIGHT)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,3)) == animal
            
        def test_move_occupied_cell(self):
            animal = entities.Animal(grid=self.grid, position=(3,3))
            animal2 = entities.Animal(grid=self.grid, position=(3,4))
            
            # Move on already occupied cell
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
            animal.move(entities.Direction.DOWN)
            assert animal.position == (3,3)
            assert self.entity_grid.get_cell_value(cell_coordinates=(3,4)) == animal2
            assert animal2.position == (3,4)
            
        def test_move_out_of_bounds_cell(self):
            animal = entities.Animal(grid=self.grid, position=(0,0))
            
            # Left
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(cell_coordinates=(0,0)) == animal
            animal.move(entities.Direction.LEFT)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(cell_coordinates=(0,0)) == animal
            
            # Up
            animal.move(entities.Direction.UP)
            assert animal.position == (0,0)
            assert self.entity_grid.get_cell_value(cell_coordinates=(0,0)) == animal
            
            # Right
            animal2 = entities.Animal(grid=self.grid, position=(4,9))
            assert animal2.position == (4,9)
            assert self.entity_grid.get_cell_value(cell_coordinates=(4,9)) == animal2
            animal2.move(entities.Direction.RIGHT)
            assert animal2.position == (4,9)
            assert self.entity_grid.get_cell_value(cell_coordinates=(4,9)) == animal2
            
            #Down
            animal2.move(entities.Direction.DOWN)
            assert animal2.position == (4,9)
            assert self.entity_grid.get_cell_value(cell_coordinates=(4,9)) == animal2
            
        def test_drop_energy_on_death(self):
            # Drop all energy on death
            animal = self.grid.create_entity(size=1, position=(0,0), blue_energy=5, red_energy=10, entity_type=EntityType.Animal.value)
            animal._die()
                    
            energies = []
            energie_cells = animal._find_energies_cells()
            energies =  [self.grid.resource_grid.get_cell_value(cell_coordinates=energy) for energy in energie_cells]
                            
            assert len(energies) == 2
            blue = 0
            red = 0
            for energy in energies:
                if energy.type.value == EnergyType.BLUE.value:
                    assert energy.quantity == 5 
                    blue += 1
                elif energy.type.value == EnergyType.RED.value:
                    assert energy.quantity == 10  
                    red += 1
            assert (blue,red) == (1,1)
                    
            
            # Drop energy left on death
            for energy in energies:
                self.grid.remove_energy(energy=energy)
                
            animal2 = self.grid.create_entity(size=1, position=(0,0), blue_energy=6, red_energy=10, entity_type=EntityType.Animal.value)
            animal2._action_cost = 0
            animal2._drop_energy(energy_type=EnergyType.RED, quantity=5, cell_coordinates=(4,7))
            animal2._die()
            
            energies = []
            energie_cells = animal2._find_energies_cells()
            energies =  [self.grid.resource_grid.get_cell_value(cell_coordinates=energy) for energy in energie_cells]
                            
            assert len(energies) == 2
            blue = 0
            red = 0
            for energy in energies:
                if energy.type.value == EnergyType.BLUE.value:
                    assert energy.quantity == 6 
                    blue += 1
                elif energy.type.value == EnergyType.RED.value:
                    assert energy.quantity == 5  
                    red += 1
            assert (blue,red) == (1,1)
        
        def test_plant_tree(self):
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=10)
            assert animal.get_red_energy() == 10
            animal.plant_tree()
            assert animal.get_red_energy() == 0
            tree_cell, = animal._find_tree_cells(include_self=True, radius=1)
            tree = self.grid.entity_grid.get_cell_value(cell_coordinates=tree_cell)
            assert tree.__class__.__name__ == "Tree"
            
            # No free cells
            grid2 = Grid(height=1, width=1)
            animal2 = grid2.create_entity(entity_type=EntityType.Animal.value, position=(0,0), size=10, blue_energy=10, red_energy=10)
            animal2.plant_tree()
            assert len(animal2._find_tree_cells(include_self=True, radius=1)) == 0
        
        def test_pick_up_seed(self):
            seed = entities.Seed(grid=self.grid, position=(3,2), blue_energy=5 ,red_energy=7, production_type=EnergyType.BLUE)
            position = seed.position
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=10)
            assert not animal.seed_pocket
            assert self.grid.resource_grid.get_cell_value(cell_coordinates=position) == seed
            
            animal._pick_up_resource(cell_coordinates=position)
            assert animal.seed_pocket == seed
            assert not self.grid.resource_grid.get_cell_value(cell_coordinates=position)
            
        def test_recycle_seed(self):
            seed = entities.Seed(grid=self.grid, position=(3,2), blue_energy=5 ,red_energy=7, production_type=EnergyType.BLUE)
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=10)
            animal.recycle_seed()
            assert len(animal._find_energies_cells()) == 0
            animal._pick_up_resource(cell_coordinates=seed.position)
            
            animal.recycle_seed()
            assert not animal.seed_pocket 
            energie_cells = animal._find_energies_cells(radius=1)
            energies =  [self.grid.resource_grid.get_cell_value(cell_coordinates=energy) for energy in energie_cells]
            assert len(energies) == 2
            
            blue, red = 0, 0
            for energy in energies:
                if energy.type.value == EnergyType.BLUE.value:
                    assert energy.quantity == 5 
                    blue += 1
                elif energy.type.value == EnergyType.RED.value:
                    assert energy.quantity == 7  
                    red += 1
            assert (blue,red) == (1,1)
            
        def test_replant_seed(self):
            tree = entities.Tree(grid=self.grid, position=(3,2), blue_energy=12 ,red_energy=27, max_age=30)
            max_age, blue_energy, red_energy = tree._max_age, tree.get_blue_energy(), tree.get_red_energy()
            tree._die()
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=20)
            animal._pick_up_resource(cell_coordinates=tree.position)
            animal.get_red_energy() == 10
            animal.get_blue_energy() == 10
            animal.plant_tree()
            animal.get_red_energy() == 0
            animal.get_blue_energy() == 9
            
            cell, = animal._find_tree_cells()
            tree = self.grid.entity_grid.get_cell_value(cell_coordinates=cell)
            assert tree._max_age == max_age
            assert tree.get_blue_energy() == blue_energy
            assert tree.get_red_energy() == red_energy
            
            tree._die()
            animal.plant_tree()
            cell, = animal._find_tree_cells()
            tree = self.grid.entity_grid.get_cell_value(cell_coordinates=cell)
            assert not tree._max_age == max_age
            assert not tree.get_blue_energy() == blue_energy
            assert not tree.get_red_energy() == red_energy
            
        def test_modify_cell_color(self):
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=10)
            cell_color = self.grid._color_grid.get_cell_value(cell_coordinates=animal.position)
            assert np.array_equal(cell_color, np.array([255,255,255], dtype=np.uint8))
            
            new_color = tuple(np.random.choice(range(256), size=3))
            animal.modify_cell_color(cell_coordinates=animal.position, color=new_color)
            cell_color = self.grid._color_grid.get_cell_value(cell_coordinates=animal.position)
            assert np.array_equal(cell_color, np.array(new_color, dtype=np.uint8))
            
            new_color2 = tuple(np.random.choice(range(256), size=3))
            animal.modify_cell_color(color=new_color2)
            cell_color = self.grid._color_grid.get_cell_value(cell_coordinates=animal.position)
            assert np.array_equal(cell_color, np.array(new_color2, dtype=np.uint8))
            
        def test_animal_reproduce(self):
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(3,3), size=10, blue_energy=10, red_energy=150)
            mate = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(2,4), size=9, blue_energy=10, red_energy=250)
            
            #Successufull reproduction
            assert animal.get_red_energy() == 150
            assert mate.get_red_energy() == 250
            child = animal.reproduce(mate=mate)
            assert animal.get_red_energy() == 50
            assert mate.get_red_energy() == 160
            
            assert child._adult_size == int((10+9)/2)
            assert child.size == 1
            assert child._age == 0
            assert child.get_red_energy() == entities.Animal.INITIAL_RED_ENERGY
            assert child.get_blue_energy() == entities.Animal.INITIAL_BLUE_ENERGY
            assert child.is_adult == False
            
            # Only 2 adults can reproduce
            none_child = child.reproduce(mate=mate)
            assert child.get_red_energy() == entities.Animal.INITIAL_RED_ENERGY
            assert mate.get_red_energy() == 160
            assert not none_child
            
            # Only happen if both mates have enough energy
            none_child = animal.reproduce(mate=mate)
            assert animal.get_red_energy() == 50
            assert mate.get_red_energy() == 160
            assert not none_child
            
            # Mates should be close enough
            mate.position = (1,1)
            animal._gain_energy(energy_type=EnergyType.RED, quantity=100)
            none_child = animal.reproduce(mate=mate)
            assert not none_child
            assert animal.get_red_energy() == 150
            assert mate.get_red_energy() == 160
                
class TestEntity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.grid = world.Grid(width=5, height=10)
        self.entity_grid = self.grid.entity_grid
        world.init_pygame()
        self.entity = self.grid.create_entity(size=1, position=(0,0), blue_energy=5, red_energy=10, entity_type=EntityType.Animal.value)
        yield
    
    def test_loose_energy(self):
        # Loose blue energy
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        self.entity._loose_energy(energy_type=EnergyType.BLUE, quantity=5)
        assert self.entity.energies_stock == {"blue energy": 0, "red energy": 10}
        assert self.entity.get_blue_energy() == 0
        
        # Loose red energy
        self.entity._loose_energy(energy_type=EnergyType.RED, quantity=5)
        assert self.entity.energies_stock == {"blue energy": 0, "red energy": 5}
        assert self.entity.get_red_energy() == 5
        
    def test_drop_energy(self):
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        self.entity._action_cost = 0
        
        # Drop blue energy
        blue_cell = (1,1)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=blue_cell) == None
        self.entity._drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell_coordinates=blue_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 10}
        assert self.entity.get_blue_energy() == 4
        blue_energy = self.grid.resource_grid.get_cell_value(cell_coordinates=blue_cell)
        assert blue_energy != None
        assert self.grid.energy_group.has(blue_energy)
        assert type(blue_energy).__name__ == 'BlueEnergy'
        assert blue_energy.quantity == 1
        
        # Drop red energy
        red_cell = (3,2)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell) == None
        assert self.entity.get_red_energy() == 10
        self.entity._drop_energy(energy_type=EnergyType.RED, quantity=3, cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 7}
        assert self.entity.get_red_energy() == 7
        red_energy = self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell)
        assert red_energy != None
        assert self.grid.energy_group.has(red_energy)
        assert type(red_energy).__name__ == 'RedEnergy'
        assert red_energy.quantity == 3
        
        # Drop energy on occupied cell
        self.entity._drop_energy(energy_type=EnergyType.BLUE, quantity=1, cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 7}
        assert self.entity.get_blue_energy() == 4
        red_energy2 = self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell)
        assert red_energy2 != None
        assert self.grid.energy_group.has(red_energy2)
        assert type(red_energy2).__name__ == 'RedEnergy' 
        assert red_energy.quantity == 3
        
        # Drop too much energy
        red_cell2 = (3,3)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell2) == None
        assert self.entity.get_red_energy() == 7
        self.entity._drop_energy(energy_type=EnergyType.RED, quantity=10, cell_coordinates=red_cell2)
        assert self.entity.energies_stock == {"blue energy": 4, "red energy": 0}
        assert self.entity.get_red_energy() == 0
        red_energy2 = self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell2)
        assert red_energy2.quantity == 7
        
    def test_actions_cost(self):
        entity = self.entity
        entity.energies_stock['blue energy'] = 10
        entity.energies_stock['red energy'] = 100
        
        assert self.entity.get_blue_energy() == 10
        
        entity.move(entities.Direction.LEFT)
        assert self.entity.get_blue_energy() == 9
        
        entity.plant_tree()
        assert self.entity.get_blue_energy() == 8
        
        entity._grow()
        assert self.entity.get_blue_energy() == 7
        assert self.entity._action_cost == 2
                
        entity._drop_energy(energy_type=EnergyType.RED, quantity=1, cell_coordinates=(1,1))
        assert self.entity.get_blue_energy() == 5
        
        entity._pick_up_resource(cell_coordinates=(1,1))
        assert self.entity.get_blue_energy() == 3

    def test_pick_up_energy(self):
        self.entity._action_cost = 0
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_blue_energy() == 5
        
        # Blue energy
        blue_cell = (1,1)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=blue_cell) == None
        self.grid.create_energy(energy_type=EnergyType.BLUE, quantity=10, cell_coordinates=blue_cell)
        blue_energy = self.grid.resource_grid.get_cell_value(cell_coordinates=blue_cell)
        assert  blue_energy != None
        assert self.grid.energy_group.has(blue_energy)
        
        # Energy picked up
        self.entity._pick_up_resource(cell_coordinates=blue_cell)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=blue_cell) == None
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 10}
        assert self.entity.get_blue_energy() == 15
        assert not self.grid.energy_group.has(blue_energy)
        
        # Red energy
        red_cell = (2,2)
        self.entity.get_red_energy() == 10
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell) == None
        self.grid.create_energy(energy_type=EnergyType.RED, quantity=5, cell_coordinates=red_cell)
        red_energy = self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell)
        assert red_energy != None
        assert self.grid.energy_group.has(red_energy)
        
        # Energy picked up
        self.entity._pick_up_resource(cell_coordinates=red_cell)
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=red_cell) == None
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 15}
        assert self.entity.get_red_energy() == 15
        assert not self.grid.energy_group.has(red_energy)
        
        # Pick up empty cell
        self.entity._pick_up_resource(cell_coordinates=red_cell)
        assert self.entity.energies_stock == {"blue energy": 15, "red energy": 15}
        
    def test_pick_up_seed(self):
        seed = self.grid.create_entity(entity_type=EntityType.Seed.value, position=(1,1))
        position = seed.position
        assert self.entity.seed_pocket == None
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=position) == seed
        self.entity._pick_up_resource(cell_coordinates=position)
        assert self.entity.seed_pocket == seed
        assert self.grid.resource_grid.get_cell_value(cell_coordinates=position) == None
        
        # Can't pick up another seed
        seed2 = self.grid.create_entity(entity_type=EntityType.Seed.value, position=(1,2))
        self.entity._pick_up_resource(cell_coordinates=seed2.position)
        assert self.entity.seed_pocket != seed2
        assert self.entity.seed_pocket == seed
        
    def test_grow(self):
        assert self.entity.energies_stock == {"blue energy": 5, "red energy": 10}
        assert self.entity.get_red_energy() == 10
        assert self.entity.size == 1
        assert self.entity._max_age == self.entity.size*5
        assert self.entity._action_cost == 1
        
        # Grow
        self.entity._grow()
        assert self.entity.get_red_energy() == 0
        assert self.entity.size == 2
        assert self.entity._max_age == 10
        assert self.entity._action_cost == 2
        
    def test_age(self):
        assert self.entity._age == 0
        self.entity._increase_age()
        
        # +1
        assert self.entity._age == 1
        
        # +5
        self.entity._increase_age(amount=4)
        assert self.entity._age == 5
        
        # Above max age
        self.entity._increase_age()
        assert self.grid.entity_grid.get_cell_value(cell_coordinates=self.entity.position) == None
        
    def test_die(self):
        assert self.entity
        position = self.entity.position
        assert self.grid.entity_grid.get_cell_value(cell_coordinates=position) == self.entity
        assert self.grid.entity_group.has(self.entity)
        
        # Die
        self.entity._die()
        assert self.grid.entity_grid.get_cell_value(cell_coordinates=position) == None
        assert not self.grid.entity_group.has(self.entity)
        
    def test_run_out_of_energy(self):
        assert self.grid.entity_group.has(self.entity)
        self.entity._loose_energy(energy_type=EnergyType.BLUE, quantity=5)
        assert not self.grid.entity_group.has(self.entity)
        
    def test_reached_adulthood(self):
        entity = self.grid.create_entity(size=1, position=(0,0), blue_energy=5, red_energy=100, entity_type=EntityType.Animal.value, adult_size=2)
        assert not entity.is_adult 
        assert entity.size == 1
        assert entity.get_red_energy() == 100
        entity._grow()
        red_energy = 100 - (entity.size-1) * entities.Entity.CHILD_GROWTH_ENERGY_REQUIRED
        assert entity.get_red_energy() == red_energy
        assert entity.size == 2
        assert entity.is_adult
        entity._grow()
        assert entity.get_red_energy() == red_energy - (entity.size-1) * entities.Entity.GROWTH_ENERGY_REQUIRED
        assert entity.size == 3
        assert entity.is_adult
        
    class TestEntityPrivateMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            self.grid = world.Grid(width=5, height=10)
            self.entity_grid = self.grid.entity_grid
            world.init_pygame()
            self.entity = self.grid.create_entity(size=1, position=(1,1), blue_energy=5, red_energy=10, entity_type=EntityType.Animal.value)
            yield
            
        def test_find_free_cells(self):
            cells = []
            position = self.entity.position
            radius = 1
            for x in range(-radius,radius+1):
                for y in range(-radius,radius+1):
                    cells.append(tuple(np.add(position,(x,y))))
            
            for _ in range(100):
                free_cell = self.entity._select_free_cell(subgrid=self.grid.resource_grid,radius=radius)
                assert free_cell in cells
                
            position = (3,5)
            self.entity.position = position
            radius = 2
            cells = []
            for x in range(-radius,radius+1):
                for y in range(-radius,radius+1):
                    cells.append(tuple(np.add(position,(x,y))))
            
            for _ in range(100):
                free_cell = self.entity._select_free_cell(subgrid=self.grid.resource_grid,radius=radius)
                assert free_cell 
                assert free_cell in cells
                
        def test_find_tree_cells(self):
            tree1 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(1,1))
            assert len(tree1._find_tree_cells()) == 0
            tree2 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(2,1))
            
            assert len(tree1._find_tree_cells())  == 1       
            assert len(tree1._find_tree_cells(include_self=True))  == 2
            
            # Does not detect animal
            animal = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(1,2))
            assert len(tree1._find_tree_cells())  == 1
            
            # Handle error if animal and not tree
            assert len(animal._find_tree_cells())  == 2
            assert len(animal._find_tree_cells(include_self=True))  == 2
            
        def test_find_animal_cells(self):
            animal1 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(1,1))
            assert len(animal1._find_animal_cells())  == 0
            animal2 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(2,1))
            
            assert len(animal1._find_animal_cells())  == 1       
            assert len(animal1._find_animal_cells(include_self=True))  == 2
            
            # Does not detect animal
            tree = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(1,2))
            assert len(animal1._find_animal_cells())  == 1
            
            # Handle error if animal and not tree
            assert len(tree._find_animal_cells())  == 2
            assert len(tree._find_animal_cells(include_self=True))  == 2
            
        def test_find_entity_cells(self):
            tree1 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(1,1))
            assert len(tree1._find_entities_cells()) == 0
            
            tree2 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(2,1))
            assert len(tree1._find_entities_cells()) == 1
            animal1 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(1,2))
            assert len(tree1._find_entities_cells()) == 2
            animal2 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(2,2))
            
            assert len(tree1._find_entities_cells()) == 3      
            assert len(tree1._find_entities_cells(include_self=True)) == 4

        def test_find_occupied_cells_by_entities(self):
            animal = self.grid.create_entity(EntityType.Animal.value ,position=(2,2))
            self.grid.create_entity(EntityType.Animal.value ,position=(2,3))
            self.grid.create_entity(EntityType.Animal.value ,position=(2,1))
            self.grid.create_entity(EntityType.Tree.value ,position=(3,2))
   
            assert len(animal._find_entities_cells()) == 4
            result = [True, False, False, True, True, False, True, False]
            assert (animal._find_occupied_cells_by_entities() == np.array(result)).all()
            
            
        def test_find_occupied_cells_by_energies(self):
            animal = self.grid.create_entity(EntityType.Animal.value ,position=(2,2))
            self.grid.create_energy(energy_type=EnergyType.RED, quantity=10, cell_coordinates=(1,1))
            self.grid.create_energy(energy_type=EnergyType.BLUE, quantity=10, cell_coordinates=(2,3))
            self.grid.create_energy(energy_type=EnergyType.RED, quantity=10, cell_coordinates=(2,1))
            self.grid.create_energy(energy_type=EnergyType.BLUE, quantity=10, cell_coordinates=(3,2))

            assert len(animal._find_energies_cells()) == 4
            result = [True, False, False, True, True, False, True, False]
            assert (animal._find_occupied_cells_by_energies() == np.array(result)).all()
            
        def test_distance_between_objects(self):
            animal1 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(1,1))
            animal2 = self.grid.create_entity(entity_type=EntityType.Animal.value, position=(2,1))
            distance = animal1._distance_to_object(distant_object=animal2)
            assert distance == 1.0
            
            tree1 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(5,1))
            tree2 = self.grid.create_entity(entity_type=EntityType.Tree.value, position=(2,3))
            distance = tree1._distance_to_object(distant_object=tree2)
            assert distance == 3.61
            
        
    