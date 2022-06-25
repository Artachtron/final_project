from __future__ import annotations
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
        """Class method:
            Create a new network corresponding to the given genome

        Args:
            genome (Genome): genome containing the encoding for this network

        Returns:
            Network: created network
        """        
        network = cls(network_id=genome.id)
        
        network._synthetize_nodes(node_genes=genome.node_genes)    
        network._synthetize_links(link_genes=genome.link_genes)
        
        return network
    
    def _synthetize_nodes(self, node_genes: Dict[int, NodeGene]):
        """Private method:
            Decode the NodeGenes to synthesize Nodes, and
            sort the Nodes based on their positions in the network

        Args:
            node_genes (Dict[int, NodeGene]): dictionary containing the NodeGenes
        """        
        nodes = dict()
        for key, node_gene in node_genes.items():
            nodes[key] = Node.synthesis(node_gene.transcript())
            
        self._sort_nodes(nodes)
      
    def _synthetize_links(self, link_genes: Dict[int, LinkGene]):
        """Private method:
            Decode the LinkGenes to synthesize Links,
            add them to the network, and
            connect the incoming Node to the outgoing Node.
            

        Args:
            link_genes (Dict[int, LinkGene]): dictionary containing the LinkGenes

        Raises:
            ValueError: Thrown if an output is an incoming Node in a Link
            ValueError: Thrown if a sensor is an outgoing Node in a Link

        """        
        for key, link_gene in link_genes.items():
            link = Link.synthesis(link_gene.transcript())
            # Replace id  by the actual Node
            in_node = self._all_nodes[link.in_node]
            out_node =  self._all_nodes[link.out_node]
            
            if in_node.is_output():
               raise ValueError(f"{in_node} is an output it can not be an in node")
           
            if out_node.is_sensor():
                raise ValueError(f"{out_node} is a sensor it can not be an out node")
            
            link.in_node = in_node
            link.out_node = out_node
            self._links[key] = link
            if link_gene.enabled: 
                self._connect_link(link)                
        
    def _connect_link(self, link: Link) -> None:
        """ Private method:
            Add the link to the list of incoming links of 
            the out node and outgoing link of the in node

        Args:
            link (Link): link to add
        """        
        in_node = self._all_nodes[link.in_node.id]
        out_node = self._all_nodes[link.out_node.id] 
        
        out_node.incoming[link.id] = link
        in_node.outgoing[link.id] = link
    
    def _sort_nodes(self, nodes: Dict[int, Node]) -> None:
        """Private method:
            Sort the Nodes by positions in the network,
            add them to their respective dictionary, and
            add themm all to the all_nodes dictionary

        Args:
            nodes (Dict[int, Node]): Dictionary of Nodes to sort
        """        
              
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
    
    def verify_complete_post_genesis(self):
        """Public method:
            Verify if the complete network's structure is correct

        Raises:
            ValueError: Outputs must be connected to all inputs
            ValueError: Outputs incoming connections must be equal to set of inputs
            ValueError: Outputs must not have any outgoing connections
            ValueError: Inputs must be connected to all outputs
            ValueError: Inputs outgoing connections must be equal to set of outputs
            ValueError: Inputs must not have any incoming connections
        """        
        # Complete
        for node in self.get_outputs():
            if len(node.incoming) != len(self.inputs):
               raise ValueError(f"{node} is connected to {len(node.incoming)}/{len(self.inputs)}")
            
            if {n.in_node.id for n in node.get_incoming()} != set(self.inputs.keys()):
                raise ValueError(f"{node} is not connected to all inputs ")
            
            if node.outgoing:
                raise ValueError(f"{node} has some outgoing connections")
            
        for node in self.get_inputs():
            if len(node.outgoing) != len(self.outputs):
               raise ValueError(f"{node} is connected to {len(node.outgoing)}/{len(self.outputs)}")
            
            if {n.out_node.id for n in node.get_outgoing()} != set(self.outputs.keys()):
                raise ValueError(f"{node} is not connected to all outputs")
            
            if node.incoming:
                raise ValueError(f"{node} has some incoming connections")
            
        
    
    def activate(self, input_values: np.array) -> np.array:
        """Public method:
            Activate the whole network after recieving input values

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
        self._activate_inputs(values=input_values)
        # travel through the network to calculate the output values
        output_values = self._activate_outputs()
                                 
        return output_values
    
    def _activate_inputs(self, values: np.array):
        """ Private method:
            Store the input values in the input nodes
    
        Args:
            values (np.array): values to store in the input nodes
        """ 
        # Make sure inputs are in the right order
        inputs = list(self.inputs.values())
        
        for node, value in zip(inputs, values): 
            if not node.is_sensor():
                raise ValueError("The node must be a sensor")
            node.activation_value = value
            node.activation_phase = self.activation_phase
        
    def _activate_outputs(self) -> np.array:
        """Private method:
            Travel through the network calculating the
            activation values necessary for each output
        

        Raises:
            ValueError: The nodes in the outputs list 
                        are not of the proper type

        Returns:
            np.array: list of the output values after calculation 
        """        
        output_values = {}
        
        for node in self.get_outputs():
            if not node.is_output():
                raise ValueError("The node must be an output")
            
            output_value = node.get_activation(activation_phase=self.activation_phase) 
            output_values[node.id] = output_value
            node.activation_value = output_value
        
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
    def inputs(self)  -> Dict[int, Node]:  
        return self._inputs
    
    @property
    def outputs(self)  -> Dict[int, Node]:  
        return self._outputs
    
    @property
    def hidden(self)  -> Dict[int, Node]:  
        return self._hidden
    
    @property
    def all_nodes(self) -> Dict[int, Node]:
        return self._all_nodes
    
    @property
    def links(self) -> Dict[int, Node]:
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
        
   
    
    
        