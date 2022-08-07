from __future__ import annotations

from random import choice, random, sample
from typing import Any, Dict, Optional, Set, Tuple, TypeVar

from project.src.platform.running.config import config

from .genes import (BaseGene, LinkGene, NodeGene, NodeType, OutputNodeGene,
                    OutputType)
from .innovation import InnovationType, InnovTable

Gene = TypeVar('Gene', bound=BaseGene)

class Genome:
    """Class:
        Genotype containing the information to build a network

        Attributes:
            __id (int):                         unique identifier
            _node_genes (Dict[int, NodeGene]):  dictionary of NodeGenes
            _link_genes (Dict[int, LinkGene]):  dictionary of LinkGenes
            complete (bool):                    whether the network is fully connected

        Methods:
            add_link:       Add a LinkGene to the dictionary of LinkGenes
            add_node:       Add a NodeGene to the dictionary of NodeGenes
            get_link_genes: Return only the LinkGenes values from the dictionary
            get_node_genes: Return only the NodeGenes values from the dictionary
            mutate:         mutate the genome

        Static methods:
            insert_gene:            Insert a Gene into a dictionary of Genes
            verify_post_genesis:    Check that the genome is valid
            genetic_distance:       Calculate the genetic distance between two genomes
            crossover:              Create new Genome from 2 parents

        class methods:
            Initialize a genome based on configuration


    """
    def __init__(self,
                 genome_id: int,
                 node_genes: Dict[int, NodeGene] | None = None,
                 link_genes: Dict[int, LinkGene] | None = None,
                 complete: bool = False):

        self.__id: int = genome_id                                  # unique identifier
        self._node_genes: Dict[int, NodeGene] | None = node_genes   # list of network's nodes
        self._link_genes: Dict[int, LinkGene] | None = link_genes   # list of link's genes
        #self.ancestors: Set = {}                                   # set of ancestors
        self.complete = complete                                    # wheter the network is fully connected

    @property
    def id(self) -> int:
        """property:
            return genome's id

        Returns:
            int: genome's id
        """
        return self.__id

    @property
    def node_genes(self) -> Dict[int, NodeGene]:
        """Return the dictionary of NodeGenes

        Returns:
            Dict[int, NodeGene]: dictionary of NodeGenes
        """
        return self._node_genes

    @property
    def link_genes(self) -> Dict[int, LinkGene]:
        """Return the dictionary of LinkGenes

        Returns:
            Dict[int, LinkGene]: dictionary of LinkGenes
        """
        return self._link_genes

    @property
    def n_node_genes(self) -> int:
        """Return the number of NodeGenes

        Returns:
            int: number of NodeGenes
        """
        return len(self._node_genes)

    @property
    def n_link_genes(self) -> int:
        """Return the number of LinkGenes

        Returns:
            int: number of LinkGenes
        """
        return len(self._link_genes)

    @property
    def size(self) -> Dict[str, int]:
        """Return a dictionary with the size of the Genome,
           with the number of NodeGenes and LinkGenes

        Returns:
            Dict[str, int]: dictionary with the size of the Genome
        """
        return {'node genes': self.n_node_genes,
                'link genes': self.n_link_genes}

    def add_link(self, link: LinkGene) -> None:
        """Public method:
            Add a LinkGene to the dictionary of LinkGenes

        Args:
            link (LinkGene): LinkGene to add
        """
        self._link_genes[link.id] = link

    def add_node(self, node: NodeGene) -> None:
        """Public method:
            Add a NodeGene to the dictionary of NodeGenes

        Args:
            link (NodeGene): NodeGene to add
        """
        self._node_genes[node.id] = node

    @staticmethod
    def insert_gene(genes_dict: Dict[int, Gene],
                    gene: Gene) -> Dict[int, Gene]:
        """Static method:
            Insert a Gene into a dictionary of Genes

        Args:
            genes_dict (Dict[int, BaseGene]):   dictionary of genes to insert into
            gene (BaseGene):                    gene to insert

        Returns:
            Dict[int, BaseGene]: the final dictionary of genes after insertion
        """
        genes_dict[gene.id] = gene
        return genes_dict

    def get_link_genes(self) ->  Set[LinkGene]:
        """Return only the LinkGenes values from the dictionary

        Returns:
            np.array[LinkGene]: Array of LinkGenes
        """
        return set(self._link_genes.values())

    def get_node_genes(self) ->  Set[NodeGene]:
        """Return only the NodeGenes values from the dictionary

        Returns:
            np.array[NodeGene]: Array of NodeGenes
        """
        return set(self._node_genes.values())

    @classmethod
    def genesis(cls, genome_id: int, genome_data: Dict[str, Any]) -> Genome:
        """Constructor:
            Initialize a genome based on configuration.
            Create the input GeneNodes, output GeneNodes and
            GeneLinks connecting each input to each output

        Args:
            genome_id (int):                id of the genome to initialize
            genome_data (Dict[str, Any]):   contain the brain's genome information

        Returns:
            Genome: genome created
        """

        complete: bool = genome_data.get('complete', True)
        n_inputs: int = genome_data['n_inputs']
        n_outputs: int = genome_data['n_outputs']
        n_actions: int = genome_data['n_actions']
        actions = genome_data['actions']


        # Initialize inputs
        count_node_id: int = 1            # keep track of number of nodes created for ids
        inputs: Dict[int, NodeGene] = {}  # dictionary of inputs
        for _ in range(n_inputs):
            inputs = Genome.insert_gene(genes_dict=inputs,
                                        gene=NodeGene(node_id=count_node_id,
                                                      node_type=NodeType.INPUT,
                                                      bias=0.0))
            count_node_id += 1

        # Initialize outputs
        outputs: Dict[int, NodeGene] = {}  # dictionary of outputs
        last_trigger_id: int = count_node_id + n_actions
        for i in range(n_outputs):
            if i < n_actions:
                output_type = OutputType.TRIGGER
                associated_values = [node_id + last_trigger_id for node_id in list(actions.values())[i]]
                name = list(actions.keys())[i]
            else:
                output_type = OutputType.VALUE
                name = None
                associated_values = None

            node_gene = OutputNodeGene(node_id=count_node_id,
                                       name=name,
                                       output_type=output_type,
                                       associated_values=associated_values)

            outputs = Genome.insert_gene(genes_dict=outputs,
                                         gene=node_gene)
            count_node_id += 1

        # Connect each input to each output
        links: Dict[int, LinkGene] = {}     # dictionary of links
        count_link_id: int = 1              # keep track of number of links created for ids
        for node1 in inputs.keys():
            for node2 in outputs.keys():
                if  (not complete
                 and random() < config["NEAT"]["skip_connection"]):
                    continue

                links = Genome.insert_gene(genes_dict=links,
                                           gene=LinkGene(link_id=count_link_id,
                                                         in_node=node1,
                                                         out_node=node2))
                count_link_id += 1

        Genome.verify_post_genesis(n_inputs=n_inputs,
                                   n_outputs=n_outputs,
                                   inputs=inputs,
                                   outputs=outputs,
                                   links=links,
                                   complete=complete)

        # Set the innovation tables to the number
        # of links and nodes craeted
        InnovTable.node_number = count_node_id
        InnovTable.node_number = count_link_id

        genome = cls(genome_id=genome_id,
                     node_genes=inputs|outputs,
                     link_genes=links,
                     complete=complete)

        return genome

    @staticmethod
    def verify_post_genesis(n_inputs: int, n_outputs: int, links: Dict[int, LinkGene],
                            inputs: Dict[int, NodeGene], outputs: Dict[int, NodeGene],
                            complete: bool) -> None:
        """Static method:
            Check that the genome is valid

        Args:
            n_inputs (int):                 number of inputs
            n_outputs (int):                number of outputs
            links (Dict[int, LinkGene]):    dictionary of LinkGenes
            inputs (Dict[int, NodeGene]):   dictionary of inputs NodeGenes
            outputs (Dict[int, NodeGene]):  dictionary of outputs NodeGenes
            complete (bool):                whether the network is fully connected

        Raises:
            ValueError: incorrect number of inputs
            ValueError: incorrect number of outputs
            ValueError: incorrect number of links
            ValueError: link has an output as ingoing NodeGene
            ValueError: link has an input as incoming NodeGene
        """

        if (size:= len(inputs)) != n_inputs:
            raise ValueError(f"Number of inputs {size} instead of {n_inputs}")

        if (size:= len(outputs)) != n_outputs:
            raise ValueError(f"Number of inputs {size} instead of {n_outputs}")

        for link in links.values():
            if link.in_node not in range(0, n_inputs+1):
                raise ValueError(f"{link} has an output as in_node")
            if link.in_node not in inputs:
                raise ValueError(f"{link} is not in inputs")

            if link.out_node <= n_inputs:
                raise ValueError(f"{link} has an input as out_node")
            if link.out_node not in outputs:
                raise ValueError(f"{link} is not in outputs")

        # Fully connected
        if complete:
            if n_links:= len(links) != n_inputs*n_outputs:
                raise ValueError(f"Number of links {n_links} instead of {n_inputs*n_outputs}")

    @staticmethod
    def genetic_distance(genome1: Genome, genome2: Genome) -> float:
        """Static method:
            Calculate the genetic distance between two genomes

        Args:
            genome1 (Genome): first genome
            genome2 (Genome): second genome

        Returns:
            float: calculated genetic distance
        """
        node_distance: float = Genome._genetic_gene_distance(gene_dict1 = genome1.node_genes,
                                                             gene_dict2 = genome2.node_genes)

        link_distance: float = Genome._genetic_gene_distance(gene_dict1 = genome1.link_genes,
                                                             gene_dict2 = genome2.link_genes)

        return node_distance + link_distance

    @staticmethod
    def _genetic_gene_distance(gene_dict1: Dict[int, Gene],
                               gene_dict2: Dict[int, Gene]) -> float:
        """Static method:
            Calculate the genetic distance between a set of genes

        Args:
            gene_dict1 (Dict[int, BaseGene]): first set of genes
            gene_dict2 (Dict[int, BaseGene]): second set of genes

        Returns:
            float: calculated genetic distance
        """
        # Find the maximum innovation numbers for each genome
        max_g1: int = max(gene_dict1.keys())
        max_g2: int = max(gene_dict2.keys())

        # Order the genomes depending on which has the highest innovation number
        if max_g1 > max_g2:
           big_genome, small_genome = gene_dict1, gene_dict2
        else:
            small_genome, big_genome = gene_dict1, gene_dict2

        # Threshold above which genes are in excess in the big genome
        # (meaning all ids above this threshold are above
        # the max ids from the small genome)
        excess_threshold: int = min(max_g1, max_g2)

        num_excess: int = 0               # number of excess genes
        num_disjoint: int = 0             # number of disjoint genes
        num_matching: int = 0             # number of matching genes
        mutation_difference: float = 0.0  # total mutation difference

        # Loop through all the genes from the big genome
        for node_id, gene_node in big_genome.items():
            # genes with ids above the threshold are excess genes
            if node_id > excess_threshold:
                num_excess += 1
            # genes present only in the big genome
            # below the excess threshold are disjoint
            elif node_id not in small_genome:
                num_disjoint += 1
            # deal with genes present in both genomes
            elif node_id in small_genome:
                num_matching += 1
                other_node = small_genome[node_id]
                # Calculate the mutation difference between same innovation genes
                mutation_difference += gene_node.mutation_distance(other_gene=other_node)

        # Add the disjoint genes present in small genome
        # but not in the big genome,
        # obtained by subtracting the number of matching genome
        # from the total size of genome
        num_disjoint += len(small_genome) - num_matching

        # Calulate the final genetic distance by applying formula,
        # with coefficient from settings
        genetic_distance: float = (num_excess * config["NEAT"]["excess_coeff"]
                                 + num_disjoint * config["NEAT"]["disjoint_coeff"]
                                 + config["NEAT"]["mutation_difference_coeff"]
                                    * mutation_difference/max(num_matching, 1))

        return genetic_distance

    def mutate(self) -> None:
        """Public method:
            Mutate the genome
        """
        # Add a node to the genome
        if random() < config["NEAT"]["add_node_prob"]:
            self._mutate_add_node()
        # Add a link to the genome
        if random() < config["NEAT"]["add_link_prob"]:
            self._mutate_add_link(tries=config["NEAT"]["add_link_tries"])
        # Modify the weights of the links
        # and their enabled status
        self._mutate_links()
        self._mutate_nodes()

    def _mutate_links(self) -> None:
        """Private method:
            mutate the LinkGenes
        """
        for link in self.get_link_genes():
            if random() < config["NEAT"]["link_mutate_prob"]:
                link.mutate()

    def _mutate_nodes(self) -> None:
        """Private method:
            mutate the NodeGenes
        """
        for node in self.get_node_genes():
            if random() < config["NEAT"]["node_mutate_prob"]:
                node.mutate()

    def _find_random_link(self) -> Optional[LinkGene]:
        """Pivate method:
            Find a random LinkGene containing a NodeGene to mutate

        Returns:
            LinkGene: LinkGene containing the NodeGene to mutate
        """
        enabled_links = [link for link in self.get_link_genes() if link.enabled]

        if enabled_links:
            return choice(enabled_links)

        else:
            return None

    def _create_node(self, node_id: int, in_node: int, out_node: int,
                         innovation_number1: int, innovation_number2: int,
                         old_weight: float) -> Tuple[NodeGene, LinkGene, LinkGene]:
        """Private method:
            Create the new NodeGene and two LinkGenes connecting this NodeGene in and out

        Args:
            node_id (int):              id of the NodeGene
            in_node (int):              id of incoming NodeGene
            out_node (int):             id of outgoing NodeGene
            innovation_number1 (int):   incoming link's innovation number
            innovation_number2 (int):   outgoing link's innovation number
            old_weight (float):         weight of the disabled old link

        Returns:
            Tuple[NodeGene, LinkGene, LinkGene]:    NodeGene: new NodeGene created
                                                    LinkGene: new LinkGene connecting in the new NodeGene
                                                    LinkGene: new LinkGene connecting out the new NodeGene
        """
        new_node = NodeGene(node_id=node_id,
                            node_type=NodeType.HIDDEN)

        new_link1 = LinkGene(link_id=innovation_number1,
                             weight=1.0,
                             in_node=in_node,
                             out_node=new_node.id,
                             mutation_number=0)

        new_link2 = LinkGene(link_id=innovation_number2,
                             weight=old_weight,
                             in_node=new_node.id,
                             out_node=out_node,
                             mutation_number=0)

        return new_node, new_link1, new_link2

    def _new_node_innovation(self, old_link: LinkGene) -> Tuple[NodeGene, LinkGene, LinkGene]:
        """Private method:
            Check to see if this innovation has already been done in another genome

        Args:
            old_link (LinkGene): LinkGene which innovation to check

        Returns:
            Tuple[Node, LinkGene, LinkGene]:    NodeGene: new NodeGene created
                                                LinkGene: new LinkGene connecting in the new NodeGene
                                                LinkGene: new LinkGene connecting out the new NodeGene
        """
        # Extract the link
        old_weight: float = old_link.weight

        # Extract the nodes
        in_node: int = old_link.in_node
        out_node: int = old_link.out_node

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
        """Private method:
            Mutate genome by adding a NodeGene

        Returns:
            bool: True if mutation was successful
                  False if failure
        """
        link: Optional[LinkGene] = self._find_random_link()

        # End if no link was found
        if not link:
            return False

        # Disabled the old link
        link.enabled = False

        new_node, new_link1, new_link2 = self._new_node_innovation(old_link=link)

        # Add the new NodeGene and
        # the two new LinkGenes
        # to the genome
        self.add_link(link=new_link1)
        self.add_link(link=new_link2)
        self.add_node(node=new_node)

        return True

    def _link_already_exists(self, node1: NodeGene, node2: NodeGene) -> bool:
        """Private method:
            See if a LinkGene connecting the two NodeGenes already exists

        Args:
            node1 (NodeGene): first NodeGene
            node2 (NodeGene): second NodeGene

        Returns:
            bool: True if a similar LinkGene already exists
                  False if it's novel
        """
        for link in self.get_link_genes():
            if (link.in_node == node1.id and
                link.out_node == node2.id):

                return True


        return False

    def _new_link_gene(self, in_node: NodeGene, out_node: NodeGene) -> LinkGene:
        """Private method:
            Create a new LinkGene between two NodeGenes, and return it

        Args:
            in_node (NodeGene):     incoming NodeGene
            out_node (NodeGene):    outgoing NodeGene

        Returns:
            LinkGene: newly created LinkGene
        """

        the_innovation = InnovTable.get_innovation( in_node=in_node.id,
                                                    out_node=out_node.id,
                                                    innovation_type=InnovationType.NEW_LINK)

        new_link = LinkGene(weight=the_innovation.weight,
                            in_node=in_node.id,
                            out_node=out_node.id,
                            link_id=the_innovation.innovation_number1,
                            mutation_number=0)

        return new_link

    def _is_valid_link(self, node_in: NodeGene, node_out: NodeGene) -> bool:
        """Private method:
            Check if a LinkGene is valid, the incoming NodeGene cannot be an output,
            the outgoing NodeGene cannot be an input, the two cannot be the same

        Args:
            node_in (NodeGene):     incoming NodeGene
            node_out (NodeGene):    outgoing NodeGene

        Returns:
            bool: True if the LinkGene is valid
                  False if not valid
        """
        # Verify that the two NodeGenes
        # are not the same
        if node_in == node_out:
            return False

        # incoming NodeGene not an output and
        # outgoing NodeGene not an input
        if (node_in.type.name == NodeType.OUTPUT.name or
            node_out.type.name == NodeType.INPUT.name):
            return False

        return True

    def _find_valid_link(self, tries: int=20) -> Tuple[NodeGene|None, NodeGene|None]:
        """Private method:
            Find a valid open link to add a new LinkGene after mutation

        Args:
            tries (int): Number of tries before giving up

        Returns:
            Tuple[Node, Node]:  Node: incoming NodeGene
                                Node: outgoing NodeGene
        """
        # Try until it's time to give up
        for _ in range(tries + 1):
            # Select two NodeGenes at random
            node1, node2 = sample(self.get_node_genes(), 2)

            # Check if the LinkGene is valid
            if self._is_valid_link(node_in=node1,
                                   node_out=node2):

                # Search for open link between the two NodeGenes
                if not self._link_already_exists(node1=node1,
                                                 node2=node2):
                    return node1, node2

        return None, None

    def _mutate_add_link(self, tries: int=20) -> bool:
        """Private method:
            Mutate the genome by adding a new LinkGene
            between 2 random NodeGenes

        Args:
            tries (int): Amount of tries before giving up

        Returns:
            bool: True if mutation was successful
                  False if failure
        """
        # Find an open link
        node1, node2 = self._find_valid_link(tries=tries)

        # Continue only if an open link was found
        if node1 and node2:
            new_link = self._new_link_gene(in_node=node1,
                                           out_node=node2)
            self.add_link(new_link)
            return True

        else:
            return False

    def get_last_node_id(self) -> int:
        """Public method:
            Return highest id of NodeGene in Genome

        Returns:
            int: max NodeGene's id
        """
        return max(set(self.node_genes.keys()))

    def get_last_link_id(self) -> int:
        """Public method:
            Return highest id of LinkGene in Genome

        Returns:
            int: max LinkGene's id
        """
        return max(set(self.link_genes.keys()))

    @staticmethod
    def _is_edge_node(node: NodeGene) -> bool:
        """Private static method:
            Check if the NodeGene is an input or output

        Args:
            node (NodeGene): NodeGene to check

        Returns:
            bool: True if the NodeGene is an input, bias or output,
                  False if the NodeGene is an Hidden one
        """
        return node.type.name in {"INPUT", "OUTPUT", "BIAS"}

    @staticmethod
    def _check_gene_conflict(chosen_genes: Dict[int, Gene],
                             chosen_gene: Gene) -> bool:
        """Private static method:
            Check if the BaseGene already has an equivalent
            in the dictionary of already added BaseGenes

        Args:
            chosen_genes (Dict[int, BaseGene]): dictionary of already chosen BaseGenes
            chosen_gene (BaseGene):             BaseGene to check for conflict (equivalent)

        Returns:
            bool: True if an equivalent BaseGene was found in the dictionary,
                  False if no equivalent was found
        """

        for gene in chosen_genes.values():
            if gene.is_allele(other_gene=chosen_gene):
                return True

        return False

    @staticmethod
    def _insert_non_conflict_gene(genes_dict: Dict[int, Gene],
                                  gene: Gene) -> Dict[int, Gene]:
        """Private static method:
            Insert a BaseGene into a dictionary only if it doesn't conflict
            with already present BaseGene in the dictionary

        Args:
            genes_dict (Dict[int, BaseGene]):   dictionary of BaseGene to check into
            gene (BaseGene):                    BaseGene to check for conflict (equivalent)

        Returns:
            Dict[int, BaseGene]: final dictionary with BaseGene added if it doesn't conflict
        """

        # Only insert if there is no conflict
        if not Genome._check_gene_conflict(chosen_gene=gene,
                                           chosen_genes=genes_dict):

            genes_dict = Genome.insert_gene(genes_dict=genes_dict,
                                            gene=gene.duplicate())

        return genes_dict

    @staticmethod
    def _genes_to_transmit(main_genome: Dict[int, Gene],
                           sub_genome: Dict[int, Gene]) -> Dict[int, Gene]:
        """Private static method
            Select the BaseGenes to transmit to offspring, take extra BaseGenes from
            the main genome, choose randomly if BaseGenes are present in both genomes

        Args:
            main_genome (Dict[int, BaseGene]): dominant genome's dicitonary of BaseGenes
            sub_genome (Dict[int, BaseGene]):  subsidiary genome's dicitonary of BaseGenes

        Returns:
            Dict[int, BaseGene]: final dictionary of chosen BaseGenes to transmit
        """

        chosen_genes: Dict[int, Gene] = {}
        # Loop through all the BaseGenes
        # from the main genome
        for key in main_genome:
            if key in sub_genome:
                # If present in both, choose randomly between genomes
                chosen_gene = choice([main_genome[key], sub_genome[key]])

            else:
                chosen_gene = main_genome[key]

            # Verify for conflict before adding the BaseGene
            Genome._insert_non_conflict_gene(genes_dict=chosen_genes,
                                             gene=chosen_gene)

        return chosen_genes

    @staticmethod
    def _add_missing_nodes(new_links: Dict[int, LinkGene], new_nodes: Dict[int, NodeGene],
                           main_nodes: Dict[int, NodeGene]) -> Dict[int, NodeGene]:
        """Private static method:
            Verify that all the NodeGenes referenced by LinkGenes are present in the dictionary
            before passing it to offspring, if not: add the missing GeneNodes

        Args:
            new_links (Dict[int, LinkGene]):    dictionary of LinkGenes that will be transmitted
            new_nodes (Dict[int, NodeGene]):    dictionary of NodeGenes that will be transmitted
            main_nodes (Dict[int, NodeGene]):   dictionary of NodeGenes from the main genome

        Returns:
            Dict[int, NodeGene]: final dictionary with all the missing GeneNodes added
        """

        # Loop through the LinkGenes that will be transmitted
        for link in new_links.values():

            # Take the incoming and
            # outgoing GeneNodes
            in_node = link.in_node
            out_node = link.out_node

            # Add if not already in the
            # dictionary and no conflict
            if in_node not in new_nodes:
                new_node = main_nodes[in_node]
                Genome._insert_non_conflict_gene(genes_dict=new_nodes,
                                                 gene=new_node)
            # Same for outgoing GeneNode
            if out_node not in new_nodes:
                new_node = main_nodes[out_node]
                Genome._insert_non_conflict_gene(genes_dict=new_nodes,
                                                 gene=new_node)

        return new_nodes

    @staticmethod
    def crossover(genome_id: int, parent1: Genome, parent2: Genome) -> Genome:
        """static method:
            Create new Genome from 2 parents, selecting which genes to transmit

        Args:
            genome_id (int):    id of the baby Genome
            parent1 (Genome):   first parent Genome
            parent2 (Genome):   second parent Genome

        Returns:
            Genome: baby genome created
        """
        # Choose randomly which parent will be the dominant one,
        # which will transmit most of its genes
        main_genome, sub_genome  = sample([parent1, parent2], 2)

        new_nodes: Dict[int, NodeGene] = {}

        # Make sure all sensors and outputs are included
        for node in parent1.get_node_genes():
            if(Genome._is_edge_node(node)):

                # Create a new node off the sensor or output
                new_node: NodeGene = node.duplicate()

                # Add the new node
                Genome.insert_gene(genes_dict=new_nodes,
                                   gene=new_node)

        # Choose the links to transmit to offspring
        main_links: Dict[int, LinkGene] = main_genome.link_genes
        sub_links: Dict[int, LinkGene] = sub_genome.link_genes
        new_links = Genome._genes_to_transmit(main_genome=main_links,
                                              sub_genome=sub_links)

        # Choose the nodes to transmit to offspring
        main_nodes: Dict[int, NodeGene] = main_genome.node_genes
        sub_nodes: Dict[int, NodeGene] = sub_genome.node_genes
        chosen_nodes = Genome._genes_to_transmit(main_genome=main_nodes,
                                                 sub_genome=sub_nodes)

        # Uniting the two dictionary
        # of nodes into a entire one
        new_nodes |= chosen_nodes
        # Make sure all the nodes in the links chosen
        # are present in offspring's genome
        Genome._add_missing_nodes(new_links=new_links,
                                  new_nodes=new_nodes,
                                  main_nodes=main_nodes)

        # The baby genome resulting from the crossover
        baby_genome = Genome(genome_id=genome_id,
                             node_genes=new_nodes,
                             link_genes=new_links)

        return baby_genome
