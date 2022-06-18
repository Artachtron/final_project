from __future__ import annotations
from functools import cached_property
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from genome import Genome
    from genes import NodeGene, LinkGene
    
from typing import Dict, Set

import numpy as np
from project.src.rtNEAT.phenes import Node, Link

class Network:
    def __init__(self,
                 network_id: int = 0,
                #  inputs: Dict[int, Node] = dict(),
                #  outputs: Dict[int, Node] = dict(),
                #  all_nodes: Dict[int, Node] = dict(),
                #  hidden: Dict[int, Node] = dict(),
                 frozen: bool = False):
        
        self.__id = network_id
        
        self._inputs: Dict[int, Node] = dict() # Nodes that input into the network
        self._outputs: Dict[int, Node] = dict() # Values output by the network
        self._hidden: Dict[int, Node] = dict() #
        self._all_nodes: Dict[int, Node] = dict() # A list of all the nodes
        
        self._links: Dict[int, Link] = dict()

        self.activation_phase: int = 0
        self.frozen: bool = frozen

    @property
    def id(self):
        return self.__id 
            
    @classmethod
    def genesis(cls, genome: Genome) -> Network:
        network = cls(network_id=genome.id)
        
        network._synthetize_nodes(node_genes=genome.node_genes)    
        network._synthetize_links(link_genes=genome.link_genes)
        
        return network
    
    def _synthetize_nodes(self, node_genes: Dict[int, NodeGene]):
        nodes = dict()
        for key, node_gene in node_genes.items():
            nodes[key] = Node.synthesis(node_gene.transcript())
            
        self._sort_nodes(nodes)
      
    def _synthetize_links(self, link_genes: Dict[int, LinkGene]) -> Dict[int, Link]:
        for key, link_gene in link_genes.items():
            link = Link.synthesis(link_gene.transcript())
            # Replace id  by the actual Node
            link.in_node = self._all_nodes[link.in_node]
            link.out_node = self._all_nodes[link.out_node]
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
        inputs_dict = self.inputs        
        inputs = [inputs_dict[key] for key in sorted(inputs_dict.keys(), reverse=False)]
        
        for node, value in zip(inputs, values): 
            node.activation_value = value
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
        output_values = {}
        
        for node in self.get_outputs():
            """ if node.type != NodeType.OUTPUT:
                raise ValueError """
            
            output_value = node.get_activation(activation_phase=self.activation_phase) 
            output_values[node.id]= output_value
            # node.activation_value = output_value
        
        return output_values
    
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
        return self._inputs
    
    @property
    def outputs(self)  -> np.array[Node]:  
        return self._outputs
    
    @property
    def hidden(self)  -> np.array[Node]:  
        return self._hidden
    
    @property
    def all_nodes(self) -> np.array:
        return self._all_nodes
    
    @property
    def links(self) -> np.array:
        return self._links
    
    def get_inputs(self) ->  Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Array of inputs Nodes
        """        
        return set(self._inputs.values())
    
    def get_outputs(self) ->  Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Array of outputs Nodes
        """        
        return set(self._outputs.values())
    
    def get_hidden(self) -> Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Array of hidden Nodes
        """
        return set(self._hidden.values())
    
    def get_all_nodes(self) ->  Set[Node]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Node]: Array of all Nodes
        """        
        return set(self._all_nodes.values())
    
    def get_links(self) ->  Set[Link]:
        """Return only the Nodes values from the dictionary

        Returns:
            Set[Link]: Array of Links
        """        
        return set(self._links.values())
        
   
    
    
        