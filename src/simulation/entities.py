from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid, SubGrid
    from simulation import Environment
    from project.src.rtNEAT.network import Network
    
from typing import Tuple, Final, Dict, Any
import enum
import numpy as np
import inspect

from energies import EnergyType, Energy, Resource
from universal import SimulatedObject, Position, EntityType
from project.src.rtNEAT.organism import Organism


class Direction(enum.Enum):
    RIGHT   =   (1, 0)
    LEFT    =   (-1, 0)
    DOWN    =   (0, 1)
    UP      =   (0, -1)
    
class Status(enum.Enum):
    ALIVE = 0
    DEAD = 1


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
        
        self.status = Status.ALIVE                              # Current status
        
        self._energies_stock: Dict[str, int] = {                # energy currently owned
            EnergyType.BLUE.value: blue_energy,
            EnergyType.RED.value: red_energy
            }
            
        self._age: int = 0                                      # age of the entity
        self._max_age: int = (max_age or                        # maximum longevity before dying
                              (size * 
                               Entity.MAX_AGE_SIZE_COEFF))
        
        self._adult_size: int = adult_size                      # size to reach before becoming adult
        self._is_adult: bool = False                            # can reproduce only if adult
        self._reached_adulthood()                               # check if the adult size was reached                          
        
        self._action_cost: int = action_cost                    # blue energy cost of each action
        
        self.organism: Organism                                 # Organism containing genotype and mind
        self.mind: Network     
                                           
        self._create_mind()
        
    def _create_mind(self):
        self.organism = Organism.genesis(organism_id=self.id,
                                            entity_type=EntityType.Animal.value)   
        
        self.mind = self.organism.mind
        self.mind.verify_post_genesis()                          
        
     
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
        if self._is_adult:
            energy_required = self._size * Entity.GROWTH_ENERGY_REQUIRED
            
        else:
            energy_required = self._size * Entity.CHILD_GROWTH_ENERGY_REQUIRED
        
        # Perfrom action if possible: if enough energy is available   
        if self._can_perform_action(energy_type=EnergyType.RED, quantity=energy_required):
            # Increase size,
            # maximum age,
            # action cost
            self._size += 1
            self._max_age += 5
            self._action_cost += 1
        
        # Check if new size
        # changes adulthood status
        if not self._is_adult:
            self._reached_adulthood()
    
    def _reached_adulthood(self) -> None:
        """ Private method:
            Check if the entity reached maturity size and
            assign the result in the is_adult instance variable
        """
        self._is_adult = self._size >= self._adult_size
   
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
        
    def _quantity_from_stock(self, energy_type: EnergyType, quantity: int) -> int:
        """Private method:
            Calculate the quantity that can be taken from the stock for a certain energy type,
            either the quantity asked or the energy left in the stock

        Args:
            energy_type (EnergyType):   type of energy to check in stock
            quantity (int):             initial quantity

        Raises:
            ValueError: quantity cannot be negative

        Returns:
            int: calculated quantity that can be taken
        """        
        # quantiy can't be negative
        if quantity < 0 :
            raise ValueError
        
        energy_amount: int = self._energies_stock[energy_type.value]
                
        return min(quantity, energy_amount)
            
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
        
        quantity = self._quantity_from_stock(energy_type=energy_type,
                                             quantity=quantity)

        self._energies_stock[energy_type.value] -= quantity
        
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
                    coordinates: Tuple[int, int], environment: Environment) -> None:
        """Private method:
            Action: Drop an amount energy of the specified type at a coordinate

        Args:
            energy_type (EnergyType):       type of energy to drop
            quantity (int):                 amount of energy to drop
            coordinates (Tuple[int,int]):   coordinates on which to drop energy
            grid (Grid):                    grid on which to drop energy         
        """           
        
        # Calculate the energy capable of being dropped
        quantity = self._quantity_from_stock(energy_type=energy_type,
                                                quantity=quantity)
        # Create the energy
        if environment.create_energy(energy_type=energy_type,
                                     coordinates=coordinates,
                                     quantity=quantity):
            
            # Remove energy amount from stock
            self._loose_energy(energy_type=energy_type,
                               quantity=quantity)

        # Energy cost of action
        self._perform_action()
        
    def _pick_up_resource(self, coordinates: Tuple[int, int], environment: Environment) -> None:
        """Private method:
            Action: Pick energy up at coordinates

        Args:
            coordinates (Tuple[int, int]):  coordinates to pick up energy from
            grid (Grid):                    grid on which to pick up energy
        """

        # Get the resource at coordinates from the environment 
        resource = environment.get_resource_at(coordinates=coordinates)
        
        if resource:
            # If resource is an energy
            if type(resource).__base__.__name__ == 'Energy':
                self._gain_energy(energy_type=resource.type,
                                  quantity=resource.quantity)
             
            # If resource is a seed   
            elif resource.__class__.__name__ == "Seed" and isinstance(self, Animal):
                self._store_seed(seed=resource)       

            environment.remove_resource(resource=resource)
        
        self._perform_action()

    def _die(self) -> None:
        """Private method:
            Action: Death of the entity
        """
       
        print(f"{self} died at age {self._age}")
        self.status = Status.DEAD
        
        
        
    def _decompose(self, entity: Entity, environment: Environment) -> None:
        """Private method:
            Action: decompose an entity into its energy components

        Args:
            entity (Entity):    entity to decompose in energy
            grid (Grid):        grid on which to deposit energy
        """
        resource_grid: SubGrid = environment.grid.resource_grid
        
        # Select free cells to place energy on
        free_cells: Tuple[int, int] = resource_grid.select_free_coordinates(
                                                     position=self.position,
                                                     num_cells=2)
        
        # Red energy        
        environment.create_energy(energy_type=EnergyType.RED,
                                  coordinates=free_cells[0],
                                  quantity=entity.energies[EnergyType.RED.value])
        
        # Blue energy                            

        environment.create_energy(energy_type=EnergyType.BLUE,
                                  coordinates=free_cells[1],
                                  quantity=entity.energies[EnergyType.BLUE.value])
     
    ################################################################################################ 
        
    
    # def _find_occupied_cells_by_value(self, subgrid, value,
    #                          radius: int = 1, include_self: bool = False) -> np.array[bool]:
    #     """ Find the cells occupied by the given value, return a list of boolean

    #     Args:
    #         subgrid (SubGrid):              subgrid on which to look for
    #         value (Class):                  value to search for
    #         radius (int, optional):         radius of search. Defaults to 1.
    #         include_self (bool, optional):  include self in the list. Defaults to False.

    #     Returns:
    #         np.array[bool]: List of occupied (True) and empty cells (False)
    #     """        
        # position: Tuple[int, int] = self._position
        # occupied_cells = []
        
        # for x in range(-radius, radius + 1):
        #     for y in range(-radius, radius + 1):
        #         if not include_self and x == 0 and y == 0:
        #             continue
        #         coordinate = tuple(np.add(position,(x, y)))
        #         occupied_cells.append((issubclass(type(subgrid.get_cell_value(coordinates=coordinate)),value)))

        # return np.array(occupied_cells)         
           
    # def _find_occupied_cells_by_entities(self, radius: int = 1) -> np.array[bool]:
    #     """ Find the cells occupied by entities, return a list of boolean

    #     Args:
    #         radius (int, optional): radius of search. Defaults to 1.

    #     Returns:
    #         np.array[bool]: List of occupied (True) and empty cells (False)
    #     """               
    #     return self._find_occupied_cells_by_value(subgrid=self.entity_grid,
    #                                                 value=Entity,
    #                                                 radius=radius) 
        
    # def _find_occupied_cells_by_energies(self, radius: int = 1) -> np.array[bool]:
    #     """ Find the cells occupied by energies, return a list of boolean

    #     Args:
    #         radius (int, optional): radius of search. Defaults to 1.

    #     Returns:
    #         np.array[bool]: List of occupied (True) and empty cells (False)
    #     """               
    #     return self._find_occupied_cells_by_value(subgrid=self.grid.resource_grid,
    #                                                 value=Energy,
    #                                                 radius=radius,
    #                                                 include_self=True)     
            
    
    # def _find_tree_cells(self, include_self: bool = False,
    #                      radius: int = 1) -> Set[Tuple[int, int]]:
    #     """Find the cells at proximity on which trees are located

    #     Args:
    #         include_self (bool, optional):  include self in the list. Defaults to False.
    #         radius (int, optional):         radius of search. Defaults to 1.

    #     Returns:
    #         Set[Tuple[int,int]]: set of found trees' cells' coordinates
    #     """
    #     trees: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(subgrid=self.entity_grid,
    #                                                             value=Tree,
    #                                                             radius=radius)
    #     if not include_self and self._position in trees:
    #         trees.remove(self._position)
    #     return trees

    # def _find_animal_cells(self, include_self: bool = False,
    #                        radius: int = 1) -> Set[Tuple[int, int]]:
    #     """Find the cells at proximity on which animals are located

    #     Args:
    #         include_self (bool, optional):  include self in the list. Defaults to False.
    #         radius (int, optional):         radius of search. Defaults to 1.

    #     Returns:
    #         Set[Tuple[int,int]]: set of found animals' cells' coordinates
    #     """
    #     animals: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
    #         subgrid=self.entity_grid, value=Animal, radius=radius)
    #     if not include_self and self._position in animals:
    #         animals.remove(self._position)
    #     return animals

    # def _find_entities_cells(self, include_self: bool = False,
    #                        radius: int = 1) -> Set[Tuple[int, int]]:
    #     """Find the cells at proximity on which entities are located

    #     Args:
    #         include_self (bool, optional):  include self in the list. Defaults to False.
    #         radius (int, optional):         radius of search. Defaults to 1.

    #     Returns:
    #         Set[Tuple[int,int]]: set of found entities' cells' coordinates
    #     """
    #     entities: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
    #         subgrid=self.entity_grid, value=Entity, radius=radius)
    #     if not include_self and self._position in entities:
    #         entities.remove(self._position)
    #     return entities

    # def _find_energies_cells(self, radius: int = 1) -> Set[Tuple[int, int]]:
    #     """Find cells at proximity on which energies are located

    #     Args:
    #         radius (int, optional): radius of search. Defaults to 1.

    #     Returns:
    #         Set[Tuple[int,int]]: set of found energies' cells' coordinates
    #     """
    #     energies: Set[Tuple[int, int]] = self._find_cells_coordinate_by_value(
    #         subgrid=self.grid.resource_grid, value=Energy, radius=radius)
    #     return energies

           
    
    def update(self, environment):
        self._increase_age()
        return self._activate_mind(environment=environment)


class Animal(Entity):
    """ INITIAL_BLUE_ENERGY: Final[int] = 10
    INITIAL_RED_ENERGY: Final[int] = 10 """
    
    REPRODUCTION_ENERGY_COST: Final[int] = 10
    PLANTING_COST: Final[int] = 10
    
    def __init__(self,
                 position: Tuple[int, int],
                 animal_id: int = 0,
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
            
        self._pocket: Seed = None       # Pocket in which to store seed
        self.want_to_mate: bool = False # Want to mate if possible

    def _move(self, direction: Direction, environment: Environment) -> None:
        """Private method: 
            Action: Move the animal in the given direction

        Args:
            direction (Direction):  direction in which to move
            grid (Grid):            grid on which to move 
        """        
        entity_grid: SubGrid = environment.grid.entity_grid
        next_pos = Position.add(position=self.position,
                                vect=direction.value)()
                    
        # Ask the grid to update, changing old position to empty,
        #and new position to occupied by self
        if entity_grid.update_cell(new_coordinates=next_pos,
                                    value=self):
            
            # update self position
            self.position = next_pos
           
        # Energy cost of action
        self._perform_action()
        
    def _plant_tree(self, environment: Environment) -> None:
        """Private method:
            Action: Plant a tree nearby, consume red energy
        """
        
        entity_grid: SubGrid = environment.grid.entity_grid
        
        # Verifiy that enough enough energy is available
        if self._can_perform_action(energy_type=EnergyType.RED,
                                    quantity=Animal.PLANTING_COST):
            
            # Get a free cell around
            free_cell: Tuple[int, int] = entity_grid.select_free_coordinates(
                                            position=self.position)
            
            if free_cell:
                # If animal possess a seed plant it,
                # else plant a new tree
                if self._pocket:
                    self._replant_seed(position=free_cell,
                                       environment=environment)
                    
                else:
                    environment.create_tree(coordinates=free_cell)
                 
                print(f"Tree was created at {free_cell}") 
                    
            # Energy cost of action
            self._perform_action()
            
    def _store_seed(self, seed: Seed) -> None:
        """Private method:
            Action: Pick up a seed and store it"""
         
        # Only store a seed if the pocket is empty   
        if not self._pocket:
            self._pocket = seed

        # Energy cost of action
        self._perform_action()
        
    def _recycle_seed(self, environment: Environment) -> None:
        """Private method:
        Action: Destroy seed stored and drop energy content
        """
        
        # if pocket is empty nothing to recycle
        if not self._pocket:
            return
        
        tree = self._pocket.germinate()
        
        # Drop energy from seed on the ground
        self._decompose(entity=tree,
                        environment=environment)
        # Empty pocket
        self._pocket = None
        # Energy cost of action
        self._perform_action()
        
    def _replant_seed(self, position: Tuple[int, int], environment: Environment) -> None:
        """Private method:
        Action: Replant seed store in pocket

        Args:
            position (Tuple[int, int]): cell coordinates on which to plant seed
        """
        # Nothing to replant if pocket is empty
        if not self._pocket:
            return
               
        # spawn the tree from seed, 
        # at given position on the grid
        environment.spawn_tree(seed=self._pocket,
                               position=position)
               
        # Emtpy pocket
        self._pocket = None
        
    def on_death(self, environment: Environment) -> None:
        """Private method:
            Event: on animal death, release energy on cells around death position"""
        environment.decompose_entity(entity=self)
        
        environment.remove_entity(entity=self)

    def _paint(self, color: Tuple[int,int,int], environment: Environment,
                          coordinates: Tuple[int,int] = None) -> None:
        """Private method:
            Modfify the color of a given cell, usually the cell currently sat on

        Args:
            color (Tuple[int,int,int]):                     color to apply
            environment (Environment):    
            coordinates (Tuple[int, int], optional):        coordinates of the cell to modify. Defaults to None.
        """
        
        coordinates = coordinates or self.position
        environment.modify_cell_color(color=color,
                                      coordinates=coordinates)

        self._perform_action()
        
    def _activate_mind(self, environment: Environment) -> None:
        inputs = self._normalize_inputs(environment=environment)
        mind = self.organism.mind
        outputs = mind.activate(input_values=inputs)
        return self._interpret_outputs(outputs=outputs,
                                       environment=environment)                                                          
        
    def _normalize_inputs(self, environment: Environment):
        #Inputs
        ## Internal properties
        age = self._age/self._max_age
        size = self._size/100
        blue_energy, red_energy = (energy/100000 for energy in self.energies.values())
        ## Perceptions
        entities = environment.find_if_entities_around(coordinates=self.position,
                                                       include_self=False)
        see_entities = list(map(int, entities))
        energies = environment.find_if_resources_around(coordinates=self.position,
                                                        include_self=True)
        see_energies = list(map(int, energies))
        
        colors = environment.get_colors_around(coordinates=self.position,
                                               radius=2)
        
        see_colors = (1 - colors.flatten()/255).tolist()
        # see_colors = np.random.random(75).tolist()
                
        return np.array([age, size, blue_energy, red_energy] + see_entities + see_energies + see_colors)
    
    def _interpret_outputs(self, outputs: np.array, environment: Environment):
        self.want_to_mate = False
        request = ''
        
        # Get the most absolute active value of all the outputs
        most_active_output = max(outputs, key = lambda k : abs(outputs.get(k)))
        value = outputs[most_active_output]
        
        sorted_output_keys = sorted(outputs.keys())

        match out:= sorted_output_keys.index(most_active_output):
            ## Simple actions ##
            # Move action
            case key if key in range(0,2):
                if out == 0:
                    if value > 0:
                        direction = Direction.UP
                    else:
                        direction = Direction.DOWN 
                       
                else:
                    if value > 0:
                        direction = Direction.LEFT
                    else:
                        direction = Direction.RIGTH 
                        
                request = self._move(direction=direction,
                                     environment=environment)
            
            # Modify cell color
            case key if key in range(2,5):
                color = (outputs[sorted_output_keys[2]]*255,
                         outputs[sorted_output_keys[3]]*255,
                         outputs[sorted_output_keys[4]]*255)
                
                request = self._paint(coordinates=self.position,
                                      color=color,
                                      environment=environment)
            
            # Drop energy   
            case key if key in range(5,7):
                if out == 5:
                    request = self._drop_energy(energy_type=EnergyType.BLUE,
                                                coordinates=self.position,
                                                quantity=10,
                                                environment=environment)
                
                else:
                    request = self._drop_energy(energy_type=EnergyType.RED,
                                                coordinates=self.position,
                                                quantity=10,
                                                environment=environment)
                
            # Pick up resource       
            case 7:
                request = self._pick_up_resource(coordinates=self.position,
                                                 environment=environment)
                    
            # Recycle seed    
            case 8:
                request = self._recycle_seed(environment=environment)
            
            ## Complex actions ##   
            # Plant tree
            case 9:
                request = self._plant_tree(environment=environment)
                
            #Grow
            case 10:
                request = self._grow()
                
            case 11:
                self.want_to_mate = True
                # self.reproduce()
                
        return request
                    

        
        ###########################################################################
           
    
    
    
    def reproduce(self, mate: Animal, environment: Environment) -> Animal:
        """Create an offspring from 2 mates

        Args:
            mate (Animal): Animal to mate with

        Returns:
            Animal: Generated offsrping
        """        
        self._loose_energy(energy_type=EnergyType.BLUE, quantity=self._action_cost)
        pass
        
        if not (self._is_adult and mate._is_adult):
            return
        
        if self._distance_to_object(distant_object=mate) > 2:
            return
        
        self_energy_cost = Animal.REPRODUCTION_ENERGY_COST * self._size
        mate_energy_cost = Animal.REPRODUCTION_ENERGY_COST * mate._size
        
        if (self._can_perform_action(energy_type=EnergyType.RED,
                                    quantity=self_energy_cost) and
            mate._can_perform_action(energy_type=EnergyType.RED,
                                     quantity=mate_energy_cost)):
        
            birth_position = self._select_free_cell(subgrid=self.grid.entity_grid)
            adult_size = int((self._size + mate._size)/2)
            
            child = environment.create_entity(entity_type=EntityType.Animal.value,
                                                position=birth_position,
                                                size=1,
                                                blue_energy=Animal.INITIAL_BLUE_ENERGY,
                                                red_energy=Animal.INITIAL_RED_ENERGY,
                                                adult_size=adult_size)
            return child


class Tree(Entity):
    def __init__(self,
                 position: Tuple[int, int],
                 tree_id: int = 0,
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
                                    appearance="plant.png")
        
        self._production_type: EnergyType = (production_type or                 # Type of energy produce by the tree
                                            np.random.choice(list(EnergyType)))
        
    def produce_energy(self) -> None:
        """Produce energy
        """
        MINUMUM_AGE: Final[int] = 20
        if self._age < MINUMUM_AGE:
            pass

        count_trees_around = len(self._find_tree_cells())

        self._gain_energy(energy_type=self._production_type,
                         quantity=int((5 * self._size) / 2**count_trees_around))
        
        self._loose_energy(energy_type=EnergyType.BLUE,
                          quantity=self._action_cost)

    def on_death(self, environment: Environment) -> None:
        """Action on tree death, create a seed on dead tree position"""
        
        environment.create_seed_from_tree(tree=self)
        

    def _encode_genetic_data(self, data: Dict) -> Dict:
        """Private method:
            Encode the genetic information necessary
            to spawn another tree

        Returns:
            Dict: dictionary containing the genetic information
        """      
         
        original_dict: Dict[str, Any] = self.__dict__   # original dictionary with tree data
        genetic_data: Dict[str, Any] = {}               # new dictionary with formatted value                      
        args = inspect.getfullargspec(Tree)[0]          # list of parameters to create a tree
        # loop through original dictionary and
        # take desired values after reformatting 
        for key, value in original_dict.items(): 
            final_key = key[1:]
            if final_key in args:
                genetic_data[final_key] = value
        
        # Work on the parameter that need some custom transformation   
        genetic_data['tree_id'] = original_dict['_SimulatedObject__id']
        genetic_data['position'] = genetic_data['position']()
        genetic_data['blue_energy'] = original_dict['_energies_stock'][EnergyType.BLUE.value]
        genetic_data['red_energy'] = original_dict['_energies_stock'][EnergyType.RED.value]
        
        # Extra given data from environment
        for key, value in data.items():
            genetic_data[key] = value
                    
        return genetic_data
    
    def create_seed(self, data: Dict) -> Seed:
        genetic_data = self._encode_genetic_data(data=data)
        
        seed = Seed(seed_id=self.id,
                    position=self.position,
                    genetic_data=genetic_data)
        
        return seed
       
    def _activate_mind(self, environment: Environment):
        pass
        
class Seed(Resource):
    def __init__(self,
                 seed_id: int,
                 position: Tuple[int, int],
                 genetic_data: Dict):
        
        super(Seed, self).__init__(resource_id=seed_id,
                                   position=position,
                                   size=10,
                                   appearance="seed.png",
                                   quantity=-1)
                
        self.genetic_data = genetic_data
        
    def germinate(self) -> Tree:
        """Public method:
            Spawn a tree from genetic data
            contained in this seed

        Returns:
            Tree: tree spawned
        """        
        return Tree(**self.genetic_data)