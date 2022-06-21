from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Animal, Tree, Entity 
    import numpy as np
    
from typing import Dict, Tuple, Final

from random import randint, sample, random
from itertools import product

from grid import Grid  
from entities import Animal, Tree, Entity, Seed, Status
from energies import Energy, EnergyType, BlueEnergy, RedEnergy, Resource 


class SimState:
    def __init__(self,
                 sim_id: int):
        
        self.__id: int = sim_id
        self.next_entity_id: int  = 1
        self.next_energy_id: int = 1
        
        self.animals: Dict[int, Animal] = {}
        self.trees: Dict[int, Tree] = {}
        self.energies: Dict[int, Tree] = {}
        self.seeds: Dict[int, Seed] = {}
        
        self.added_entities: Dict[int, Entity] = {}
        self.removed_entities: Dict[int, Entity] = {}
        self.added_resources: Dict[int, Resource] = {}
        self.removed_resources: Dict[int, Resource] = {}
        
        self.cycle: int = 1
      
    @property
    def id(self):
        return self.__id
    
    def get_entities(self):
        return (self.animals|self.trees).values()
    
    @property
    def entities(self):
        return self.animals|self.trees
     
    def get_entity_id(self, increment: bool=False) -> int:
        """Public method:
            Get the current entity id

        Args:
            increment (bool): increment the entity id
            
        Returns:
            int: current entity id
        """
        entity_id = self.next_entity_id
        
        if increment:
            self.increment_entity_id()
         
        return entity_id
    
    def increment_entity_id(self, amount: int=1) -> None:
        """ Increment the current entity id by a given amount

        Args:
            amount (int, optional): entity id's increment. Defaults to 1.
        """        
        self.next_entity_id += amount
        
    def get_energy_id(self, increment: bool=False) -> int:
        """Public method:
            Get the current energy id

        Args:
            increment (bool): increment the energy id
            
        Returns:
            int: current energy id
        """
        energy_id = self.next_energy_id
        
        if increment:
            self.increment_energy_id()
         
        return energy_id
    
    def increment_energy_id(self, amount: int=1) -> None:
        """ Increment the current energy id by a given amount

        Args:
            amount (int, optional): energy id's increment. Defaults to 1.
        """        
        self.next_energy_id += amount
        
    def add_entity(self, new_entity: Entity) -> None:
        """Public method:
            Add an entity to the register

        Args:
            new_entity (Entity): new entity to register
        """        
            
        match new_entity.__class__.__name__:
            case "Animal":
                self.animals[new_entity.id] = new_entity
            case "Tree":
                self.trees[new_entity.id] = new_entity
        
        self.added_entities[new_entity.id] = new_entity
                
    def remove_entity(self, entity: Resource) -> None:
        """Public method:
            Remove a entity from the register

        Args:
            entity (Entity):entity to remove
        """ 
         
        self.removed_entities[entity.id] = entity
            
        match entity.__class__.__name__:
            case "Animal":
                self.animals.pop(entity.id)
            case "Tree":
                self.trees.pop(entity.id)
               
                
    def add_resource(self, new_resource: Resource) -> None:
        """Public method:
            Add an resource to the register

        Args:
            new_resource (Resource): new resource to register
        """  
            
        if new_resource.__class__.__base__.__name__ == "Energy":
            self.energies[new_resource.id] = new_resource
            
        else:
            self.seeds[new_resource.id] = new_resource
            
        self.added_resources[new_resource.id] = new_resource
                
    def remove_resource(self, resource: Resource) -> None:
        """Public method:
            Remove a resource from the register

        Args:
            resource (Resource):resource to remove
        """  
            
        if resource.__class__.__base__.__name__ == "Energy":
            self.energies.pop(resource.id)
        else:
            self.seeds.pop(resource.id)
            
        self.removed_resources[resource.id] = resource
        
    def new_cycle(self):
        self.added_entities: Dict[int, Entity] = {}
        self.removed_entities: Dict[int, Entity] = {}
        self.added_resources: Dict[int, Resource] = {}
        self.removed_resources: Dict[int, Resource] = {} 
        
        self.cycle += 1               

class Environment:
    GRID_WIDTH: Final[int] = 20
    GRID_HEIGHT: Final[int] = 20
    
    def __init__(self,
                 env_id: int,
                 sim_state: SimState = None,
                 dimensions: Tuple[int, int] = (20, 20)):
        
        self.__id: int = env_id
        
        self.state: SimState = sim_state or SimState(sim_id=env_id)
        self.grid: Grid
        self.dimensions: Tuple[int, int] = dimensions
        
        self.init()
        
        
    def init(self, populate: bool=False):
        # self.state = SimState(sim_id=self.id)
        self.grid = Grid(grid_id=self.id,
                         dimensions=self.dimensions)
        
        if populate:
            return self.populate()
              
    def populate(self):
        width, height = self.dimensions
        MIN_HORIZONTAL_SIZE_SECTION = 5
        MAX_HORIZONTAL_SIZE_SECTION = 10
        
        MIN_VERTICAL_SIZE_SECTION = 5
        MAX_VERTICAL_SIZE_SECTION = 10
        
        # How much time the grid can be divided by sections
        num_min_section_horizontal = int(width/MIN_HORIZONTAL_SIZE_SECTION)
        num_min_section_vertical = int(height/MIN_VERTICAL_SIZE_SECTION)
        
        num_max_section_horizontal = int(width/MAX_HORIZONTAL_SIZE_SECTION)
        num_max_section_vertical = int(height/MAX_VERTICAL_SIZE_SECTION)
        
        # Choose the number of divisions into section h * v 
        horizontal_divisor = randint(num_max_section_horizontal,
                                     num_min_section_horizontal+1)
        
        vertical_divisor = randint(num_max_section_vertical,
                                   num_min_section_vertical+1)
        
        section_horizontal_size = int(width/horizontal_divisor)
        section_vertical_size = int(height/vertical_divisor)
        
        possible_coordinates = set(product(range(section_horizontal_size),
                                           range(section_vertical_size)))
   
        section_dimension = len(possible_coordinates)
        
        SPARSITY = 5
        DENSITY = int(section_dimension/SPARSITY)
        
        for h in range(horizontal_divisor):
            x_offset = h * section_horizontal_size
            for v in range(vertical_divisor):
                y_offset = v * section_vertical_size
                
                num_animal_section = randint(0, DENSITY)
                coordinates = sample(possible_coordinates,
                                     num_animal_section)
                
                for x, y in coordinates:
                    self.create_animal(coordinates=(x + x_offset,
                                                    y + y_offset),
                                       blue_energy=100,
                                       red_energy=5000,
                                       size=15)
                
        return self.state
   
    @property
    def id(self):
        return self.__id
              
    def interpret_request(self, request, entity):
        
        match entity.status:
            case Status.DEAD:
                self._entity_died(entity=entity)
                
            case Status.FERTILE:
                entities_around = self.grid._find_occupied_cells_by_animals(coordinates=entity.position)  
                for other_entity in entities_around:
                    if other_entity.status == Status.FERTILE:
                        self._reproduce_entities(parent1=entity,
                                                 parent2=other_entity)  
        
    def _add_new_resource_to_world(self, new_resource: Resource):
        """Private method:
            Register the resource into the simulation state

        Args:
            new_resource (Resource): new resource to register
        """ 
        if self.grid.place_resource(value=new_resource):
            self.state.add_resource(new_resource=new_resource)
        

    def _add_new_entity_to_world(self, new_entity: Entity):
        """Private method:
            Register the entity into the simulation state

        Args:
            new_entity (Entity): new entity to register
        """  
        if self.grid.place_entity(value=new_entity):     
            self.state.add_entity(new_entity=new_entity)
            
    def _reproduce_entities(self, parent1: Entity, parent2: Entity):
     
        if not (parent1._is_adult and parent2._is_adult):
            return
                
        parent1_energy_cost = Animal.REPRODUCTION_ENERGY_COST * parent1._size
        parent2_energy_cost = Animal.REPRODUCTION_ENERGY_COST * parent2._size
        
        if (parent1._can_perform_action(energy_type=EnergyType.RED,
                                        quantity=parent1_energy_cost) and
            parent2._can_perform_action(energy_type=EnergyType.RED,
                                        quantity=parent2_energy_cost)):
        
            birth_position = self.grid.entity_grid.select_free_coordinates(coordinates=parent1.position)
            
            if birth_position:
                adult_size = int((parent1.size + parent2.size)/2)
                ancestors = ({parent1.id: parent1, parent2.id: parent2}|
                             parent1.ancestors|
                             parent2.ancestors)
                
                child = self.create_animal(coordinates=birth_position,
                                            size=1,
                                            blue_energy=Animal.INITIAL_BLUE_ENERGY,
                                            red_energy=Animal.INITIAL_RED_ENERGY,
                                            adult_size=adult_size,
                                            generation=self.state.cycle,
                                            ancestors=ancestors)
                
                child.born(parent1=parent1,
                           parent2=parent2)
                
                DIE_GIVING_BIRTH_PROB = 0.02
                if random() < DIE_GIVING_BIRTH_PROB:
                    parent1.status = (Status.DEAD 
                                      if random() < DIE_GIVING_BIRTH_PROB
                                      else Status.ALIVE)
                    
                    parent2.status = (Status.DEAD 
                                      if random() < DIE_GIVING_BIRTH_PROB
                                      else Status.ALIVE)
            
                return child
            
    def create_animal(self, coordinates: Tuple[int, int], **kwargs) -> Animal:
        if not self.grid.entity_grid.are_vacant_coordinates(coordinates=coordinates):
            return None
        
        animal_id = self.state.get_entity_id(increment=True)
          
        animal = Animal(animal_id=animal_id,
                        position=coordinates,
                        **kwargs)
        
        self._add_new_entity_to_world(new_entity=animal)  
        
        return animal
    
    def create_tree(self, coordinates: Tuple[int, int], **kwargs) -> Tree:
        """Create a tree and add it to the world

        Args:
            coordinates (Tuple[int, int]): coordinates where the tree should be created

        Returns:
            Tree: tree that was created
        """ 
        if not self.grid.entity_grid.are_vacant_coordinates(coordinates=coordinates):
            return None
               
        tree_id = self.state.get_entity_id(increment=True)
        tree = Tree(tree_id=tree_id,
                    position=coordinates,
                    **kwargs) 
        
        self._add_new_entity_to_world(new_entity=tree) 
        
        return tree
    
    def create_seed_from_tree(self, tree: Tree) -> Seed:
        """Public method:
            Create a seed from a tree remove the tree from the world 
            and place the seed instead

        Args:
            tree (Tree): tree from which to create the seed
            
        Returns:
            seed (Seed): seed created from the tree
        """        

        # Create a seed from a tree
        seed = tree.create_seed(data={'size': 5,
                                      'action_cost': 1})
        # Remove tree from world
        self.remove_entity(tree)
        
        # Add the seed to the world
        self._add_new_resource_to_world(new_resource=seed)
           
        return seed
    
    def spawn_tree(self, seed: Seed, position: Tuple[int, int]) -> Tree:
        """public method:
            Spawn a tree on a grid at a given position

        Args:
            seed (Seed):            seed from which to create the tree
            position (Position):    position at which the tree should be created

        Returns:
            Energy: energy created
        """        
        # Spawn the tree
        tree = seed.germinate()
                
        # Move tree to proper position
        tree.position = position
        
        # Add the tree to the world
        self._add_new_entity_to_world(new_entity=tree) 
        
        return tree
    
    def create_energy(self, energy_type: EnergyType, quantity: int,
                      coordinates: Tuple[int, int]) -> Energy:
        """Public method:
            Create energy on the grid

        Args:
            energy_type (EnergyType):   type of energy to be created
            quantity (int):             amount of energy to be created
            cell (Tuple[int, int]):     cell of the grid on which the energy should be created
            
        Returns:
            bool:   True if the energy was created successfully,
                    False if it couldn't be created
        """  
        
        if quantity < 1:
            return None
              
        print(f"{energy_type}:{quantity} was created at {coordinates}")
        if not self.grid.resource_grid.are_vacant_coordinates(coordinates=coordinates):
            return None
        
        energy_id = self.state.get_energy_id(increment=True)
        
        match energy_type.value:
            case EnergyType.BLUE.value:
                energy = BlueEnergy(energy_id=energy_id,
                                    position=coordinates,
                                    quantity=quantity)
                
            case EnergyType.RED.value:
                energy = RedEnergy(energy_id=energy_id,
                                   position=coordinates,
                                   quantity=quantity)
                
        self._add_new_resource_to_world(new_resource=energy)
        
        return energy
            
    def remove_resource(self, resource: Resource) -> None:
        """Public method:
            Remove resource from the grid

        Args:
            resource (Resource): resource to remove
        """
        resource_grid = self.grid.resource_grid
        position = resource._position()
        resource_grid._empty_cell(coordinates=position)
        
        self.state.remove_resource(resource=resource)
        print(f"{resource} was deleted at {position}")
        
    def remove_entity(self, entity: Entity):
        """Public method:
            Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.grid.entity_grid
        position = entity._position()
        entity_grid._empty_cell(coordinates=position)
        
        self.state.remove_entity(entity=entity)
        print(f"{entity} was deleted at {position}")
        
    def _entity_died(self, entity: Entity) -> None:
        """Private method:
            Event: an entity died

        Args:
            entity (Entity): entity that died
        """        
        entity.on_death(environment=self)
        
    def decompose_entity(self, entity: Entity) -> None:
        """Public method
            Decompose an entity into its energy components

        Args:
            entity (Entity): entity to decompose
        """        
        # Select free cells to place energy on
        free_cells: Tuple[int, int] = self.grid.resource_grid.select_free_coordinates(
                                                                coordinates=entity.position,
                                                                num_cells=2)
        
        if not free_cells:
            return
        
        # Red energy       
        self.create_energy(energy_type=EnergyType.RED,
                            coordinates=free_cells[0],
                            quantity=entity.energies[EnergyType.RED.value])
    
        # Blue energy  
        if len(free_cells) == 2:                           
            self.create_energy(energy_type=EnergyType.BLUE,
                               coordinates=free_cells[1],
                               quantity=entity.energies[EnergyType.BLUE.value])
        
        
    def get_resource_at(self, coordinates: Tuple[int, int]) -> Resource:
        """Public method:
            Get the resource at the given coordinates and return it

        Args:
            coordinates (Tuple[int, int]): coordinates of the resource

        Returns:
            Resource: resource found
        """        
        return self.grid.resource_grid.get_cell_value(coordinates=coordinates)  
    
    def find_if_entities_around(self, coordinates: Tuple[int, int],
                                include_self: bool=False, radius: int=1) -> np.array:
        """Public method:
            Look for entities in a radius around certain coordinates and
            return a boolean array of cells occupied by entities

        Args:
            coordinates (Tuple[int, int]):  coordinates to search around
            include_self (bool, optional):  central coordinates included. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array: boolean array of cells occupied by entities
        """        
        
        return self.grid.entity_grid.are_instance_baseclass_around(coordinates=coordinates,
                                                                    base_class=Entity,
                                                                    include_self=include_self,
                                                                    radius=radius)
        
    def find_if_resources_around(self, coordinates: Tuple[int, int],
                                 include_self: bool=False, radius: int=1) -> np.array:
        """Public method:
            Look for resources in a radius around certain coordinates and
            return a boolean array of cells occupied by resources

        Args:
            coordinates (Tuple[int, int]):  coordinates to search around
            include_self (bool, optional):  central coordinates included. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array: boolean array of cells occupied by resources
        """       
        
        return self.grid.resource_grid.are_instance_baseclass_around(coordinates=coordinates,
                                                                        base_class=Resource,
                                                                        include_self=include_self,
                                                                        radius=radius)
        
    def get_colors_around(self, coordinates: Tuple[int, int], radius: int=1) -> np.array:
        """Public method:
            Get the colors in a radis around certain coordinates

        Args:
            coordinates (Tuple[int, int]):  coordinates to search around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array: array of colors around
        """        
                                               
        return self.grid.color_grid.get_sub_region(initial_pos=coordinates,
                                                   radius=radius) 
        
    def modify_cell_color(self, coordinates: Tuple[int, int], color: Tuple[int, int, int]):
        """Public method:
            Change the color of a cell

        Args:
            coordinates (Tuple[int, int]):  coordinates of the cell to change color
            color (Tuple[int, int, int]):   color to put
        """        
        self.grid.modify_cell_color(coordinates=coordinates,
                                    color=color) 
        
    def find_trees_around(self, coordinates: Tuple[int, int], radius: int=1):
        return self.grid._find_occupied_cells_by_trees(coordinates=coordinates)
                   
        
class Simulation:
    def __init__(self,
                 sim_id: int,
                 dimensions: Tuple[int, int] = (20, 20)):
    
        self.id = sim_id
        
        self.state: SimState
        self.environment: Environment
        self.dimensions = dimensions
        
            
    def init(self, populate: bool=True):
        self.state = SimState(sim_id=self.id)
        self.environment = Environment(env_id=self.id,
                                       dimensions=self.dimensions,
                                       sim_state=self.state)
        
        self.environment.init(populate=populate)
     
        return self.state
        
    def update(self):
        self.state.new_cycle()
        
        for entity in self.state.get_entities():
            request = entity.update(environment=self.environment)
            self.environment.interpret_request(request=request,
                                               entity=entity)
            
        return self.environment.grid, self.state
      
        
 

    
        