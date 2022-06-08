from __future__ import annotations
import numpy as np
from neat import config
from node import Node, NodePlace
from link import Link
from gene import Gene
from innovation import Innovation, InnovationType, InnovTable
from network import Network
from typing import List, Iterator, Tuple
from numpy.random import choice, randint, random, uniform

class Genome:
    def __init__(self,
                 genome_id: int,
                 nodes: np.array = None,
                 genes: np.array = None):
        
        self.id: int = genome_id
        self.nodes: np.array = nodes   # List of network's nodes 
        self.genes: np.array = genes   # List of link's genes
        
        if genes is not None:
            self.size = len(genes)
        self.phenotype = None          # Node network associated with the genome
    
        if self.nodes is None:
            self._genesis()
        
    
    def _genesis(self):
        # Initialize input
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
            self.nodes = np.array(bias + inputs + outputs)
        
        genes = []
        for node1 in inputs + bias:
            for node2 in outputs:
                genes.append(Gene(  in_node=node1,
                                    out_node=node2,
                                    innovation_number=InnovTable.get_innovation_number()))

                InnovTable.increment_innov()
        else:
            self.genes = np.array(genes)
                
        # Create the new network        
        new_network = Network(inputs=bias+inputs,
                              outputs=outputs,
                              all_nodes=bias+inputs+outputs,
                              network_id=self.id)
            
        # Attach genotype and phenotype together
        new_network.genotype = self
        self.phenotype = new_network
        
        return new_network       
   
    def mutate(self) -> None:
        """ Mutate the genome
        """        
        if random() < config.add_node_prob:
            self._mutate_add_node()
            
        if random() < config.add_link_prob:
            self._mutate_add_link(tries=config.add_link_tries)
            
        self._mutate_link_weights()
    
    @staticmethod
    def compatibility(genome1: Genome, genome2: Genome) -> float:
        """ Find the compatibility score between two genomes

        Args:
            genome1 (Genome): the first genome to compare compatibility
            genome1 (Genome): the second genome to compare compatibility

        Returns:
            float: compatibility score
        """        
        g1_innovation: int
        g2_innovation: int
        
        mutation_difference: float
        
        number_disjoint: int = 0
        number_excess: int = 0
        mutation_difference_total: float= 0.0
        number_matching: int = 0
        
        g1_genome = iter(genome1.genes)
        g2_genome = iter(genome2.genes)
        
        g1_gene = next(g1_genome)
        g2_gene = next(g2_genome)
        
        while g1_gene or g2_gene:
            # Excess genes
            if not g1_gene:
                g2_gene = next(g2_genome, None)
                number_excess += 1
            elif not g2_gene:
                g1_gene = next(g1_genome, None)
                number_excess += 1
            
            # Non excess genes, we must compare innovation numbers
            else:
                g1_innovation = g1_gene.innovation_number
                g2_innovation = g2_gene.innovation_number
                
                # Matching genes
                if(g1_innovation == g2_innovation):
                    number_matching += 1
                    mutation_difference = abs(g1_gene.mutation_number - g2_gene.mutation_number)
                    mutation_difference_total += mutation_difference
                    g1_gene = next(g1_genome, None)
                    g2_gene = next(g2_genome, None)
                 
                # disjoint genes   
                elif g1_innovation < g2_innovation:
                    g1_gene = next(g1_genome, None)
                    number_disjoint += 1
                    
                elif g2_innovation < g1_innovation:
                    g2_gene = next(g2_genome, None)
                    number_disjoint += 1

        # Compatibility score calculations
        disjoint = config.disjoint_coeff * (number_disjoint)
        excess =  config.excess_coeff * (number_excess)
        if number_matching > 0:
             mutation_difference = config.mutation_difference_coeff * (mutation_difference_total/number_matching)
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
     
    @staticmethod   
    def insert_node(nodes_list: np.array,
                    node: Node) -> np.array:
        """ Insert a node into a list of nodes

        Args:
            nodes_list (np.array):  the list of nodes to insert in
            node (Node):            the node to insert

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
     
    @staticmethod 
    def _is_IO_node(node: Node) -> bool:
        """ Check if the node is an input or output node

        Args:
            node (Node): the node to check

        Returns:
            bool: is an input or output node
        """        
        return (node.node_place == NodePlace.INPUT or
               node.node_place == NodePlace.BIAS or
               node.node_place == NodePlace.OUTPUT)
    
    @staticmethod
    def _choose_gene_to_transmit(   parent1_gene: Gene, parent2_gene: Gene, parent1_genes: Iterator,
                                    parent2_genes: Iterator, p1_dominant: bool
                                ) -> Tuple[Gene, bool, bool, Gene, Gene, Iterator, Iterator]:
        """Choose the gene to transmit to offspring

        Args:
            parent1_gene (Gene):        the gene from the first genome
            parent2_gene (Gene):        the gene from the second genome
            parent1_genes (Iterator):   the iterator of genes from first genome
            parent2_genes (Iterator):   the iterator of genes from second genome
            parent1_dominant (bool):    the first genome is the dominant one

        Returns:
            Tuple[Gene, bool, bool, 
            Gene, Gene, Iterator, Iterator]:    
                                            Gene: the chosen gene that will be transmitted
                                            bool: the gene must be skipped
                                            bool: the gene must be disabled
                                            ... : args for the next iteration
                                        
        """        
        disable: bool = False   # if the gene must be disabled
        skip: bool = False      # if the gene must be skipped and not transmitted
        
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
    
    @staticmethod   
    def _check_gene_conflict(new_genes: List[Gene],
                             chosen_gene: Gene) -> bool:
        """ Check to see if the chosengene conflicts with an already chosen gene
            i.e. do they represent the same link

        Args:
            new_genes (List[Gene]): the list of genes to check for conflicts
            chosen_gene (Gene):     the chosen gene that should not conflict with existing ones

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
    
    @staticmethod
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
    
    @staticmethod
    def mate_multipoint(parent1, parent2: Genome, genome_id: int,) -> Genome:
        """mates this Genome with another Genome  
		   For every point in each Genome, where each Genome shares
		   the innovation number, the Gene is chosen randomly from 
		   either parent.  If one parent has an innovation absent in 
		   the other, the baby will inherit the innovation 
		   Otherwise, excess genes come from the dominant parent.

        Args:
            parent1 (Genome): genome of the first parent
            parent2 (Genome): genome of the second parent
            genome_id (int): id of the child genome

        Returns:
            Genome: the child genome created
        """        
                
        new_nodes = np.array([], dtype=Node) # already added nodes
        parent1_dominant: bool = choice([0,1]) # Determine which genome will give its excess genes
        
        new_genes: List[Gene] = [] # already chosen genes
        
        # Make sure all sensors and outputs are included
        for current_node in parent2.nodes:
            if(Genome._is_IO_node(current_node)):
                
                # Create a new node off the sensor or output
                new_output_node = Node.constructor_from_node(current_node)
                
                # Add the new node
                new_nodes = Genome.insert_node(nodes_list=new_nodes, node=new_output_node)
          
        # Now move through the Genes of each parent until both genomes end  
        parent1_genes = iter(parent1.genes)
        parent2_genes =iter(parent2.genes)
        parent1_gene = next(parent1_genes, None)
        parent2_gene = next(parent2_genes, None)
        args = (parent1_gene, parent2_gene, parent1_genes, parent2_genes)
        while parent1_gene or parent2_gene:
         
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(*args,
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
           
    """ def genesis(self, network_id: int) -> Network:
        Generate a network phenotype from this Genome with specified id

        Args:
            id (int): id of the network
            
        Returns:
            Network: the network created as phenotype
          
        
        max_weight:float = 0.0
       
        inlist: List[Node] = []
        outlist: List[Node] = []
        all_list: List[Node] = []
                
        for current_node in self.nodes:
            new_node = Node.constructor_from_node(node=current_node)
            
            # Check for input or output designation of node
            match current_node.node_place:
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
        
        return new_network """
    
    def _mutate_link_weights(self) -> None:
        """Simplified mutate link weight method
        """        
        for current_gene in self.genes:
            if current_gene.frozen:
                continue
            
            if random() < config.weight_mutate_prob:
                if random() < config.new_link_prob:
                    current_gene.link.weight = uniform(-1,1)
                else:
                    current_gene.link.weight += uniform(-1,1) * config.weight_mutate_power 
                    
        # Record the innovation 
        current_gene.mutation_number = current_gene.link.weight
                         
    def _find_random_gene(self, tries:int = 20) -> Tuple[Gene, bool]:
        """ Find a random gene containing a node to mutate

        Returns:
            Tuple[Gene, bool]:  Gene: gene containing the node to mutate
                                bool: gene was found
        """     
                  
        try_count: int = 0      # number of attempt already made
        found: bool = False     # a valid gene was found
        the_gene: Gene = None   # the found gene
        
        while try_count < tries and not found:
            for gene in self.genes:
                if gene.enabled and gene.link.in_node.node_place != NodePlace.BIAS:
                    found = True
                    the_gene = gene
                    
            try_count += 1
        
        return the_gene, found
    
    def _create_new_node(self, node_id: int, in_node: Node, out_node: Node, recurrence: bool,
                         innovation_number1: int, innovation_number2: int, old_weight: int
                         ) -> Tuple[Node, Gene, Gene]:
        """Create the new node and two genes connecting this node in and out

        Args:
            node_id (int):              node's id
            in_node (Node):             incoming node
            out_node (Node):            outgoing node
            recurrence (bool):          recurrence flag
            innovation_number1 (int):   incoming link's innovation number
            innovation_number2 (int):   outgoing link's innovation number'
            old_weight (int):           weight of the disabled old link

        Returns:
            Tuple[Node, Gene, Gene]:    Node: the new node created
                                        Gene: the gene connecting in the new node
                                        Gene: the gene connecting out the new node
        """        
        new_node = Node(node_id=node_id,
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
            innovation (Innovation):    innovation to check for
            in_node (Node):             incoming node of the innovation
            out_node (Node):            outgoing node of the innovation
            the_gene (Gene):            the gene with the innovation number

        Returns:
            bool: the innovation already exist
        """        
        return (innovation.innovation_type == InnovationType.NEW_NODE and 
                 innovation.node_in_id == in_node.id and
                 innovation.node_out_id == out_node.id and
                 innovation.old_innovation_number == the_gene.innovation_number)
    
    def _new_node_innovation(self, the_gene: Gene) -> Tuple[Node, Gene, Gene]:
        """ Check to see if this innovation has already been done in another genome

        Args:
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
        
        the_innovation = InnovTable.get_innovation( node_in=in_node,
                                                    node_out=out_node,
                                                    innovation_type=InnovationType.NEW_NODE,
                                                    recurrence=recurrence,
                                                    old_innovation_number=the_gene.innovation_number)
     
        new_node, new_gene1, new_gene2 = self._create_new_node( node_id=the_innovation.new_node_id,
                                                                in_node=in_node,
                                                                out_node=out_node,
                                                                recurrence=recurrence,
                                                                innovation_number1=the_innovation.innovation_number1,
                                                                innovation_number2=the_innovation.innovation_number2,
                                                                old_weight=old_weight)
        
                
        return  new_node, new_gene1, new_gene2
                    
    def _mutate_add_node(self) -> bool:
        """Mutate genome by adding a node representation 

        Returns:
            bool: mutation worked
        """        
        the_gene, found = self._find_random_gene()
               
        if not found:
            return False
        
        # Disabled the gene
        the_gene.enabled = False
                
        new_node, new_gene1, new_gene2 = self._new_node_innovation(the_gene=the_gene)
                
        self.add_gene(gene=new_gene1)
        self.add_gene(gene=new_gene2)
        self.nodes = Genome.insert_node(self.nodes, new_node)
        return True  
          
    
    def _find_first_non_sensor(self) -> Tuple[Node, int]:
        """Find the first non-sensor so that the to-node won't look at sensors as possible destinations

        Returns:
            Tuple[Node, int]:   Node:   the first non-sensor found
                                int:    the index
        """                 
        for index, node in enumerate(self.nodes):
            if not node.is_sensor():
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
                node_number1 = randint(first_non_sensor, self.nodes.size)
                node_number2 = node_number1
            else:
                node_number1 = randint(0, self.nodes.size)
                node_number2 = randint(first_non_sensor, self.nodes.size)
                
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

    def _new_link_gene(self, recurrence: bool, node_in: Node, node_out: Node) -> Gene:
        """ Create a new gene representing a link between two nodes, and return this gene

        Args:
            recurrence (bool):  recurrence flag
            node_in (Node):     incoming node
            node_out (Node):    outgoing node

        Returns:
            Gene: the newly created gene
        """        
        
        the_innovation = InnovTable.get_innovation(node_in=node_in,
                                                    node_out=node_out,
                                                    innovation_type=InnovationType.NEW_LINK,
                                                    recurrence=recurrence)
            
        new_gene = Gene(weight=the_innovation.weight,
                        in_node=node_in,
                        out_node=node_out,
                        recurrence=recurrence,
                        innovation_number=the_innovation.innovation_number1,
                        mutation_number=0)
                    
        return new_gene
      
    def _find_valid_link(self, tries:int, recurrence: bool) -> Tuple[bool, Node, Node]: 
        """ Find a valid open link to add a new link after mutation

        Args:
            tries (int): Number of tries before giving up

        Returns:
            Tuple[bool, Node, Node]:    bool: An open link was found
                                        Node: the first node of the link
                                        Node: the second node of the link
        """        

        # Find the first non-sensor so that the to-node won't look at sensors as possible destinations
        first_non_sensor = self._find_first_non_sensor()
        
        for _ in range(tries + 1):
            # Select two nodes at random
            node1, node2 = self._select_nodes_for_link( recurrence=recurrence,
                                                        first_non_sensor=first_non_sensor)
            # Search for open link between the two nodes
            found: bool = not self._link_already_exists(node1=node1,
                                                        node2=node2,
                                                        recurrence=True)
            if found: 
                return found, node1, node2
            
            
            
    def _mutate_add_link(self, tries: int) -> bool:
        """Mutate the genome by adding a new link between 2 random Nodes 

        Args:
            tries (int):                Amount of tries before giving up

        Returns:
            bool: Successful mutation
        """
         # Decide whether to make this recurrent
        recurrence: bool = random() < config.recurrence_only_prob
        
        # Find an open link
        found, node1, node2 = self._find_valid_link(tries=tries,
                                                    recurrence=recurrence)
                    
        # Continue only if an open link was found
        if found:
            new_gene = self._new_link_gene(recurrence=recurrence,
                                           node_in=node1,
                                           node_out=node2)
            self.add_gene(new_gene)
            return True
                                       
    """ def mutate_add_sensor(self, innovations: List, current_innovation: int):
        
        # Find all the sensors and outputs
        sensors = []
        outputs = []
        for node in self.nodes:
            if node.node_type == NodeType.SENSOR:
                sensors.append(node)
            elif node.node_place == NodeType.OUTPUT:
                outputs.append(node)
        
        # eliminate from contention any sensors that are already connected
        for sensor in sensors:
            outputConnections = 0
            
            for gene in self.genes:
                if gene.link.out_node.node_place == NodeType.OUTPUT:
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
    