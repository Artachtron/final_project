from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid, SubGrid
    
from typing import Tuple, Set, Final, Dict
from types import NoneType
import enum
import random
from energies import EnergyType, Energy
import numpy as np
from itertools import combinations

from simulation import SimulatedObject, Position

class Direction(enum.Enum):
    RIGHT   =   (1, 0)
    LEFT    =   (-1, 0)
    DOWN    =   (0, 1)
    UP      =   (0, -1)


class EntityType(enum.Enum):
    Animal  =   "animal"
    Tree    =   "tree"
    Seed    =   "seed"


class Entity(SimulatedObject):
    MAX_AGE_SIZE_COEFF: Final[int] = 5
    GROWTH_ENERGY_REQUIRED: Final[int] = 10
    CHILD_ENERGY_COST_DIVISOR: Final[int] = 2
    CHILD_GROWTH_ENERGY_REQUIRED: Final[int] = (GROWTH_ENERGY_REQUIRED /
                                                CHILD_ENERGY_COST_DIVISOR)
    INITIAL_SIZE: Final[int] = 20
    INITIAL_BLUE_ENERGY: Final[int] = 100
    INITIAL_RED_ENERGY: Final[int] = 100
    INITIAL_ACTION_COST: Final[int] = INITIAL_SIZE/20
    
    def __init__(self,
                 position: Tuple[int, int],
                 entity_id: int = 0,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = INITIAL_SIZE,
                 action_cost: int = INITIAL_ACTION_COST,
                 blue_energy: int = INITIAL_BLUE_ENERGY,
                 red_energy: int = INITIAL_RED_ENERGY,
                 appearance: str = "",
                 ):
        
        appearance = "models/entities/" + appearance
        super(Entity, self).__init__(sim_obj_id=entity_id,
                                     position=position,
                                     size=size,
                                     appearance=appearance)                 
        
        self._energies_stock: Dict[str, int] = {              # energy currently owned
            EnergyType.BLUE.value: blue_energy,
            EnergyType.RED.value: red_energy
            }
            
        self._age: int = 0                                     # age of the entity
        self._max_age: int = (max_age or                       # maximum longevity before dying
                              (size * 
                               Entity.MAX_AGE_SIZE_COEFF))
        
        self._adult_size: int = adult_size                     # size to reach before becoming adult
        self.is_adult: bool = False                            # can reproduce only if adult
        self._reached_adulthood()                              # check if the adult size was reached                          
        
        self._action_cost: int = action_cost                   # blue energy cost of each action
        
    
    @property
    def energies(self) -> Dict[str, int]:
        """Public property:
        
        Returns:
            Dict[str, int]:     dictionary summarising owned energies, 
                                arranged by EnergyType
        """        
        return self._energies_stock

    @property
    def blue_energy(self) -> int:
        """Public property:
        
        Returns:
            int: amount of blue energy owned 
        """
        return self._energies_stock[EnergyType.BLUE.value]
    
    @property
    def red_energy(self) -> int:
        """Public property:
        
        Returns:
            int: amount of red energy owned 
        """
        return self._energies_stock[EnergyType.RED.value]       
    
    def _increase_age(self, amount: int = 1) -> None:
        """Private method:
            Action: Increase age by a given amount

        Args:
            amount (int, optional): amount to increase age by. Defaults to 1.
        """
        self._age += amount

        # if new age above maximum age threshold,
        # the entity dies
        if self._age > self._max_age:
            self._die()
            
    def _grow(self) -> None:
        """Private method:
        Action:     Grow the entity to bigger size,
                    consumming red energy
        """
        
        # Action's blue energy cos
        self._loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self._action_cost)
        
        # Red energy cost depend on adulthood status,
        # cost less energy for a child
        if self.is_adult:
            energy_required = self.size * Entity.GROWTH_ENERGY_REQUIRED
            
        else:
            energy_required = self.size * Entity.CHILD_GROWTH_ENERGY_REQUIRED
        
        # Perfrom action if possible: if enough energy is available   
        if self._can_perform_action(energy_type=EnergyType.RED, quantity=energy_required):
            # Increase size,
            # maximum age,
            # action cost
            self.size += 1
            self._max_age += 5
            self._action_cost += 1
        
        # Check if new size
        # changes adulthood status
        if not self.is_adult:
            self._reached_adulthood()
    
    def _reached_adulthood(self) -> None:
        """ Private method:
            Check if the entity reached maturity size and
            assign the result in the is_adult instance variable
        """
        self.is_adult = self.size >= self._adult_size
   
    def _gain_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Private method:
            Gain energy of specified type and adds it to energies stock

        Args:
            energy_type (EnergyType):   type of energy to gain
            quantity (int):             amount of energy to gain
            
        Raises:
            ValueError: amount should not be negative
        """
        # quantiy can't be negative
        if quantity < 0 :
            raise ValueError
        
        # Add the quantity
        self._energies_stock[energy_type.value] += quantity
        
    def _loose_energy(self, energy_type: EnergyType, quantity: int) -> int:
        """Private method:
            Loose energy of specified type from energies stock,
            if quantity greater than stock set stock to 0

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose
        
        Raises:
            ValueError: quantity should not be negative
            
        Returns:
            int: quantity of energy that was effectively lost
        """
        # quantiy can't be negative
        if quantity < 0 :
            raise ValueError
        
        energy_amount = self._energies_stock[energy_type.value]
        # if quantity is more than stock, set stock to 0
        if energy_amount - quantity > 0:
            self._energies_stock[energy_type.value] -= quantity
        
        else:
            quantity = energy_amount
            self._energies_stock[energy_type.value] = 0

        # dies if the entity run out of blue energy
        if self._energies_stock[EnergyType.BLUE.value] <= 0:
            self._die()

        # effective quantity lost
        return quantity

    def _perform_action(self) -> None:
        """Private method:
            Consume blue energy when performing an action
        """        
        self._loose_energy(
            energy_type=EnergyType.BLUE,
            quantity=self._action_cost)
    
    def _can_perform_action(self, energy_type: EnergyType, quantity: int) -> bool:
        """Private method:
            Check if the entity has enough energy to perform an action,
            use the energy if it's the case

        Args:
            energy_type (EnergyType):   type of energy to loose
            quantity (int):             amount of energy to loose

        Returns:
            bool: True the entity had enough energy
                  False if the action can't be performed
        """        
        if can_perform:= (self.energies[energy_type.value] >= quantity):
            self._loose_energy(energy_type=energy_type,
                               quantity=quantity)
           
        return can_perform
        
    def _drop_energy(self, energy_type: EnergyType, quantity: int,
                    coordinates: Tuple[int, int], grid: Grid) -> None:
        """Private method:
            Action: Drop an amount energy of the specified type at a coordinate

        Args:
            energy_type (EnergyType):       type of energy to drop
            quantity (int):                 amount of energy to drop
            coordinates (Tuple[int,int]):   coordinates on which to drop energy
            grid (Grid):                    grid on which to drop energy         
        """
        
        resource_grid: SubGrid = grid.resource_grid
        # Check if the coordinates are available to drop on
        if self._is_available_coordinates(coordinates=coordinates,
                                          subgrid=resource_grid):
            
            # Remove energy amount from stock
            quantity = self._loose_energy(energy_type=energy_type,
                                          quantity=quantity)

            # Create the energy at coordinates
            grid.create_energy(energy_type=energy_type,
                               quantity=quantity,
                               coordinates=coordinates)
        # Energy cost of action
        self._perform_action()
     
    ################################################################################################ 
     
        
    def _die(self) -> None:
        """Private method:
            Action: Death of the entity
        """
        self.grid.remove_entity(entity=self)
        self.on_death()

        print(f"{self} died at age {self._age}")
        
        
        
    
    
    
    

    def _pick_up_resource(self, coordinates: Tuple[int, int]) -> None:
        """Private method:
            Action: Pick energy up at coordinates

        Args:
            coordinates (Tuple[int, int]): coordinates to pick up energy from
        """
        resource_grid = self.grid.resource_grid
        resource = resource_grid.get_cell_value(
            cell_coordinates=coordinates)
        if resource:
            if type(resource).__base__ == Energy:
                self._gain_energy(
                    energy_type=resource.type,
                    quantity=resource.quantity)
            elif resource.__class__.__name__ == "Seed" and isinstance(self, Animal):
                self.store_seed(seed=resource)
            self.grid.remove_energy(energy=resource)

        self._perform_action()

    def _decompose(self, entity: Entity) -> None:
        """Private method:
            Action: decompose an entity into its energy components

        Args:
            entity (Entity): entity to decompose in energy
        """
        resource_grid = self.grid.resource_grid
        
        free_cell = self._select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.RED,
                                quantity=entity.energies[EnergyType.RED.value],
                                cell_coordinates=free_cell)
        
        free_cell = self._select_free_cell(subgrid=resource_grid)
        self.grid.create_energy(energy_type=EnergyType.BLUE,
                                quantity=entity.energies[EnergyType.BLUE.value],
                                cell_coordinates=free_cell)
    
    



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
    
        positions = [coordinate for x, y in set(b) 
                     if issubclass(type(subgrid.get_cell_value(coordinate:=tuple(np.add(pos,(x,y))))), value)]

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
    
    def __init__(self,
                 position: Tuple[int, int],
                 animal_id: int = None,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = 20,
                 action_cost: int = 1,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 ):
        
        super(Animal, self).__init__(position=position,
                                     entity_id=animal_id,
                                     adult_size=adult_size,
                                     max_age=max_age,
                                     size=size,
                                     action_cost=action_cost,
                                     blue_energy=blue_energy,
                                     red_energy=red_energy,
                                     appearance="animal.png")
            
        self._pocket: Seed = None

    def _move(self, direction: Direction, grid: Grid) -> None:
        """ Private method: 
            Move the animal in the given direction

        Args:
            direction (Direction):  direction in which to move
            grid (Grid):            grid on which to move 
        """        
        entity_grid: SubGrid = grid.entity_grid
        next_pos = Position.add(position=self.position,
                                vect=direction.value)
        
        if entity_grid.are_available_coordinates(coordinates=next_pos.vect):
            
            entity_grid.update_cell(new_coordinate=next_pos.vect,
                                    value=self)
        
            self.position = next_pos

        self._perform_action()
        
        ###########################################################################
           
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

    def _plant_tree(self) -> None:
        """Private method:
           Plant a tree nearby, consume red energy
        """
        PLANTING_COST: Final[int] = 10
        if self._energies_stock[EnergyType.RED.value] >= PLANTING_COST:
            self._loose_energy(
                energy_type=EnergyType.RED,
                quantity=PLANTING_COST)

            free_cell = self._select_free_cell(subgrid=self.entity_grid)
            if free_cell:
                if self._pocket:
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
        if not self._pocket:
            return
        seed = self._pocket
        self.grid.create_entity(entity_type="tree",
                                position=position,
                                blue_energy=seed.blue_energy(),
                                red_energy=seed.red_energy(),
                                max_age=seed._max_age,
                                production_type=seed.production_type)
        self._pocket = None

    def store_seed(self, seed: Seed) -> None:
        """Pick up a seed and stor it"""
        if not self._pocket:
            self._pocket = seed

        self._perform_action()

    def recycle_seed(self) -> None:
        """Destroy seed stored and drop energy content
        """
        if not self._pocket:
            return

        self._decompose(self._pocket)
        self._pocket = None
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
        inputs = self._normalize_inputs()
        mind = self.organism.mind
        outputs = mind.activate(input_values=inputs)
 
        self._interpret_outputs(outputs=outputs)                                                       
        #Outputs
        
    def _normalize_inputs(self):
         #Inputs
        ## Internal properties
        age = self._age/100
        size = self.size/100
        blue_energy, red_energy = (energy/100 for energy in self.energies.values())
        ## Perceptions
        see_entities = [int(x) for x in self._find_occupied_cells_by_entities()]
        see_energies = [int(x) for x in self._find_occupied_cells_by_energies()]
        see_colors = self.grid.color_grid.get_sub_region(initial_pos=self.position,
                                                         radius=2).flatten()/255
        see_colors = see_colors.tolist()
        
        return np.array([age, size, blue_energy/100, red_energy/100] + see_entities + see_energies + see_colors)
    
    def _interpret_outputs(self, outputs: np.array):
        pass
    
    def random_update(self) -> None:
        """Test behaviour by doing random actions"""
        direction = random.choice(list(Direction))
        # print(direction)
        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2, 2), np.random.randint(-2, 2)
            coordinates = tuple(np.add(self.position, (x, y)))
            if self._is_available_coordinates(coordinates=coordinates,
                                       subgrid=self.grid.resource_grid):
                self._drop_energy(energy_type=np.random.choice(EnergyType),
                                 coordinates=coordinates,
                                 quantity=1)

        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2, 2), np.random.randint(-2, 2)
            coordinates = tuple(np.add(self.position, (x, y)))
            self._pick_up_resource(coordinates=coordinates)

        if np.random.uniform() < 0.1:
            color = tuple(np.random.choice(range(256), size=3))
            self.modify_cell_color(cell_coordinates=self.position,
                                   color=color)

        # self.die()
        self.move(direction=direction)


class Tree(Entity):
    def __init__(self,
                 position: Tuple[int, int],
                 tree_id: int = None,
                 adult_size: int = 0,
                 max_age: int = 0,
                 size: int = 20,
                 action_cost: int = 1,
                 blue_energy: int = 10,
                 red_energy: int = 10,
                 production_type: EnergyType = None,
                 ):
        
        super(Tree, self).__init__( position=position,
                                    entity_id=tree_id,
                                    adult_size=adult_size,
                                    max_age=max_age,
                                    size=size,
                                    action_cost=action_cost,
                                    blue_energy=blue_energy,
                                    red_energy=red_energy,
                                    appearance="tree.png")
        
        self._production_type: EnergyType = (production_type or
                                            np.random.choice(list(EnergyType)))

    def produce_energy(self) -> None:
        """Produce energy
        """
        MINUMUM_AGE: Final[int] = 20
        if self._age < MINUMUM_AGE:
            pass

        count_trees_around = len(self._find_tree_cells())

        self._gain_energy(energy_type=self._production_type,
                         quantity=int((5 * self.size) / 2**count_trees_around))
        
        self._loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self._action_cost)

    def on_death(self) -> None:
        """Action on tree death, create a seed on dead tree position"""
        self.grid.create_entity(entity_type="seed",
                                position=self.position,
                                blue_energy=self.blue_energy(),
                                red_energy=self.red_energy(),
                                max_age=self._max_age)

    def test_update(self):
        pass

class Seed(Entity):
    def __init__(self,
                 position: Tuple[int, int],
                 production_type: EnergyType,
                 max_age: int = 0,
                 size: int = 15,
                 blue_energy: int = 0,
                 red_energy: int = 0,
                 ):
        
        super(Seed, self).__init__(size=size,
                                   position=position,
                                   blue_energy=blue_energy,
                                   red_energy=red_energy)
        
        self.grid.resource_grid.set_cell_value(
            cell_coordinates=(self.position), value=self)
        
        self._max_age = max_age if max_age else size * 5
        self.production_type = production_type