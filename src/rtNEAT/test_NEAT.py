import pytest
from gene import Gene
from node import Node, NodePlace, FuncType
from link import Link
from innovation import Innovation, InnovationType, InnovTable
from genome import Genome
import numpy as np
from neat import config
from src.rtNEAT.organism import Organism

class TestNode:
    def test_create_node(self):
        sensor_node = Node(node_id=0,
                           node_place=NodePlace.INPUT)
        assert sensor_node
        assert type(sensor_node) == Node
        
        
        
    def test_node_fields(self):
        sensor_node = Node(node_id=0,
                           
                           node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                           
                           node_place=NodePlace.OUTPUT)
      
        assert set(['id', 'node_place', 'activation', 'ftype', 'frozen', 'incoming','outgoing']).issubset(vars(action_node))
        
        assert sensor_node.id == 0
        assert sensor_node.node_place == NodePlace.INPUT
        assert sensor_node.activation == 0.0
        assert sensor_node.ftype == FuncType.SIGMOID
        assert sensor_node.frozen == False
        
        assert action_node.id == 1
        assert action_node.node_place == NodePlace.OUTPUT
        assert action_node.activation == 0.0
        assert action_node.ftype == FuncType.SIGMOID
        assert action_node.frozen == False

    """ def test_add_incoming_link(self):
        sensor_node = Node(node_id=0,
                           node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                           node_place=NodePlace.OUTPUT)
        
        assert len(action_node.incoming) == 0
        action_node.add_incoming(feednode=sensor_node, weight=1.0)
        assert len(action_node.incoming) == 1 """
               
   
class TestLink:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.sensor_node = Node(node_id=0,
                                
                                node_place=NodePlace.INPUT)
        
        self.action_node = Node(node_id=1,
                                
                                node_place=NodePlace.OUTPUT) 
        
    def test_create_link(self):
        link = Link(in_node=self.sensor_node, out_node=self.action_node, weight=1.0)
        
        assert link
        assert type(link) == Link
        
    def test_link_fields(self):
        link = Link(in_node=self.sensor_node, out_node=self.action_node, weight=1.0)
        
        assert set(['in_node', 'out_node', 'weight', 'is_recurrent', 'time_delay', 'added_weight']).issubset(vars(link))
        assert link.in_node == self.sensor_node
        assert link.out_node == self.action_node
        assert link.weight == 1.0
        assert link.is_recurrent == False
        assert link.time_delay == False
        assert link.added_weight == 0.0
        

class TestGene:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.sensor_node = Node(node_id=0,
                                node_place=NodePlace.INPUT)
        
        self.action_node = Node(node_id=1,
                                node_place=NodePlace.OUTPUT) 
        
    def test_create_gene(self):
        gene = Gene(in_node=self.sensor_node,
                    out_node=self.action_node,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        assert gene
        assert type(gene) == Gene
        
    def test_gene_fields(self):
        gene = Gene(in_node=self.sensor_node,
                    out_node=self.action_node,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        assert set(['link', 'innovation_number', 'mutation_number','enabled', 'frozen']).issubset(vars(gene))
        assert gene.innovation_number == 0
        assert gene.mutation_number == 0
        assert gene.enabled == True
        assert gene.frozen == False
        
class TestGenome:
    @pytest.fixture(autouse=True)
    def setup(self):
        sensor_node = Node(node_id=0,
                                
                                node_place=NodePlace.INPUT)
            
        action_node = Node(node_id=1,
                                
                                node_place=NodePlace.OUTPUT)
        
        gene0 = Gene(in_node=sensor_node,
                    out_node=action_node,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        self.nodes = np.array([sensor_node, action_node])
        self.genes = np.array([gene0])
        
    def test_create_genome(self):
        genome = Genome(genome_id=0,
                        nodes=self.nodes,
                        genes=self.genes)
        
        assert genome
        assert type(genome) == Genome

    def test_init_genome(self):
        n_inputs = config.num_inputs
        n_outputs = config.num_outputs
        n_total = n_inputs + n_outputs + 1
        assert InnovTable.get_node_number() == 0
        genome = Genome(genome_id=0)
        Organism(genome=genome,
                 generation=0)
        
        
        for i in range(n_total):
            assert genome.nodes[i].id == i
        
        for i in range(1,n_inputs):
            assert genome.nodes[i].node_place == NodePlace.INPUT
        
        for i in range(n_outputs, n_total):
            assert genome.nodes[i].node_place == NodePlace.OUTPUT
            
        assert genome.nodes.size == n_total
        assert InnovTable.get_node_number() == n_total
        
        assert genome.genes.size == (n_inputs + 1) * n_outputs
        for i, gene in enumerate(genome.genes):
            assert gene.innovation_number == i
            assert gene.link.in_node.node_place == NodePlace.INPUT or NodePlace.BIAS
            assert gene.link.out_node.node_place == NodePlace.OUTPUT
        
        assert InnovTable.get_innovation_number() == (n_inputs + 1) * n_outputs
        
       
    def test_genome_fields(self):
        genome = Genome(genome_id=0, nodes=self.nodes, genes=self.genes)
        assert set(['id', 'genes', 'nodes']).issubset(vars(genome))
        
        assert genome.id == 0
        assert genome.nodes is self.nodes
        assert genome.genes is self.genes
    
    class TestGenomeMethods:  
        @pytest.fixture(autouse=True)
        def setup(self):
            sensor_node = Node(node_id=0,
                               node_place=NodePlace.INPUT)
            
            action_node = Node(node_id=1,
                               node_place=NodePlace.OUTPUT)
            
            gene0 = Gene(in_node=sensor_node,
                        out_node=action_node,
                        weight=1.0,
                        innovation_number=0,
                        mutation_number=0)
            
            sensor_node2 = Node(node_id=2,
                                node_place=NodePlace.INPUT)
            
            action_node2 = Node(node_id=3,
                                    node_place=NodePlace.OUTPUT)
            
            gene1 = Gene(in_node=sensor_node2,
                        out_node=action_node2,
                        weight=1.0,
                        innovation_number=1,
                        mutation_number=0)
            
            sensor_node3 = Node(node_id=4,
                                node_place=NodePlace.INPUT)
            
            action_node3 = Node(node_id=5,
                                node_place=NodePlace.OUTPUT)
            
            gene2 = Gene(in_node=sensor_node3,
                    out_node=action_node3,
                    weight=1.0,
                    innovation_number=2,
                    mutation_number=0)
            
            gene3 = Gene(in_node=sensor_node3,
                    out_node=action_node3,
                    weight=1.0,
                    innovation_number=2,
                    mutation_number=1)
           
            self.nodes = np.array([sensor_node, action_node, sensor_node2, action_node2, sensor_node3, action_node3], dtype=Node)
            self.genes = np.array([gene0, gene1, gene2, gene3], dtype=Gene)
            
            self.genome1 = Genome(genome_id=0,
                            nodes=self.nodes,
                            genes=self.genes)
            
            yield
            InnovTable.reset_innovation_table()
        
          
        def test_add_gene(self):
            assert self.genome1.genes.size == 4
            self.genome1.add_gene(gene=self.genes[1])
            assert self.genome1.genes.size == 5
            
            genes_list = list(self.genome1.genes)
            genes_list.insert(2, self.genes[1])
            assert self.genome1.genes.all() == np.array(genes_list).all()
            
        def test_insert_node(self):
            assert self.genome1.nodes.size == 6
            node = self.genome1.nodes[3]
            self.genome1.nodes = Genome.insert_node(nodes_list=self.genome1.nodes,
                                                node=node)
            assert self.genome1.nodes.size == 7
            
            nodes_list = list(self.genome1.nodes)
            nodes_list.insert(3, self.genome1.nodes[3])
            assert self.genome1.nodes.all() == np.array(nodes_list).all()

        def test_choose_gene(self):
            genome1 = Genome(genome_id=0,
                        nodes=self.nodes,
                        genes=self.genes[[0,1,3]])
            
            genome2 = Genome(genome_id=1,
                        nodes=self.nodes,
                        genes=self.genes[[0,2,1,3]])  
            
            p1_genes = iter(genome1.genes)
            p2_genes = iter(genome2.genes)
            p1_gene = next(p1_genes)
            p2_gene = next(p2_genes)
            
            # same gene
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(parent1_gene=p1_gene,
                                                             parent2_gene=p2_gene,
                                                             parent1_genes=p1_genes,
                                                             parent2_genes=p2_genes,
                                                             p1_dominant=True)
            assert not skip
            assert type(disable) == bool     
            assert chosen_gene == self.genes[0]  
            
            # innovation1 < innovation 2 non-dominant  genome 1
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(*args,
                                                                    p1_dominant=False) 
            assert skip
            assert chosen_gene == self.genes[1]  
            
            # different gene same innovation number
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(*args,
                                                                     p1_dominant=True)
            
            np.random.seed(1)
            assert not skip
            assert chosen_gene == np.random.choice([self.genes[3], self.genes[2]]) 
            
            # innovation2 < innovation1 non-dominant genome 2
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(*args,
                                                                    p1_dominant=True)
            assert skip
            assert chosen_gene == self.genes[1]  
            
            # same gene in non-dominant genome 2
            chosen_gene, skip, disable, *args = Genome._choose_gene_to_transmit(*args,
                                                                     p1_dominant=True)
            assert skip
            assert chosen_gene == self.genes[3] 
                         
        def test_check_gene_conflict(self):            
            genes = self.genes[[0, 1]]
            
            # conflict
            conflict = Genome._check_gene_conflict(new_genes=genes,
                                        chosen_gene=self.genes[0]) 
            assert conflict
            
            # no conflict
            conflict = Genome._check_gene_conflict(new_genes=genes,
                                        chosen_gene=self.genes[2])
            assert not conflict
        
        def test_check_node_existence(self):
            new_nodes = self.nodes[:4]
            target_node = self.nodes[3]
            
            assert len(new_nodes) == 4
            # node exists
            new_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                target_node=target_node)
            assert new_node == target_node
            assert len(new_nodes) == 4
            
            # node does not exist
            target_node = self.nodes[4]
            new_node, new_nodes = Genome._check_new_node_existence(new_nodes=new_nodes,
                                                                target_node=target_node)
            
            assert new_node.id == target_node.id
            assert len(new_nodes) == 5
            
        def test_mate_multipoint(self):
            sensor_node = Node(node_id=6,
                                node_place=NodePlace.INPUT)
            
            action_node = Node(node_id=7,
                                node_place=NodePlace.OUTPUT)
            
            gene3 = Gene(in_node=sensor_node,
                    out_node=action_node,
                    weight=1.0,
                    innovation_number=3,
                    mutation_number=0)
            self.genes[3] = gene3
            genome1 = Genome(genome_id=0,
                        nodes=self.nodes,
                        genes=self.genes[[0,1,3]])
            
            genome2 = Genome(genome_id=1,
                        nodes=self.nodes,
                        genes=self.genes[[0,2,3]]) 
            
            np.random.seed(1)
            new_genome = Genome.mate_multipoint(parent1=genome1,
                                                parent2=genome2,
                                                genome_id=2)
            
            assert new_genome.id == 2
            assert new_genome.nodes.size == 8
            assert new_genome.genes.size == 3
            genes = [gene.innovation_number for gene in new_genome.genes]
            
            p1_dominant = np.random.choice([0,1])
            if not p1_dominant:
                the_set = set([0,2,3])
            else:
                the_set = set([0,1,3])
            assert set(genes) == the_set
        
        def test_genome_compatibility(self):
            # Excess
            genome1 = Genome(genome_id=0,
                        nodes=self.nodes,
                        genes=self.genes)
            
            genome2 = Genome(genome_id=1,
                        nodes=self.nodes[:4],
                        genes=self.genes[:2])
            
            compatibility = Genome.compatibility(genome1=genome1,
                                                 genome2=genome2)
            assert compatibility == 2.0 * config.excess_coeff
            
            # Disjoint
            genome3 = Genome(genome_id=2,
                        nodes=self.nodes[[0,1,4,5]],
                        genes=self.genes[0:3])
            
            genome4 = Genome(genome_id=3,
                        nodes=self.nodes[2:5],
                        genes=self.genes[1:3])
                    
            compatibility = Genome.compatibility(genome1=genome4,
                                                  genome2=genome3)
            assert compatibility == 1.0 * config.disjoint_coeff
            
            # Mutation
            genome5 = Genome(genome_id=4,
                            nodes=self.nodes[2:4],
                            genes=self.genes[2:3])
            
            genome6 = Genome(genome_id=5,
                            nodes=self.nodes[4:],
                            genes=self.genes[3:])
            
            compatibility = Genome.compatibility(genome1=genome5,
                                                  genome2=genome6)
            assert compatibility == 1.0 * config.mutation_difference_coeff
            
        def test_get_last_node_info(self):        
            assert self.genome1.get_last_node_id() == 5+1
            assert self.genome1.get_last_gene_innovation_number() == 2+1
         
        """ def test_create_new_link(self):
            self.genome1._genesis()
            gene = self.genome1.genes[0]
            
            in_node = gene.link.in_node.analogue
            out_node = gene.link.out_node.analogue
            
            assert len(out_node.incoming) == 1
            assert len(in_node.outgoing) == 1
            
            link = self.genome1._create_new_link(gene = gene) 
            
            assert link.weight == gene.link.weight
            assert link.in_node == gene.link.in_node.analogue
            assert link.out_node == gene.link.out_node.analogue
            assert link.is_recurrent == gene.link.is_recurrent
            
            in_node = gene.link.in_node.analogue
            out_node = gene.link.out_node.analogue
            
            assert link in out_node.incoming
            assert link in in_node.outgoing
            
            assert len(out_node.incoming) == 2
            assert len(in_node.outgoing) == 2 """
            
        def test_genesis(self):        
            network = self.genome1.genesis(network_id=self.genome1.id) 
            assert self.genome1.phenotype == network
            assert network.genotype == self.genome1
        
        def test_mutate_links_weight_simplified(self):
            config.weight_mutate_prob = 1.0
            config.new_link_prob = 0.5
            config.weight_mutate_power = 0.5
            
            weights = [gene.link.weight for gene in self.genome1.genes]
            self.genome1._mutate_link_weights()
            new_weights = [gene.link.weight for gene in self.genome1.genes]
            
            for new_weight, weight in zip(new_weights, weights):
                assert new_weight != weight
                            
        def test_find_gene(self):
            gene, found = self.genome1._find_random_gene()
            assert gene in self.genome1.genes
            assert found
            
        def test_create_new_node(self):
            in_node, out_node = self.nodes[:2]
            node, gene1, gene2 = self.genome1._create_node(node_id=0,
                                          in_node=in_node,
                                          out_node=out_node,
                                          recurrence=False,
                                          innovation_number1=0,
                                          innovation_number2=1,
                                          old_weight=0.34)
           
            assert node.id == 0
            assert node.node_place == NodePlace.HIDDEN
            assert gene1.link.in_node == in_node
            assert gene1.link.out_node == node
            assert gene1.link.weight == 1.0
            assert gene1.innovation_number == 0
            assert gene2.link.in_node == node
            assert gene2.link.out_node == out_node
            assert gene2.link.weight == 0.34
            assert gene2.innovation_number == 1
            
        def test_mutate_add_node(self):
            genome1 = Genome(genome_id=1,
                             nodes=self.nodes[:2],
                             genes=self.genes[:1])
            
            genome2 = Genome(genome_id=1,
                             nodes=self.nodes[:2],
                             genes=self.genes[:1])
            
            # Innovation is novel
            assert InnovTable.get_innovation_number() == 0
            assert genome1.nodes.size == 2
            assert genome1.genes.size == 1
            success = genome1._mutate_add_node()
            assert genome1.genes[0].enabled == False
            assert success
            assert InnovTable.get_innovation_number() == 2
            assert genome1.nodes.size == 3
            assert genome1.genes.size == 3
            
            # Innovation exists                     
            genome2.genes[0].enabled = True
            assert InnovTable.get_innovation_number() == 2
            assert genome2.nodes.size == 2
            assert genome2.genes.size == 1
            success = genome2._mutate_add_node()
            assert success
            assert InnovTable.get_innovation_number() == 2
            assert genome2.nodes.size == 3
            assert genome2.genes.size == 3
            
        def test_find_first_non_sensor(self):
            self.genome1.nodes = self.nodes[[0,2,4,1,3,5]]
            index = self.genome1._find_first_non_sensor()
            assert index == 3
        
        def test_select_nodes_for_link(self):
            self.genome1.nodes = self.nodes[[0,2,4,1,3,5]]
            
            for _ in range(10):
                # Not recurrent link
                node1, node2 = self.genome1._select_nodes_for_link( recurrence = False,
                                                                    first_non_sensor=3)
                assert node1
                assert not node2.is_sensor()
                
            np.random.seed(100)      
            # Recurrent link   
            node1, node2 = self.genome1._select_nodes_for_link( recurrence = True,
                                                                first_non_sensor=3)
            assert node1 != node2
            assert not node2.is_sensor()
            
            node1, node2 = self.genome1._select_nodes_for_link( recurrence = True,
                                                                first_non_sensor=3)
            assert node1 != node2
            assert not node2.is_sensor()
            
            node1, node2 = self.genome1._select_nodes_for_link( recurrence = True,
                                                                first_non_sensor=3)
            assert node1 == node2
            assert not node2.is_sensor()
                   
        def test_link_already_exists(self):
            node1 = self.nodes[0]
            node2 = self.nodes[1]

            # Recurrence already exists
            found = self.genome1._link_already_exists(  node1=node1,
                                                        node2=node2,
                                                        recurrence=True)
            assert not found
            
            
            
            
            # Non-recurrence does not exist
            found = self.genome1._link_already_exists(  node1=node1,
                                                        node2=node2,
                                                        recurrence=False)
            assert found
            
            # Non-recurrence already exists
            node3 = self.nodes[1]
            recurrent_gene = Gene(weight=1.0,
                                  in_node=node3,
                                  out_node=node3,
                                  innovation_number=2,
                                  mutation_number=0,
                                  recurrence=True)
            
            genome2 = Genome(genome_id=1, nodes=[node3],
                             genes=[recurrent_gene])

            found = genome2._link_already_exists(   node1=node3,
                                                    node2=node3,
                                                    recurrence=False)
            assert not found
            
            
        def test_new_link_gene(self):
            innovation_type = InnovationType.NEW_LINK
            node1, node2 = self.nodes[:2]
            weight = 0.23
            innovation_number1 = 3
            recurrence = False
            
            # exists
            innovation = Innovation(node_in_id=node1.id,
                                    node_out_id=node2.id,
                                    innovation_type=innovation_type,
                                    new_weight=weight,
                                    innovation_number1=innovation_number1)
            InnovTable.add_innovation(innovation)
            
            gene = self.genome1._new_link_gene( recurrence=recurrence,
                                                node_in=node1,
                                                node_out=node2)
            
            assert gene.link.weight == 0.23
            assert gene.innovation_number == 3
            
            # not exists
            np.random.seed(1)
            new_weight = np.random.choice([-1,1]) * np.random.random() 
            innovation.innovation_type = InnovationType.NEW_NODE
            np.random.seed(1)
            gene = self.genome1._new_link_gene( recurrence=recurrence,
                                                node_in=node1,
                                                node_out=node2)
            
            assert gene.link.weight == new_weight
            
        def test_mutate_add_link(self):
            genes_size = self.genes.size
            assert self.genome1.genes.size == genes_size
            success = self.genome1._mutate_add_link(tries=1)
            
            assert success
            assert self.genome1.genes.size == genes_size + 1   

class TestInnovTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        sensor_node = Node(node_id=0,
                                
                                node_place=NodePlace.INPUT)
            
        action_node = Node(node_id=1,
                                
                                node_place=NodePlace.OUTPUT)
        
        gene0 = Gene(in_node=sensor_node,
                    out_node=action_node,
                    weight=1.0,
                    innovation_number=7,
                    mutation_number=0)
        
        self.nodes = np.array([sensor_node, action_node])
        self.genes = np.array([gene0])
        
        yield
        InnovTable.reset_innovation_table() 
        
    def test_check_innovation_already_exists(self):
            innovation_type = InnovationType.NEW_LINK
            node1, node2 = self.nodes[:2]
            weight = 1.0
            innovation_number1 = 0
            recurrence = False
            
            # exists
            innovation = Innovation(node_in_id=node1.id,
                                    node_out_id=node2.id,
                                    innovation_type=innovation_type,
                                    new_weight=weight,
                                    innovation_number1=innovation_number1)
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=innovation_type,
                                                                    node_in=node1,
                                                                    node_out=node2,
                                                                    recurrence=recurrence)
            assert exists 
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=innovation_type,
                                                                    node_in=node1,
                                                                    node_out=node2,
                                                                    recurrence=not recurrence)  
            assert not exists
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=innovation_type,
                                                                    node_in=node2,
                                                                    node_out=node1,
                                                                    recurrence=recurrence) 
            assert not exists
            
            exists = InnovTable._check_innovation_already_exists(the_innovation=innovation,
                                                                    innovation_type=InnovationType.NEW_NODE,
                                                                    node_in=node1,
                                                                    node_out=node2,
                                                                    recurrence=recurrence) 
            assert not exists
            
    def test_get_innovation(self):
        node1, node2 = self.nodes[:2]
        assert InnovTable.get_innovation_number() == 0
        
        # new innovation
        innovation = InnovTable.get_innovation( node_in=node1,
                                                node_out=node2,
                                                innovation_type=InnovationType.NEW_NODE,
                                                recurrence=False)
        
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.recurrence_flag == False
        assert innovation.new_node_id == InnovTable.get_node_number() - 1
        assert innovation.innovation_number1 == InnovTable.get_innovation_number() - 2
        assert innovation.innovation_number2 == InnovTable.get_innovation_number() - 1
        assert InnovTable.get_innovation_number() == 2
        
        # same innovaiton
        innovation = InnovTable.get_innovation( node_in=node1,
                                                node_out=node2,
                                                innovation_type=InnovationType.NEW_NODE,
                                                recurrence=False)
        
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.recurrence_flag == False
        assert innovation.new_node_id == InnovTable.get_node_number() - 1
        assert innovation.innovation_number1 == InnovTable.get_innovation_number() - 2
        assert innovation.innovation_number2 == InnovTable.get_innovation_number() - 1
        assert InnovTable.get_innovation_number() == 2
            
    def test_create_innovation(self):
        node1, node2  = self.nodes[:2]
        initial_innov_num = 3
        initial_node_num = 5
        InnovTable.increment_node(amount=initial_node_num)
        InnovTable.increment_innov(amount=initial_innov_num)
        current_innovation = InnovTable.get_innovation_number()
        
        assert InnovTable.get_innovation_number() == initial_innov_num
        
        # New link
        innovation = InnovTable._create_innovation(node_in=node1,
                                                    node_out=node2,
                                                    innovation_type=InnovationType.NEW_LINK)
        
        assert InnovTable.get_innovation_number() == current_innovation + 1
        assert innovation.innovation_type == InnovationType.NEW_LINK
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.recurrence_flag == False
        assert innovation.innovation_number1 == current_innovation
        assert innovation.innovation_number2 == -1
        assert innovation.weight != -1
        assert innovation.old_innovation_number == -1
        assert innovation.new_node_id == -1
        
        # New node
        current_innovation = InnovTable.get_innovation_number()
        innovation = InnovTable._create_innovation(node_in=node1,
                                                    node_out=node2,
                                                    innovation_type=InnovationType.NEW_NODE,
                                                    old_innovation_number=7)
        
        assert innovation.innovation_number1 == current_innovation
        assert innovation.innovation_number2 == current_innovation + 1
        assert InnovTable.get_innovation_number() == current_innovation + 2
        assert innovation.innovation_type == InnovationType.NEW_NODE
        assert innovation.node_in_id == node1.id
        assert innovation.node_out_id == node2.id
        assert innovation.recurrence_flag == False
        assert innovation.weight == -1
        assert innovation.new_node_id == 5
        assert innovation.old_innovation_number == 7
    
""" class TestPopulation:
    @pytest.fixture(autouse=True)
    def setup(self):
        sensor_node = Node(node_id=0,
                                
                                node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                                
                                node_place=NodePlace.OUTPUT)
        
        gene1 = Gene(in_node=sensor_node,
                    out_node=action_node,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        sensor_node2 = Node(node_id=2,
                                
                                node_place=NodePlace.INPUT)
        
        action_node2 = Node(node_id=3,
                                
                                node_place=NodePlace.OUTPUT)
        
        gene2 = Gene(in_node=sensor_node2,
                    out_node=action_node2,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        nodes = np.array([sensor_node, action_node, sensor_node2, action_node2])
        genes = np.array([gene1, gene2])
        
        genome = Genome(genome_id=0,
                        inputs=nodes,
                        genes=genes)
        
        genome2 = Genome(genome_id=1,
                         inputs = np.array([sensor_node, action_node]),
                         genes=np.array([gene1]))
        
        self.organisms = np.array([genome, genome2])

    def test_create_population(self):
        population = Population(organisms=self.organisms, species=np.array([]))
        assert population
        
    def test_population_fields(self):
        population = Population(organisms=self.organisms, species=np.array([]))
        assert set(['organisms', 'species', 'size']).issubset(vars(population)) """
        
    