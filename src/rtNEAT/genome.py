from __future__ import annotations
from hashlib import new
import numpy as np
from neat import NEAT
from node import Node, NodePlace, NodeType
from link import Link
from gene import Gene
from innovation import Innovation, InnovationType
from network import Network
from typing import List, Iterator, Tuple
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
    
    def add_gene(self,
                 gene: Gene) -> None:
        """Adds a new gene that has been created through a mutation in the correct order into the list of genes in the genome

        Args:
            gene (_type_): _description_
        """
        innovation_number = gene.innovation_number
        gene_index = 0
        for current_gene in self.genes:
            if current_gene.innovation_number > innovation_number:
                break
            gene_index += 1
            
        self.genes = np.insert(self.genes, gene_index, gene)
        
    def insert_node(nodes_list: np.array,
                    node: Node) -> np.array:
        
        node_id = node.id
        node_index: int = 0
        for current_node in nodes_list:
            if current_node.id > node_id:
                break
            node_index += 1
            
        return np.insert(nodes_list, node_index, node)   
      
    def _is_IO_node(node: Node) -> bool:
        return (node.gen_node_label == NodePlace.INPUT or
               node.gen_node_label == NodePlace.BIAS or
               node.gen_node_label == NodePlace.OUTPUT)
    
    def _choose_gene(p1_gene: Gene,
                     p2_gene: Gene,
                     p1_genes: Iterator,
                     p2_genes: Iterator,
                     p1_dominant: bool) -> Tuple[Gene, bool, bool]:
        """Choose the gene to transmit to offspring

        Args:
            p1_gene (Gene): _description_
            p2_gene (Gene): _description_
            p1_genes (Iterator): _description_
            p2_genes (Iterator): _description_
            p1_dominant (bool): _description_

        Returns:
            Tuple[Gene, bool, bool]: _description_
        """        
        disable: bool = False
        skip: bool = False
        
        if not p1_gene: 
            chosen_gene = p2_gene
            p2_gene = next(p2_genes, None)
            if p1_dominant: skip = True
                    
        elif not p2_gene:
            chosen_gene = p1_gene
            p1_gene = next(p1_genes, None)
            if not p1_dominant: skip = True
        
        else:
            p1_innovation = p1_gene.innovation_number
            p2_innovation = p2_gene.innovation_number
            
            if p1_innovation == p2_innovation:
                np.random.seed(2022)
                chosen_gene = np.random.choice([p1_gene, p2_gene])
            
                # If one is disabled, the corresponding gene in the offspring will likely be disabled
                if not p1_gene.enabled or not p2_gene.enabled:
                    if random.random() < 0.75:
                        disable = True
                
                p1_gene = next(p1_genes, None)
                p2_gene = next(p2_genes, None)  
                
            elif p1_innovation < p2_innovation:
                chosen_gene = p1_gene
                p1_gene = next(p1_genes, None)
                if not p1_dominant: skip = True
                    
            elif p2_innovation < p1_innovation:
                chosen_gene = p2_gene
                p2_gene = next(p2_genes, None)
                if p1_dominant: skip = True
                    
        return chosen_gene, skip, disable, p1_gene, p2_gene, p1_genes, p2_genes
        
    def _check_gene_conflict(new_genes: List[Gene],
                             chosen_gene: Gene) -> Gene:
        """ Check to see if the chosengene conflicts with an already chosen gene
            i.e. do they represent the same link

        Args:
            new_genes (List[Gene]): _description_
            chosen_gene (Gene): _description_

        Returns:
            Gene: _description_
        """        
        
        iter_genes = iter(new_genes)  
        current_gene = next(iter_genes, None)
        while (current_gene and 
                not(current_gene.link.in_node.id == chosen_gene.link.in_node.id and 
                    current_gene.link.out_node.id == chosen_gene.link.out_node.id and
                    current_gene.link.is_recurrent == chosen_gene.link.is_recurrent) and
                not(current_gene.link.in_node.id == chosen_gene.link.out_node.id and
                    current_gene.link.out_node.id == chosen_gene.link.in_node.od and
                    current_gene.link.is_recurrent == chosen_gene.link.is_reccurent) and
                not chosen_gene.link.is_recurrent):
            
            current_gene = next(iter_genes, None)
        
        return current_gene 
    
    def _check_new_node_existence(new_nodes: np.array,
                              target_node: Node):
        """ Find new node to 

        Args:
            new_nodes (List[Node]): _description_
            target_node (Node): _description_
        """        
        
        iter_nodes = iter(new_nodes)
        current_node = next(iter_nodes, None)
        while (current_node and
                current_node.id != target_node.id):
            current_node = next(iter_nodes, None) 
            
        if not current_node:
            # Here we know the node doesn't exist so we have to add it 
            new_node = Node.constructor_from_node(target_node)
            new_nodes = Genome.insert_node(nodes_list=new_nodes,
                                           node=new_node)
            
        else:
            new_node = current_node
            
        return new_node, new_nodes
    
    def mate_multipoint(self,
                        genome_mate: Genome,
                        genome_id: int,) -> Genome:
                
        new_nodes = np.array([], dtype=Node) # already added nodes
        np.random.seed(2022)
        p1_dominant: bool = np.random.choice([True, False]) # Determine which genome will give its excess genes
        
        new_genes: List[Gene] = [] # already chosen genes
        
        # Make sure all sensors and outputs are included
        for current_node in genome_mate.nodes:
            if(Genome._is_IO_node(current_node)):
                
                # Create a new node off the sensor or output
                new_output_node = Node.constructor_from_node(current_node)
                
                # Add the new node
                new_nodes = Genome.insert_node(nodes_list=new_nodes, node=new_output_node)
          
        # Now move through the Genes of each parent until both genomes end  
        p1_genes = iter(self.genes)
        p2_genes =iter(genome_mate.genes)
        p1_gene = next(p1_genes, None)
        p2_gene = next(p2_genes, None)
        args = (p1_gene, p2_gene, p1_genes, p2_genes)
        while p1_gene or p2_gene:
         
            (chosen_gene, skip, disable, *args) = Genome._choose_gene(*args,
                                                                      p1_dominant=p1_dominant)
            p1_gene, p2_gene = args[0:2]           
            
            current_gene = Genome._check_gene_conflict(new_genes=new_genes,
                                                       chosen_gene=chosen_gene)     
            if current_gene: skip = True
            
            if not skip:
                # Now add the chosengene to the baby
                
                # Check for the nodes, add them if not in the baby Genome already
                in_node = chosen_gene.link.in_node
                out_node = chosen_gene.link.out_node 

                #Check for inode in the newnodes list
                if in_node.id < out_node.id:
                    # inode before onode

                    # Checking for inode's existence                       
                    new_in_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                             target_node=in_node)
                        
                    # Checking for onode's existence
                    new_out_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                              target_node=out_node)
                    
                # If the onode has a higher id than the inode we want to add it first     
                else:
                    new_out_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                              target_node=out_node)
                        
                    new_in_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                              target_node=in_node)
                
                # Add gene        
                new_gene = Gene.constructor_from_gene(gene=chosen_gene,
                                                      in_node=new_in_node,
                                                      out_node=new_out_node)
                if disable:
                    new_gene.enabled = False
                    disable = False
                    
                new_genes.append(new_gene)
        
        new_genome = Genome(genome_id=genome_id,
                            nodes=new_nodes,
                            genes=np.array(new_genes))
        
        return new_genome
           
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
                    
    def mutate_add_node(self, innovations: List, current_node_id: int, current_innovation: int) -> True:
        """Mutate genome by adding a node respresentation 

        Args:
            innovations (List): _description_
            current_node_id (int): _description_
            current_innovation (int): _description_

        Returns:
            True: _description_
        """        
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
    
    def mutate_add_link(self, innovations: List, current_innovation: int, tries: int) -> bool:
        """Mutate the genome by adding a new link between 2 random Nodes 

        Args:
            innovations (List): _description_
            current_innovation (int): _description_
            tries (int): _description_

        Returns:
            bool: _description_
        """
        
        threshold: int = self.nodes.size**2
        count: int = 0
        
        # Make attempts to find an unconnected pair
        try_count: int = 0
        
        # Decide whether to make this recurrent
        recurrence = random.random() < NEAT.recurrence_only_prob
        
        # Find the first non-sensor so that the to-node won't look at sensors as possible destinations
        first_non_sensor: int = 0      
        for node in self.nodes:
            if not node.nde_type == NodeType.SENSOR:
                the_node1 = node
                break; 
            first_non_sensor += 1
            
        if recurrence:
            while try_count < tries:
                loop_recurrence = random.random() > 0.5
                
                if loop_recurrence:
                    node_number1 = random.randint(first_non_sensor, self.nodes.size - 1)
                    node_number2 = node_number1
                else:
                    node_number1 = random.randint(0, self.nodes.size - 1)
                    node_number2 = random.randint(first_non_sensor, self.nodes.size - 1)
                    
                the_node1 = self.nodes[node_number1]
                the_node2 = self.nodes[node_number2]
                
                genes = iter(self.genes)
                the_gene = next(genes, None)
                # See if a recur link already exists  ALSO STOP AT END OF GENES!!!!
                while (the_gene and 
                       the_node2.node_type == NodeType.SENSOR and # Don't allow SENSORS to get input
                       not (the_gene.link.in_node == the_node1 and
                            the_gene.link.out_node == the_node2 and
                            the_gene.link.is_recurrent)):
                    
                    the_gene = next(genes)
                    if the_gene:
                        try_count += 1
                    else:
                        count = 0
                        recurrence_flag = self.phenotype.is_recurrent(the_node1.analogue,
                                                                      the_node2.analogue,
                                                                      count,
                                                                      threshold)
                        
                        # CONSIDER connections out of outputs recurrent
                        if (the_node1.node_type == NodeType.OUTPUT or
                            the_node2.node_type == NodeType.OUTPUT):
                            recurrence_flag = True
                            
                        # Make sure it finds the right kind of link (recur)
                        if not recurrence_flag:
                            try_count += 1
                        else:
                            try_count = tries
                            found = True
        
        else:
            # Loop to find a nonrecurrent link
            while try_count < tries:
                # Choose random node numbers
                node_number1 = random.randint(0, self.nodes.size - 1)
                node_number2 = random.randint(first_non_sensor, self.nodes.size - 1)
                                        
                # Find the first node
                the_node1 = self.nodes[node_number1]
                the_node2 = self.nodes[node_number2]
                
                genes = iter(self.genes)
                the_gene = next(genes, None)
                while (the_gene and
                       not the_node2.node_type == NodeType.SENSOR and
                       not (the_gene.link.in_node == the_node1 and
                            the_gene.link.out_node == the_node2 and
                            the_gene.link.is_recurrent)):
                    
                    if the_gene:
                        try_count += 1
                    else:
                        count = 0
                        recurrence_flag = self.phenotype.is_recurrent(the_node1.analogue,
                                                                      the_node2.analogue,
                                                                      count,
                                                                      threshold)
                        
                        # CONSIDER connections out of outputs recurrent
                        if (the_node1.node_type == NodeType.OUTPUT or
                            the_node2.node_type == NodeType.OUTPUT):
                            recurrence_flag = True
                        
                        # Make sure it finds the right kind of link (recur or not)
                        if recurrence_flag:
                            try_count += 1
                        else:
                            try_count = tries
                            found = True
                    
                    innovs = iter(innovations)
                    the_innovation = next(innovs, None)
                    # Continue only if an open link was found
                    if found:
                       
                        if recurrence:
                           recurrence_flag = 1 
                           
                        done = False
                        
                        while not done:
                            # The innovation is totally novel
                            if not the_innovation:
                                 # If the phenotype does not exist, exit on false,print error
				                # Note: This should never happen- if it does there is a bug
                                if self.phenotype == 0:
                                    return False
                                                        
                                # Choose the new weight
                                new_weight = [-1,1][random.randrange(2)] * random.random() 
                                # Create the new gene
                                new_gene = Gene(weight=new_weight,
                                                in_node=the_node1,
                                                out_node=the_node2,
                                                recurrence=recurrence_flag,
                                                innovation_number=current_innovation,
                                                mutation_number=new_weight)
                                
                                # Add the innovation
                                new_innovation = Innovation(node_in_id=the_node1.id,
                                                            node_out_id=the_node2.id,
                                                            innovation_type=InnovationType.NEWLINK,
                                                            innovation_number1=current_innovation,
                                                            weight=new_weight,
                                                            )
                                innovations.append()
                                current_innovation += 1
                                done = True   
                                
                            # OTHERWISE, match the innovation in the innovs list
                            elif(the_innovation.innvation_type == InnovationType.NEWLINK and
                                the_innovation.node_in_id == the_node1.id and
                                the_innovation.node_out_id == the_node2.id and
                                the_innovation.recurrence_flag == recurrence_flag):
                                
                                new_gene = Gene(weight=the_innovation.weight,
                                                in_node=the_node1,
                                                out_node=the_node2,
                                                recurrence=recurrence_flag,
                                                innovation_number=the_innovation.innovation_number,
                                                mutation_number=0)
                                
                                done = True
                                
                            else:
                                the_innovation = next(innovs, None)
                        
                        self.add_gene(self.genes, new_gene)
                                       
    def mutate_add_sensor(self, innovations: List, current_innovation: int):
        
        # Find all the sensors and outputs
        sensors = []
        outputs = []
        for node in self.nodes:
            if node.node_type == NodeType.SENSOR:
                sensors.append(node)
            elif node.gen_node_label == NodeType.OUTPUT:
                outputs.append(node)
        
        # eliminate from contention any sensors that are already connected
        for sensor in sensors:
            outputConnections = 0
            
            for gene in self.genes:
                if gene.link.out_node.gen_node_label == NodeType.OUTPUT:
                    outputConnections += 1
            
        if outputConnections == len(outputs):
            sensors.remove(node)
        
        # If all sensors are connected, quit
        if len(sensors) == 0:
            return
        
        # Pick randomly from remaining sensors
        sensor = sensors[random.randint(0, len(sensors) - 1)]
        
        # Add new links to chosen sensor, avoiding redundancy
        for output in outputs:
            found = False
            
            for gene in self.genes:
                if (gene.link.in_node == sensor and
                    gene.link.out_node == output):
                    found = True
        
        
        innovs = iter(innovations)       
        # Record the innovation
        if not found:
            the_innovation = next(innovs, None)
            done = False
            while not done:
                # The innovation is novel
                if not the_innovation:
                    # Choose the new weight
                    new_weight = [-1,1][random.randrange(2)]*random.random() * 3.0
                    
                    # Create the new gene
                    new_gene = Gene(weight=new_weight,
                                    in_node=sensor,
                                    out_node=output,
                                    recurrence=False,
                                    innovation_number=current_innovation,
                                    mutation_number=new_weight) 
                    
                    new_innovation = Innovation(node_in_id=sensor.id,
                                                node_out_id=output.id,
                                                innovation_number1=current_innovation,
                                                new_weight=new_weight)
                    
                    innovations.append(new_innovation)
                    current_innovation += 1
                    
                    done = True
                    
                elif (the_innovation.innovation_type == InnovationType.NEWLINK and
                      the_innovation.node_in_id == sensor.id and
                      the_innovation.node_out_id == output.id and
                      the_innovation.recurrence_flag == False):
                    
                    new_gene = Gene(weight=the_innovation.weight,
                                    recurrence=False,
                                    innovation_number=the_innovation.innovation_number1,
                                    mutation_number=0)
                    
                    done = True
                    
                else:
                    the_innovation = next(innovs, None)
                    
            self.add_gene(gene=new_gene)