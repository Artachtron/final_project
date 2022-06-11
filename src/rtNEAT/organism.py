from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Entity
    
from genome import Genome
from network import Network
from node import Node, NodeType
from genes import LinkGene
from neat import Config
import numpy as np


class Organism:
    def __init__(self,
                 genome: Genome,
                 organism_id: int = 0,
                 entity: Entity=None,
                 generation: int=0):
        
        self.id = organism_id
        self.genotype: Genome = genome # The Organism's genotype 
        self.mind: Network = genome.phenotype
        self.body: Entity = entity
                
        self.species: int = 0 # The Organism's Species 
        self.genaration: int = generation # Tells which generation this Organism is from
        
        if generation == 0 and not self.genotype.node_genes:
            self._initial_generation_organism()
        elif self.genotype.node_genes:
            self.genotype.genesis()
 
    def update_phenotype(self) -> Organism:
        self.mind = self.genotype.genesis(mind_id=self.genotype.id)
        
    def _initial_generation_organism(self):
        """ Initialize a mind based on configuration.
            Create the input nodes, output nodes and
            genes connecting each input to each output 
        """        
        # Initialize inputs
        inputs = []
        for _ in range(Config.num_inputs):
            inputs.append(Node(node_type=NodeType.INPUT))               
        
         # Initialize bias
        bias =[]
        bias.append(Node(node_type=NodeType.BIAS))
                
        # Initialize outputs    
        outputs = []  
        for _ in range(Config.num_outputs):
            outputs.append(Node(node_type=NodeType.OUTPUT))

        else:
            self.genotype.node_genes = {node.id: node for node in inputs + bias + outputs}
        
        genes = []
        for node1 in inputs + bias:
            for node2 in outputs:
                genes.append(LinkGene(  in_node=node1,
                                    out_node=node2))

        else:
            self.genotype.link_genes = np.array(genes)
        
        self.mind = Network.create_network( genome=self.genotype,
                                            inputs=np.array(inputs+bias),
                                            outputs=np.array(outputs),
                                            all_nodes=np.array(inputs+bias+outputs))
                   
     