from __future__ import annotations
from genes import NodeType, ActivationFuncType, AggregationFuncType
from typing import Dict


class Link:
        def __init__(self,
                    link_id: int,
                    weight: float,
                    in_node: Node,
                    out_node: Node,
                    enabled: bool = True,
                    ):
            
            self.id = link_id
            self.weight: float = weight # Weight of connection
            self.in_node: Node = in_node # Node inputting into the link
            self.out_node: Node = out_node # Node that the link affects
            self.enabled: bool = enabled


class Node:
    def __init__(self,
                  node_id: int,
                  node_type: NodeType = NodeType.HIDDEN,
                  activation_function: ActivationFuncType=ActivationFuncType.SIGMOID,
                  aggregation_function: AggregationFuncType=AggregationFuncType.SUM,
                  enabled: bool = True,
                  ):

        self.id: int = node_id
        
        self.activation_phase: int = 0
        self.activation_value: float = 0.0              # The total activation entering the Node
        self.enabled: bool = enabled
        self.type: NodeType = node_type     # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.activation_function: ActivationFuncType = activation_function 
        self.aggregation_function: AggregationFuncType = aggregation_function
            
        self.incoming: Dict[int, Link] = {}                         # A list of pointers to incoming weighted signals from other nodes
        self.outgoing: Dict[int, Link] = {}                         #  A list of pointers to links carrying this node's signal
        
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
            
            self.activation_value = self.activation_function.value(
                                    self.aggregation_function.value(values))
            
            # set the activation phase to the current one,
            # since the value is now already calculated
            self.activation_phase = activation_phase            
        return self.activation_value
    
    
    