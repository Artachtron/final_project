from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Entity
from genome import Genome
from network import Network
from innovation import InnovTable
from node import Node, NodePlace
from gene import Gene
from neat import Config
import numpy as np


class Organism:
    def __init__(self,
                 genome: Genome,
                 entity: Entity=None,
                 generation: int=0):
        
        self.genotype: Genome = genome # The Organism's genotype 
        self.mind: Network = genome.phenotype
        self.body: Entity = entity
                
        self.species: int = 0 # The Organism's Species 
        self.genaration: int = generation # Tells which generation this Organism is from
        
        if generation == 0 and self.genotype.nodes is None:
            self._initial_generation_organism()
        elif self.genotype.nodes is not None:
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
            inputs.append(Node(node_place=NodePlace.INPUT))               
        
         # Initialize bias
        bias =[]
        bias.append(Node(node_place=NodePlace.BIAS))
                
        # Initialize outputs    
        outputs = []  
        for _ in range(Config.num_outputs):
            outputs.append(Node(node_place=NodePlace.OUTPUT))

        else:
            self.genotype.nodes = {node.id: node for node in inputs + bias + outputs}
        
        genes = []
        for node1 in inputs + bias:
            for node2 in outputs:
                genes.append(Gene(  in_node=node1,
                                    out_node=node2,
                                    innovation_number=InnovTable.get_innovation_number()))

                InnovTable.increment_innov()
        else:
            self.genotype.genes = np.array(genes)
        
        Network.create_network( genome=self.genotype,
                                inputs=np.array(inputs+bias),
                                outputs=np.array(outputs),
                                all_nodes=np.array(inputs+bias+outputs))
                   
     