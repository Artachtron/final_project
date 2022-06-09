from __future__ import annotations
from genome import Genome
from network import Network
from innovation import InnovTable
from node import Node, NodePlace
from gene import Gene
from neat import config
import numpy as np

class Organism:
    def __init__(self,
                 genome: Genome,
                 generation: int=0):
        self.genome: Genome = genome # The Organism's genotype 
        self.network: Network = genome.phenotype
                
        self.species: int = 0 # The Organism's Species 
        self.genaration: int = generation # Tells which generation this Organism is from
        
        if generation == 0 and self.genome.nodes is None:
            self._initial_generation_organism()
 
    def update_phenotype(self) -> Organism:
        self.network = self.genome.genesis(network_id=self.genome.id)
        
    def _initial_generation_organism(self):
        # Initialize bias
        bias =[]
        bias.append(Node(node_id=InnovTable.get_node_number(),
                        node_place=NodePlace.BIAS))
        
        InnovTable.increment_node()
        
        # Initialize inputs
        inputs = []
        for _ in range(config.num_inputs):
            inputs.append(Node(node_id=InnovTable.get_node_number(),
                                node_place=NodePlace.INPUT))
                
            InnovTable.increment_node()                    
        
        # Initialize outputs    
        outputs = []  
        for _ in range(config.num_outputs):
            outputs.append(Node(node_id=InnovTable.get_node_number(),
                                node_place=NodePlace.OUTPUT))
            
            InnovTable.increment_node() 
        else:
            self.genome.nodes = np.array(bias + inputs + outputs)
        
        genes = []
        for node1 in inputs + bias:
            for node2 in outputs:
                genes.append(Gene(  in_node=node1,
                                    out_node=node2,
                                    innovation_number=InnovTable.get_innovation_number()))

                InnovTable.increment_innov()
        else:
            self.genome.genes = np.array(genes)
            
        # Create the new network        
        new_network = Network(inputs=bias+inputs,
                              outputs=outputs,
                              all_nodes=bias+inputs+outputs,
                              network_id=self.genome.id)
        
         # Attach genotype and phenotype together
        new_network.genotype = self
        self.phenotype = new_network
        
        return new_network       