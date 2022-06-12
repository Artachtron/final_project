from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid, SubGrid
    
from config import WorldTable    
import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from typing import Tuple, Set, Final
from types import NoneType
import enum
import random
from energies import EnergyType, Energy
import numpy as np
import sys, os
from itertools import combinations

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rtNEAT')))
from project.src.rtNEAT.organism import Organism
from project.src.rtNEAT.genome import Genome

assets_path = join(
    Path(
        dirname(
            realpath(__file__))).parent.absolute(),
    "assets/models/entities")


class Direction(enum.Enum):
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    UP = (0, -1)


class EntityType(enum.Enum):
    Animal = "animal"
    Tree = "tree"
    Seed = "seed"


class EntitySprite(pg.sprite.Sprite):
    def __init__(self,
                 image_filename: str,
                 grid,
                 position: Tuple[int, int],
                 size: int = 20,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 ):
        super().__init__()
        self.position: Tuple[int, int] = position
        image: pg.Surface = pg.image.load(
            join(assets_path,
                image_filename)).convert_alpha()
        self.size: int = size
        self.image: pg.Surface = pg.transform.scale(image, (size, size))
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(
            center=(pos_x *grid.BLOCK_SIZE + grid.BLOCK_SIZE /2,
                pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE /2))

        self._energies_stock: dict[EnergyType, int] = {
            EnergyType.BLUE.value: blue_energy,
            EnergyType.RED.value: red_energy}

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
                 position: Tuple[int, int],
                 production_type: EnergyType,
                 max_age: int = 0,
                 size: int = 15,
                 blue_energy: int = 0,
                 red_energy: int = 0,
                 ):
        super(Seed, self).__init__(image_filename="Seed.png",
                                   size=size,
                                   grid=grid,
                                   position=position,
                                   blue_energy=blue_energy,
                                   red_energy=red_energy)
        self.grid.resource_grid.set_cell_value(
            cell_coordinates=(self.position), value=self)
        self._max_age = max_age if max_age else size * 5
        self.production_type = production_type


class Entity(EntitySprite):
    MAX_AGE_SIZE_COEFFICIENT: Final[int] = 5
    GROWTH_ENERGY_REQUIRED: Final[int] = 10
    CHILD_ENERGY_COST_DIVISOR: Final[int] = 2
    CHILD_GROWTH_ENERGY_REQUIRED: Final[int] = GROWTH_ENERGY_REQUIRED/CHILD_ENERGY_COST_DIVISOR
    
    def __init__(self,
                 image_filename: str,
                 grid: Grid,
                 position: Tuple[int, int],
                 entitiy_id: int = None,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = 20,
                 action_cost: int = 1,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 ):
        super(Entity, self).__init__(image_filename=image_filename,
                                     size=size,
                                     grid=grid,
                                     position=position,
                                     blue_energy=blue_energy,
                                     red_energy=red_energy)

        self.id = entitiy_id or WorldTable.get_organism_id(increment=True)
        self.organism = self._create_organism() 
               
        self._age: int = 0
        self._max_age: int = max_age if max_age else size * Entity.MAX_AGE_SIZE_COEFFICIENT
        self._adult_size: int = adult_size
        self._reached_adulthood()

        self.entity_grid.set_cell_value(cell_coordinates=(self.position),
                                        value=self)
        
        
        self._action_cost: int = action_cost if self.is_adult else action_cost
        
        
    def _create_organism(self):
        organism = Organism(organism_id=self.id,
                        genome=Genome(genome_id=self.id),
                        generation = 0,
                        entity=self)
        
        return organism
        
    
    def _reached_adulthood(self) -> None:
        """Check if the entity reached maturity size and assign the result in the is_adult instance variable
        """
        self.is_adult = self.size >= self._adult_size
   
    def _drop_energy(self, energy_type: EnergyType, quantity: int,
                    cell_coordinates: Tuple[int, int]) -> None:
        """Drop some energy on a cell

        Args:
            energy_type (EnergyType):           type of energy (blue/red) to drop
            quantity (int):                      amount of energy to drop
            cell_coordinates (Tuple[int,int]):  coordinates of the cell on which to drop energy
        """
        if self._check_coordinates(
                cell_coordinates=cell_coordinates,
                subgrid=self.grid.resource_grid):
            quantity = self._loose_energy(
                energy_type=energy_type, quantity=quantity)

            self.grid.create_energy(
                energy_type=energy_type,
                quantity=quantity,
                cell_coordinates=cell_coordinates)

        self._perform_action()

    def _pick_up_resource(self, cell_coordinates: Tuple[int, int]) -> None:
        """Pick energy up from a cell

        Args:
            cell_coordinates (Tuple[int, int]): coordinates of the cell from which to pick up energy
        """
        resource_grid = self.grid.resource_grid
        resource = resource_grid.get_cell_value(
            cell_coordinates=cell_coordinates)
        if resource:
            if type(resource).__base__ == Energy:
                self._gain_energy(
                    energy_type=resource.type,
                    quantity=resource.quantity)
            elif resource.__class__.__name__ == "Seed" and isinstance(self, Animal):
                self.store_seed(seed=resource)
            self.grid.remove_energy(energy=resource)

        self._perform_action()

    def _gain_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Gain energy from specified type to energies stock

        Args:
            energy_type (EnergyType):   type of energy to gain
            quantity (int):             amount of energy to gain
        """
        self._energies_stock[energy_type.value] += quantity

    def _perform_action(self):
        self._loose_energy(
            energy_type=EnergyType.BLUE,
            quantity=self._action_cost)
    
    def _loose_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Loose energy of specified type from energies stock

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose
        """
        energy_amount = self._energies_stock[energy_type.value]
        if energy_amount - quantity > 0:
            self._energies_stock[energy_type.value] -= quantity
        else:
            quantity = energy_amount
            self._energies_stock[energy_type.value] = 0

        if self._energies_stock[EnergyType.BLUE.value] <= 0:
            self._die()

        return quantity

    def _can_perform_action(self, energy_type: EnergyType, quantity: int) -> bool:
        """Check if the entity has enough energy to perform an action, use the energy if it's the case

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose

        Returns:
            bool: if the entity had enough energy
        """        
        if self.energies_stock[energy_type.value] >= quantity:
            self._loose_energy(energy_type=energy_type,
                               quantity=quantity)
            return True
        else:
            return False
    
    def _grow(self) -> None:
        """grow the entity to bigger size, consumming red energy
        """
        self._loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self._action_cost)
        if self.is_adult:
            energy_required = self.size * Entity.GROWTH_ENERGY_REQUIRED
        else:
            energy_required = self.size * Entity.CHILD_GROWTH_ENERGY_REQUIRED
            
        if self._can_perform_action(energy_type=EnergyType.RED, quantity=energy_required):
        
            self.size += 1
            self._max_age += 5
            self._action_cost += 1
        
        if not self.is_adult:
            self._reached_adulthood()

    def _increase_age(self, amount: int = 1) -> None:
        """Increase age of certain amount

        Args:
            amount (int, optional): amount to increase age by. Defaults to 1.
        """
        self._age += amount
       # self.loose_energy(energy_type=EnergyType.BLUE, quantity=self.action_cost)

        if self._age > self._max_age:
            self._die()

    def _die(self) -> None:
        """Death of the entity
        """
        self.grid.remove_entity(entity=self)
        self.on_death()

        print(f"{self} died at age {self._age}")

    def _check_coordinates(
            self, cell_coordinates: Tuple[int, int], subgrid) -> bool:
        """Check if the next move is valid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Validity of the next move
        """
        return self._is_cell_in_bounds(
            next_move=cell_coordinates,
            subgrid=subgrid) and self._is_vacant_cell(
            next_move=cell_coordinates,
            subgrid=subgrid)

    def _is_vacant_cell(self, subgrid, next_move: Tuple[int, int]) -> bool:
        """Check if a cell is vacant

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Vacancy of the cell
        """
        return not subgrid.get_cell_value(cell_coordinates=next_move)

    def _is_cell_in_bounds(self, subgrid, next_move: Tuple[int, int]) -> bool:
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

    def _find_cells_coordinate_by_value(self, subgrid, value,
                             radius: int = 1) -> Set[Tuple[int, int]]:
        """Find the list of cells in a range with specified value

        Args:
            subgrid (_type_):       subgrid to look for cells
            value (_type_):         value to search for
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found cells' coordinates
        """
      
        pos = self.position
        a = list(range(-radius, radius+1))
        b = combinations(a*2, 2)
    
        positions = [coordinate for x, y in set(b) if issubclass(type(subgrid.get_cell_value(coordinate:=tuple(np.add(pos,(x,y))))), value)]

        return positions
    
    def _find_occupied_cells_by_value(self, subgrid, value,
                             radius: int = 1, include_self: bool = False) -> np.array[bool]:
        """ Find the cells occupied by the given value, return a list of boolean

        Args:
            subgrid (SubGrid):              subgrid on which to look for
            value (Class):                  value to search for
            radius (int, optional):         radius of search. Defaults to 1.
            include_self (bool, optional):  include self in the list. Defaults to False.

        Returns:
            np.array[bool]: List of occupied (True) and empty cells (False)
        """        
        position: Tuple[int, int] = self.position
        occupied_cells = []
        
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                if not include_self and x == 0 and y == 0:
                    continue
                coordinate = tuple(np.add(position,(x, y)))
                occupied_cells.append((issubclass(type(subgrid.get_cell_value(cell_coordinates=coordinate)),value)))

        return np.array(occupied_cells)         
           
    def _find_occupied_cells_by_entities(self, radius: int = 1) -> np.array[bool]:
        """ Find the cells occupied by entities, return a list of boolean

        Args:
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            np.array[bool]: List of occupied (True) and empty cells (False)
        """               
        return self._find_occupied_cells_by_value(subgrid=self.entity_grid,
                                                    value=Entity,
                                                    radius=radius) 
        
    def _find_occupied_cells_by_energies(self, radius: int = 1) -> np.array[bool]:
        """ Find the cells occupied by energies, return a list of boolean

        Args:
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            np.array[bool]: List of occupied (True) and empty cells (False)
        """               
        return self._find_occupied_cells_by_value(subgrid=self.grid.resource_grid,
                                                    value=Energy,
                                                    radius=radius,
                                                    include_self=True)     
            
    
    def _find_tree_cells(self, include_self: bool = False,
                         radius: int = 1) -> Set[Tuple[int, int]]:
        """Find the cells at proximity on which trees are located

        Args:
            include_self (bool, optional):  include self in the list. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found trees' cells' coordinates
        """
        trees: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(subgrid=self.entity_grid,
                                                                value=Tree,
                                                                radius=radius)
        if not include_self and self.position in trees:
            trees.remove(self.position)
        return trees

    def _find_animal_cells(self, include_self: bool = False,
                           radius: int = 1) -> Set[Tuple[int, int]]:
        """Find the cells at proximity on which animals are located

        Args:
            include_self (bool, optional):  include self in the list. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found animals' cells' coordinates
        """
        animals: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
            subgrid=self.entity_grid, value=Animal, radius=radius)
        if not include_self and self.position in animals:
            animals.remove(self.position)
        return animals

    def _find_entities_cells(self, include_self: bool = False,
                           radius: int = 1) -> Set[Tuple[int, int]]:
        """Find the cells at proximity on which entities are located

        Args:
            include_self (bool, optional):  include self in the list. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found entities' cells' coordinates
        """
        entities: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
            subgrid=self.entity_grid, value=Entity, radius=radius)
        if not include_self and self.position in entities:
            entities.remove(self.position)
        return entities

    def _find_energies_cells(self, radius: int = 1) -> Set[Tuple[int, int]]:
        """Find cells at proximity on which energies are located

        Args:
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found energies' cells' coordinates
        """
        energies: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
            subgrid=self.grid.resource_grid, value=Energy, radius=radius)
        return energies

    def _find_free_cells(
            self, subgrid: SubGrid, radius: int = 1) -> Set[Tuple[int, int]]:
        """Find a free cell in range

        Args:
            subgrid (SubGrid):      subgrid to look for free cells
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of free cells' coordinates
        """
        return self._find_cells_coordinate_by_value(
            subgrid=subgrid, value=NoneType, radius=radius)

    def _select_free_cell(self, subgrid: SubGrid, radius: int = 1) -> Tuple[int, int]:
        """Select randomly from the free cells available

        Args:
            subgrid (_type_):       subgrid to look for free cell
            radius (int, optional): radius of search. Defaults to 1.

        Returns:
            Tuple[int,int]: coordinates of the free cell
        """
        free_cells: Set[Tuple[int, int]] = self._find_free_cells(
            subgrid=subgrid, radius=radius)

        if len(free_cells) != 0:
            return random.choice(tuple(free_cells))
        return None

    def _decompose(self, entity: EntitySprite) -> None:
        """decompose an entity into its energy components

        Args:
            entity (EntitySprite): entity to decompose in energy
        """
        resource_grid = self.grid.resource_grid
        free_cell = self._select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.RED,
                                quantity=entity.energies_stock[EnergyType.RED.value],
                                cell_coordinates=free_cell)
        free_cell = self._select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.BLUE,
                                quantity=entity.energies_stock[EnergyType.BLUE.value],
                                cell_coordinates=free_cell)

    def _distance_to_object(self, distant_object: Entity|Energy) -> float:
        from math import sqrt
        distance = sqrt((self.position[0] - distant_object.position[0])**2 + (self.position[1] - distant_object.position[1])**2)
        return round(distance, 2)
    
    def update(self):
        self._increase_age()
        self.test_update()


class Animal(Entity):
    INITIAL_BLUE_ENERGY: Final[int] = 10
    INITIAL_RED_ENERGY: Final[int] = 10
    REPRODUCTION_ENERGY_COST: Final[int] = 10
    
    def __init__(self, *args, **kwargs):
        super(
            Animal,
            self).__init__(
            image_filename='Animal.png',
            *args,
            **kwargs)
        self.seed_pocket: Seed = None
     

    def move(self, direction: Direction) -> None:
        """Move the animal in the given direction

        Args:
            direction (Direction): direction in which to move
        """
        next_move = tuple(np.add(self.position, direction.value))
        if self._check_coordinates(
                cell_coordinates=next_move,
                subgrid=self.grid.entity_grid):
            self.entity_grid.set_cell_value(
                cell_coordinates=(self.position), value=None)
            self.entity_grid.set_cell_value(
                cell_coordinates=next_move, value=self)
            self.position = next_move

            self.rect.x = next_move[0] * self.grid.BLOCK_SIZE
            self.rect.y = next_move[1] * self.grid.BLOCK_SIZE
        self._perform_action()

       
    def reproduce(self, mate: Animal) -> Animal:
        """Create an offspring from 2 mates

        Args:
            mate (Animal): Animal to mate with

        Returns:
            Animal: Generated offsrping
        """        
        self._loose_energy(energy_type=EnergyType.BLUE, quantity=self._action_cost)
        
        if not (self.is_adult and mate.is_adult):
            return
        
        if self._distance_to_object(distant_object=mate) > 2:
            return
        
        self_energy_cost = Animal.REPRODUCTION_ENERGY_COST * self.size
        mate_energy_cost = Animal.REPRODUCTION_ENERGY_COST * mate.size
        
        if (self._can_perform_action(energy_type=EnergyType.RED,
                                    quantity=self_energy_cost) and
            mate._can_perform_action(energy_type=EnergyType.RED,
                                     quantity=mate_energy_cost)):
        
            birth_position = self._select_free_cell(subgrid=self.grid.entity_grid)
            adult_size = int((self.size + mate.size)/2)
            
            child = self.grid.create_entity(entity_type=EntityType.Animal.value,
                                    position=birth_position,
                                    size=1,
                                    blue_energy=Animal.INITIAL_BLUE_ENERGY,
                                    red_energy=Animal.INITIAL_RED_ENERGY,
                                    adult_size=adult_size)
            return child

    def plant_tree(self) -> None:
        """Plant a tree nearby, consume red energy
        """
        PLANTING_COST: Final[int] = 10
        if self._energies_stock[EnergyType.RED.value] >= PLANTING_COST:
            self._loose_energy(
                energy_type=EnergyType.RED,
                quantity=PLANTING_COST)

            free_cell = self._select_free_cell(subgrid=self.entity_grid)
            if free_cell:
                if self.seed_pocket:
                    self.replant_seed(position=free_cell)
                else:
                    self.grid.create_entity(
                        entity_type="tree", position=free_cell)

            self._loose_energy(
                energy_type=EnergyType.BLUE,
                quantity=self._action_cost)

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
                                max_age=seed._max_age,
                                production_type=seed.production_type)
        self.seed_pocket = None

    def store_seed(self, seed: Seed) -> None:
        """Pick up a seed and stor it"""
        if not self.seed_pocket:
            self.seed_pocket = seed

        self._perform_action()

    def recycle_seed(self) -> None:
        """Destroy seed stored and drop energy content
        """
        if not self.seed_pocket:
            return

        self._decompose(self.seed_pocket)
        self.seed_pocket = None
        self._perform_action()

    def on_death(self) -> None:
        """Action on animal death, release energy on cells around death position"""
        self._decompose(entity=self)

    def modify_cell_color(self, color: Tuple[int,int,int], cell_coordinates: Tuple[int,int] = None) -> None:
        """Modfify the color of a given cell, usually the cell currently sat on

        Args:
            color (Tuple[int,int,int]):                     color to apply
            cell_coordinates (Tuple[int, int], optional):   the coordinates of the cell to modify. Defaults to None.
        """
        cell_coordinates = cell_coordinates if cell_coordinates else self.position
        self.grid.color_grid.set_cell_value(
            cell_coordinates=cell_coordinates,
            value=color)

        self._perform_action()

    def test_update(self):
        self.activate_mind()
        
    def activate_mind(self) -> None:
        inputs = self.normalize_inputs()
        mind = self.organism.mind
        outputs = mind.activate(input_values=inputs)
 
        self.interpret_outputs(outputs=outputs)                                                       
        #Outputs
        
    def normalize_inputs(self):
         #Inputs
        ## Internal properties
        age = self._age/100
        size = self.size/100
        blue_energy, red_energy = (energy/100 for energy in self.energies_stock.values())
        ## Perceptions
        see_entities = [int(x) for x in self._find_occupied_cells_by_entities()]
        see_energies = [int(x) for x in self._find_occupied_cells_by_energies()]
        see_colors = self.grid.color_grid.get_sub_region(initial_pos=self.position,
                                                         radius=2).flatten()/255
        see_colors = see_colors.tolist()
        
        return np.array([age, size, blue_energy/100, red_energy/100] + see_entities + see_energies + see_colors)
    
    def interpret_outputs(self, outputs: np.array):
        pass
    
    def random_update(self) -> None:
        """Test behaviour by doing random actions"""
        direction = random.choice(list(Direction))
        # print(direction)
        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2, 2), np.random.randint(-2, 2)
            coordinates = tuple(np.add(self.position, (x, y)))
            if self._check_coordinates(cell_coordinates=coordinates,
                                       subgrid=self.grid.resource_grid):
                self._drop_energy(energy_type=np.random.choice(EnergyType),
                                 cell_coordinates=coordinates,
                                 quantity=1)

        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2, 2), np.random.randint(-2, 2)
            coordinates = tuple(np.add(self.position, (x, y)))
            self._pick_up_resource(cell_coordinates=coordinates)

        if np.random.uniform() < 0.1:
            color = tuple(np.random.choice(range(256), size=3))
            self.modify_cell_color(cell_coordinates=self.position,
                                   color=color)

        # self.die()
        self.move(direction=direction)


class Tree(Entity):
    def __init__(self,
                 production_type: EnergyType = None,
                 *args,
                 **kwargs
                 ):
        super(Tree, self).__init__(image_filename='Plant.png', *args, **kwargs)
        self.production_type: EnergyType = production_type if production_type else np.random.choice(
            list(EnergyType))

    def produce_energy(self) -> None:
        """Produce energy
        """
        MINUMUM_AGE: Final[int] = 20
        if self._age < MINUMUM_AGE:
            pass

        count_trees_around = len(self._find_tree_cells())

        self._gain_energy(energy_type=self.production_type,
                         quantity=int((5 * self.size) / 2**count_trees_around))
        self._loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self._action_cost)

    def on_death(self) -> None:
        """Action on tree death, create a seed on dead tree position"""
        self.grid.create_entity(entity_type="seed",
                                position=self.position,
                                blue_energy=self.get_blue_energy(),
                                red_energy=self.get_red_energy(),
                                max_age=self._max_age)

    def test_update(self):
        pass
