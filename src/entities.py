import re
from types import NoneType
import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from typing import Tuple, Set, Final
import enum
import random
from energies import EnergyType, Energy, BlueEnergy, RedEnergy
import numpy as np


assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets/models/entities")

class Direction(enum.Enum):
    RIGHT = (1,0)
    LEFT = (-1,0)
    DOWN = (0,1)
    UP = (0,-1)
    
class EntityType(enum.Enum):
    Animal = "animal"
    Tree = "tree"
    Seed = "seed"

class EntitySprite(pg.sprite.Sprite):
    def __init__(self,
                 image_filename: str,
                 grid,
                 position: Tuple[int,int],
                 size: int=20,
                 blue_energy: int=10,
                 red_energy: int=10,
                 ):
        super().__init__()
        self.position = position
        image = pg.image.load(join(assets_path, image_filename)).convert_alpha()
        self.size = size
        self.image = pg.transform.scale(image, (size,size))
        pos_x, pos_y = self.position
        self.rect = self.image.get_rect(center=(pos_x * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2, pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2))
        
        self._energies_stock = {EnergyType.BLUE.value: blue_energy, EnergyType.RED.value: red_energy}
        
        self.grid = grid
        self.entity_grid = grid.entity_grid
        
    @property
    def energies_stock(self):
        return self._energies_stock

    def get_blue_energy(self):
        return self._energies_stock["blue energy"]
    
    def get_red_energy(self):
        return self._energies_stock["red energy"]

class Seed(EntitySprite):
    def __init__(self,
                 grid,
                 position: Tuple[int,int],
                 production_type: EnergyType, 
                 max_age: int=0,
                 size: int=15,
                 blue_energy: int=0,
                 red_energy: int=0,
                 ):
        super(Seed, self).__init__(image_filename="Seed.png", size=size, grid=grid, position=position, blue_energy=blue_energy, red_energy=red_energy)
        self.grid.resource_grid.set_cell_value(cell_coordinates=(self.position), value=self)
        self.max_age = max_age if max_age else size*5
        self.production_type = production_type           
   
class Entity(EntitySprite):
    def __init__(self,
                 image_filename: str,
                 grid,
                 position: Tuple[int,int],
                 max_age: int = 0,
                 size: int=20,
                 action_cost: int=1,
                 blue_energy: int=10,
                 red_energy: int=10,
                 ):
        super(Entity, self).__init__(image_filename=image_filename, size=size, grid=grid, position=position, blue_energy=blue_energy, red_energy=red_energy)
        
        self.action_cost = action_cost
        self.age = 0
        self.max_age = max_age if max_age else size*5
        
        self.entity_grid.set_cell_value(cell_coordinates=(self.position), value=self)
        
    
    def drop_energy(self, energy_type: EnergyType, quantity: int, cell_coordinates: Tuple[int,int]) -> None:
        """Drop some energy on a cell

        Args:
            energy_type (EnergyType): the type of energy (blue/red) to drop
            quantity (int): the amount of energy to drop
            cell_coordinates (Tuple[int,int]): the coordinates of the cell on which to drop energy
        """        
        if self._check_coordinates(cell_coordinates=cell_coordinates, subgrid=self.grid.resource_grid):
            quantity = self.loose_energy(energy_type=energy_type, quantity=quantity)   
                
            self.grid.create_energy(energy_type=energy_type, quantity=quantity, cell_coordinates=cell_coordinates)
            
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
            
    def pick_up_resource(self, cell_coordinates: Tuple[int, int]) -> None:
        """Pick energy up from a cell

        Args:
            cell_coordinates (Tuple[int, int]): coordinates of the cell from which to pick up energy
        """
        resource_grid = self.grid.resource_grid
        resource = resource_grid.get_cell_value(cell_coordinates=cell_coordinates)
        if resource:
            if type(resource).__base__ == Energy:
                self.gain_energy(energy_type=resource.type, quantity=resource.quantity)     
            elif resource.__class__.__name__ == "Seed" and type(self) == Animal:
                self.store_seed(seed=resource)
            self.grid.remove_energy(energy=resource)
            
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
                        
    def gain_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Gain energy from specified type to energies stock

        Args:
            energy_type (EnergyType): the type of energy to gain
            quantity (int): amount of energy to gain
        """        
        self._energies_stock[energy_type.value] += quantity
    
    def loose_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Loose energy of specified type from energies stock

        Args:
            energy_type (EnergyType): the type of energy to loose
            quantity (int): amount of energy to loose
        """
        energy_amount = self._energies_stock[energy_type.value]
        if energy_amount - quantity > 0:
            self._energies_stock[energy_type.value] -= quantity
        else:
            quantity = energy_amount
            self._energies_stock[energy_type.value] = 0 
        
        if self._energies_stock[EnergyType.BLUE.value] <= 0:
            self.die()
            
        return quantity
            
    def grow(self) -> None:
        """grow the entity to bigger size, consumming red energy
        """  
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)      
        energy_required = self.size * 10
        if self.energies_stock[EnergyType.RED.value] >= energy_required:
            self.loose_energy(energy_type=EnergyType.RED, quantity=energy_required)
            self.size += 1
            self.max_age += 5
            self.action_cost += 1
            
    def increase_age(self, amount: int=1) -> None:
        """Increase age of certain amount

        Args:
            amount (int, optional): amount to increase age by. Defaults to 1.
        """        
        self.age += amount
       # self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
        
        if self.age > self.max_age:
            self.die()
        
    def die(self) -> None:
        """Death of the entity
        """
        self.grid.remove_entity(entity=self)
        self.on_death()
        
        print(f"{self} died at age {self.age}")    
        
    def _check_coordinates(self, cell_coordinates: Tuple[int,int], subgrid) -> bool:
        """Check if the next move is valid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Validity of the next move
        """
        return self._is_cell_in_bounds(next_move=cell_coordinates, subgrid=subgrid) and self._is_vacant_cell(next_move=cell_coordinates, subgrid=subgrid)
     
    def _is_vacant_cell(self, subgrid, next_move: Tuple[int,int])-> bool:
        """Check if a cell is vacant

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Vacancy of the cell
        """
        return not subgrid.get_cell_value(cell_coordinates=next_move)
     
    def _is_cell_in_bounds(self, subgrid, next_move: Tuple[int,int])-> bool:
        """Check if a cell is in the bounds of the grid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Cell is inside the grid
        """
        next_x, next_y = next_move
        if next_x < 0 or next_x >= subgrid.dimensions[0] or next_y < 0 or next_y >= subgrid.dimensions[1]:
            return False
        return True
    
    def _find_cells_by_value(self, subgrid, value, radius: int=1) -> Set[Tuple[int,int]]:
        """Find the list of cells in a range with specified value

        Args:
            subgrid (_type_): subgrid to look for cells
            value (_type_): value to search for
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found cells' coordinates
        """        
        position = self.position
        cells =  set()
        for x in range(-radius,radius+1):
            for y in range(-radius,radius+1):
                coordinate = tuple(np.add(position,(x,y)))
                if issubclass(type(subgrid.get_cell_value(cell_coordinates=coordinate)),value):
                    cells.add(coordinate)
                    
        return cells
    
    def _find_tree_cells(self, include_self: bool=False, radius: int=1) -> Set[Tuple[int,int]]:
        """Find the cells at proximity on which trees are located

        Args:
            include_self (bool, optional): include self in the list. Defaults to False.
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found trees' cells' coordinates
        """        
        trees: Set[Tuple[int,int]] = self._find_cells_by_value(subgrid=self.entity_grid, value=Tree, radius=radius)
        if not include_self and self.position in trees:
            trees.remove(self.position)
        return trees
    
    def _find_animal_cells(self, include_self: bool=False, radius: int=1) -> Set[Tuple[int,int]]:
        """Find the cells at proximity on which animals are located

        Args:
            include_self (bool, optional): include self in the list. Defaults to False.
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found animals' cells' coordinates
        """        
        animals: Set[Tuple[int,int]] = self._find_cells_by_value(subgrid=self.entity_grid, value=Animal, radius=radius)
        if not include_self and self.position in animals:
            animals.remove(self.position)
        return animals
    
    def _find_energy_cells(self, radius: int=1) -> Set[Tuple[int,int]]:
        """Find cells at proximity on which energies are located

        Args:
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found energies' cells' coordinates
        """
        energies: Set[Tuple[int,int]] = self._find_cells_by_value(subgrid=self.grid.resource_grid, value=Energy, radius=radius)
        return energies
    
    def _find_free_cells(self, subgrid, radius: int=1) -> Set[Tuple[int,int]]:
        """Find a free cell in range

        Args:
            subgrid (_type_): subgrid to look for free cells
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of free cells' coordinates
        """        
        return self._find_cells_by_value(subgrid=subgrid, value=NoneType, radius=radius)
        
    def select_free_cell(self, subgrid, radius: int=1) -> Tuple[int,int]:
        """Select randomly from the free cells available
        
        Args:
            subgrid (_type_): subgrid to look for free cell
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Tuple[int,int]: coordinates of the free cell
        """ 
        free_cells: Set[Tuple[int,int]] = self._find_free_cells(subgrid=subgrid, radius=radius)    
                    
        if len(free_cells) != 0:    
            return random.choice(tuple(free_cells))
        return None
    
    def decompose(self, entity: EntitySprite) -> None:
        """decompose an entity into its energy components

        Args:
            entity (EntitySprite): entity to decompose in energy
        """        
        resource_grid = self.grid.resource_grid
        free_cell = self.select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.RED, quantity=entity.energies_stock[EnergyType.RED.value], cell_coordinates=free_cell)
        free_cell = self.select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.BLUE, quantity=entity.energies_stock[EnergyType.BLUE.value], cell_coordinates=free_cell)         
       
    def update(self):
        self.increase_age()
        self.test_update()

class Animal(Entity):
    def __init__(self, *args, **kwargs):
        super(Animal, self).__init__(image_filename='Animal.png',*args, **kwargs)
        self.seed_pocket = None
        
    def move(self, direction: Direction) -> None:
        """Move the animal in the given direction

        Args:
            direction (Direction): direction in which to move
        """
        next_move = tuple(np.add(self.position, direction.value))
        if self._check_coordinates(cell_coordinates=next_move, subgrid=self.grid.entity_grid):
            self.entity_grid.set_cell_value(cell_coordinates=(self.position), value=None)
            self.entity_grid.set_cell_value(cell_coordinates=next_move, value=self)
            self.position = next_move
                   
            self.rect.x = next_move[0]  * self.grid.BLOCK_SIZE
            self.rect.y = next_move[1]  * self.grid.BLOCK_SIZE
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
    
    def plant_tree(self) -> None:
        """Plant a tree nearby, consume red energy
        """        
        PLANTING_COST: Final[int] = 10
        if self._energies_stock[EnergyType.RED.value] >= PLANTING_COST:
            self.loose_energy(energy_type=EnergyType.RED, quantity=PLANTING_COST)
       
            free_cell = self.select_free_cell(subgrid=self.entity_grid)
            if free_cell:
                if self.seed_pocket:
                    self.replant_seed(position=free_cell)
                else:
                    self.grid.create_entity(entity_type="tree", position=free_cell)
                
            self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
 
    def replant_seed(self, position: Tuple[int, int]) -> None:
        """Replant seed store in pockect

        Args:
            position (Tuple[int, int]): cell coordinates on which to plant seed
        """
        if not self.seed_pocket:
            return
        seed = self.seed_pocket
        self.grid.create_entity(entity_type="tree",
                                position=position,
                                blue_energy=seed.get_blue_energy(),
                                red_energy=seed.get_red_energy(),
                                max_age=seed.max_age,
                                production_type=seed.production_type)
        self.seed_pocket = None
        
    def store_seed(self, seed: Seed)-> None: 
        """Pick up a seed and stor it"""
        if not self.seed_pocket:
            self.seed_pocket = seed
        
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
    
    def recycle_seed(self) -> None:
        """Destroy seed stored and drop energy content
        """        
        if not self.seed_pocket:
            return
    
        self.decompose(self.seed_pocket)
        self.seed_pocket = None
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)        
                  
    def on_death(self) -> None:
        """Action on animal death, release energy on cells around death position"""
        self.decompose(entity=self)
                    
    def modify_cell_color(self, color: Tuple[int,int,int], cell_coordinates: Tuple[int, int]=None) -> None:
        """Modfify the color of a given cell, usually the cell currently sat on

        Args:
            color (Tuple[int,int,int]): color to apply
            cell_coordinates (Tuple[int, int], optional): the coordinates of the cell to modify. Defaults to None.
        """        
        cell_coordinates = cell_coordinates if cell_coordinates else self.position
        self.grid.color_grid.set_cell_value(cell_coordinates=cell_coordinates, value=color)
        
        self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)
            
    def test_update(self) -> None:
        """Test behaviour by doing random actions"""
        direction = random.choice(list(Direction))
        #print(direction)
        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2,2), np.random.randint(-2,2)
            coordinates = tuple(np.add(self.position, (x,y)))
            if self._check_coordinates(cell_coordinates=coordinates,
                                       subgrid=self.grid.resource_grid):
                self.drop_energy(energy_type=np.random.choice(EnergyType),
                                 cell_coordinates=coordinates,
                                 quantity=1)
                
        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2,2), np.random.randint(-2,2)
            coordinates = tuple(np.add(self.position, (x,y)))
            self.pick_up_resource(cell_coordinates=coordinates)
        
        if np.random.uniform() < 0.1:
            color = tuple(np.random.choice(range(256), size=3))
            self.modify_cell_color(cell_coordinates=self.position,
                                   color=color)
        
        #self.die()
        self.move(direction=direction)
        
class Tree(Entity):
    def __init__(self,
                 production_type: EnergyType=None,
                 *args,
                 **kwargs
                 ):
        super(Tree, self).__init__(image_filename='Plant.png',*args, **kwargs)
        self.production_type = production_type if production_type else np.random.choice(list(EnergyType))
        
    def produce_energy(self) -> None:
        """Produce energy
        """
        MINUMUM_AGE: Final[int] = 20
        if self.age < MINUMUM_AGE:
            pass
        
        count_trees_around = len(self._find_tree_cells())
        
        self.gain_energy(energy_type=self.production_type,
                         quantity=int((5*self.size)/2**count_trees_around))
        self.loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self.action_cost)
        
    def on_death(self) -> None:
        """Action on tree death, create a seed on dead tree position"""
        self.grid.create_entity(entity_type="seed",
                                position=self.position,
                                blue_energy=self.get_blue_energy(),
                                red_energy=self.get_red_energy(),
                                max_age=self.max_age)
    
    def test_update(self):
        pass

       



        
 


