from __future__ import annotations
import numpy as np
from node import Node, NodePlace
from neat import Config
from typing import List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from genome import Genome


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
        
        self.activation_phase: int = 0
        self.number_nodes: int = -1 # The number of nodes in the net (-1 means not yet counted)
        self.number_links: int = -1 # The number of links in the net (-1 means not yet counted)
        self.id = network_id # Allow for a network id
        self.adaptable = adaptable # Tells whether network can adapt or not
        
    
    def create_network(genome: Genome,
                       inputs: List[Node],
                       outputs: List[Node],
                       all_nodes: List[Node]) -> Network:
        
        for current_gene in genome.genes:
            # Only create the link if the gene is enabled
            if current_gene.enabled:
                # Create the new link               
                genome._create_new_link(gene=current_gene)
           
        # Create the new network        
        new_network = Network(inputs=inputs,
                              outputs=outputs,
                              all_nodes=all_nodes,
                              network_id=genome.id)
        
         # Attach genotype and phenotype together
        new_network.genotype = genome
        genome.phenotype = new_network
        
        return new_network  
    
    def activate(self, input_values: np.array) -> np.array:
        """ Activate the whole network after recieving input values

        Args:
            input_values (np.array): input values

        Raises:
            ValueError: The number of input values given does not correspond to the network

        Returns:
            np.array: activated values coming out of outputs nodes
        """        
        # Compare the size of input values given to the network's inputs (minus bias)
        if len(input_values) != self.inputs.size - 1:
            raise ValueError
        
        # increment the activation_phase            
        self.activation_phase += 1 

        # store the input values in the input nodes
        self.activate_inputs(values=input_values)
        # travel through the network to calculate the output values
        output_values = self.activate_outputs()
                                 
        return output_values
    
    def activate_inputs(self, values: np.array):
        """ Store the input values in the input nodes
            and initiate the bias node with a value of 1

        Args:
            values (np.array): values to store in the input nodes

        Raises:
            ValueError: the node in the inputs list 
                        are not of the proper type
            ValueError: the bias node is not of the proper type
        """        
        inputs: np.array = self.inputs[:-1]
        bias_node: Node = self.inputs[-1]
        
        if bias_node.node_place != NodePlace.BIAS:
            raise ValueError

        for node, value in zip(inputs, values):
            if node.node_place != NodePlace.INPUT:
                raise ValueError
            
            node.output_value = value
            node.activation_phase = self.activation_phase
    
        bias_node.output_value = 1
        bias_node.activation_phase = self.activation_phase
        
    def activate_outputs(self) -> np.array:
        """ Travel through the network calculating the
            activation values necessary for each output
        

        Raises:
            ValueError: The nodes in the outputs list 
                        are not of the proper type

        Returns:
            np.array: list of the output values after calculation 
        """        
        output_values = []
        
        for node in self.outputs:
            if node.node_place != NodePlace.OUTPUT:
                raise ValueError
            
            output_value = node.get_activation(activation_phase=self.activation_phase) 
            output_values.append(output_value)
        
        return np.array(output_values)
            
    
    
    
    
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
        