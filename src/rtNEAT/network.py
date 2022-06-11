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
                 bias: Dict[int, Node] = {},
                 inputs: Dict[int, Node] = {},
                 outputs: Dict[int, Node] = {},
                 all_nodes: Dict[int, Node] = {},
                 hidden: Dict[int, Node] = {},
                 frozen: bool = False):
        
        self.id = network_id
        
        self.inputs: Dict[int, Node] = inputs # Nodes that input into the network
        self.bias: Node = bias
        self.outputs: Dict[int, Node] = outputs # Values output by the network
        self.hidden: Dict[int, Node] = hidden #
        self.all_nodes: Dict[int, Node] = all_nodes # A list of all the nodes
        
        self.links: Dict[int, Link] = {}

        self.activation_phase: int = 0
        self.frozen: bool = frozen
        self.number_nodes: int = -1 # The number of nodes in the net (-1 means not yet counted)
        self.number_links: int = -1 # The number of links in the net (-1 means not yet counted)
         # Allow for a network id
         # Tells whether network can adapt or not
        
    def get_all_nodes(self):
        return np.array(list(self.all_nodes.values()))
    
    def get_links(self):
        return np.array(list(self.links.values()))
    
    @staticmethod
    def genesis(genome: Genome) -> Network:
        network = Network(network_id=genome.id)
        
        network._synthetize_nodes(node_genes=genome.node_genes)    
        network._synthetize_links(link_genes=genome.link_genes)
        network.calculate_properties()
        
        return network
    
    def _synthetize_nodes(self, node_genes: Dict[int, NodeGene]):
        nodes = {}
        for key, node_gene in node_genes.items():
            nodes[key] = Node.synthesis(**node_gene.transcript())

        self._sort_nodes(nodes)
      
    def _synthetize_links(self, link_genes: Dict[int, LinkGene]) -> Dict[int, Link]:
        for key, link_gene in link_genes.items():
            link = Link.synthesis(**link_gene.transcript())
            self.links[key] = link
            if link_gene.enabled: 
                self._connect_link(link)                
        
    def _connect_link(self, link: Link) -> None:
        """ Add the link to the list of incoming links of 
            the out node and outgoing link of the in node

        Args:
            link (Link): link to add
        """        
        in_node = self.all_nodes[link.in_node.id]
        out_node = self.all_nodes[link.out_node.id] 
        
        out_node.incoming[link.id] = link
        in_node.outgoing[link.id] = link
    
    def _sort_nodes(self, nodes: Dict[int, Node]):
              
        for key, node in nodes.items():         
            # Check for input or output designation of node
            match node.type.name:
                case 'INPUT':
                    self.inputs[key] = node
                case 'OUTPUT':
                    self.outputs[key] = node
                case 'HIDDEN':
                    self.hidden[key] = node
                case 'BIAS':
                    self.bias[key] = node
                    
            # Keep track of all nodes, not just input and output    
            self.all_nodes[key] = node
                
    def calculate_properties(self):
        self.number_nodes = len(self.all_nodes)
        self.number_links = len(self.links)
    
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
        if input_values.size != len(self.inputs) - 1:
            raise ValueError(f"""Input values {(input_values.size)} does not correspond
                             to number of input nodes {len(self.inputs)}""")
        
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
        
        if bias_node.type != NodeType.BIAS:
            raise ValueError

        for node, value in zip(inputs, values):
            if node.type != NodeType.INPUT:
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
            if node.type != NodeType.OUTPUT:
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
        