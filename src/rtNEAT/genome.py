from __future__ import annotations
import numpy as np
from neat import Config

from innovation import InnovationType, InnovTable
from typing import List, Tuple, Dict, Set
from numpy.random import choice, random

from genes import LinkGene, NodeGene, BaseGene, NodeType

Config.configure()

class Genome:
    def __init__(self,
                 genome_id: int,
                 node_genes: Dict[int, NodeGene] = {},
                 link_genes: Dict[int, LinkGene] = {}):
        
        self.id: int = genome_id
        self._node_genes: Dict[int, NodeGene] = node_genes   # List of network's nodes 
        self._link_genes: Dict[int, LinkGene] = link_genes   # List of link's genes
     
    
    @property
    def node_genes(self) -> Set[NodeGene]:
        return set(self._node_genes.values())
    
    @property
    def link_genes(self) -> Set[LinkGene]:
        return set(self._link_genes.values())
    
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
      
    def add_link(self, link: LinkGene) -> None:
        self._link_genes[link.id] = link
     
    def add_node(self, node: NodeGene) -> None:
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
     
        # Initialize outputs    
        outputs = {}  
        for _ in range(n_outputs):
            outputs = Genome.insert_gene_in_dict(genes_dict=outputs,
                                                 gene=NodeGene(node_id=count_node_id,
                                                               node_type=NodeType.OUTPUT)) 
            count_node_id += 1
        # Connect each input to each output   
        genes = {}
        count_link_id = 1
        for node1 in list(inputs.values()):
            for node2 in outputs.values():
                genes = Genome.insert_gene_in_dict(genes_dict=genes,
                                                   gene=LinkGene(   link_id=count_link_id, 
                                                                    in_node=node1,
                                                                    out_node=node2))
                count_link_id += 1
                        
        InnovTable.node_number = count_node_id
        InnovTable.node_number = count_link_id
        
        return Genome(genome_id=genome_id,
                      node_genes=inputs|outputs,
                      link_genes=genes)
    
    @staticmethod
    def genetical_distance(genome1: Genome, genome2: Genome) -> float:
        node_distance = Genome._genetical_gene_distance(gene_dict1 = genome1._node_genes,
                                                        gene_dict2 = genome2._node_genes)
        
        link_distance = Genome._genetical_gene_distance(gene_dict1 = genome1._link_genes,
                                                        gene_dict2 = genome2._link_genes)
        
        return node_distance + link_distance
        
    @staticmethod
    def _genetical_gene_distance(gene_dict1: Dict[int, BaseGene],
                                 gene_dict2: Dict[int, BaseGene]) -> float:
        
        max_g1: int = max(gene_dict1.keys())
        max_g2: int = max(gene_dict2.keys()) 
        
        if max_g1 > max_g2:
           big_genome, small_genome = gene_dict1, gene_dict2
        else:
            small_genome, big_genome = gene_dict1, gene_dict2
            
        excess_threshold: int = min(max_g1, max_g2)
        num_excess: int = 0
        num_disjoint: int = 0
        num_matching: int = 1
        mutation_difference: float = 0.0
        
        for node_id, gene_node in big_genome.items():
            if node_id > excess_threshold:
                num_excess += 1
            elif node_id not in small_genome:
                num_disjoint += 1
            else:
                num_matching += 1
                other_node = small_genome[node_id]
                mutation_difference += gene_node.mutation_distance(other_gene=other_node)
                
        node_distance: float = (num_excess * Config.excess_coeff + 
                                num_disjoint * Config.disjoint_coeff+
                                Config.mutation_difference_coeff * mutation_difference/num_matching)
        
        return node_distance
    
    def mutate(self) -> None:
        """ Mutate the genome
        """        
        if random() < Config.add_node_prob:
            self._mutate_add_node()
            
        if random() < Config.add_link_prob:
            self._mutate_add_link(tries=Config.add_link_tries)
            
        self._mutate_link_weights() 
        
    def _find_random_link(self) -> LinkGene:
        """ Find a random link gene containing a node to mutate

        Returns:
            LinkGene:  LinkGene: link gene containing the node to mutate
                                
        """     
        enabled_links = [link for link in self.link_genes if link.enabled]
        
        if enabled_links:
            return choice(enabled_links)
        
        else:
            return None    
    
    def _create_node(self, node_id: int, in_node: NodeGene, out_node: NodeGene,
                         innovation_number1: int, innovation_number2: int,
                         old_weight: int) -> Tuple[NodeGene, LinkGene, LinkGene]:
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
                
        new_link1 = LinkGene(link_id=innovation_number1,
                            weight=1.0,
                            in_node=in_node,
                            out_node=new_node,
                            mutation_number=0)
        
        new_link2 = LinkGene(link_id=innovation_number2,
                            weight=old_weight,
                            in_node=new_node,
                            out_node=out_node,
                            mutation_number=0)
        
        return new_node, new_link1, new_link2
    
    def _new_node_innovation(self, old_link: LinkGene) -> Tuple[NodeGene, LinkGene, LinkGene]:
        """ Check to see if this innovation has already been done in another genome

        Args:
            the_gene (LinkGene): the gene which innovation to check

        Returns:
            Tuple[Node, LinkGene, LinkGene]:    Node: the new node created
                                        LinkGene: the gene connecting in the new node
                                        LinkGene: the gene connecting out the new node
        """        
        # Extract the link
        old_weight: float = old_link.weight
        
        # Extract the nodes
        in_node: NodeGene = old_link.in_node
        out_node: NodeGene = old_link.out_node
        
        the_innovation = InnovTable.get_innovation( in_node=in_node,
                                                    out_node=out_node,
                                                    innovation_type=InnovationType.NEW_NODE,
                                                    old_innovation_number=old_link.id)
     
        new_node, new_link1, new_link2 = self._create_node( node_id=the_innovation.new_node_id,
                                                            in_node=in_node,
                                                            out_node=out_node,
                                                            innovation_number1=the_innovation.innovation_number1,
                                                            innovation_number2=the_innovation.innovation_number2,
                                                            old_weight=old_weight)
        
        return  new_node, new_link1, new_link2
                    
    def _mutate_add_node(self) -> bool:
        """Mutate genome by adding a node representation 

        Returns:
            bool: mutation worked
        """        
        link = self._find_random_link()
               
        if not link:
            return
        
        # Disabled the gene
        link.enabled = False
                
        new_node, new_link1, new_link2 = self._new_node_innovation(old_link=link)
                
        self.add_link(link=new_link1)
        self.add_link(link=new_link2)
        self.add_node(node=new_node)
        return True   
    
    def _mutate_link_weights(self) -> None:
        """Simplified mutate link weight method
        """        
        for current_link in self.link_genes:
            if random() < Config.weight_mutate_prob:                
                current_link.mutate()           
                        
    
    def _link_already_exists(self, node1: NodeGene, node2: NodeGene) -> bool:
        """See if a recurrent link already exists

        Args:
            recurrence (bool):  is recurrent
            node1 (Node):       in node
            node2 (Node):       out node

        Returns:
            Tuple[bool, int]:   bool: found an already existing link  
        """  
        found: bool = False 
        for link in self.link_genes:
            if (link.in_node == node1 and
                link.out_node == node2):
                
                found = True
                break
                
        return found
    
    def _new_link_gene(self, in_node: NodeGene, out_node: NodeGene) -> LinkGene:
        """ Create a new gene representing a link between two nodes, and return this gene

        Args:
            recurrence (bool):  recurrence flag
            in_node (Node):     incoming node
            out_node (Node):    outgoing node

        Returns:
            LinkGene: the newly created gene
        """        
        new_gene = None
        
        the_innovation = InnovTable.get_innovation( in_node=in_node,
                                                    out_node=out_node,
                                                    innovation_type=InnovationType.NEW_LINK)
            
        new_gene = LinkGene(weight=the_innovation.weight,
                            in_node=in_node,
                            out_node=out_node,
                            link_id=the_innovation.innovation_number1,
                            mutation_number=0)
                    
        return new_gene
      
    def _is_valid_link(self, node_in: NodeGene, node_out: NodeGene) -> bool:
        if node_in == node_out:
            return False
        
        if (node_in.type.name == NodeType.OUTPUT.name or
            node_out.type.name == NodeType.INPUT.name):
            return False
        
        return True  
      
    def _find_valid_link(self, tries: int=20) -> Tuple[NodeGene, NodeGene]: 
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
            node1, node2 = choice(tuple(self.node_genes), 2)
            
            if not self._is_valid_link( node_in=node1,
                                        node_out=node2):
                continue
            
            # Search for open link between the two nodes
            if not self._link_already_exists(node1=node1,
                                             node2=node2):
                return node1, node2
            
        return None, None
                      
    def _mutate_add_link(self, tries: int=20) -> bool:
        """Mutate the genome by adding a new link between 2 random Nodes 

        Args:
            tries (int):                Amount of tries before giving up

        Returns:
            bool: Successful mutation
        """       
        # Find an open link
        node1, node2 = self._find_valid_link(tries=tries)
                    
        # Continue only if an open link was found
        if node1:
            new_link = self._new_link_gene(in_node=node1,
                                           out_node=node2)
            self.add_link(new_link)
            return True
        
        else:
            return False
                                               
    def _get_input_links(self, node_id: int) -> List[Link]:
        """ get all the links that connects to the node and return the list

        Args:
            node_id (int): id of the node

        Returns:
            List[Link]: the list of links connecting to the node
        """        
        return [gene.link for gene in self._link_genes if gene.link.out_node.id == node_id]
    
            
    def get_last_node_id(self) -> int:
        """ Return id of final Node in Genome

        Returns:
            int: last node's id
        """    
        return max(list(self._node_genes.keys()))

    def get_last_link_id(self) -> int:
        """ Return last innovation number in Genome

        Returns:
            int: last gene's innovation number
        """    
        return max(list(self._link_genes.keys()))
           
    @staticmethod 
    def _is_IO_node(node: NodeGene) -> bool:
        """ Check if the node is an input or output node

        Args:
            node (Node): the node to check

        Returns:
            bool: is an input or output node
        """        
        return node.type.name in {"INPUT", "OUTPUT", "BIAS"}
    
                
    @staticmethod
    def _check_gene_conflict(chosen_genes: Dict[int, BaseGene],
                             chosen_gene: BaseGene) -> bool:
        
        for gene in chosen_genes.values():
            if gene.is_allele(other_gene=chosen_gene):
                return True
            
        else:
            return False
    
    @staticmethod
    def _insert_non_conflict_gene(genes_dict: Dict[int, BaseGene],
                                  gene: BaseGene):
        
        if not Genome._check_gene_conflict(chosen_gene=gene,
                                            chosen_genes=genes_dict):
                
                genes_dict = Genome.insert_gene_in_dict(genes_dict=genes_dict,
                                                        gene=gene.duplicate())
                
        return genes_dict
        
    @staticmethod
    def _genes_to_transmit(main_genome: Dict[int, BaseGene],
                           sub_genome: Dict[int, BaseGene]) -> Dict[int, BaseGene]:
        
        chosen_genes: Dict[int, BaseGene] = {}
        for key in main_genome:
            if key in sub_genome:
                chosen_gene = choice([main_genome[key], sub_genome[key]])
            
            else:
                chosen_gene = main_genome[key]
                
            Genome._insert_non_conflict_gene(genes_dict=chosen_genes,
                                             gene=chosen_gene)
                
        return chosen_genes
    
    @staticmethod
    def _add_missing_nodes(new_links: Dict[int, LinkGene], new_nodes: Dict[int, NodeGene],
                           main_nodes: Dict[int, NodeGene]) -> Dict[int, NodeGene]:
            
        for link in new_links.values():
            in_node = link.in_node
            out_node = link.out_node
            if in_node not in new_nodes:
                new_node = main_nodes[in_node]
                Genome._insert_non_conflict_gene(genes_dict=new_nodes,
                                                 gene=new_node)
                            
            if out_node not in new_nodes:
                new_node = main_nodes[out_node]
                Genome._insert_non_conflict_gene(genes_dict=new_nodes,
                                                 gene=new_node)
                
        return new_nodes
    
    def reproduce(genome_id:int, parent1: Genome, parent2: Genome) -> Genome:       
        main_genome, sub_genome  = choice([parent1, parent2], 2, replace=False)
        
        new_nodes: Dict[int, NodeGene] = {}
        # Make sure all sensors and outputs are included
        for current_node in parent1.node_genes:
            if(Genome._is_IO_node(current_node)):
                
                # Create a new node off the sensor or output
                new_node: NodeGene = current_node.duplicate()
                
                # Add the new node
                Genome.insert_gene_in_dict(genes_dict=new_nodes,
                                           gene=new_node)
                
        # Choose the links to transmit to offspring   
        main_links: Dict[int, LinkGene] = main_genome._link_genes 
        sub_links: Dict[int, LinkGene] = sub_genome._link_genes  
        new_links = Genome._genes_to_transmit(main_genome=main_links,
                                                 sub_genome=sub_links)
        
        # Choose the nodes to transmit to offspring
        main_nodes: Dict[int, NodeGene] = main_genome._node_genes
        sub_nodes: Dict[int, NodeGene] = sub_genome._node_genes
        chosen_nodes = Genome._genes_to_transmit(main_genome=main_nodes,
                                                 sub_genome=sub_nodes)
        new_nodes |= chosen_nodes
        # Make sure all the nodes in the links chosen
        # are present in offspring's genome
        Genome._add_missing_nodes(new_links=new_links,
                                  new_nodes=new_nodes,
                                  main_nodes=main_nodes)
        
        baby_genome = Genome(genome_id=genome_id,
                             node_genes=new_nodes,
                             link_genes=new_links)
        
        return baby_genome 

        
           
   
                               
    
