from __future__ import annotations
from project.src.rtNEAT.genes import NodeType, ActivationFuncType, AggregationFuncType
from typing import Dict, Set


class BasePhene:
    def __init__(self,
                 phene_id: int,
                 enabled: bool = True):
        
        self.__id: int = phene_id
        self.enabled: bool = enabled
     
    @property
    def id(self):
        return self.__id 
        
    @classmethod    
    def synthesis(cls, kwargs):
        raise NotImplementedError("Please Implement the synthesis method")
        
class Link(BasePhene):
    def __init__(self,
                link_id: int,
                weight: float,
                in_node: int,
                out_node: int,
                enabled: bool = True,
                ):
        
        super(Link, self).__init__(phene_id=link_id,
                                    enabled=enabled)
        
        self.weight: float = weight # Weight of connection
        self.in_node: Node = in_node # Node inputting into the link
        self.out_node: Node = out_node # Node that the link affects

    @classmethod
    def synthesis(cls, kwargs) -> Link:
        """ Synthesize a Link from a GeneLink
            and return it

        Returns:
            Link: the created Link
        """        
        return Link(**kwargs)

class Node(BasePhene):
    def __init__(self,
                  node_id: int,
                  node_type: NodeType = NodeType.HIDDEN,
                  activation_function: ActivationFuncType=ActivationFuncType.SIGMOID,
                  aggregation_function: AggregationFuncType=AggregationFuncType.SUM,
                  bias: float = 1.0,
                  enabled: bool = True,
                  ):

        super(Node, self).__init__( phene_id=node_id,
                                    enabled=enabled)
        
        self.activation_phase: int = 0
        self.activation_value: float = 0.0              # The total activation entering the Node
        self.type: NodeType = node_type     # HIDDEN, INPUT, OUTPUT, BIAS
        self.bias = bias
       
        self.activation_function: ActivationFuncType = activation_function 
        self.aggregation_function: AggregationFuncType = aggregation_function
            
        self.incoming: Dict[int, Link] = {}                         # A list of pointers to incoming weighted signals from other nodes
        self.outgoing: Dict[int, Link] = {}                         #  A list of pointers to links carrying this node's signal
        
    def get_incoming(self)  ->  Set[Link]:
        """Public method:
            Return only the Links values from
            the incoming dictionary

        Returns:
            Set[Link]: set of incoming links
        """        
        return set(self.incoming.values())
    
    def get_outgoing(self)  ->  Set[Link]:
        """Public method:
            Return only the Links values from
            the outgoing dictionary

        Returns:
            Set[Link]: set of outgoing links
        """        
        return set(self.outgoing.values())
        
    @classmethod
    def synthesis(cls, kwargs) -> Node:
        """ Synthesize a Node from a NodeGene
            and return it

        Returns:
            Node: the created Node
        """ 
        return Node(**kwargs)    
                  
    def is_sensor(self) -> bool:
        """ determine if the node is a sensor (INPUT or BIAS)

        Returns:
            bool: node is a sensor
        """        
        return (self.type == NodeType.INPUT or 
                self.type == NodeType.BIAS)
        
    def is_output(self) -> bool:
        """ determine if the node is an OUTPUT

        Returns:
            bool: node is an output
        """        
        return self.type == NodeType.OUTPUT
        
        
    def get_activation(self, activation_phase: int) -> float:
        """ Browse the list of incoming links and calculate the output value

        Args:
            activation_phase (int): current activation phase of the network

        Returns:
            float: the output value of the node after activation
        """  
        # If the output was already calculated during the current phase, 
        # or the node is an input: then just return the value      
        if self.activation_phase != activation_phase and not self.is_sensor():
            
            values = [self.bias]
            # Loop through the list of incoming links and
            # calculate the sum of its incoming activation
            for link in self.get_incoming():
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
    
    
    