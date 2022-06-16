from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Animal, Tree, Entity 
    
from typing import Dict, Tuple

from grid import Grid  
from entities import Animal, Tree, Entity, Seed
from energies import Energy, EnergyType, BlueEnergy, RedEnergy, Resource   

class SimState:
    def __init__(self,
                 sim_id: int):
        
        self.__id: int = sim_id
        self.next_entity_id: int  = 1
        self.next_energy_id: int = 1
        
        self.animals: Dict[int, Animal] = {}
        self.trees: Dict[int, Tree] = {}
      
    @property
    def id(self):
        return self.__id
     
    def get_entity_id(self, increment: bool=False) -> int:
        """ Get the current innovation number

        Returns:
            int: current innovation number
        """
        number = self.next_entity_id
        
        if increment:
            self.increment_entity_id()
         
        return number
    
    def increment_entity_id(self, amount: int=1) -> None:
        """ Increment the current innovation number by a given amount

        Args:
            number (int, optional): innovation number's increment. Defaults to 1.
        """        
        self.next_entity_id += amount
        
    def add_entity(self, new_entity: Entity) -> None:
        """ Add an innovation to the history's list of innovations

        Args:
            new_innovation (Innovation): innovation to add to the list
        """        
            
        match new_entity.__class__.__name__:
            case "Animal":
                self.animals[new_entity.id] = new_entity
            case "Tree":
                self.trees[new_entity.id] = new_entity
                

class Environment:
    def __init__(self,
                 env_id: int):
        
        self.__id: int = env_id
        
        self.state: SimState
        self.grid: Grid
        
        self._init_environment()
        
    def _init_environment(self):
        self.state = SimState(sim_id=self.id)
        self.grid = Grid(grid_id=self.id,
                         dimensions=(20,20))
        

    @property
    def id(self):
        return self.__id

    def _add_new_entity_to_world(self, new_entity):
        
        self.state.add_entity(new_entity)
        self.grid.place_entity(new_entity)

    def create_animal(self, coordinates: Tuple[int, int]) -> Animal:
        animal_id = self.state.get_entity_id(increment=True)
          
        animal = Animal(animal_id=animal_id,
                        position=coordinates)
        
        self._add_new_entity_to_world(new_entity=animal)  
        
        return animal
    
    def create_tree(self, coordinates: Tuple[int, int]) -> Tree:
        tree_id = self.state.get_entity_id(increment=True)
        tree = Tree(tree_id=tree_id,
                    position=coordinates) 
        
        self._add_new_entity_to_world(new_entity=tree) 
        
        return tree
    
    def create_seed_from_tree(self, tree: Tree):
    
        seed = tree.create_seed()
        
        self.remove_entity(tree)
        
        self.grid.place_resource(value=seed)
    
    def spawn_tree(self, seed: Seed, position: Tuple[int, int]) -> Tree:
        """public method:
            Spawn a tree on a grid at a given position

        Args:
            seed (Seed):            seed from which to create the tree
            grid (Grid):            grid on which to create the tree
            position (Position):    position at which the tree should be created

        Returns:
            Tree: tree that was spawned
        """        
        # Spawn the tree
        tree = seed.germinate()
        # Move it to the proper position
        tree.position = position
        self.grid.place_entity(value=tree)
        
        return tree
    
    def create_energy(self, energy_type: EnergyType, quantity: int, coordinates: Tuple[int, int]) -> bool:
        """Create energy on the grid

        Args:
            energy_type (EnergyType):   type of energy to be created
            quantity (int):             amount of energy to be created
            cell (Tuple[int, int]):     cell of the grid on which the energy should be created
            
        Returns:
            bool:   True if the energy was created successfully,
                    False if it couldn't be created
        """        
        print(f"{energy_type} was created at {coordinates}")
        match energy_type.value:
            case EnergyType.BLUE.value:
                energy = BlueEnergy(energy_id=0,
                                    position=coordinates,
                                    quantity=quantity)
                
            case EnergyType.RED.value:
                energy = RedEnergy(energy_id=0,
                                   position=coordinates,
                                   quantity=quantity)
          
        return self.grid.place_resource(energy)
        
        
    
    def remove_energy(self, energy: Energy) -> None:
        """Remove energy from the grid

        Args:
            energy (Energy): energy to remove
        """
        resource_grid = self.grid.resource_grid
        position = energy._position()
        resource_grid._empty_cell(coordinates=position)
        print(f"{energy} was deleted at {position}")
        
    def remove_entity(self, entity: Entity):
        """Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.grid.entity_grid
        position = entity._position()
        entity_grid._empty_cell(coordinates=position)
        print(f"{entity} was deleted at {position}")
        
    def get_resource_at(self, coordinates: Tuple[int, int]) -> Resource:
        return self.grid.resource_grid.get_cell_value(coordinates=coordinates)        
        
class Simulation:
    def __init__(self,
                 sim_id: int):
    
        self.id = sim_id
        
        self.environment: Environment
        
        self._init_simulation()
    
    def _init_simulation(self):
        self.environment = Environment(env_id=self.id)   
    
   
        