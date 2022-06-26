# Typing
from __future__ import annotations
from typing import Tuple, Any, Set, Type

# Internals packages
from energies import Resource
from entities import Entity, Animal, Tree

# External libraries
import enum
import numpy as np
from random import sample
from itertools import combinations

class SubGridType(enum.Enum):
    ENTITY = 0
    RESOURCE = 1
    COLOR = 2

class SubGrid:
    def __init__(self,
                 dimensions: Tuple[int,int],
                 data_type: Any = Any,
                 initial_value: Any = None):
        
        self.dimensions: Tuple[int,int] = dimensions                # dimensions of the grid
        self.data_type = data_type                                  # type of data allowed on the grid
        self.initial_value = initial_value                          # value to fill the emtpy cells with
        self._array: np.array = np.full(self.dimensions,            # array containing the values
                                        fill_value=initial_value,
                                        dtype=data_type)
        
    @property
    def array(self) -> np.array:
        return self._array
    
    def _empty_cell(self, coordinates: Tuple[int, int]):
        """Private method:
            Emtpy the cell, putting it back to inital state

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
        return (self._are_coordinates_in_bounds(coordinates=coordinates) and
                self.are_vacant_coordinates(coordinates=coordinates) and
                self._is_of_valid_type(value=value))
    
    def _place_on_grid(self, value: Any) -> bool:
        """Private method:
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
         
        coordinates: Tuple[int, int] = value.position # position of the value
          
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
        return (self._are_coordinates_in_bounds(coordinates=coordinates) and
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

    def _are_coordinates_in_bounds(self, coordinates: Tuple[int, int]) -> bool:
        """Private method:
            Check if a cell is in the bounds of the grid

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the coordinates are in the bounds of the grid,
                    False if the coordinates are out of the grid
        """
        x, y = coordinates
        
        return not (x < 0 or x >= self.dimensions[0] or
                    y < 0 or y >= self.dimensions[1])
 
    def are_instance_baseclass_around(self, coordinates: Tuple[int, int], base_class: Type, 
                                       include_self: bool=False, radius: int=1) -> np.array:
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
    
        subregion = self.get_sub_region(initial_pos=coordinates,
                                        radius=radius) 
    
        occupied_cells = []
        for x in range(0, 2*radius + 1):
                for y in range(-0, 2*radius + 1):
                    if not include_self and x == int(radius/2 + 1) and y == int(radius/2 + 1):
                        continue                    
                    occupied_cells.append(Grid.is_subclass(derived=subregion[x,y],
                                          base_class=base_class))
                    
                       
        return np.array(occupied_cells) 
    
    
    def _find_coordinates_baseclass(self, base_class: Any, coordinates: Tuple[int, int],
                                     radius: int = 1) -> Set[Tuple[int, int]]:
        """Private method:
            Find the list of cells at given radius distance from specified class
            
        Args:
            base_class (Any):               class to search for
            coordinates (Tuple[int,int]):   starting position to look around
            radius (int, optional):         radius of search. Defaults to 1.
            
        Returns:
            Set[Tuple[int,int]]: set of found cells' coordinates
        """
        
        if not (self._are_coordinates_in_bounds(coordinates=np.add(coordinates,-radius)) and
                self._are_coordinates_in_bounds(coordinates=np.add(coordinates, radius))):
            
            a = list(range(radius*2 + 1))  # List from (0, 2*radius)
            b = combinations(a*2, 2)       # ALl the combinations of coordinates
        
            subregion = self.get_sub_region(initial_pos=coordinates,
                                            radius=radius) 
        
            # Optimised code to search if the cell at those coordinates contain an object
            # that is a subclass of the class given, if yes add it to the list of coordinates.
            # Avoid indexError when out of bounds
            positions = [tuple(np.add(coordinates, coordinate)-1) for x, y in set(b) if
                         Grid.is_subclass(derived=subregion[coordinate:=tuple((x,y))],
                                          base_class=base_class
                        )]
        else:
        # Faster when no risk of indexError  
            a = list(range(-radius, radius+1))  # List from (-radius, radius)
            b = combinations(a*2, 2)            # ALl the combinations of coordinates
        
            # Optimised code to search if the cell at those coordinates contain an object
            # that is a subclass of the class given, if yes add it to the list of coordinates   
            positions = [coordinate for x, y in set(b) 
                        if (Grid.is_subclass(derived=self.get_cell_value(
                                                          coordinate:=tuple(np.add(coordinates,
                                                                                   (x,y))))
                                            ,base_class=base_class))]

        return positions
    
    def _find_instances_baseclass_around(self, base_class: Any, coordinates: Tuple[int, int],
                                         include_self: bool=False, radius: int = 1) -> Set[Any]:
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
        a = list(range(-radius, radius + 1))  # List from (-radius, radius)
        for x in a:
            for y in a:
                if not include_self and x == 0 and y == 0:
                        continue
                     
                position = tuple(np.add(coordinates, (x, y)))
                obj = self.get_cell_value(coordinates=position)
                if obj:
                    if Grid.is_subclass(derived=obj,
                                        base_class=base_class):
                    
                        instances.add(obj)
                    
        return instances
    
    def find_free_coordinates(self, coordinates: Tuple[int, int],
                              radius: int = 1) -> Set[Tuple[int, int]]:
        """Public method:
            Find a free cell in range

        Args:
            radius (int, optional):     radius of search. Defaults to 1.
            position (Tuple[int,int]):  starting position to look around

        Returns:
            Set[Tuple[int,int]]: set of free cells' coordinates
        """
        a = list(range(-radius, radius+1))  # List from (-radius, radius)
        b = combinations(a*2, 2)            # ALl the combinations of coordinates
        
        positions = [coordinate for x, y in set(b) 
                     if self.get_cell_value(coordinate:=tuple(np.add(coordinates,(x, y)))) is None]
        
        return positions
    
    def select_free_coordinates(self, coordinates: Tuple[int, int], radius: int = 1,
                                num_cells: int = 1) -> Tuple[int, int]:
        """Public method:
            Select randomly from the free cells available

        Args:
            coordinates (Tuple[int,int]):   starting position to look around
            radius (int, optional):         radius of search. Defaults to 1.
            num_cells (int):                number of cells to return. Defaults to 1

        Returns:
            Tuple[int,int]:         coordinates of the free cell, if num_cells = 1
            List[Tuple[int,int]]:   list of coordinates of free cells, if num_cells > 1
        """
        free_cells: Set[Tuple[int, int]] = self.find_free_coordinates(coordinates=coordinates,
                                                                      radius=radius)

        if free_cells:
            # Make sure no more than free cells
            # are being requested
            num_choice = min(len(free_cells), num_cells)
            
            samples = sample(free_cells, num_choice)
            
            if num_cells == 1:
                return samples[0]
            
            else:
                return samples
        
        return None
    
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
        if success:= self._set_cell_value(coordinates=new_coordinates,
                                         value=value):

                            # Reset the old position
                            old_position = value.position
                            self._empty_cell(coordinates=old_position)
                            
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
        if success:= self._set_operation_valid(coordinates=coordinates,
                                               value=value):
            try:
                self._array[coordinates] = value
            except IndexError:
                print("{coordinates} is out of bounds")
                
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
            return self._array[tuple(coordinates)]
        except IndexError:
            print(f"{coordinates} is out of bounds")
            return False
        
    def get_sub_region(self, initial_pos: Tuple[int,int], radius:int=1) -> np.array:
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
        x1, x2, y1, y2 = (initial_pos[0] - radius, initial_pos[0] + radius+1,
                          initial_pos[1] - radius, initial_pos[1] + radius+1)
        
        ndim = self._array.ndim
        if ndim == 3:
            width, height, depth = self.dimensions
            padded_subregion = np.full(fill_value=-255, shape=(x2-x1, y2-y1, depth))
        elif ndim == 2:
            width, height = self.dimensions
            padded_subregion = np.full(fill_value=None, shape=(x2-x1, y2-y1))
            
        left_pad = right_pad = up_pad = down_pad = 0
        
        if x1 < 0:
            left_pad = -x1
            x1=0
        if x2 > width:
            right_pad = x2 - width
            x2 = width
        if y1 < 0:
            up_pad = -y1
            y1 = 0
        if y2 > height:
            down_pad = y2 - height
            y2 = height
    
        subregion = self._array[x1:x2, y1:y2]
        
        x_shape, y_shape = subregion.shape[:2]
        
        for x in range(x_shape):
            for y in range(y_shape):
                padded_subregion[x+left_pad, y+up_pad] = subregion[x-right_pad,y-down_pad]
                
        return padded_subregion
            
class Grid:
    def __init__(self,
                 grid_id: int,
                 dimensions: Tuple[int,int]):
        
        self.__id = grid_id                                                     # unique identifier
        self.dimensions: Tuple[int,int] = dimensions                            # dimensions of the grid
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions,        # subgrid containing the entities
                                             data_type=Entity,
                                             initial_value=None)
        
        self._resource_grid: SubGrid = SubGrid(dimensions=self.dimensions,      # subgrid containing the resources
                                               data_type=Resource,
                                               initial_value=None)
        
        self._color_grid: SubGrid = SubGrid(dimensions=(*self.dimensions, 3),   # subgrid containing the color values
                                            data_type=np.uint8,
                                            initial_value=255)       
            
    @property
    def id(self):
        return self.__id
     
    @property
    def entity_grid(self) -> SubGrid:
        return self._entity_grid
   
    @property
    def resource_grid(self) -> SubGrid:
        return self._resource_grid
    
    @property
    def color_grid(self) -> SubGrid:
        return self._color_grid
        
    @property
    def width(self) -> int:
        return self.dimensions[0]
    
    @property
    def height(self) -> int:
        return self.dimensions[1]
    
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
            Place a resource on the appropriate subgrid

        Args:
            value (Resource): resource to place on the grid

        Returns:
            bool:   True if the operation was successful
                    False if the resource couldn't be placed
        """        
        return self.resource_grid._place_on_grid(value=value)
        
    def place_entity(self, value: Entity) -> bool:
        """Public method:
            Place an entity on the appropriate subgrid

        Args:
            value (Entity): entity to place on the grid

        Returns:
            bool:   True if the operation was successful
                    False if the entity couldn't be placed
        """ 
        return self.entity_grid._place_on_grid(value=value)
    
    def modify_cell_color(self, coordinates: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Public method:
            Modify the color of a cell in the color grid

        Args:
            coordinates (Tuple[int, int]): coordinates of the cell
            color (Tuple[int, int, int]):  color to apply to the cell
        """        
        if self.color_grid._are_coordinates_in_bounds(coordinates=coordinates):
            self.color_grid.array[coordinates] = color
            
    def _find_occupied_cells_by_animals(self, coordinates: Tuple[int, int],
                                        radius: int = 1) -> np.array[bool]:
        return self.entity_grid._find_instances_baseclass_around(coordinates=coordinates,
                                                                 radius=radius,
                                                                 base_class=Animal)
        
    def _find_occupied_cells_by_trees(self, coordinates: Tuple[int, int],
                                      radius: int = 1) -> np.array[bool]:
        
        return self.entity_grid._find_instances_baseclass_around(coordinates=coordinates,
                                                                 radius=radius,
                                                                 base_class=Tree)

        
    def get_nearby_colors(self, radius: int = 1) -> np.array:
        position: Tuple[int, int] = self.position
        color_cells = []
                
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                coordinate = tuple(np.add(position,(x, y)))
                color_cells.append(self.color_grid.get_cell_value(coordinate=coordinate))
                
        return np.array(color_cells)