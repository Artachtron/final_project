from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from genome import Genome
    from genes import NodeGene, LinkGene
    
from typing import Dict

import numpy as np
from phenes import Node, Link

class Network:
    def __init__(self,
                 network_id: int = 0,
                 inputs: Dict[int, Node] = {},
                 outputs: Dict[int, Node] = {},
                 all_nodes: Dict[int, Node] = {},
                 hidden: Dict[int, Node] = {},
                 frozen: bool = False):
        
        self.id = network_id
        
        self._inputs: Dict[int, Node] = inputs # Nodes that input into the network
        self._outputs: Dict[int, Node] = outputs # Values output by the network
        self._hidden: Dict[int, Node] = hidden #
        self._all_nodes: Dict[int, Node] = all_nodes # A list of all the nodes
        
        self._links: Dict[int, Link] = {}

        self.activation_phase: int = 0
        self.frozen: bool = frozen

            
    @staticmethod
    def genesis(genome: Genome) -> Network:
        network = Network(network_id=genome.id)
        
        network._synthetize_nodes(node_genes=genome._node_genes)    
        network._synthetize_links(link_genes=genome._link_genes)
        
        return network
    
    def _synthetize_nodes(self, node_genes: Dict[int, NodeGene]):
        nodes = {}
        for key, node_gene in node_genes.items():
            nodes[key] = Node.synthesis(**node_gene.transcript())

        self._sort_nodes(nodes)
      
    def _synthetize_links(self, link_genes: Dict[int, LinkGene]) -> Dict[int, Link]:
        for key, link_gene in link_genes.items():
            link = Link.synthesis(**link_gene.transcript())
            self._links[key] = link
            if link_gene.enabled: 
                self._connect_link(link)                
        
    def _connect_link(self, link: Link) -> None:
        """ Add the link to the list of incoming links of 
            the out node and outgoing link of the in node

        Args:
            link (Link): link to add
        """        
        in_node = self._all_nodes[link.in_node.id]
        out_node = self._all_nodes[link.out_node.id] 
        
        out_node.incoming[link.id] = link
        in_node.outgoing[link.id] = link
    
    def _sort_nodes(self, nodes: Dict[int, Node]) -> None:
              
        for key, node in nodes.items():         
            # Check for nodes' type 
            # and sort them accordingly
            # in their dictionary
            match node.type.name:
                case 'INPUT':
                    self._inputs[key] = node
                case 'OUTPUT':
                    self._outputs[key] = node
                case 'HIDDEN':
                    self._hidden[key] = node
                    
            # Keep track of all nodes    
            self._all_nodes[key] = node
    
    def activate(self, input_values: np.array) -> np.array:
        """ Activate the whole network after recieving input values

        Args:
            input_values (np.array): input values

        Raises:
            ValueError: The number of input values given does not correspond to the network

        Returns:
            np.array: activated values coming out of outputs nodes
        """        
        # Compare the size of input values given to the network's inputs
        if input_values.size != len(self._inputs):
            raise ValueError(f"""Input values {(input_values.size)} does not correspond
                             to number of input nodes {len(self._inputs)}""")
        
        # increment the activation_phase            
        self.activation_phase += 1 

        # store the input values in the input nodes
        self.activate_inputs(values=input_values)
        # travel through the network to calculate the output values
        output_values = self.activate_outputs()
                                 
        return output_values
    
    def activate_inputs(self, values: np.array):
        """ Store the input values in the input nodes
    
        Args:
            values (np.array): values to store in the input nodes
        """        
 
        for node, value in zip(self.inputs, values): 
            node.output_value = value
            node.activation_phase = self.activation_phase
        
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
            """ if node.type != NodeType.OUTPUT:
                raise ValueError """
            
            output_value = node.get_activation(activation_phase=self.activation_phase) 
            output_values.append(output_value)
        
        return np.array(output_values)
            
    @property
    def n_inputs(self) -> int:
        return len(self._inputs)
    
    @property
    def n_outputs(self)-> int:
        return len(self._outputs)
    
    @property
    def n_nodes(self)-> int:
        return len(self._all_nodes)
    
    @property
    def n_links(self)-> int:
        return len(self._links) 
    
    @property
    def inputs(self)  -> np.array[Node]:  
        return np.array(list(self._inputs.values()))
    
    @property
    def outputs(self)  -> np.array[Node]:  
        return np.array(list(self._outputs.values()))
        
    @property
    def hidden(self)  -> np.array[Node]:  
        return np.array(list(self._hidden.values()))
    
    @property
    def all_nodes(self) -> np.array:
        return np.array(list(self._all_nodes.values()))
    
    @property
    def links(self) -> np.array:
        return np.array(list(self._links.values()))
    
    
    
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
        