from __future__ import annotations
from typing import Tuple
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid
    
from simulation import SimState    
from entities import Animal, Tree, Entity, Seed
from energies import Energy, EnergyType, BlueEnergy, RedEnergy

class Environment:
    def __init__(self,
                 env_id: int):
        
        self.__id: int = env_id
        
        self.state: SimState
        self.grid: Grid
        
        self._init_environment()
        
    def _init_environment(self):
        self.state = SimState(sim_id=self.id)
        self.grid = self.state.grid
        

    @property
    def id(self):
        return self.__id

    def _add_new_entity_to_world(self, new_entity):
        
        self.state.add_entity(new_entity)
        self.grid.place_entity(new_entity)

    def create_animal(self, coordinates: Tuple[int, int]) -> Animal:
        animal_id = self.state.get_entity_id(increment=True)
          
        animal = Animal(animal_id=animal_id,
                        position=coordinates,
                        environment=self)
        
        self._add_new_entity_to_world(new_entity=animal)  
        
        return animal
    
    def create_tree(self, coordinates: Tuple[int, int]) -> Tree:
        tree_id = self.state.get_entity_id(increment=True)
        tree = Tree(tree_id=tree_id,
                    position=coordinates,
                    environment=self) 
        
        self._add_new_entity_to_world(new_entity=tree) 
        
        return tree
    
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
    
    def create_energy(self, energy_type: EnergyType, quantity: int, coordinates: Tuple[int, int]):
        """Create energy on the grid

        Args:
            energy_type (EnergyType):   type of energy to be created
            quantity (int):             amount of energy to be created
            cell (Tuple[int, int]):     cell of the grid on which the energy should be created
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
          
        self.grid.resource_grid._set_cell_value(coordinates=coordinates,
                                          value=energy)
    
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