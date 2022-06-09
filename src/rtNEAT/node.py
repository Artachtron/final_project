from __future__ import annotations
from neat import ActivationFuncType
import enum  
from typing import List
from link import Link
from neat import Config
   
class NodePlace(enum.Enum):
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2
    BIAS = 3

class Node:
    def __init__(self,
                  node_id: int,
                  node_place: NodePlace = NodePlace.HIDDEN,
                  ):
        
        self.id: int = node_id
        self.active_flag: bool = False              # To make sure outputs are active
        self.activesum: float = 0.0                 # The incoming activity before being processed
        
        self.activation_phase: int = 0
        self.output_value: float = 0.0              # The total activation entering the Node
        self.output: float = 0.0                    # Output of the Node- the value in the Node

        self.node_place: NodePlace = node_place     # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.ftype: ActivationFuncType = ActivationFuncType.SIGMOID
    
        self.frozen: bool = False                   # When frozen, cannot be mutated (meaning its trait pointer is fixed)
        
        self.incoming: List[Link] = []                          # A list of pointers to incoming weighted signals from other nodes
        self.outgoing: List[Link] = []                          #  A list of pointers to links carrying this node's signal
        
  
    @classmethod
    def constructor_from_node(cls, node:Node):
        return Node(node_id=node.id,
                    node_place=node.node_place)
        
    def is_sensor(self) -> bool:
        """ determine if the node is a sensor (INPUT or BIAS)

        Returns:
            bool: node is a sensor
        """        
        return (self.node_place == NodePlace.INPUT or 
                self.node_place == NodePlace.BIAS)
        
        
    def get_activation(self, activation_phase: int) -> float:
        """ Browse the list of incoming links and calculate the output value

        Args:
            activation_phase (int): current activation phase of the network

        Returns:
            float: the output value of the node after activation
        """  
        # If the output was already calculated during the current phase, 
        # then just return the value      
        if self.activation_phase != activation_phase:
            
            values = []
            # Loop through the list of incoming links and
            # calculate the sum of its incoming activation
            for link in self.incoming:
                # ONly take the value of activated links
                if link.enabled:
                    # Recurrence call to calculate all the
                    # necessary incoming activation values
                    values += link.node_in.get_activation() 
            
            self.output_value = Config.activation_function(
                                    Config.aggregation_func(values))
            
            # set the activation phase to the current one,
            # since the value is now already calculated
            self.activation_phase = activation_phase            
        return self.output_value