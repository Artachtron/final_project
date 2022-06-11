from population import Population
from genome import Genome
from node import Node, NodeType
from gene import Gene
from neat import Config
import numpy as np

def function() -> Population:
    sensor_node = Node(node_id=0, node_type=NodeType.INPUT)
    action_node = Node(node_id=1, node_type=NodeType.OUTPUT)
    gene = Gene(in_node=sensor_node, out_node=action_node, weight=1, innovation_number=0, mutation_number=0)
    
    nodes = np.array([sensor_node, action_node])
    genes = np.array([gene])
    
    start_genome = Genome(genome_id=0, nodes=nodes, genes=genes)

    organisms = np.array([start_genome])
    population = Population(organisms=organisms, species=np.array([]), size=organisms.size)
    
    return population

def create_a_genome():
    pass

def main():
    internal_properties = 4
    see_entities = 8
    see_energies = 9
    see_cells = 25 * 3
    n_inputs = internal_properties + see_entities + see_energies + see_cells
    
    move = 2
    modify_cell_color = 3
    drop_energy = 2
    other_actions = 5
    n_outputs = move + modify_cell_color + drop_energy + other_actions
    
    Config.num_inputs = n_inputs
    Config.num_outputs = n_outputs
    
    genome = Genome(genome_id=0)
    
if __name__ == '__main__':
    main()
    