from __future__ import annotations

import enum
from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Tuple


class EntityType(enum.Enum):
    """Enum:
        Type of entity
    """
    Animal  =   "animal"
    Tree    =   "tree"

@dataclass
class Position:
    """Utility class:
        Coordinates in the world,
        with useful methods

    Attributes:
        x (int): x coordinate
        y (int): y coordinate

    Methods:
        move: move to a new position, by adding a vector

    Static methods:
        add:        add a vector to a position and return the new position
        distance:   distance between two positions
    """
    x: int
    y: int

    def __call__(self):
        return self.x, self.y

    @property
    def vect(self):
        return self.x, self.y

    def move(self, vect: Tuple[int, int]):
        """Public method:
            Move to a new position,
            by adding a vector to the current position

        Args:
            vect (Tuple[int, int]): vector to add
        """
        self.x += vect[0]
        self.y += vect[1]

    @staticmethod
    def add(position: Position, vect: Tuple[int, int]) -> Position:
        """Static method:
            Add a vector to a position and return the new position

        Args:
            position (Position):    start position
            vect (Tuple[int, int]): vector to add

        Returns:
            Position: end position
        """
        pos = position()

        return Position(pos[0] + vect[0],
                        pos[1] + vect[1])
        
    def norm_angle(self, other_pos: Position) -> float:
        return self.angle(other_pos)/(2*pi)
    
    def angle(self, other_pos: Position) -> float:
        x1 = self.x
        x2 = other_pos.x
        adj = x2 - x1
        hyp = self.distance(other_pos)
        
        add = 0
        if (self.y - other_pos.y > 0):
            add = pi
        
        return acos(adj/hyp) + add
    
    def distance(self, other_pos: Position) -> float: 
        distance = sqrt((self.x - other_pos.x)**2 +
                        (self.y - other_pos.y)**2)
        
        return round(distance, 2)
        
    @staticmethod
    def ang(object1: Any, object2: Any) -> float:
        """ x1 = object1.position.x
        x2 = object2.position.x
        adj = x2 - x1
        hyp = Position.distance(object1, object2) """
    
        return object1.position.angle(object2.position)

    @staticmethod
    def dist(object1: Any, object2: Any) -> float:
        """Static method:
            Distance between two positions

        Args:
            object1 (Any): first position
            object2 (Any): second position

        Returns:
            float: distance between the positions
        """
        distance = sqrt((object1.position[0] - object2.position[0])**2 +
                        (object1.position[1] - object2.position[1])**2)

        return round(distance, 2)


class SimulatedObject:
    """Class:
        Object being modified during simulation execution's cycles

        Attributes:
            __id (int):             unique identifier
            _size (int):            sprite's scaling factor
            _position (Position):   coordinates in the world
            _appearance (str):      path of the sprite's image
    """
    def __init__(self,
                 sim_obj_id: int,
                 size: int,
                 position: Tuple[int, int],
                 appearance: str):
        """Super constructor:
            Get the necessary information about a simulated object

        Args:
            sim_obj_id (int):           unique identifier
            size (int):                 sprite's scaling factor
            position (Tuple[int, int]): coordinates in the world
            appearance (str):           path of the sprite's image
        """


        self.__id: int = sim_obj_id
        self._size: int = size
        self._position: Position = Position(*position)

        self._appearance: str = appearance

    @property
    def id(self) -> int:
        """Property:
            Return the simulated object's id

        Returns:
            int: simulated object's id
        """
        return self.__id

    @property
    def size(self) -> int:
        """Property:
            Return the scaling factor

        Returns:
            int: scaling factor
        """
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        """Setter:
            Modify the size

        Args:
            value (int): new size
        """
        self._size = value
    
    @property
    def pos(self) -> Position:
        """Porperty:
            return the position

        Returns:
            Position: position
        """
        return self._position

    @property
    def position(self) -> Tuple[int, int]:
        """Porperty:
            return the position's coordinates

        Returns:
            Tuple[int, int]: position's coordinates
        """
        return self._position()

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """Setter:
            Modify the position

        Args:
            value (Tuple[int, int]): new position
        """
        self._position = Position(*value)

    @property
    def appearance(self) -> str:
        """Property:
            Return the path to the sprite's image

        Returns:
            str: path to the sprite's image
        """
        return self._appearance
