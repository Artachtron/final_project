from __future__ import annotations

import enum
from functools import lru_cache
from itertools import combinations
from random import sample
from typing import Any, Optional, Set, Tuple, Type

import numpy as np
import numpy.typing as npt

from .energies import Energy, Resource
from .entities import Animal, Entity, Tree


class SubGridType(enum.Enum):
    """Enum:
        Layer of grid
    """
    ENTITY = 0
    RESOURCE = 1
    COLOR = 2


class SubGrid:
    """Class:
        Layer of the grid

        Attributes:
            dimensions (Tuple[int, int]):   dimensions of the grid
            data_type (Any):                type of data allowed
            initial_value (Any):            value to fill empty cells with
            _array (npt.NDArray):           array of values

        Methods:
            are_available_coordinates:      check if the coordinates correspond to valid cell
            are_vacant_coordinates:         check if a cell is vacant
            are_coordinates_in_bounds:      check if a cell is in the bounds of the grid
            are_instance_baseclass_around:  find all the instance of a certain base class in an area
            find_free_coordinates:          find a free cell in range
            select_free_coordinates:        select randomly from the free cells available
            update_cell:                    move an element from a cell to another
            empty_cell:                     empty the cell, putting it back to inital state
            get_cell_value:                 get the value of a cell
            get_sub_region:                 Return an array around a given position of a defined size
    """
    def __init__(
        self,
        dimensions: Tuple[int, ...],
        data_type: Any = Any,
        initial_value: Any = None,
    ):
        """Constructor:
            Initialize a subgrid

        Args:
            dimensions (Tuple[int, int]):   dimensions of the grid
            data_type (Any, optional):      type of data allowed. Defaults to Any.
            initial_value (Any, optional):  value to fill the emtpy cells with. Defaults to None.
        """

        self.dimensions: Tuple[int, ...]  = dimensions                      # dimensions of the grid
        self.data_type: Any = data_type                                     # type of data allowed
        self.initial_value: Any = initial_value                             # value to fill the emtpy cells with
        self._array: npt.NDArray[Any] = np.full(self.dimensions,            # array of values
                                                fill_value=initial_value,
                                                dtype=data_type
        )

    @property
    def array(self) -> npt.NDArray[Any]:
        """Property:
            Return the array of values

        Returns:
            npt.NDArray[Any]: array of values
        """
        return self._array

    def empty_cell(self, coordinates: Tuple[int, int]):
        """Public method:
            Empty the cell, putting it back to inital state

        Args:
            coordinates (Tuple[int, int]): coordinates of the cell to emtpy
        """
        self._array[coordinates] = self.initial_value

    def _set_operation_valid(self, coordinates: Tuple[int, int], value: Any) -> bool:
        """Private method:
            Check if the set operation is valid, by applying 3 checks:
            - the coordinates are inside the bounds of the grid
            - the cell of given coordinates is free
            - the value is of valid type

        Args:
            coordinates (Tuple[int, int]):  coordinates to check for
            value (Any):                  value to check type of

        Returns:
            bool: True if all checks passed,
                  False if at least one check failed
        """
        return (self.are_coordinates_in_bounds(coordinates=coordinates)
            and self.are_vacant_coordinates(coordinates=coordinates)
            and self._is_of_valid_type(value=value))

    def place_on_grid(self, value: Any) -> bool:
        """Public method:
            (Call place_entity or place_resource
            from grid instead)
            Place a given value on the grid,
            based on its position

        Args:
            value (Any): value to place on the grid

        Returns:
            bool:   True if the value was placed on the grid
                    False if it couldn't place it
        """

        coordinates: Tuple[int, int] = value.position  # position of the value

        return self._set_cell_value(coordinates=coordinates,
                                    value=value)

    def _is_of_valid_type(self, value: Any) -> bool:
        """Private method:
            Verify if the value's type is valid

        Args:
            value (Any): value of which to check type

        Returns:
            bool:   True if the value if of a valid type,
                    False if invalid type
        """
        return Grid.is_subclass(value, self.data_type)

    def are_available_coordinates(self, coordinates: Tuple[int, int]) -> bool:
        """Public method:
            Check if the coordinates correspond to valid cell,
            the cell has to be on the grid and be vacant

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the cell is on the grid and vacant,
                    False if the cell is not on the grid or occupied
        """
        return (self.are_coordinates_in_bounds(coordinates=coordinates) and
                self.are_vacant_coordinates(coordinates=coordinates))

    def are_vacant_coordinates(self, coordinates: Tuple[int, int]) -> bool:
        """Public method:
            Check if a cell is vacant

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the cell is vacant,
                    False if the cell is already occupied
        """
        return not self.get_cell_value(coordinates=coordinates)

    def are_coordinates_in_bounds(self, coordinates: Tuple[int, int]) -> bool:
        """Private method:
            Check if a cell is in the bounds of the grid

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the coordinates are in the bounds of the grid,
                    False if the coordinates are out of the grid
        """
        x, y = coordinates

        return not (x < 0 or
                    x >= self.dimensions[0] or
                    y < 0 or
                    y >= self.dimensions[1])

    def are_instance_baseclass_around(
        self,
        coordinates: Tuple[int, int],
        base_class: Type,
        include_self: bool = False,
        radius: int = 1
        ) -> npt.NDArray[Any]:

        """Public method:
            Find all the instance of a certain base class in a radius around some coordinates,
            return an boolean array with cells filled by baseclass' instances

        Args:
            coordinates (Tuple[int, int]):  coordinates to search around
            base_class (Type):              base class as reference for the search
            include_self (bool, optional):  include the coordinates in the search. Defaults to False.
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array[bool]: boolean mask of instance of baseclass in cells
        """

        subregion: npt.NDArray[Any] = self.get_sub_region(initial_pos=coordinates,
                                                          radius=radius)

        occupied_cells = []
        for x in range(0, 2 * radius + 1):
            for y in range(-0, 2 * radius + 1):
                if (not include_self and
                    x == int(radius / 2 + 1) and
                    y == int(radius / 2 + 1)):

                    continue

                occupied_cells.append(Grid.is_subclass(derived=subregion[x, y],
                                                       base_class=base_class))

        return np.array(occupied_cells)

    def _find_coordinates_baseclass(
        self,
        base_class: Any,
        coordinates: Tuple[int, int],
        radius: int = 1
        ) -> Set[Tuple[int, int]]:

        """Private method:
            Find the list of cells at given radius distance from specified class

        Args:
            base_class (Any):               class to search for
            coordinates (Tuple[int,int]):   starting position to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found cells' coordinates
        """

        if not (
            self.are_coordinates_in_bounds(coordinates=tuple(np.add(coordinates, (-radius, -radius))))
            and self.are_coordinates_in_bounds(coordinates=tuple(np.add(coordinates, (radius, radius))))
        ):

            search_interval = list(range(radius * 2 + 1))   # List from (0, 2*radius)
            search_area = combinations(search_interval * 2, 2)        # ALl the combinations of coordinates

            subregion: npt.NDArray[Any] = self.get_sub_region(
                initial_pos=coordinates, radius=radius
            )

            # Optimised code to search if the cell at those coordinates contain an object
            # that is a subclass of the class given, if yes add it to the list of coordinates.
            # Avoid indexError when out of bounds
            positions = {
                tuple(np.add(coordinates, coordinate) - radius)
                for x, y in set(search_area)
                if Grid.is_subclass(derived=subregion[coordinate:= tuple((x, y))],
                                    base_class=base_class)
            }
        else:
            # Faster when no risk of indexError
            search_interval = list(range(-radius, radius + 1))  # List from (-radius, radius)
            search_area = combinations(search_interval * 2, 2)  # ALl the combinations of coordinates

            # Optimised code to search if the cell at those coordinates contain an object
            # that is a subclass of the class given, if yes add it to the list of coordinates
            positions: Set[Tuple[int, int]] = {
                coordinate
                for x, y in set(search_area)
                if (
                    Grid.is_subclass(
                        derived=self.get_cell_value(
                            coordinate := tuple(np.add(coordinates, (x, y)))
                        ),
                        base_class=base_class,
                    )
                )
            }

        return positions

    def find_instances_baseclass_around(
        self, base_class: Any,
        coordinates: Tuple[int, int],
        include_self: bool = False,
        radius: int = 1,
    ) -> Set[Any]:

        """Private method:
            Find all the instances of a certain base class around and
            return a set containing them

            Args:
                coordinates (Tuple[int, int]):  coordinates to search around
                base_class (Type):              base class as reference for the search
                include_self (bool, optional):  include the coordinates in the search. Defaults to False.
                radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set of instances of the base class around
        """

        instances = set()
        search_interval = np.arange(-radius, radius + 1)  # List from (-radius, radius)
        a, b = coordinates
        for x in search_interval:
            for y in search_interval:
                if not include_self and x == 0 and y == 0:
                    continue

                position = (a+x, b+y)
                obj = self.get_cell_value(coordinates=position)
                if obj:
                    if Grid.is_subclass(derived=obj,
                                        base_class=base_class):

                        instances.add(obj)

        return instances
    
    def find_closest_instances_baseclass(
        self, base_class: Any,
        coordinates: Tuple[int, int],
        radius: int = 1,
    ) -> Set[Any]:

        """Private method:
            Find all the instances of a certain base class around and
            return a set containing them

            Args:
                coordinates (Tuple[int, int]):  coordinates to search around
                base_class (Type):              base class as reference for the search
                include_self (bool, optional):  include the coordinates in the search. Defaults to False.
                radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set of instances of the base class around
        """
        def find_instance(position:Tuple[int, int], instances: Set, base_class: Any):
            obj = self.get_cell_value(coordinates=position)
            if obj:
                if Grid.is_subclass(derived=obj,
                                    base_class=base_class):

                    instances.add(obj)
        
        instances = set()
        a, b = coordinates
        for n in range(1, radius):
            for x in (-n, n):
                for y in range(-n+1, n):
                    find_instance(position=(a+x, b+y),
                                  instances=instances,
                                  base_class=base_class)

                    find_instance(position=(a+y, b+x),
                                  instances=instances,
                                  base_class=base_class)
  
                find_instance(position=(a+x, b+x),
                              instances=instances,
                              base_class=base_class)
                
                find_instance(position=(a+x, b-x),
                              instances=instances,
                              base_class=base_class)

            if instances:
                break
            
        return instances

        
        

    def find_free_coordinates(
        self, coordinates: Tuple[int, int], radius: int = 1
    ) -> Set[Tuple[int, int]]:

        """Public method:
            Find a free cell in range

        Args:
            radius (int, optional):     radius of search. Defaults to 1.
            position (Tuple[int,int]):  starting position to look around

        Returns:
            Set[Tuple[int,int]]: set of free cells' coordinates
        """
        search_interval = list(range(-radius, radius + 1))  # List from (-radius, radius)
        search_area = combinations(search_interval * 2, 2)  # ALl the combinations of coordinates

        positions = {
            coordinate
            for x, y in set(search_area)
            if self.get_cell_value(coordinate:= tuple(np.add(coordinates, (x, y))))
            is None
        }

        return positions

    def select_free_coordinates(
        self, coordinates: Tuple[int, int], radius: int = 1, num_cells: int = 1
    ) -> Optional[Set[Tuple[int, int]]]:

        """Public method:
            Select randomly from the free cells available

        Args:
            coordinates (Tuple[int,int]):   starting position to look around
            radius (int, optional):         radius of search. Defaults to 1.
            num_cells (int):                number of cells to return. Defaults to 1

        Returns:
            Optional[Set[Tuple[int, int]]]: Set of coordinates of free cells, if num_cells > 1
        """
        free_cells: Set[Tuple[int, int]] = self.find_free_coordinates(
                                                    coordinates=coordinates,
                                                    radius=radius
                                                )

        if free_cells:
            # Make sure no more than free cells
            # are being requested
            num_choice = min(len(free_cells), num_cells)

            samples = sample(free_cells, num_choice)

            free_cells = set(samples)
        
        return free_cells

    def update_cell(self, new_coordinates: Tuple[int, int], value: Any) -> bool:
        """Public method:
            Move an element from a cell to another,
            filling the new one and emptying the old one

        Args:
            new_coordinates (Tuple[int, int]):  coordinates in which to move the element
            value (Any):                        value to move at different coordinates

        Returns:
            bool:   True if the element was moved successfully
                    False if it couldn't be move and nothing changed
        """

        # try to insert the new value at the given coordinates
        if success := self._set_cell_value(coordinates=new_coordinates,
                                           value=value):

            # Reset the old position
            old_position = value.position
            self.empty_cell(coordinates=old_position)

        return success

    def _set_cell_value(self, coordinates: Tuple[int, int], value: Any) -> bool:
        """Private method:
            Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): coordinates of the cell in the grid
            value (int):                new value to assign

        Returns:
            bool:   True if the value was successfully set
                    False if it couldn't be updated
        """
        if success := self._set_operation_valid(coordinates=coordinates,
                                                value=value):
            try:
                self._array[coordinates] = value
            except IndexError:
                pass
                # print("{coordinates} is out of bounds")

        return success

    def get_cell_value(self, coordinates: Tuple[int, int]) -> Any:
        """Public method:
            Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            Any: value of the cell, None if empty
        """
        try:
            if coordinates[0] < 0 or coordinates[1] < 0:
                raise IndexError

            return self._array[coordinates]

        except IndexError:
            # print(f"{coordinates} is out of bounds")
            return False

    def get_sub_region(self, initial_pos: Tuple[int, int], radius: int = 1) -> npt.NDArray[Any]:
        """Public method:
            Return an array around a given position of a defined size,
            even if the inital position is close from borders,
            pad with -1 values for cells out of boundaries

        Args:
            initial_pos (Tuple[int,int]):   position from which to search around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array: padded subregion with dimensions depending only on radius
        """
        x1, x2, y1, y2 = (
            initial_pos[0] - radius,
            initial_pos[0] + radius + 1,
            initial_pos[1] - radius,
            initial_pos[1] + radius + 1,
        )

        padded_subregion: npt.NDArray[Any]
        ndim: int = self._array.ndim
        width = height = 0

        if ndim == 3:
            width, height, depth = self.dimensions
            padded_subregion = np.full(fill_value=-255, shape=(x2 - x1, y2 - y1, depth))
        elif ndim == 2:
            width, height = self.dimensions
            padded_subregion = np.full(fill_value=None, shape=(x2 - x1, y2 - y1))

        left_pad = right_pad = up_pad = down_pad = 0

        if x1 < 0:
            left_pad = -x1
            x1 = 0
        if x2 > width:
            right_pad = x2 - width
            x2 = width
        if y1 < 0:
            up_pad = -y1
            y1 = 0
        if y2 > height:
            down_pad = y2 - height
            y2 = height

        subregion: npt.NDArray[Any] = self._array[x1:x2, y1:y2]

        x_shape, y_shape = subregion.shape[:2]

        for x in range(x_shape):
            for y in range(y_shape):
                padded_subregion[x + left_pad, y + up_pad] = subregion[
                    x - right_pad, y - down_pad
                ]

        return padded_subregion


class Grid:
    """Class:
        2D world with different layers composed of cells

        Attributes:
            __id (int):                     unique identifier
            dimensions(Tuple[int, int]):    dimensions of the grid
            _resource_grid (SubGrid):       subgrid containing the resources
            _entity_grid (SubGrid):         subgrid containing the entities
            _color_grid (SubGrid):          subgrid containing the color values

        Static methods:
            is_subclass:        check if an object is an instance of a subclass
            place_resource:     place a resource on the appropriate subgrid
            remove_resource:    remove a resource from the appropriate subgrid
            place_entity:       place an entity on the appropriate subgrid
            remove_entity:      remove a entity from the appropriate subgrid
            modify_cell_color:  modify the color of a cell in the color grid

    """
    def __init__(self, grid_id: int, dimensions: Tuple[int, int]):
        """Constructor:
            Initialize a grid

        Args:
            grid_id (int):                  unique identifier
            dimensions (Tuple[int, int]):   dimensions of the grid
        """

        self.__id = grid_id  # unique identifier
        self.dimensions: Tuple[int, int] = dimensions  # dimensions of the grid

        self._entity_grid: SubGrid = SubGrid(
            dimensions=self.dimensions,  # subgrid containing the entities
            data_type=Entity,
            initial_value=None,
        )

        self._resource_grid: SubGrid = SubGrid(
            dimensions=self.dimensions,  # subgrid containing the resources
            data_type=Resource,
            initial_value=None,
        )

        self._color_grid: SubGrid = SubGrid(
            dimensions=(*self.dimensions, 3),  # subgrid containing the color values
            data_type=np.uint8,
            initial_value=255,
        )

    @property
    def id(self) -> int:
        """property:
            get the id of this grid

        Returns:
            int: grid's id
        """
        return self.__id

    @property
    def entity_grid(self) -> SubGrid:
        """property:
            get the entity subgrid of this grid

        Returns:
            SubGrid: entity subgrid
        """
        return self._entity_grid

    @property
    def resource_grid(self) -> SubGrid:
        """property:
            get the resource subgrid of this grid

        Returns:
            SubGrid: resource subgrid
        """
        return self._resource_grid

    @property
    def color_grid(self) -> SubGrid:
        """property:
            get the color subgrid of this grid

        Returns:
            SubGrid: color subgrid
        """
        return self._color_grid

    @property
    def width(self) -> int:
        """property:
            get the width of the grid

        Returns:
            int: width of the grid
        """
        return self.dimensions[0]

    @property
    def height(self) -> int:
        """property:
            get the heigth of the grid

        Returns:
            int: heigth of the grid
        """
        return self.dimensions[1]

    @lru_cache
    @staticmethod
    def is_subclass(derived: Any, base_class: Type) -> bool:
        """Static public method:
            Check if an object is an instance
            of a subclass of a certain base class

        Args:
            derived (Any):      instance to check for base classes
            base_class (Type):  reference base class

        Returns:
            bool:   True if derived is an instance of a subclass of the base class
                    False if base class is not in the list of derived base classes
        """
        for cls in derived.__class__.__mro__[:-1]:
            if cls.__name__ == base_class.__name__:
                return True

        return False

    def place_resource(self, value: Resource) -> bool:
        """Public method:
            Place a resource from the appropriate subgrid

        Args:
            value (Resource): resource to place on the grid

        Returns:
            bool:   True if the operation was successful
                    False if the resource couldn't be placed
        """
        return self.resource_grid.place_on_grid(value=value)
    
    def remove_resource(self, resource: Resource)  -> None:
        """Public method:
            Remove a resource on the appropriate subgrid

        Args:
            resource (Resource): resource to remove
        """  
        self.resource_grid.empty_cell(coordinates=resource.position)      

    def place_entity(self, value: Entity) -> bool:
        """Public method:
            Place an entity on the appropriate subgrid

        Args:
            value (Entity): entity to place on the grid

        Returns:
            bool:   True if the operation was successful
                    False if the entity couldn't be placed
        """
        return self.entity_grid.place_on_grid(value=value)
    
    def remove_entity(self, entity: Entity)  -> None:
        """Public method:
            Remove a entity on the appropriate subgrid

        Args:
            entity (Entity): entity to remove
        """  
        self.entity_grid.empty_cell(coordinates=entity.position) 

    def modify_cell_color(self, coordinates: Tuple[int, int],
                          color: Tuple[int, int, int]) -> None:
        """Public method:
            Modify the color of a cell in the color grid

        Args:
            coordinates (Tuple[int, int]): coordinates of the cell
            color (Tuple[int, int, int]):  color to apply to the cell
        """
        if self.color_grid.are_coordinates_in_bounds(coordinates=coordinates):
            self.color_grid.array[coordinates] = color

    def find_animal_instances(self, coordinates: Tuple[int, int],
                              radius: int = 1) -> Set[Any]:
        """Private method:
            Find all the animals in a radius around given coordinates,
            return a set of all the animals found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the animals found
        """
        return self.entity_grid.find_instances_baseclass_around(
                coordinates=coordinates,
                radius=radius,
                base_class=Animal
            )
    
    def find_close_animal_instances(self, coordinates: Tuple[int, int],
                                    radius: int = 1) -> Set[Any]:
        """Private method:
            Find all the animals in a radius around given coordinates,
            return a set of all the animals found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the animals found
        """
        return self.entity_grid.find_closest_instances_baseclass(
                coordinates=coordinates,
                radius=radius,
                base_class=Animal
            ) 
        
        
    def find_energy_instances(self, coordinates: Tuple[int, int],
                              radius: int = 1) -> Set[Any]:
        """Private method:
            Find all the energies in a radius around given coordinates,
            return a set of all the energies found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the energies found
        """
        return self.resource_grid.find_instances_baseclass_around(
                coordinates=coordinates,
                radius=radius,
                base_class=Energy
            )
        
    def find_close_energy_instances(self, coordinates: Tuple[int, int],
                                    radius: int = 1) -> Set[Any]:
        """Private method:
            Find all the energies in a radius around given coordinates,
            return a set of all the energies found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the energies found
        """
        return self.entity_grid.find_closest_instances_baseclass(
                coordinates=coordinates,
                radius=radius,
                base_class=Energy
            ) 
                
    def find_occupied_cells_by_animals(self, coordinates: Tuple[int, int],
                                       radius: int = 1) -> Set[Any]:
        """Private method:
            Find all the cells occupied by animals in a radius around given coordinates,
            return a set of all the cells found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the cells found
        """
        return self.entity_grid._find_coordinates_baseclass(
                coordinates=coordinates,
                radius=radius,
                base_class=Animal
            )

    def find_occupied_cells_by_trees(
        self, coordinates: Tuple[int, int], radius: int = 1
    ) -> Set[Any]:
        """Private method:
            Find all the cells occupied by trees in a radius around given coordinates,
            return a set of all the cells found

        Args:
            coordinates (Tuple[int, int]):  coordinates to look around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            Set[Any]: set containing all the cells found
        """
        return self.entity_grid.find_instances_baseclass_around(
                coordinates=coordinates,
                radius=radius,
                base_class=Tree
            )
