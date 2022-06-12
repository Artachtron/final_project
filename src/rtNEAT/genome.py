from __future__ import annotations
import numpy as np
from neat import Config

from link import Link

from innovation import Innovation, InnovationType, InnovTable
from typing import List, Iterator, Tuple, Dict
from numpy.random import choice, random, uniform

from genes import LinkGene, NodeGene, BaseGene, NodeType

class Genome:
    def __init__(self,
                 genome_id: int,
                 node_genes: Dict[int, NodeGene] = {},
                 link_genes: Dict[int, LinkGene] = {}):
        
        self.id: int = genome_id
        self._node_genes: Dict[int, NodeGene] = node_genes   # List of network's nodes 
        self._link_genes: Dict[int, LinkGene] = link_genes   # List of link's genes
   
    @property
    def node_genes(self):
        return np.array(list(self._node_genes.values()))
    
    @property
    def link_genes(self):
        return np.array(list(self._link_genes.values()))
    
    @property
    def n_node_genes(self):
        return len(self._node_genes)
    
    @property
    def n_link_genes(self):
        return len(self._link_genes)
    
    @property
    def size(self):
        return {'node genes': self.n_node_genes,
                'link genes': self.n_link_genes}
      
    def add_gene(self, link: LinkGene) -> None:
        self._link_genes[link.id] = link
     
    def insert_node(self, node: NodeGene) -> None:
        self._node_genes[node.id] = node
    
    @staticmethod   
    def insert_gene_in_dict(genes_dict: Dict[int, BaseGene],
                            gene: BaseGene) -> Dict[int, BaseGene]:
        """ Insert a gene into a dictionary of genes

        Args:
            genes_dict (Dict[int, BaseGene]):   dictionary of genes to insert in
            gene (BaseGene):                        gene to insert

        Returns:
            Dict[int, BaseGene]: the final dicitonary of genes after insertion
        """        
        genes_dict[gene.id] = gene        
        return genes_dict  
      
    def create_bias_gene(self) -> NodeGene:
        return NodeGene(node_type=NodeType.BIAS)
    
    def get_link_genes(self) -> np.array[LinkGene]:
        return np.array(list(self._link_genes.values()))
    
    def get_node_genes(self) -> np.array[LinkGene]:
        return np.array(list(self._node_genes.values()))
    
    @staticmethod
    def genesis(genome_id: int, n_inputs: int, n_outputs: int):        
        """ Initialize a genome based on configuration.
            Create the input nodes, output gene nodes and
            gene links connecting each input to each output 
        """        
        # Initialize inputs
        inputs = {}
        count_node_id = 1
        for _ in range(n_inputs):
            inputs = Genome.insert_gene_in_dict(genes_dict=inputs,
                                                gene=NodeGene(node_id=count_node_id,
                                                              node_type=NodeType.INPUT))
            count_node_id += 1
     
         # Initialize bias
        bias = NodeGene(node_id=count_node_id,
                        node_type=NodeType.BIAS)  
        count_node_id += 1
                   
        # Initialize outputs    
        outputs = {}  
        for _ in range(n_outputs):
            outputs = Genome.insert_gene_in_dict(genes_dict=outputs,
                                                 gene=NodeGene(node_id=count_node_id,
                                                               node_type=NodeType.OUTPUT)) 
            count_node_id += 1
        # Connect all the inputs and bias to each output   
        genes = {}
        count_link_id = 1
        for node1 in list(inputs.values()) + [bias]:
            for node2 in outputs.values():
                genes = Genome.insert_gene_in_dict(genes_dict=genes,
                                                   gene=LinkGene(   link_id=count_link_id, 
                                                                    in_node=node1,
                                                                    out_node=node2))
                count_link_id += 1
                
        Genome.insert_gene_in_dict(genes_dict=inputs,
                                   gene=bias)
        
        InnovTable.node_number = count_node_id
        InnovTable.link_number = count_link_id
        
          
        return Genome(genome_id=genome_id,
                      node_genes=inputs|outputs,
                      link_genes=genes)
      
         
            
    def mutate(self) -> None:
        """ Mutate the genome
        """        
        if random() < Config.add_node_prob:
            self._mutate_add_node()
            
        if random() < Config.add_link_prob:
            self._mutate_add_link(tries=Config.add_link_tries)
            
        self._mutate_link_weights()
    
    @staticmethod
    def genetical_distance(genome1: Genome, genome2: Genome) -> float:
        """ Find the genetical distance between two genomes

        Args:
            genome1 (Genome): the first genome to compare compatibility
            genome1 (Genome): the second genome to compare compatibility

        Returns:
            float: genetical distance
        """        
        g1_innovation: int
        g2_innovation: int
        
        mutation_difference: float
        
        number_disjoint: int = 0
        number_excess: int = 0
        mutation_difference_total: float= 0.0
        number_matching: int = 0
        
        g1_genome = iter(genome1._link_genes)
        g2_genome = iter(genome2._link_genes)
        
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
        disjoint = Config.disjoint_coeff * (number_disjoint)
        excess =  Config.excess_coeff * (number_excess)
        if number_matching > 0:
             mutation_difference = Config.mutation_difference_coeff * (mutation_difference_total/number_matching)
        else:
            mutation_difference = 0
       
        compatibility = disjoint + excess + mutation_difference
        return compatibility
    
    def get_last_node_id(self) -> int:
        """ Return id of final Node in Genome

        Returns:
            int: last node's id
        """    
        return max(list(self._node_genes.keys())) + 1

    def get_last_gene_innovation_number(self) -> int:
        """ Return last innovation number in Genome

        Returns:
            int: last gene's innovation number
        """    
        return self._link_genes[-1].innovation_number + 1
           
    @staticmethod 
    def _is_IO_node(node: NodeGene) -> bool:
        """ Check if the node is an input or output node

        Args:
            node (Node): the node to check

        Returns:
            bool: is an input or output node
        """        
        return (node.type == NodeType.INPUT or
                node.type == NodeType.BIAS or
                node.type == NodeType.OUTPUT)
    
    @staticmethod
    def _choose_gene_to_transmit(   parent1_gene: LinkGene, parent2_gene: LinkGene, parent1_genes: Iterator,
                                    parent2_genes: Iterator, p1_dominant: bool
                                ) -> Tuple[LinkGene, bool, bool, LinkGene, LinkGene, Iterator, Iterator]:
        """Choose the gene to transmit to offspring

        Args:
            parent1_gene (LinkGene):        the gene from the first genome
            parent2_gene (LinkGene):        the gene from the second genome
            parent1_genes (Iterator):   the iterator of genes from first genome
            parent2_genes (Iterator):   the iterator of genes from second genome
            parent1_dominant (bool):    the first genome is the dominant one

        Returns:
            Tuple[LinkGene, bool, bool, 
            LinkGene, LinkGene, Iterator, Iterator]:    
                                            LinkGene: the chosen gene that will be transmitted
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
    def _check_gene_conflict(new_genes: List[LinkGene],
                             chosen_gene: LinkGene) -> bool:
        """ Check to see if the chosengene conflicts with an already chosen gene
            i.e. do they represent the same link

        Args:
            new_genes (List[LinkGene]): the list of genes to check for conflicts
            chosen_gene (LinkGene):     the chosen gene that should not conflict with existing ones

        Returns:
           bool: a conflict was detected 
        """        
        for current_gene in new_genes:
            if not( not(current_gene.link.in_node.id == chosen_gene.link.in_node.id and 
                        current_gene.link.out_node.id == chosen_gene.link.out_node.id and
                        current_gene.link.is_recurrent == chosen_gene.link.is_recurrent) and
                    not(current_gene.link.in_node.id == chosen_gene.link.out_node.id and
                        current_gene.link.out_node.id == chosen_gene.link.in_node.id and
                        current_gene.link.is_recurrent == chosen_gene.link.is_reccurent) and
                    not (chosen_gene.link.is_recurrent)):
                
                return True
        
        return False
    
    @staticmethod
    def _check_new_node_existence(new_nodes: Dict[int, NodeGene], target_node: NodeGene) -> Tuple[NodeGene, List[NodeGene]]:
        """ Find if the target node already exists in the new nodes list return the final list and new node

        Args:
            new_nodes Dict[int, Node]: the list of nodes already added
            target_node (Node): the node to check existence in the list

        Returns:
            Tuple[Node, List[Node]]:    Node: the new node, either an existing node or a created one
                                        List[Node]: the final list of nodes (updated if new node wasn't already in it)
        """                
                       
        if target_node.id in new_nodes:
            new_node = new_nodes[target_node.id]
            
        else:
            new_node = NodeGene.constructor_from_node(target_node)
            new_nodes = Genome.insert_gene_in_dict( genes_dict=new_nodes,
                                                    gene=new_node)
            
        return new_node, new_nodes
    
    @staticmethod
    def mate_multipoint(parent1: Genome, parent2: Genome, genome_id: int,) -> Genome:
        """mates this Genome with another Genome  
		   For every point in each Genome, where each Genome shares
		   the innovation number, the LinkGene is chosen randomly from 
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
                
        new_nodes = {}    # already added nodes
        parent1_dominant: bool = choice([0,1])  # Determine which genome will give its excess genes
        
        new_genes: List[LinkGene] = [] # already chosen genes
        
        # Make sure all sensors and outputs are included
        for current_node in parent2._node_genes.values():
            if(Genome._is_IO_node(current_node)):
                
                # Create a new node off the sensor or output
                new_output_node = NodeGene.constructor_from_node(current_node)
                
                # Add the new node
                new_nodes = Genome.insert_gene_in_dict(genes_dict=new_nodes,
                                               gene=new_output_node)
          
        # Now move through the Genes of each parent until both genomes end  
        parent1_genes = iter(parent1._link_genes)
        parent2_genes =iter(parent2._link_genes)
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
                    new_out_node, new_nodes = Genome._check_new_node_existence( new_nodes=new_nodes,
                                                                                target_node=out_node)
                        
                    new_in_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                              target_node=in_node)
                
                # Add gene        
                new_gene = LinkGene.constructor_from_gene(gene=chosen_gene,
                                                      in_node=new_in_node,
                                                      out_node=new_out_node)
                if disable:
                    new_gene.enabled = False
                    disable = False
                    
                new_genes.append(new_gene)
        
        baby_genome = Genome(   genome_id=genome_id,
                                node_genes=new_nodes,
                                link_genes=np.array(new_genes))
        
        return baby_genome
    
    def _create_new_link(self, gene: LinkGene) -> Link:
        """ Create a new link from a gene's link

        Args:
            gene (LinkGene): gene from which to get link's information

        Returns:
            Link: the created link
        """        
        current_link = gene.link
        in_node = current_link.in_node
        out_node = current_link.out_node
        
        """ new_link = Link(weight=current_link.weight,
                        in_node=in_node,
                        out_node=out_node,
                        recurrence=current_link.is_recurrent) """
                        
        out_node.incoming.append(current_link)
        in_node.outgoing.append(current_link)
        
        return current_link
           
    
    
    
    def _mutate_link_weights(self) -> None:
        """Simplified mutate link weight method
        """        
        for current_gene in self._link_genes:
            if current_gene.frozen:
                continue
            
            if random() < Config.weight_mutate_prob:
                if random() < Config.new_link_prob:
                    current_gene.link.weight = uniform(-1,1)
                else:
                    current_gene.link.weight += uniform(-1,1) * Config.weight_mutate_power 
                    
        # Record the innovation 
        current_gene.mutation_number = current_gene.link.weight
                         
    def _find_random_gene(self, tries:int = 20) -> Tuple[LinkGene, bool]:
        """ Find a random gene containing a node to mutate

        Returns:
            Tuple[LinkGene, bool]:  LinkGene: gene containing the node to mutate
                                bool: gene was found
        """     
                  
        try_count: int = 0      # number of attempt already made
        found: bool = False     # a valid gene was found
        the_gene: LinkGene = None   # the found gene
        
        while try_count < tries and not found:
            for gene in self._link_genes:
                if gene.enabled and gene.link.in_node.type != NodeType.BIAS:
                    found = True
                    the_gene = gene
                    
            try_count += 1
        
        return the_gene, found
    
    def _create_node(self, node_id: int, in_node: NodeGene, out_node: NodeGene, recurrence: bool,
                         innovation_number1: int, innovation_number2: int, old_weight: int
                         ) -> Tuple[NodeGene, LinkGene, LinkGene]:
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
            Tuple[Node, LinkGene, LinkGene]:    Node: the new node created
                                        LinkGene: the gene connecting in the new node
                                        LinkGene: the gene connecting out the new node
        """        
        new_node = NodeGene(node_id=node_id,
                        node_type=NodeType.HIDDEN)
                
        new_gene1 = LinkGene(link_id=innovation_number1,
                            weight=1.0,
                            in_node=in_node,
                            out_node=new_node,
                            recurrence=recurrence,
                            mutation_number=0)
        
        new_gene2 = LinkGene(link_id=innovation_number2,
                            weight=old_weight,
                            in_node=new_node,
                            out_node=out_node,
                            recurrence=False,
                            mutation_number=0)
        
        return new_node, new_gene1, new_gene2
    
    def _check_innovation_identical(self, innovation: Innovation, in_node: NodeGene,
                                    out_node: NodeGene, the_gene: LinkGene) -> bool:
        """Check if the innovation already exists

        Args:
            innovation (Innovation):    innovation to check for
            in_node (Node):             incoming node of the innovation
            out_node (Node):            outgoing node of the innovation
            the_gene (LinkGene):            the gene with the innovation number

        Returns:
            bool: the innovation already exist
        """        
        return (innovation.innovation_type == InnovationType.NEW_NODE and 
                 innovation.node_in_id == in_node.id and
                 innovation.node_out_id == out_node.id and
                 innovation.old_innovation_number == the_gene.innovation_number)
    
    def _new_node_innovation(self, the_gene: LinkGene) -> Tuple[NodeGene, LinkGene, LinkGene]:
        """ Check to see if this innovation has already been done in another genome

        Args:
            the_gene (LinkGene): the gene which innovation to check

        Returns:
            Tuple[Node, LinkGene, LinkGene]:    Node: the new node created
                                        LinkGene: the gene connecting in the new node
                                        LinkGene: the gene connecting out the new node
        """        
        # Extract the link
        the_link: Link = the_gene.link
        old_weight: float = the_link.weight
        
        # Extract the nodes
        in_node: NodeGene = the_link.in_node
        out_node: NodeGene = the_link.out_node

        recurrence = the_link.is_recurrent
        
        the_innovation = InnovTable.get_innovation( in_node=in_node,
                                                    out_node=out_node,
                                                    innovation_type=InnovationType.NEW_NODE,
                                                    recurrence=recurrence,
                                                    old_innovation_number=the_gene.innovation_number)
     
        new_node, new_gene1, new_gene2 = self._create_node( node_id=the_innovation.new_node_id,
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
        self._node_genes = Genome.insert_gene_in_dict(self._node_genes, new_node)
        return True  
                    
    def _select_nodes_for_link(self,recurrence: bool) -> Tuple[NodeGene,NodeGene]:
        """ Select 2 random nodes to link together

        Args:
            loop_recurrence (bool): is a recurrent loop

        Returns:
            Tuple[Node,Node]:   Node: the in_node of the link
                                Node: the out_node of the link
        """ 
        inputs = self.phenotype.inputs
        neurons = self.phenotype.hidden + self.phenotype.outputs
        if recurrence:
            loop_recurrence: bool  = choice([0,1])     
            if loop_recurrence:
                node1 = choice(neurons)
                node2 = node1
            else:
                node1 = choice(inputs+neurons)
                node2 = choice(neurons)

        else:
            node1 = choice(inputs+neurons)
            node2 = choice(neurons)
        
        return node1, node2
    
    def _link_already_exists(self, recurrence: bool, node1: NodeGene, node2: NodeGene) -> bool:
        """See if a recurrent link already exists

        Args:
            recurrence (bool):  is recurrent
            node1 (Node):       in node
            node2 (Node):       out node

        Returns:
            Tuple[bool, int]:   bool: found an already existing link  
        """  
        found: bool = False 
        for the_gene in self._link_genes:
            if (the_gene.link.in_node == node1 and
                the_gene.link.out_node == node2 and
                the_gene.link.is_recurrent == recurrence):
                
                found = True
                break
                
        return found

    def _new_link_gene(self, recurrence: bool, in_node: NodeGene, out_node: NodeGene) -> LinkGene:
        """ Create a new gene representing a link between two nodes, and return this gene

        Args:
            recurrence (bool):  recurrence flag
            in_node (Node):     incoming node
            out_node (Node):    outgoing node

        Returns:
            LinkGene: the newly created gene
        """        
        
        the_innovation = InnovTable.get_innovation( in_node=in_node,
                                                    out_node=out_node,
                                                    innovation_type=InnovationType.NEW_LINK,
                                                    recurrence=recurrence)
            
        new_gene = LinkGene(weight=the_innovation.weight,
                        in_node=in_node,
                        out_node=out_node,
                        recurrence=recurrence,
                        innovation_number=the_innovation.innovation_number1,
                        mutation_number=0)
                    
        return new_gene
      
    def _find_valid_link(self, tries:int, recurrence: bool) -> Tuple[bool, NodeGene, NodeGene]: 
        """ Find a valid open link to add a new link after mutation

        Args:
            tries (int): Number of tries before giving up

        Returns:
            Tuple[bool, Node, Node]:    bool: An open link was found
                                        Node: the first node of the link
                                        Node: the second node of the link
        """        
        
        for _ in range(tries + 1):
            # Select two nodes at random
            node1, node2 = self._select_nodes_for_link( recurrence=recurrence)
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
        recurrence: bool = random() < Config.recurrence_only_prob
        
        # Find an open link
        found, node1, node2 = self._find_valid_link(tries=tries,
                                                    recurrence=recurrence)
                    
        # Continue only if an open link was found
        if found:
            new_gene = self._new_link_gene(recurrence=recurrence,
                                           in_node=node1,
                                           out_node=node2)
            self.add_gene(new_gene)
            return True
                                       
    def _get_input_links(self, node_id: int) -> List[Link]:
        """ get all the links that connects to the node and return the list

        Args:
            node_id (int): id of the node

        Returns:
            List[Link]: the list of links connecting to the node
        """        
        return [gene.link for gene in self._link_genes if gene.link.out_node.id == node_id]
                               
    
