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
                
    def is_recurrent(self, potential_in_node: Node, potential_out_node: Node, count: int, threshold: int) -> bool:
        """ Checks a potential link between a potential in_node and potential out_node to see if it must be recurrent

        Args:
            potential_in_node (Node): _description_
            potential_out_node (Node): _description_
            count (int): _description_
            threshold (int): _description_

        Returns:
            bool: found a recurrent link
        """        
        count += 1
        if count > threshold:
            return False
        
        if potential_in_node == potential_out_node:
            return True
        else:
            for current_link in potential_in_node.incoming:
                if not current_link.is_recurrent:
                    if self.is_reccurent(potential_in_node=current_link,
                                         potential_out_node=potential_out_node,
                                         count=count,
                                         threshold=threshold):
                        return True
                    
            return False 
        