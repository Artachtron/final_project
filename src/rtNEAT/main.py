from population import Population
from genome import Genome
from node import Node, NodeType, NodePlace
from gene import Gene
import numpy as np

def function() -> Population:
    sensor_node = Node(node_type=NodeType.SENSOR, node_id=0, node_place=NodePlace.INPUT)
    action_node = Node(node_type=NodeType.NEURON, node_id=1, node_place=NodePlace.OUTPUT)
    gene = Gene(in_node=sensor_node, out_node=action_node, weight=1, innovation_number=0, mutation_number=0)
    
    nodes = np.array([sensor_node, action_node])
    genes = np.array([gene])
    
    start_genome = Genome(genome_id=0, nodes=nodes, genes=genes)

    organisms = np.array([start_genome])
    population = Population(organisms=organisms, species=np.array([]), size=organisms.size)
    
    return population

def create_a_genome():
    pass