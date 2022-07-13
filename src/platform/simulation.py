from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities import Animal, Tree, Entity

from itertools import product
from random import randint, sample
from typing import Dict, Final, Optional, Set, Tuple, ValuesView

import numpy.typing as npt

from energies import BlueEnergy, Energy, EnergyType, RedEnergy, Resource
from entities import Animal, Entity, Seed, Status, Tree
from grid import Grid


class SimState:
    """Class:
        State of a simulation

        Attributes:
            __id (int):                                 unique identifier
            next_entity_id (int):                       incremental value for the next entity identifier
            next_energy_id (int):                       incremental value for the next energy identifier
            animals (Dict[int, Animal]):                register of simulation's animals
            trees (Dict[int, Tree]):                    register of simulation's trees
            energies (Dict[int, Energy]):               register of simulation's energies
            seeds (Dict[int, Seed]):                    register of simulation's seeds
            added_entities (Dict[int, Entity]):         register of added entities in the last simulation cycle
            removed_entities (Dict[int, Entity]):       register of removed entities in the last simulation cycle
            added_resources (Dict[int, Resource]):      register of added resources in the last simulation cycle
            removed_resources (Dict[int, Resource]):    register of removed resources in the last simulation cycle
            cycle (int):                                current cycle

        Methods:
            get_entities: get all   entities currently in the simulation
            get_resources: get all  resources currently in the simulation
            get_entity_id: get the  current entity id
            increment_entity_id:    increment the current entity id
            get_energy_id:          get the current energy id
            increment_energy_id:    increment the current energy id
            add_entity:             add an entity to the register
            remove_entity:          remove a entity from the register
            add_resource:           adds a resource to the register
            remove_resource:        remove a resource from the register
            new_cycle:              start a new cycle of simulation
    """
    def __init__(self,
                 sim_id: int):
        """Constructor:
            Initialize a new simulation state

        Args:
            sim_id (int): unique identifier of the simulation
        """

        self.__id: int = sim_id                             # unique identifier
        self.next_entity_id: int  = 1                       # incremental value for the next entity identifier
        self.next_energy_id: int = 1                        # incremental value for the next energy identifier

        self.animals: Dict[int, Animal] = {}                # register of simulation's animals
        self.trees: Dict[int, Tree] = {}                    # register of simulation's trees
        self.energies: Dict[int, Energy] = {}               # register of simulation's energies
        self.seeds: Dict[int, Seed] = {}                    # register of simulation's seeds

        self.added_entities: Dict[int, Entity] = {}         # register of added entities in the last simulation cycle
        self.removed_entities: Dict[int, Entity] = {}       # register of removed entities in the last simulation cycle
        self.added_resources: Dict[int, Resource] = {}      # register of added resources in the last simulation cycle
        self.removed_resources: Dict[int, Resource] = {}    # register of removed resources in the last simulation cycle

        self.cycle: int = 1

    @property
    def id(self) -> int:
        """Property:
            Return simulation state's id

        Returns:
            int: simulation's state id
        """
        return self.__id

    def get_entities(self) -> ValuesView[Entity]:
        """Public method:
            Get all entities currently in the simulation

        Returns:
            ValuesView[Entity]: all entities in the simulation
        """
        return (self.animals | self.trees).values()

    @property
    def entities(self) -> Dict[int, Entity]:
        """Property:
            Return the register of entities

        Returns:
            Dict[int, Entity]: register of entities
        """
        return self.animals | self.trees

    def get_resources(self) -> ValuesView[Resource]:
        """Public method:
            Get all the resources currently in the simulation

        Returns:
            ValuesView[Resource]: all resources in the simulation
        """
        return (self.energies | self.seeds).values()

    @property
    def resources(self) -> Dict[int, Resource]:
        """Property:
            Return the register of resources

        Returns:
            Dict[int, Resource]: register of resources
        """
        return self.energies | self.seeds

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
        """Public method:
            Increment the current entity id by a given amount

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

    def remove_entity(self, entity: Entity) -> None:
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

    def new_cycle(self) -> None:
        """Public method:
            Start a new cycle of simulation
        """
        self.added_entities: Dict[int, Entity] = {}
        self.removed_entities: Dict[int, Entity] = {}
        self.added_resources: Dict[int, Resource] = {}
        self.removed_resources: Dict[int, Resource] = {}

        self.cycle += 1

class Environment:
    """Class:
        Environment in which the entities interact

        Attributes:
            __id (int):                     unique identifier
            state (SimState):               state of the simulation
            grid (Grid):                    2 dimensional grid
            dimensions (Tuple[int, int]):   dimensions of the world

        Methods:
            spawn_animal:               create an animal at given coordinates and add it to the world
            spawn_tree:                 create a tree at given coordinates and add it to the world
            create_seed_from_tree:      create a seed from a tree
            sprout_tree:                spawn a tree from a seed at a given position on the grid
            create_energy:              create energy on the grid
            remove_resource:            remove resource from the grid
            remove_entity:              remove entity from the grid
            decompose_entity:           decompose an entity into its energy components
            get_resource_at:            get the resource at the given coordinates and return it
            find_if_entities_around:    look for entities in a radius around certain coordinates
            find_if_resources_around:   look for resources in a radius around certain coordinates
            get_colors_around:          get the colors in a radis around certain coordinates
            modify_cell_color:          change the color of a cell
            find_trees_around:          find and return all the cells occupied by trees
    """
    GRID_WIDTH: Final[int] = 20
    GRID_HEIGHT: Final[int] = 20

    def __init__(self,
                 env_id: int,
                 sim_state: Optional[SimState] = None,
                 dimensions: Tuple[int, int] = (20, 20)):
        """Constructor:
            Initiliaze an environment

        Args:
            env_id (int):                               unique identifier
            sim_state (Optional[SimState], optional):   simulation's state. Defaults to None.
            dimensions (Tuple[int, int], optional):     dimensions of the world. Defaults to (20, 20).
        """

        self.__id: int = env_id                                     # unique identifier

        self.state: SimState = sim_state or SimState(sim_id=env_id) # simulation's state
        self.grid: Grid                                             # 2 dimensional grid
        self.dimensions: Tuple[int, int] = dimensions               # dimensions of the world

        #self.init()

    def init(self, populate: bool=False) -> Optional[SimState]:
        """Public method:
            Initilize the grid and populate the world

        Args:
            populate (bool, optional): should populate the world. Defaults to False.

        Returns:
            Optional[SimState]: simulation state after populating it
        """
        # self.state = SimState(sim_id=self.id)
        self.grid = Grid(grid_id=self.id,
                         dimensions=self.dimensions)

        if populate:
            return self._populate()

    def _populate(self) -> SimState:
        """Private method:
            Populate the world with entities

        Returns:
            SimState: simulation state after populating it
        """
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
                    self.spawn_animal(coordinates=(x + x_offset,
                                                    y + y_offset),
                                       blue_energy=100,
                                       red_energy=5000,
                                       size=15)

        return self.state

    @property
    def id(self) -> int:
        """Property:
            Return the simulation's id

        Returns:
            int: simulation's id
        """
        return self.__id

    def event_on_action(self, entity: Entity) -> None:
        """Private method:
            Event on an entity's actions

        Args:
            entity (Entity): entity deciding on action
        """

        match entity.status:
            case Status.DEAD:
                self._entity_died(entity=entity)

            case Status.FERTILE:
                entities_around = self.grid.find_occupied_cells_by_animals(coordinates=entity.position)
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

    def _reproduce_entities(self, parent1: Entity, parent2: Entity) -> Optional[Entity]:
        """Private method:
            reproduce two entities together to create a child

        Args:
            parent1 (Entity): first entity parent
            parent2 (Entity): second entity parent

        Returns:
            Entity: born child
        """
        if parent1.can_reproduce() and parent2.can_reproduce():

            parent1.on_reproduction()
            parent2.on_reproduction()

            birth_position,  = self.grid.entity_grid.select_free_coordinates(coordinates=parent1.position)

            if birth_position:
                adult_size = int((parent1.size + parent2.size)/2)


                child = self.spawn_animal(coordinates=birth_position,
                                            size=1,
                                            blue_energy=Animal.INITIAL_BLUE_ENERGY,
                                            red_energy=Animal.INITIAL_RED_ENERGY,
                                            adult_size=adult_size,
                                            generation=self.state.cycle)

                if child:
                    child.on_birth(parent1=parent1,
                               parent2=parent2)


                return child

    def spawn_animal(self, coordinates: Tuple[int, int], **kwargs) -> Optional[Animal]:
        """Public method:
            Create an animal at given coordinates and add it to the world

        Args:
            coordinates (Tuple[int, int]): coordinates where the animal should be created

        Returns:
            Animal: animal that was created
        """
        if not self.grid.entity_grid.are_vacant_coordinates(coordinates=coordinates):
            return None

        animal_id = self.state.get_entity_id(increment=True)

        animal = Animal(animal_id=animal_id,
                        position=coordinates,
                        **kwargs)

        self._add_new_entity_to_world(new_entity=animal)

        return animal

    def spawn_tree(self, coordinates: Tuple[int, int], **kwargs) -> Optional[Tree]:
        """Public  method:
            Create a tree at given coordinates and add it to the world

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

    def sprout_tree(self, seed: Seed, position: Tuple[int, int]) -> Tree:
        """public method:
            Spawn a tree from a seed at a given position on the grid

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
                      coordinates: Tuple[int, int]) -> Optional[Energy]:
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
        position = resource.position
        self.grid.remove_resource(resource=resource)

        self.state.remove_resource(resource=resource)
        print(f"{resource} was deleted at {position}")

    def remove_entity(self, entity: Entity):
        """Public method:
            Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.grid.entity_grid
        position = entity.position
        entity_grid.empty_cell(coordinates=position)

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
        free_cells = self.grid.resource_grid.select_free_coordinates(
                        coordinates=entity.position,
                        num_cells=2)

        red_cell = blue_cell = None

        if not free_cells:
            return

        elif len(free_cells) == 2:
            red_cell, blue_cell = free_cells

        elif len(free_cells) == 1:
            red_cell, = free_cells

        # Red energy
        if red_cell:
            self.create_energy(energy_type=EnergyType.RED,
                                coordinates=red_cell,
                                quantity=entity.energies[EnergyType.RED.value])

        # Blue energy
        if blue_cell:
            self.create_energy(energy_type=EnergyType.BLUE,
                               coordinates=blue_cell,
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
                                include_self: bool=False, radius: int=1) -> npt.NDArray:
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
                                 include_self: bool=False, radius: int=1) -> npt.NDArray:
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

    def get_colors_around(self, coordinates: Tuple[int, int], radius: int=1) -> npt.NDArray:
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

    def find_trees_around(self, coordinates: Tuple[int, int], radius: int=1) -> Set[Tuple[int, int]]:
        """Public method:
            Find and return all the cells occupied by trees
            in a radius around a certain coordinates

        Args:
            coordinates (Tuple[int, int]): _description_
            radius (int, optional): _description_. Defaults to 1.

        Returns:
            Set[Tuple[int, int]]: _description_
        """
        return self.grid.find_occupied_cells_by_trees(coordinates=coordinates,
                                                      radius=radius)


class Simulation:
    """Class:
        Real-time simulation

        Attributes:
            __id (int):                     unique identifier
            state (SimState):               state of the simulation
            environment (Environment):      environment with which entities can interact
            dimensions (: Tuple[int, int]): dimensions of the world
    """
    def __init__(self,
                 sim_id: int,
                 dimensions: Tuple[int, int] = (20, 20)):

        self.__id: int = sim_id                         # unique identifier

        self.state: SimState                            # simulation's state
        self.environment: Environment                   # environment with which entities can interact
        self.dimensions: Tuple[int, int] = dimensions   # dimensions of the world


    def init(self, populate: bool=True) -> SimState:
        """Public method:
            Initialize the simulation,
            creating a state and environment

        Args:
            populate (bool, optional): should populate the world. Defaults to True.

        Returns:
            SimState: state of the simulation after initialization
        """
        self.state = SimState(sim_id=self.__id)
        self.environment = Environment(env_id=self.__id,
                                       dimensions=self.dimensions,
                                       sim_state=self.state)

        self.environment.init(populate=populate)

        return self.state

    def update(self) -> Tuple[Grid, SimState]:
        """Public method:
            Update the simulation,
            start a new cycle, update each entity,
            apply entities' actions on environment

        Returns:
            Tuple[Grid, SimState]:  Grid: world's state
                                    SimState: simulation's state
        """
        self.state.new_cycle()

        for entity in self.state.get_entities():
            entity.update(environment=self.environment)
            self.environment.event_on_action(entity=entity)

        # Update state of the simulation
        return self.environment.grid, self.state

    @property
    def id(self) -> int:
        """Property:
            Return the simulation's id

        Returns:
            int: simulation's id
        """
        return self.__id


