from __future__ import annotations

import enum
from typing import List
from numpy.random import choice, random

class InnovationType(enum.Enum):
    NEW_NODE = 0
    NEW_LINK = 1

class InnovTableProperties(type):
    @property
    def node_number(cls) -> int:
        return cls._node_number
    
    @node_number.setter
    def node_number(cls, value: int) -> None:
        cls._node_number = max(cls.node_number, value)
            
    @property
    def link_number(cls) -> int:
        return cls._link_number
    
    @link_number.setter
    def link_number(cls, value: int) -> None:
        cls._link_number = max(cls.link_number, value)

class InnovTable(object, metaclass=InnovTableProperties):
    innovations: List[Innovation] = []

    _node_number: int = 1
    _link_number: int = 1
       
        
    @staticmethod    
    def get_link_number(increment: bool=False) -> int:
        """ Get the current link number

        Returns:
            int: current link number
        """
        number = InnovTable._link_number 
        
        if increment:
            InnovTable.increment_link()
         
        return number
    
    @staticmethod
    def increment_link(amount: int=1) -> None:
        """ Increment the current link number by a given amount

        Args:
            number (int, optional): link number's increment. Defaults to 1.
        """        
        InnovTable._link_number += amount
    
    @staticmethod    
    def get_node_number(increment: bool=False) -> int:
        """ Get the current node number

        Returns:
            int: current node number
        """
        number = InnovTable._node_number
        
        if increment:
            InnovTable.increment_node() 
                   
        return number
    
    @staticmethod
    def increment_node(amount: int=1) -> None:
        """ Increment the current node number by a given amount

        Args:
            number (int, optional): node number's increment. Defaults to 1.
        """        
        InnovTable._node_number += amount
    
    @staticmethod
    def add_innovation(new_innovation: Innovation) -> None:
        """ Add an innovation to the history's list of innovations

        Args:
            new_innovation (Innovation): innovation to add to the list
        """        
        InnovTable.innovations.append(new_innovation)
        
    @staticmethod
    def reset_innovation_table() -> None:
        """ Reset the values of the innovation table
        """        
        InnovTable.innovations = []
        InnovTable._node_number = 1
        InnovTable._link_number = 1
    
    @staticmethod
    def _check_innovation_already_exists(the_innovation: Innovation, innovation_type: InnovationType,
                                         in_node: int, out_node: int) -> bool:
        """ See if an innovation already exists

        Args:
            the_innovation (Innovation):        innovation to check for
            innovation_type (InnovationType):   type of innovation
            in_node (int):                      incoming node's id
            out_node (int):                     outgoing node's id

        Returns:
            bool: the innovation already exists
        """        
        return (the_innovation.innovation_type == innovation_type and
                the_innovation.node_in_id == in_node and
                the_innovation.node_out_id == out_node)
           
    @staticmethod    
    def _create_innovation(in_node: int, out_node: int, innovation_type: InnovationType, 
                           old_innovation_number: int=-1) -> Innovation:
        """ Create a new innovation

        Args:
            in_node (int):                          incoming node's id
            out_node (int):                         outgoing node's id 
            innovation_type (InnovationType):       type of innovation
            old_innovation_number (int, optional):  innovation number of the disabled gene when creating a new node. Defaults to -1.

        Returns:
            Innovation: innovation created
        """         
        
        current_innovation: int = InnovTable.link_number                # current innovation number
        # NEWNODE parameters
        innovation_number2: int = -1                                    # second innovation number  
        current_node: int = InnovTable.node_number                      # current node number 
        # NEWLINK parameter
        new_weight: float = -1                                          # new weight
                            
        
        if innovation_type == InnovationType.NEW_NODE:
            # one innovation number per new link created
            innovation_number2 = current_innovation + 1
            # increment the current innovation number by 2 (1 for each new link created)
            InnovTable.increment_link(amount=2)
            # increment the current node number
            InnovTable.increment_node()
 
        elif innovation_type == InnovationType.NEW_LINK:
            # increment the current innovation number
            InnovTable.increment_link(amount=1)
            # generate a random weight
            new_weight = choice([-1,1]) * random()
            # new_node_id not applicable
            current_node = -1
        
        # create the new innovation        
        new_innovation = Innovation(node_in_id=in_node,
                                    node_out_id=out_node,
                                    innovation_type=innovation_type,
                                    innovation_number1=current_innovation,
                                    innovation_number2=innovation_number2,
                                    new_weight=new_weight,
                                    new_node_id=current_node,
                                    old_innovation_number=old_innovation_number)
        
        # add the innovation to the table's history
        InnovTable.add_innovation(new_innovation=new_innovation)
        
        return new_innovation
    
    @staticmethod
    def get_innovation(in_node: int, out_node: int, innovation_type: InnovationType,
                       old_innovation_number: int=-1) -> Innovation:
        """ Look if the innovation already exists in the table else create a new innovation

        Args:
            in_node (int):                          incoming node's id
            out_node (int):                         outgoing node's id
            innovation_type (InnovationType):       type of innovation
            old_innovation_number (int, optional):  innovation number of the disabled gene (when adding node). Defaults to -1.

        Returns:
            Innovation: the found existing innovation or the created new innovation
        """  
        
        # Check in history if an equivalent innovation already exists      
        for innovation in InnovTable.innovations:
            if InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                            innovation_type=innovation_type,
                                                            in_node=in_node,
                                                            out_node=out_node):
                return innovation
        
        # No existing innovation wa corresponding    
        else:
            # Novel innovation
            new_innovation = InnovTable._create_innovation(in_node=in_node,
                                                            out_node=out_node,
                                                            innovation_type=innovation_type,
                                                            old_innovation_number=old_innovation_number)
            return new_innovation       

class Innovation:
    def __init__(self,
                 node_in_id: int,
                 node_out_id: int,
                 innovation_type: InnovationType,
                 innovation_number1: int,
                 innovation_number2: int=-1,
                 old_innovation_number: int = -1,
                 new_node_id: int=-1,
                 new_weight: float=-1,
                 ):
        
        self.innovation_type: InnovationType = innovation_type  # NEW_NODE or NEW_LINK
        self.node_in_id: int = node_in_id                       # The incoming node's id
        self.node_out_id: int = node_out_id                     # The outgoing node's id
        self.innovation_number1: int = innovation_number1       # The number assigned to the innovation
        self.innovation_number2: int = innovation_number2       # In case of NEW_NODE two links are created
        
        self.new_node_id: int = new_node_id                     # In case of NEW_NODE the id of the created node
        self.old_innovation_number: int = old_innovation_number # In case of NEW_NODE a link is being disabled
        
        self.weight: float = new_weight                         # In case of NEW_LINK the weight associated to the link 
       