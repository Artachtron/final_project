from unittest.mock import sentinel
import numpy as np
from node import Node

class Network:
    def __init__(self,
                 inputs: np.array,
                 outputs: np.array,
                 all_nodes: np.array,
                 network_id: int,
                 adaptable: bool=False):
        self.inputs: np.array = inputs # Nodes that input into the network
        self.outputs: np.array = outputs # Values output by the network
        self.all_nodes: np.array = all_nodes # A list of all the nodes
        
        self.number_nodes: int = -1 # The number of nodes in the net (-1 means not yet counted)
        self.number_links: int = -1 # The number of links in the net (-1 means not yet counted)
        self.id = network_id # Allow for a network id
        self.adaptable = adaptable # Tells whether network can adapt or not
        
    def flush(self):
        """Puts the network back into an initial state
        """        
        for current_node in self.outputs:
            current_node.flush_back()
            
    def flush_check(self):
        """Debugger: Checks network state
        """        
        seen_list =[]
        for current_node in self.outputs:
            location = seen_list.index(current_node)
            if location == seen_list.size:
                seen_list.append(current_node)
                current_node.flush_back_check(seen_list)
            
        