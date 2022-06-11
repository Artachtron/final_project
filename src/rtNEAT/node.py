from __future__ import annotations
from innovation import InnovTable  
import enum  
from typing import List
from link import Link
import math
from functools import partial

   
class NodeType(enum.Enum):
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2
    BIAS = 3
    
def sigmoid(x):
    """ Sigmoid activation function, Logistic activation with a range of 0 to 1
    
    Args:
        x (float): input value
        
    Returns:
        float: output value
    """
    try:
        return (1.0 / (1.0 + math.exp(-x)))
    except OverflowError:
        return 0 if x < 0 else 1


def relu(x):
    """ ReLu activation function, Limits the lower range of the input to 0
    Args:
        x (float): input value
        
    Returns:
        float: output value
    """
    return max(0, x)
    
class ActivationFuncType(enum.Enum):
    SIGMOID = partial(sigmoid)
    RELU = partial(relu)

class AggregationFuncType(enum.Enum):
    SUM = sum

class Node:
    def __init__(self,
                  node_id: int = None,
                  node_type: NodeType = NodeType.HIDDEN,
                  activation_function: ActivationFuncType=ActivationFuncType.SIGMOID,
                  aggregation_function: AggregationFuncType=AggregationFuncType.SUM
                  ):

        self.id: int = node_id or InnovTable.get_node_number(increment=True)
        
        self.activation_phase: int = 0
        self.output_value: float = 0.0              # The total activation entering the Node
        
        self.type: NodeType = node_type     # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.activation_function: ActivationFuncType = activation_function 
        self.aggregation_function: AggregationFuncType = aggregation_function
    
        self.frozen: bool = False                   # When frozen, cannot be mutated (meaning its trait pointer is fixed)
        
        self.incoming: List[Link] = []                          # A list of pointers to incoming weighted signals from other nodes
        self.outgoing: List[Link] = []                          #  A list of pointers to links carrying this node's signal
        
        #Config.configure()
        
  
    @classmethod
    def constructor_from_node(cls, node:Node):
        return Node(node_id=node.id,
                    node_type=node.type)
        
    def is_sensor(self) -> bool:
        """ determine if the node is a sensor (INPUT or BIAS)

        Returns:
            bool: node is a sensor
        """        
        return (self.type == NodeType.INPUT or 
                self.type == NodeType.BIAS)
        
        
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
                    values.append(link.in_node.get_activation(activation_phase=activation_phase) * link.weight)
            
            self.output_value = self.activation_function.value(
                                    self.aggregation_function.value(values))
            
            # set the activation phase to the current one,
            # since the value is now already calculated
            self.activation_phase = activation_phase            
        return self.output_value
    
    
    
