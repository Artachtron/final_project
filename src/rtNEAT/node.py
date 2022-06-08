from __future__ import annotations
import enum
   
class FuncType(enum.Enum):
    SIGMOID = 0
    
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
        self.activation: float = 0.0                # The total activation entering the Node
        self.output: float = 0.0                    # Output of the Node- the value in the Node

        self.node_place: NodePlace = node_place # HIDDEN, INPUT, OUTPUT, BIAS
       
        self.ftype: FuncType = FuncType.SIGMOID
        
        self.analogue: Node = None                  # Used for Gene decoding
        self.frozen: bool = False                   # When frozen, cannot be mutated (meaning its trait pointer is fixed)
        
        self.incoming = []                          # A list of pointers to incoming weighted signals from other nodes
        self.outgoing = []                          #  A list of pointers to links carrying this node's signal
        
  
    @classmethod
    def constructor_from_node(cls, node:Node):
        return Node(node_id=node.id,
                    node_place=node.node_place)
        
    def is_sensor(self) -> bool:
        return (self.node_place == NodePlace.INPUT or 
                self.node_place == NodePlace.BIAS)
        
 