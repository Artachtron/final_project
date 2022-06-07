from __future__ import annotations
import numpy as np
from neat import NEAT
from node import Node, NodePlace, NodeType
from link import Link
from gene import Gene
from innovation import Innovation, InnovationType
from network import Network
from typing import List, Iterator, Tuple
from numpy.random import choice, randint, random, uniform

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array,
                 genes: np.array):
        
        self.id: int = genome_id
        self.nodes: np.array = nodes # List of Nodes for the Network
        self.genes: np.array = genes # List of innovation-tracking genes
        self.size = len(genes)
        self.phenotype = None # Network associated with genome
   
    def compatibility(self, comparison_genome: Genome) -> float:
        """ Find the compatibility score between two genomes

        Args:
            comparison_genome (Genome): the genome to compare with the current one

        Returns:
            float: compatibility score
        """        
        p1_innovation: int
        p2_innovation: int
        
        mutation_difference: float
        
        number_disjoint: int = 0
        number_excess: int = 0
        mutation_difference_total: float= 0.0
        number_matching: int = 0
        
        p1_genome = iter(self.genes)
        p2_genome = iter(comparison_genome.genes)
        
        p1_gene = next(p1_genome)
        p2_gene = next(p2_genome)
        
        while p1_gene or p2_gene:
            # Excess genes
            if not p1_gene:
                p2_gene = next(p2_genome, None)
                number_excess += 1
            elif not p2_gene:
                p1_gene = next(p1_genome, None)
                number_excess += 1
            
            # Non excess genes, we must compare innovation numbers
            else:
                p1_innovation = p1_gene.innovation_number
                p2_innovation = p2_gene.innovation_number
                
                # Matching genes
                if(p1_innovation == p2_innovation):
                    number_matching += 1
                    mutation_difference = abs(p1_gene.mutation_number - p2_gene.mutation_number)
                    mutation_difference_total += mutation_difference
                    p1_gene = next(p1_genome, None)
                    p2_gene = next(p2_genome, None)
                 
                # disjoint genes   
                elif p1_innovation < p2_innovation:
                    p1_gene = next(p1_genome, None)
                    number_disjoint += 1
                    
                elif p2_innovation < p1_innovation:
                    p2_gene = next(p2_genome, None)
                    number_disjoint += 1

        # Compatibility score calculations
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
            gene (Gene): The gene to add to the genome's list of genes
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
        """ Insert a node into a list of nodes

        Args:
            nodes_list (np.array): the list of nodes to insert in
            node (Node): the node to insert

        Returns:
            np.array: the final list of nodes after insertion
        """        
        
        node_id = node.id
        node_index: int = 0
        for current_node in nodes_list:
            if current_node.id > node_id:
                break
            node_index += 1
            
        return np.insert(nodes_list, node_index, node)   
      
    def _is_IO_node(node: Node) -> bool:
        """ Check if the node is an input or output node

        Args:
            node (Node): the node to check

        Returns:
            bool: is an input or output node
        """        
        return (node.gen_node_label == NodePlace.INPUT or
               node.gen_node_label == NodePlace.BIAS or
               node.gen_node_label == NodePlace.OUTPUT)
    
    def _choose_gene_to_transmit(   parent1_gene: Gene, parent2_gene: Gene, parent1_genes: Iterator,
                                    parent2_genes: Iterator, p1_dominant: bool
                                ) -> Tuple[Gene, bool, bool, Gene, Gene, Iterator, Iterator]:
        """Choose the gene to transmit to offspring

        Args:
            parent1_gene (Gene): the gene from the first genome
            parent2_gene (Gene): the gene from the second genome
            parent1_genes (Iterator): the iterator of genes from first genome
            parent2_genes (Iterator): the iterator of genes from second genome
            parent1_dominant (bool): the first genome is the dominant one

        Returns:
            Tuple[Gene, bool, bool, 
            Gene, Gene, Iterator, Iterator]:    
                                            Gene: the chosen gene that will be transmitted
                                            bool: the gene must be skipped
                                            bool: the gene must be disabled
                                            ... : args for the next iteration
                                        
        """        
        disable: bool = False # if the gene must be disabled
        skip: bool = False # if the gene must be skipped and not transmitted
        
        if not parent1_gene: 
            chosen_gene = parent2_gene
            parent2_gene = next(parent2_genes, None)
            if p1_dominant: skip = True
                    
        elif not parent2_gene:
            chosen_gene = parent1_gene
            parent1_gene = next(parent1_genes, None)
            if not p1_dominant: skip = True
        
        else:
            p1_innovation = parent1_gene.innovation_number
            p2_innovation = parent2_gene.innovation_number
            
            if p1_innovation == p2_innovation:
                np.random.seed(1)
                chosen_gene = choice([parent1_gene, parent2_gene])
            
                # If one is disabled, the corresponding gene in the offspring will likely be disabled
                if not parent1_gene.enabled or not parent2_gene.enabled:
                    if random() < 0.75:
                        disable = True
                
                parent1_gene = next(parent1_genes, None)
                parent2_gene = next(parent2_genes, None)  
                
            elif p1_innovation < p2_innovation:
                chosen_gene = parent1_gene
                parent1_gene = next(parent1_genes, None)
                if not p1_dominant: skip = True
                    
            elif p2_innovation < p1_innovation:
                chosen_gene = parent2_gene
                parent2_gene = next(parent2_genes, None)
                if p1_dominant: skip = True
                    
        return chosen_gene, skip, disable, parent1_gene, parent2_gene, parent1_genes, parent2_genes
        
    def _check_gene_conflict(new_genes: List[Gene],
                             chosen_gene: Gene) -> bool:
        """ Check to see if the chosengene conflicts with an already chosen gene
            i.e. do they represent the same link

        Args:
            new_genes (List[Gene]): the list of genes to check for conflicts
            chosen_gene (Gene): the chosen gene that should not conflict with existing ones

        Returns:
           bool: a conflict was detected 
        """        
        for current_gene in new_genes:
            if not( not(current_gene.link.in_node.id == chosen_gene.link.in_node.id and 
                        current_gene.link.out_node.id == chosen_gene.link.out_node.id and
                        current_gene.link.is_recurrent == chosen_gene.link.is_recurrent) and
                    not(current_gene.link.in_node.id == chosen_gene.link.out_node.id and
                        current_gene.link.out_node.id == chosen_gene.link.in_node.od and
                        current_gene.link.is_recurrent == chosen_gene.link.is_reccurent) and
                    not (chosen_gene.link.is_recurrent)):
                
                return True
        
        return False
    
    def _check_new_node_existence(new_nodes: np.array, target_node: Node) -> Tuple[Node, List[Node]]:
        """ Find if the target node already exists in the new nodes list return the final list and new node

        Args:
            new_nodes (List[Node]): the list of nodes already added
            target_node (Node): the node to check existence in the list

        Returns:
            Tuple[Node, List[Node]]:    Node: the new node, either an existing node or a created one
                                        List[Node]: the final list of nodes (updated if new node wasn't already in it)
        """                
        for current_node in new_nodes:
            if current_node.id == target_node.id:
                new_node = current_node
                break
            
        else:
            new_node = Node.constructor_from_node(target_node)
            new_nodes = Genome.insert_node(nodes_list=new_nodes,
                                           node=new_node)
            
        return new_node, new_nodes
    
    def mate_multipoint(self, genome_mate: Genome, genome_id: int,) -> Genome:
        """mates this Genome with another Genome  
		   For every point in each Genome, where each Genome shares
		   the innovation number, the Gene is chosen randomly from 
		   either parent.  If one parent has an innovation absent in 
		   the other, the baby will inherit the innovation 
		   Otherwise, excess genes come from the dominant parent.

        Args:
            genome_mate (Genome): genome of the individual to mate with
            genome_id (int): id of the child genome

        Returns:
            Genome: the child genome created
        """        
                
        new_nodes = np.array([], dtype=Node) # already added nodes
        parent1_dominant: bool = choice([0,1]) # Determine which genome will give its excess genes
        
        new_genes: List[Gene] = [] # already chosen genes
        
        # Make sure all sensors and outputs are included
        for current_node in genome_mate.nodes:
            if(Genome._is_IO_node(current_node)):
                
                # Create a new node off the sensor or output
                new_output_node = Node.constructor_from_node(current_node)
                
                # Add the new node
                new_nodes = Genome.insert_node(nodes_list=new_nodes, node=new_output_node)
          
        # Now move through the Genes of each parent until both genomes end  
        parent1_genes = iter(self.genes)
        parent2_genes =iter(genome_mate.genes)
        parent1_gene = next(parent1_genes, None)
        parent2_gene = next(parent2_genes, None)
        args = (parent1_gene, parent2_gene, parent1_genes, parent2_genes)
        while parent1_gene or parent2_gene:
         
            (chosen_gene, skip, disable, *args) = Genome._choose_gene_to_transmit(*args,
                                                                      p1_dominant=parent1_dominant)
            parent1_gene, parent2_gene = args[0:2]           
            
            conflict = Genome._check_gene_conflict( new_genes=new_genes,
                                                    chosen_gene=chosen_gene)     
            if conflict: skip = True
            
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
        
        baby_genome = Genome(genome_id=genome_id,
                            nodes=new_nodes,
                            genes=np.array(new_genes))
        
        return baby_genome
    
    def _create_new_link(self, gene: Gene) -> Link:
        """ Create a new link from a gene's link

        Args:
            gene (Gene): gene from which to get link's information

        Returns:
            Link: the created link
        """        
        current_link = gene.link
        in_node = current_link.in_node.analogue
        out_node = current_link.out_node.analogue
        
        new_link = Link(weight=current_link.weight,
                        in_node=in_node,
                        out_node=out_node,
                        recurrence=current_link.is_recurrent)
        
        out_node.incoming.append(new_link)
        in_node.outgoing.append(new_link)
        
        return new_link
           
    def genesis(self, network_id: int) -> Network:
        """Generate a network phenotype from this Genome with specified id

        Args:
            id (int): id of the network
            
        Returns:
            Network: the network created as phenotype
        """    
        
        max_weight:float = 0.0
       
        inlist: List[Node] = []
        outlist: List[Node] = []
        all_list: List[Node] = []
                
        for current_node in self.nodes:
            #new_node = Node(node_type=current_node.node_type, node_id=current_node.id, node_place=NodePlace)
            new_node = Node.constructor_from_node(node=current_node)
            
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
                # Create the new link               
                new_link = self._create_new_link(gene=current_gene)

                # Keep track of maximum weight
                weight_magnitude = abs(new_link.weight) # Measures absolute value of weights
                max_weight = max(weight_magnitude, max_weight) # Compute the maximum weight for adaptation purposes
        
        # Create the new network        
        new_network = Network(inputs=inlist, outputs=outlist,all_nodes=all_list, network_id=network_id)
            
        # Attach genotype and phenotype together
        new_network.genotype = self
        self.phenotype = new_network
        
        new_network.max_weight = max_weight
        
        return new_network
    
    def mutate_link_weights(self) -> None:
        """Simplified mutate link weight method
        """        
        for current_gene in self.genes:
            if current_gene.frozen:
                continue
            
            if random() < NEAT.mutate_link_weights_prob:
                if random() < NEAT.mutate_new_link_prob:
                    current_gene.link.weight = uniform(-1,1)
                else:
                    current_gene.link.weight += uniform(-1,1) * NEAT.weight_mutation_power 
                    
        # Record the innovation 
        current_gene.mutation_number = current_gene.link.weight
                         
    def _find_random_gene(self) -> Tuple[Gene, bool]:
        """ Find a random gene containing a node to mutate

        Returns:
            Tuple[Gene, bool]:  Gene: gene containing the node to mutate
                                bool: gene was found
        """     
                  
        try_count: int = 0
        found: bool = False
        
        while try_count < 20 and not found:
            gene_number = randint(0, self.genes.size -1)
            for gene in self.genes[:gene_number]:
                if not(not gene.enabled or gene.link.in_node.gen_node_label == NodePlace.BIAS):
                    found = True
                    the_gene = gene
                    
            try_count += 1
        
        return the_gene, found
    
    def _create_new_node(self, node_id: int, in_node: Node, out_node: Node, recurrence: bool,
                         innovation_number1: int, innovation_number2: int, old_weight: int
                         ) -> Tuple[Node, Gene, Gene]:
        """Create the new node and two genes connecting this node in and out

        Args:
            node_id (int): _description_
            in_node (Node): _description_
            out_node (Node): _description_
            recurrence (bool): _description_
            innovation_number1 (int): _description_
            innovation_number2 (int): _description_
            old_weight (int): _description_

        Returns:
            Tuple[Node, Gene, Gene]:    Node: the new node created
                                        Gene: the gene connecting in the new node
                                        Gene: the gene connecting out the new node
        """        
        new_node = Node(node_type=NodeType.NEURON,
                                node_id=node_id,
                                node_place=NodePlace.HIDDEN)
                
        new_gene1 = Gene(weight=1.0,
                            in_node=in_node,
                            out_node=new_node,
                            recurrence=recurrence,
                            innovation_number=innovation_number1,
                            mutation_number=0)
        
        new_gene2 = Gene(weight=old_weight,
                            in_node=new_node,
                            out_node=out_node,
                            recurrence=False,
                            innovation_number=innovation_number2,
                            mutation_number=0)
        
        return new_node, new_gene1, new_gene2
    
    def _check_innovation_identical(self, innovation: Innovation, in_node: Node,
                                    out_node: Node, the_gene: Gene) -> bool:
        """Check if the innovation already exists

        Args:
            innovation (Innovation): innovation to check for
            in_node (Node): in_node of the innovation
            out_node (Node): out_node of the innovation
            the_gene (Gene): the gene with the innovation number

        Returns:
            bool: the innovation already exist
        """        
        return (innovation.innovation_type == InnovationType.NEWNODE and 
                 innovation.node_in_id == in_node.id and
                 innovation.node_out_id == out_node.id and
                 innovation.old_innovation_number == the_gene.innovation_number)
    
    def _new_node_innovation(self, innovations: List[Innovation], current_innovation: int,
                            current_node_id: int, the_gene: Gene) -> Tuple[Node, Gene, Gene]:
        """ Check to see if this innovation has already been done in another genome

        Args:
            innovations (List[Innovation]): List of already existing innovations
            current_node_id (int): the id of the current node
            the_gene (Gene): the gene which innovation to check

        Returns:
            Tuple[Node, Gene, Gene]:    Node: the new node created
                                        Gene: the gene connecting in the new node
                                        Gene: the gene connecting out the new node
        """        
        # Extract the link
        the_link: Link = the_gene.link
        old_weight: float = the_link.weight
        
        # Extract the nodes
        in_node: Node = the_link.in_node
        out_node: Node = the_link.out_node

        recurrence = the_link.is_recurrent
        for innovation in innovations:
            # Innovation already exists    
            if self._check_innovation_identical(innovation=innovation,
                                                in_node=in_node,
                                                out_node=out_node,
                                                the_gene=the_gene):
                
                new_node, new_gene1, new_gene2 = self._create_new_node( node_id=innovation.new_node_id,
                                                                        in_node=in_node,
                                                                        out_node=out_node,
                                                                        recurrence=recurrence,
                                                                        innovation_number1=innovation.innovation_number1,
                                                                        innovation_number2=innovation.innovation_number2,
                                                                        old_weight=old_weight)
                break
            
        # If innovation is novel
        else:
            new_node, new_gene1, new_gene2 = self._create_new_node( node_id=current_node_id,
                                                                    in_node=in_node,
                                                                    out_node=out_node,
                                                                    recurrence=recurrence,
                                                                    innovation_number1=current_innovation,
                                                                    innovation_number2=current_innovation+1,
                                                                    old_weight=old_weight)

            new_innovation = Innovation(node_in_id=in_node.id,
                                        node_out_id=out_node.id,
                                        innovation_type=InnovationType.NEWNODE,
                                        innovation_number1=current_innovation-2.0,
                                        innovation_number2=current_innovation-1.0,
                                        new_node_id=new_node.id,
                                        old_innovation_number=the_gene.innovation_number)
            
            innovations.append(new_innovation)
            current_innovation += 2
                
        return  new_node, new_gene1, new_gene2
                    
    def mutate_add_node(self, innovations: List, current_node_id: int, current_innovation: int) -> bool:
        """Mutate genome by adding a node respresentation 

        Args:
            innovations (List):         list of innovations already existing
            current_node_id (int):      the id of the current node
            current_innovation (int):   current innovation number

        Returns:
            bool: mutation worked
        """        
        
        the_gene, found = self._find_random_gene()
               
        if not found:
            return False
        
        # Disabled the gene
        the_gene.enabled = False
                
        new_node, new_gene1, new_gene2 = self._new_node_innovation(innovations=innovations,
                                                                      current_innovation=current_innovation,
                                                                      current_node_id=current_node_id,
                                                                      the_gene=the_gene)
                
        self.add_gene(gene=new_gene1)
        self.add_gene(gene=new_gene2)
        self.nodes = Genome.insert_node(self.nodes, new_node)
        return True        
    
    def _find_first_sensor(self) -> Tuple[Node, int]:
        """Find the first non-sensor so that the to-node won't look at sensors as possible destinations

        Returns:
            Tuple[Node, int]:   Node:   the first non-sensor found
                                int:    the index
        """                 
        for index, node in enumerate(self.nodes):
            if not node.node_type == NodeType.SENSOR:
                return index
                    
    def _select_nodes_for_link(self,recurrence: bool, first_non_sensor: int) -> Tuple[Node,Node]:
        """ Select 2 random nodes to link together

        Args:
            loop_recurrence (bool): is a recurrent loop
            first_non_sensor (int): first index of non-sensor node

        Returns:
            Tuple[Node,Node]:   Node: the in_node of the link
                                Node: the out_node of the link
        """ 
        if recurrence:
            loop_recurrence: bool  = choice([0,1])     
            if loop_recurrence:
                node_number1 = randint(first_non_sensor, self.nodes.size - 1)
                node_number2 = node_number1
            else:
                node_number1 = randint(0, self.nodes.size - 1)
                node_number2 = randint(first_non_sensor, self.nodes.size - 1)
                
            node1 = self.nodes[node_number1]
            node2 = self.nodes[node_number2]
        else:
            nodes_size = self.nodes.size
            node1 = choice(self.nodes[0:nodes_size])
            node2 = choice(self.nodes[first_non_sensor:nodes_size])
        
        return node1, node2
    
    def _link_already_exists(self, recurrence: bool, node1: Node, node2: Node) -> bool:
        """See if a recurrent link already exists

        Args:
            recurrence (bool):  is recurrent
            node1 (Node):       in node
            node2 (Node):       out node

        Returns:
            Tuple[bool, int]:   bool: found an already existing link  
        """  
        found: bool = False 
        for the_gene in self.genes:
            if (the_gene.link.in_node == node1 and
                the_gene.link.out_node == node2 and
                the_gene.link.is_recurrent == recurrence):
                
                found = True
                break
                
        return found

    def _check_innovation_already_exists(the_innovation: Innovation, innovation_type: InnovationType,
                                         node1: Node, node2: Node, recurrence: bool) -> bool:
        """See if an innovation already exists

        Args:
            the_innovation (Innovation): _description_
            innovation_type (InnovationType): _description_
            node1 (Node): _description_
            node2 (Node): _description_
            recurrence (bool): _description_

        Returns:
            bool: _description_
        """        
        return (the_innovation.innovation_type == innovation_type and
                the_innovation.node_in_id == node1.id and
                the_innovation.node_out_id == node2.id and
                the_innovation.recurrence_flag == recurrence)
        
    def _new_link_gene(self, innovations: List[Innovation], recurrence: bool,
                       node1: Node, node2: Node, current_innovation: int) -> Gene:
        
        for the_innovation in innovations:          
            # OTHERWISE, match the innovation in the innovs list
            if Genome._check_innovation_already_exists( the_innovation=the_innovation,
                                                        innovation_type=InnovationType.NEWLINK,
                                                        node1=node1,
                                                        node2=node2,
                                                        recurrence=recurrence):
                
                new_gene = Gene(weight=the_innovation.weight,
                                in_node=node1,
                                out_node=node2,
                                recurrence=recurrence,
                                innovation_number=the_innovation.innovation_number1,
                                mutation_number=0)
                break
        else:
            # The innovation is totally novel

                # If the phenotype does not exist, exit on false,print error
                # Note: This should never happen- if it does there is a bug
                if self.phenotype == 0:
                    return False
                                        
                # Choose the new weight
                np.random.seed(1)
                new_weight = choice([-1,1]) * random() 
                # Create the new gene
                new_gene = Gene(weight=new_weight,
                                in_node=node1,
                                out_node=node2,
                                recurrence=recurrence,
                                innovation_number=current_innovation,
                                mutation_number=new_weight)
                
                # Add the innovation
                new_innovation = Innovation(node_in_id=node1.id,
                                            node_out_id=node2.id,
                                            innovation_type=InnovationType.NEWLINK,
                                            innovation_number1=current_innovation,
                                            new_weight=new_weight,
                                            )
                
                innovations.append(new_innovation)
                current_innovation += 1
                
        return new_gene
        
    
    def mutate_add_link(self, innovations: List, current_innovation: int, tries: int) -> bool:
        """Mutate the genome by adding a new link between 2 random Nodes 

        Args:
            innovations (List): _description_
            current_innovation (int): _description_
            tries (int): _description_

        Returns:
            bool: _description_
        """
        
        # Decide whether to make this recurrent
        recurrence: bool = random() < NEAT.recurrence_only_prob
        
        # Find the first non-sensor so that the to-node won't look at sensors as possible destinations
        first_non_sensor = self._find_first_sensor()

        
        for _ in range(tries + 1):
            node1, node2 = self._select_nodes_for_link( recurrence=recurrence,
                                                        first_non_sensor=first_non_sensor)
            
            found = not self._link_already_exists(  node1=node1,
                                                    node2=node2,
                                                    recurrence=True)
            if found: break
        """ else:
            # Choose random node 
            nodes_size = self.nodes.size
            # Loop to find a nonrecurrent link
            for _ in range(tries + 1):
                node1, node2 = self._select_nodes_for_link( recurrence=recurrence,
                                                            loop_recurrence=False,
                                                            first_non_sensor=first_non_sensor)
                
                found = not self._link_already_exists(  node1=node1,
                                                        node2=node2,
                                                        recurrence=False)
                if found: break """
                    
        # Continue only if an open link was found
        if found:
            new_gene = self._new_link_gene(innovations=innovations,
                                           recurrence=recurrence,
                                           node1=node1,
                                           node2=node2,
                                           current_innovation=current_innovation)
            
            self.add_gene(new_gene)
            return True
                                       
    """ def mutate_add_sensor(self, innovations: List, current_innovation: int):
        
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
                    new_weight = [-1,1][randrange(2)]*random.random() * 3.0
                    
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
                    
            self.add_gene(gene=new_gene) """
            
            
    """ def mutate_link_weights(self, power: float, rate: float) -> None:
            number: float = 0.0                 # counts gene placement
            total_genes: int = self.genes.size
            end_part: float = total_genes * 0.8 # Signifies the last part of the genome
            power_mod: float = 1.0              # Modified power by gene number The power of mutation will rise farther into the genome
                                                # on the theory that the older genes are more fit since they have stood the test of time      
            
            severe: bool = getrandbits(1) # Once in a while really shake things up
            
            #The following if determines the probabilities of doing cold gaussian
            #mutation, meaning the probability of replacing a link weight with
            #another, entirely random weight.  It is meant to bias such mutations
            #to the tail of a genome, because that is where less time-tested genes
            #reside.  The gausspoint and coldgausspoint represent values above
            #which a random float will signify that kind of mutation. 
            
            # Loop on all genes
            for current_gene in self.genes:
                # Don't mutate weights of frozen links
                if not current_gene.frozen:
                    if severe:
                        gauss_point = 0.3
                        cold_gauss_point = 0.1
                        
                    elif total_genes > 10 and number > end_part:
                        gauss_point = 0.5       # Mutate by modification % of connections
                        cold_gauss_point = 0.3  # Mutate the rest by replacement % of the time
                        
                    else:
                        # Half the time don't do any cold mutations
                        if getrandbits(1):
                            gauss_point = 1.0 - rate
                            cold_gauss_point = 1.0 - rate - 0.1
                        else:
                            gauss_point = 1.0 - rate
                            cold_gauss_point = 1.0 - rate
                            
                    random_number = choice([-1,1]) * random() * power * power_mod
                    
                    random_choice = random()
                    if random_choice > gauss_point:
                        current_gene.link.weight += random_number
                    elif random_choice > cold_gauss_point:
                        current_gene.link.weight = random_number
                    
                    # Record the innovation 
                    current_gene.mutation_number = current_gene.link.weight
                    
                    number += 1 """
    