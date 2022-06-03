from __future__ import annotations
from ast import In
import numpy as np
from neat import NEAT
from node import Node, NodePlace, NodeType
from link import Link
from gene import Gene
from innovation import Innovation, InnovationType
from network import Network
from typing import List
import random

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array,
                 genes: np.array):
        
        self.id: int = genome_id
        self.nodes: np.array = nodes # List of Nodes for the Network
        self.genes: np.array = genes # List of innovation-tracking genes
        self.size = len(genes)
   
    def compatibility(self, comparison_genome: Genome) -> float:
        p1_innovation: int
        p2_innovation: int
        
        mutation_difference: float
        
        number_disjoint: int = 0
        number_excess: int = 0
        mutation_difference_total: float= 0.0
        number_matching: int = 0
        
        #max_genome_size: int = max(self.size, comparison_genome.size)
        p1_genome = iter(self.genes)
        p2_genome = iter(comparison_genome.genes)
        
        p1_gene = next(p1_genome)
        p2_gene = next(p2_genome)
        
        while p1_gene or p2_gene:
            try:
                if not p1_gene:
                    p2_gene = next(p2_genome, None)
                    number_excess += 1
                elif not p2_gene:
                    p1_gene = next(p1_genome, None)
                    number_excess += 1
                else:
                    p1_innovation = p1_gene.innovation_number
                    p2_innovation = p2_gene.innovation_number
                    
                    if(p1_innovation==p2_innovation):
                        number_matching += 1
                        mutation_difference = abs(p1_gene.mutation_number - p2_gene.mutation_number)
                        mutation_difference_total += mutation_difference
                        
                        p1_gene = next(p1_genome, None)
                        p2_gene = next(p2_genome, None)
                    elif p1_innovation < p2_innovation:
                        p1_gene = next(p1_genome, None)
                        number_disjoint += 1
                    elif p2_innovation < p1_innovation:
                        p2_gene = next(p2_genome, None)
                        number_disjoint += 1
            except StopIteration:
                break

        disjoint = NEAT.disjoint_coeff * (number_disjoint)
        excess =  NEAT.excess_coeff * (number_excess)
        if number_matching > 0:
             mutation_difference = NEAT.mutation_difference_coeff * (mutation_difference_total/number_matching)
        else:
            mutation_difference = 0
       
        compatibility = disjoint + excess + mutation_difference
        return compatibility
        
    def get_last_node_id(self) -> int:
        """ Return id of final Node in Genome

        Returns:
            int: last node's id
        """    
        return self.nodes[-1].id + 1

    def get_last_gene_innovation_number(self) -> int:
        """ Return last innovation number in Genome

        Returns:
            int: last gene's innovation number
        """    
        return self.genes[-1].innovation_number + 1
        
    def genesis(self, network_id: int) -> Network:
        """Generate a network phenotype from this Genome with specified id

        Args:
            id (int): id of the network
            
        Returns:
            Network: the network created as phenotype
        """    
        new_node: Node
        current_link: Link
        new_link: Link
        
        max_weight: float = 0.0 # Compute the maximum weight for adaptation purposes
        weight_magnitude: float # Measures absolute value of weights
        
        inlist: List[Node] = []
        outlist: List[Node] = []
        all_list: List[Node] = []
                
        for current_node in self.nodes:
            new_node = Node(node_type=current_node.node_type, node_id=current_node.id)
            
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
            
        # Create the links by iterating through the genes
        for current_gene in self.genes:
            # Only create the link if the gene is enabled
            if current_gene.enabled:
                current_link = current_gene.link
                in_node = current_link.in_node.analogue
                out_node = current_link.out_node.analogue
                
                new_link = Link(weight=current_link.weight,
                                in_node=in_node,
                                out_node=out_node,
                                recurrence=current_link.is_recurrent)
                
                out_node.incoming.append(new_link)
                in_node.outgoing.append(new_link)
                
                # Keep track of maximum weight
                if new_link.weight > 0:
                    weight_magnitude = new_link.weight
                max_weight = max(weight_magnitude, max_weight)
        
        # Create the new network        
        new_network = Network(inputs=inlist, outputs=outlist,all_nodes=all_list, network_id=network_id)
            
        # Attach genotype and phenotype together
        new_network.genotype = self
        self.phenotype = new_network
        
        new_network.max_weight = max_weight
        
        return new_network
    
    def mutate_link_weights(self, power: float, rate: float) -> None:
        number: float = 0.0
        total_genes: int = self.genes.size
        end_part: float = total_genes * 0.8
        power_mod: float = 1.0       
        
        for current_gene in self.genes:
            if not current_gene.frozen:
                if total_genes > 10 and number > end_part:
                    gausspoint = 0.5
                    cold_gausspoint = 0.3
                    
                else:
                    if random.random() > 0.5:
                        gausspoint = 1.0 - rate
                        cold_gausspoint = 1.0 - rate - 0.1
                    else:
                        gausspoint = 1.0 - rate
                        cold_gausspoint = 1.0 - rate
                        
                random_number = [-1,1][random.randrange(2)] * random.random() * power * power_mod
                
                random_choice = random.random()
                if random_choice > gausspoint:
                    current_gene.link.weight += random_number
                elif random_choice > cold_gausspoint:
                    current_gene.link.weight = random_number
                    
                current_gene.mutation_number = current_gene.link.weight
                
                number += 1
                    
    def mutate_add_node(self, innovations: List, current_node_id: int, current_innovation: int):
        try_count: int = 0
        found: bool = False
        
        while try_count < 20 and not found:
            gene_number = random.randint(0, self.genes.size -1)
            for gene in self.genes[:gene_number]:
                if not(not gene.enable or gene.link.in_node.gene_node_label == NodePlace.BIAS):
                    found = True
                    the_gene = gene
                    
            try_count += 1
               
        if not found:
            return False
        
        # Disabled the gene
        the_gene.enable = False
        
        # Extract the link
        the_link = the_gene.link
        old_weight = the_link.weight
        
        # Extract the nodes
        in_node = the_link.in_node
        out_node = the_link.out_node
        
        innovation_iter = iter(innovations)
        the_innovation = next(innovation_iter, None)
        done = False
        while not done:
            reccurence = the_link.is_recurrent
            if not the_innovation:
                new_node = Node(node_type=NodeType.NEURON,
                                node_id=current_node_id,
                                node_place=NodePlace.HIDDEN)
                
                new_gene1 = Gene(weight=1.0,
                                    in_node=in_node,
                                    out_node=new_node,
                                    recurrence=reccurence,
                                    innovation_number=current_innovation,
                                    mutation_number=0)
                
                new_gene2 = Gene(weight=old_weight,
                                    in_node=new_node,
                                    out_node=out_node,
                                    recurrence=False,
                                    innovation_number=current_innovation+1,
                                    mutation_number=0)
                current_innovation += 2
                
                new_innovation = Innovation(node_in_id=in_node.id,
                                            node_out_id=out_node.id,
                                            innovation_type=InnovationType.NEWNODE,
                                            innovation_number1=current_innovation-2.0,
                                            innovation_number2=current_innovation-1.0,
                                            new_node_id=new_node.id,
                                            old_innovation_number=the_gene.innovation_number)
                innovations.append(new_innovation)
                
                done = True
                
            elif(the_innovation.innovation_type == InnovationType.NEWNODE and 
                 the_innovation.node_in_id == in_node.id and
                 the_innovation.node_out_id == out_node.id and
                 the_innovation.old_innovation_number == the_gene.innovation_number):
                
                new_node = Node(node_type=NodeType.NEURON,
                                node_id=the_innovation.new_node_id,
                                node_place=NodePlace.HIDDEN)
                
                new_gene1 = Gene(weight=1.0,
                                    in_node=in_node,
                                    out_node=new_node,
                                    recurrence=reccurence,
                                    innovation_number=the_innovation.innovation_number1,
                                    mutation_number=0)
                
                new_gene2 = Gene(weight=old_weight,
                                    in_node=new_node,
                                    out_node=out_node,
                                    recurrence=False,
                                    innovation_number=the_innovation.innovation_number2,
                                    mutation_number=0)
                
                done = True
                
            else:
                the_innovation = next(innovation_iter, None)
                
        self.add_gene(self.genes, new_gene1)
        self.add_gene(self.genes, new_gene2)
        self.node_insert(self.nodes, new_node)
        return True        
                                     