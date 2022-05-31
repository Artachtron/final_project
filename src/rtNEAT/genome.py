import numpy as np
from neat import NEAT
from node import Node, NodePlace
from link import Link
from network import Network
from typing import List

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array,
                 genes: np.array):
        
        self.id: int = genome_id
        self.nodes: np.array = nodes # List of Nodes for the Network
        self.genes: np.array = genes # List of innovation-tracking genes
        self.size = len(genes)
   
def compatibility(self, genome: Genome):
    p1_innovation: int
    p2_innovation: int
    
    mutation_difference: float
    
    number_disjoint: int
    number_excess: int = 0
    mutation_difference_total: float
    number_matching: int = 0
    
    max_genome_size: int = max(self.size, genome.size)

    p1_genome = iter(self.genes)
    p2_genome = iter(genome.genes)
    
    p1_gene = next(p1_genome)
    p2_gene = next(p2_genome)
    
    while True:
        try:
            if p1_gene == self.genes[-1]:
                p2_gene = next(p2_genome)
                number_excess += 1
            elif p2_gene == genome.genes[-1]:
                p1_gene = next(p1_genome)
                number_excess += 1
            else:
                p1_innovation = p1_gene.innovation_number
                p2_innovation = p2_gene.innovation_number
                
                if(p1_innovation==p2_innovation):
                    number_matching += 1
                    mutation_difference = abs(p1_gene.mutation_number - p2_gene.mutation_number)
                    mutation_difference_total += mutation_difference
                    
                    p1_gene = next(p1_genome)
                    p2_gene = next(p1_genome)
                elif p1_innovation < p2_innovation:
                    p1_gene = next(p1_genome)
                    number_disjoint += 1
                elif p2_innovation < p1_innovation:
                    p2_gene = next(p2_genome)
                    number_disjoint += 1
        except StopIteration:
            break

    return (NEAT.disjoint_coeff(number_disjoint) +
            NEAT.excess_coeff(number_excess) +
            NEAT.mutation_difference_total(mutation_difference_total(number_matching)))
    
def get_last_node_id(self) -> int:
    """ Return id of final Node in Genome

    Returns:
        int: last node's id
    """    
    self.nodes[-1].id + 1

def get_last_gene_innovation_number(self) -> int:
    """ Return last innovation number in Genome

    Returns:
        int: last gene's innovation number
    """    
    self.genes[-1].innovation_number + 1
    
def genesis(self, id: int):
    """Generate a network phenotype from this Genome with specified id

    Args:
        id (int): id of the network
    """    
    new_node: Node
    current_link: Link
    new_link: Link
    
    max_weight: float = 0.0 # Compute the maximum weight for adaptation purposes
    weight_magnitude: float # Measures absolute value of weights
    
    inlist: List[Node] = []
    outlist: List[Node] = []
    all_list: List[Node] = []
    
    new_net: Network
    
    for current_node in self.nodes:
        new_node = Node(node_type=current_node.type, node_id=current_node.id)
        
        # Check for input or output designation of node
        match current_node.gen_node_label:
            case NodePlace.INPUT:
                inlist.append(new_node)
            case NodePlace.OUTPUT:
                outlist.append(new_node)
            case NodePlace.BIAS:
                inlist.append(new_node)
        
        # Keep track of all nodes, not just input and output    
        all_list.append(new_node)
        
        # Have the node specifier point to the node it generated
        current_node.analogue = new_node