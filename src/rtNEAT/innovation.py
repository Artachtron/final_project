from __future__ import annotations
from node import Node
import enum
from typing import List
from numpy.random import choice, random

class InnovationType(enum.Enum):
    NEWNODE = 0
    NEWLINK = 1

class InnovTable:
    history: List[Innovation] = []
    next_innovation_number: int = 0
    next_node_number: int = 0
     
    @staticmethod    
    def get_innovation_number() -> int:
        return InnovTable.next_innovation_number
    
    @staticmethod
    def increment_innov(number: int=1) -> None:
        InnovTable.next_innovation_number += number
    
    @staticmethod    
    def get_node_number() -> int:
        return InnovTable.next_node_number
    
    @staticmethod
    def increment_node(number: int=1) -> None:
        InnovTable.next_node_number += number
    
    @staticmethod
    def add_innovation(new_innovation:Innovation) -> None:
        InnovTable.history.append(new_innovation)
    
    @staticmethod
    def _check_innovation_already_exists(the_innovation: Innovation, innovation_type: InnovationType,
                                         node_in: Node, node_out: Node, recurrence: bool) -> bool:
        """See if an innovation already exists

        Args:
            the_innovation (Innovation): _description_
            innovation_type (InnovationType): _description_
            node1 (Node): _description_
            node2 (Node): _description_
            recurrence (bool): _description_

        Returns:
            bool: _description_
        """        
        return (the_innovation.innovation_type == innovation_type and
                the_innovation.node_in_id == node_in.id and
                the_innovation.node_out_id == node_out.id and
                the_innovation.recurrence_flag == recurrence)
           
    @staticmethod    
    def _create_innovation(node_in: Node, node_out: Node, innovation_type: InnovationType, 
                           recurrence: bool=False) -> Innovation: 
        current_innovation = InnovTable.get_innovation_number()
        
        new_weight = 0
        innovation_number2 = 0
        if innovation_type == InnovationType.NEWNODE:
            InnovTable.increment_innov(number=2)
            InnovTable.increment_node()
            innovation_number2 = current_innovation + 1
        elif innovation_type == InnovationType.NEWLINK:
            InnovTable.increment_innov(number=1)
            new_weight = choice([-1,1]) * random()
            old_innovation_number = 0
        # Choose the new weight
        
        new_innovation = Innovation(node_in_id=node_in.id,
                                    node_out_id=node_out.id,
                                    innovation_type=innovation_type,
                                    innovation_number1=current_innovation,
                                    innovation_number2=innovation_number2,
                                    new_weight=new_weight,
                                    recurrence=recurrence,
                                    new_node_id=InnovTable.get_node_number()-1)
        
        InnovTable.add_innovation(new_innovation=new_innovation)
        
        return new_innovation
    
    @staticmethod
    def get_innovation(node_in: Node, node_out: Node, innovation_type: InnovationType,
                        recurrence: bool, new_node: Node=None) -> Innovation:
        for innovation in InnovTable.history:
            if InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                            innovation_type=innovation_type,
                                                            node_in=node_in,
                                                            node_out=node_out,
                                                            recurrence=recurrence):
                return innovation
            
        else:
            # novel innovation
            new_innovation = InnovTable._create_innovation(node_in=node_in,
                                                            node_out=node_out,
                                                            innovation_type=innovation_type,
                                                            recurrence=recurrence)
            return new_innovation       

class Innovation:
    def __init__(self,
                 node_in_id: int,
                 node_out_id: int,
                 innovation_type: InnovationType,
                 innovation_number1: int,
                 innovation_number2: int=0,
                 old_innovation_number: int = 0,
                 new_node_id: int=0,
                 new_weight: float=0.0,
                 recurrence: bool=False
                 ):
        
        self.innovation_type: InnovationType = innovation_type # Either NEWNODE or NEWLINK
        self.node_in_id: int = node_in_id # Two nodes specify where the innovation took place
        self.node_out_id: int = node_out_id
        self.innovation_number1: int = innovation_number1 # The number assigned to the innovation
        self.innovation_number2: int = innovation_number2 # If this is a new node innovation, then there are 2 innovations (links) added for the new node 
        self.weight: float = new_weight # If a link is added, this is its weight  
        
        self.new_node_id: int = new_node_id # If a new node was created, this is its node_id 
        self.old_innovation_number: int = old_innovation_number # If a new node was created, this is the innovnum of the gene's link it is being stuck inside 
        self.recurrence_flag: bool = recurrence