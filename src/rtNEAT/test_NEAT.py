import pytest
from gene import Gene
from node import Node, NodeType, NodePlace, FuncType
from link import Link
from innovation import Innovation, InnovationType
from genome import Genome
from population import Population
import numpy as np

class TestNode:
    def test_create_node(self):
        sensor_node = Node(node_id=0, node_type=NodeType.SENSOR, node_place=NodePlace.INPUT)
        assert sensor_node
        assert type(sensor_node) == Node
        
        
        
    def test_node_fields(self):
        sensor_node = Node(node_id=0,
                           node_type=NodeType.SENSOR,
                           node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                           node_type=NodeType.NEURON,
                           node_place=NodePlace.OUTPUT)
      
        assert set(['id', '_node_type', 'gen_node_label', 'activation', 'ftype', 'analogue', 'frozen', 'incoming','outgoing']).issubset(vars(action_node))
        
        assert sensor_node.id == 0
        assert sensor_node._node_type == NodeType.SENSOR
        assert sensor_node.gen_node_label == NodePlace.INPUT
        assert sensor_node.activation == 0.0
        assert sensor_node.ftype == FuncType.SIGMOID
        assert sensor_node.analogue == None
        assert sensor_node.frozen == False
        
        assert action_node.id == 1
        assert action_node._node_type == NodeType.NEURON
        assert action_node.gen_node_label == NodePlace.OUTPUT
        assert action_node.activation == 0.0
        assert action_node.ftype == FuncType.SIGMOID
        assert action_node.analogue == None
        assert action_node.frozen == False

    def test_add_incoming_link(self):
        sensor_node = Node(node_id=0,
                           node_type=NodeType.SENSOR,
                           node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                           node_type=NodeType.NEURON,
                           node_place=NodePlace.OUTPUT)
        
        assert len(action_node.incoming) == 0
        action_node.add_incoming(feednode=sensor_node, weight=1.0)
        assert len(action_node.incoming) == 1
               
   
class TestLink:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.sensor_node = Node(node_id=0,
                                node_type=NodeType.SENSOR,
                                node_place=NodePlace.INPUT)
        
        self.action_node = Node(node_id=1,
                                node_type=NodeType.NEURON,
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
                                node_type=NodeType.SENSOR,
                                node_place=NodePlace.INPUT)
        
        self.action_node = Node(node_id=1,
                                node_type=NodeType.NEURON,
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
                                node_type=NodeType.SENSOR,
                                node_place=NodePlace.INPUT)
            
        action_node = Node(node_id=1,
                                node_type=NodeType.NEURON,
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
        
    def test_genome_fields(self):
        genome = Genome(genome_id=0, nodes=self.nodes, genes=self.genes)
        assert set(['id', 'genes', 'nodes']).issubset(vars(genome))
        
        assert genome.id == 0
        assert genome.nodes.all() == self.nodes.all()
        assert genome.genes.all() == self.genes.all()
    
    class TestGenomeMethods:  
        @pytest.fixture(autouse=True)
        def setup(self):
            sensor_node = Node(node_id=0,
                                    node_type=NodeType.SENSOR,
                                    node_place=NodePlace.INPUT)
            
            action_node = Node(node_id=1,
                                    node_type=NodeType.NEURON,
                                    node_place=NodePlace.OUTPUT)
            
            gene0 = Gene(in_node=sensor_node,
                        out_node=action_node,
                        weight=1.0,
                        innovation_number=0,
                        mutation_number=0)
            
            sensor_node2 = Node(node_id=2,
                                    node_type=NodeType.SENSOR,
                                    node_place=NodePlace.INPUT)
            
            action_node2 = Node(node_id=3,
                                    node_type=NodeType.NEURON,
                                    node_place=NodePlace.OUTPUT)
            
            gene1 = Gene(in_node=sensor_node2,
                        out_node=action_node2,
                        weight=1.0,
                        innovation_number=1,
                        mutation_number=0)
            
            sensor_node3 = Node(node_id=4,
                                    node_type=NodeType.SENSOR,
                                    node_place=NodePlace.INPUT)
            
            action_node3 = Node(node_id=5,
                                    node_type=NodeType.NEURON,
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
        
          
        def test_add_genes(self):
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
            chosen_gene, skip, disable, *args = Genome._choose_gene(p1_gene=p1_gene,
                                                             p2_gene=p2_gene,
                                                             p1_genes=p1_genes,
                                                             p2_genes=p2_genes,
                                                             p1_dominant=True)
            assert not skip
            assert type(disable) == bool     
            assert chosen_gene == self.genes[0]  
            
            # innovation1 < innovation 2 non-dominant  genome 1
            chosen_gene, skip, disable, *args = Genome._choose_gene(*args,
                                                                    p1_dominant=False) 
            assert skip
            assert chosen_gene == self.genes[1]  
            
            # different gene same innovation number
            chosen_gene, skip, disable, *args = Genome._choose_gene(*args,
                                                                     p1_dominant=True)
            
            np.random.seed(2022)
            assert not skip
            assert chosen_gene == np.random.choice([self.genes[3], self.genes[2]]) 
            
            # innovation2 < innovation1 non-dominant genome 2
            chosen_gene, skip, disable, *args = Genome._choose_gene(*args,
                                                                    p1_dominant=True)
            assert skip
            assert chosen_gene == self.genes[1]  
            
            # same gene in non-dominant genome 2
            chosen_gene, skip, disable, *args = Genome._choose_gene(*args,
                                                                     p1_dominant=True)
            assert skip
            assert chosen_gene == self.genes[3] 
                         
        def test_check_gene_conflict(self):            
            genes = self.genes[[0, 1]]
            
            # conflict
            gene = Genome._check_gene_conflict(new_genes=genes,
                                        chosen_gene=self.genes[0]) 
            assert gene
            
            # no conflict
            gene = Genome._check_gene_conflict(new_genes=genes,
                                        chosen_gene=self.genes[2])
            assert not gene
        
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
                                    node_type=NodeType.SENSOR,
                                    node_place=NodePlace.INPUT)
            
            action_node = Node(node_id=7,
                                    node_type=NodeType.NEURON,
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
            
            new_genome = genome1.mate_multipoint(genome_mate=genome2,
                                                genome_id=2)
            
            assert new_genome.id == 2
            assert new_genome.nodes.size == 8
            assert new_genome.genes.size == 3
            genes = [gene.innovation_number for gene in new_genome.genes]
            assert set(genes) == set([0,2,3])
        
        def test_genome_compatibility(self):
            # Excess
            
            genome1 = Genome(genome_id=0,
                        nodes=self.nodes,
                        genes=self.genes)
            
            genome2 = Genome(genome_id=1,
                        nodes=self.nodes[:4],
                        genes=self.genes[:2])
            
            compatibility = genome1.compatibility(comparison_genome=genome2)
            assert compatibility == 2.0
            
            # Disjoint
            
            genome3 = Genome(genome_id=2,
                        nodes=self.nodes[[0,1,4,5]],
                        genes=self.genes[0:3])
            
            genome4 = Genome(genome_id=3,
                        nodes=self.nodes[2:5],
                        genes=self.genes[1:3])
                    
            compatibility = genome4.compatibility(comparison_genome=genome3)
            assert compatibility == 1.0
            
            # Mutation
            
            genome5 = Genome(genome_id=4,
                            nodes=self.nodes[2:4],
                            genes=self.genes[2:3])
            
            genome6 = Genome(genome_id=5,
                            nodes=self.nodes[4:],
                            genes=self.genes[3:])
            
            compatibility = genome5.compatibility(comparison_genome=genome6)
            assert compatibility == 1.0
            
        def test_get_last_node_info(self):        
            assert self.genome1.get_last_node_id() == 5+1
            assert self.genome1.get_last_gene_innovation_number() == 2+1
            
        def test_genesis(self):        
            network = self.genome1.genesis(network_id=0) 
            assert self.genome1.phenotype == network
            assert network.genotype == self.genome1
        
        def test_mutate_links_weight(self):
            self.genome1.mutate_link_weights(power=0.5, rate=0.5)
                
        def test_find_gene(self):
            gene, found = self.genome1._find_random_gene()
            assert gene in self.genome1.genes
            assert found
            
        def test_create_new_node(self):
            in_node, out_node = self.nodes[:2]
            node, gene1, gene2 = self.genome1._create_new_node(node_id=0,
                                          in_node=in_node,
                                          out_node=out_node,
                                          recurrence=False,
                                          innovation_number1=0,
                                          innovation_number2=1,
                                          old_weight=0.34)
           
            assert node.id == 0
            assert node.node_type == NodeType.NEURON
            assert node.gen_node_label == NodePlace.HIDDEN
            assert gene1.link.in_node == in_node
            assert gene1.link.out_node == node
            assert gene1.link.weight == 1.0
            assert gene1.innovation_number == 0
            assert gene2.link.in_node == node
            assert gene2.link.out_node == out_node
            assert gene2.link.weight == 0.34
            assert gene2.innovation_number == 1
            
        def test_check_innovation_novel(self):
            node_in_id, node_out_id = [node.id for node in self.nodes[:2]]
            gene = self.genes[0]
            
            # New innovation
            node, gene1, gene2 = self.genome1._check_innovation_novel(innovations=[],
                                                                      current_innovation=6,
                                                                      current_node_id=8,
                                                                      the_gene=gene)
            assert node.id == 8
            assert gene1.innovation_number == 6
            assert gene2.innovation_number == 7
            
            # Already existing innovation
            innovation = Innovation(node_in_id=node_in_id,
                                    node_out_id=node_out_id,
                                    innovation_type=InnovationType.NEWNODE,
                                    innovation_number1=2,
                                    innovation_number2=3,
                                    new_node_id=5)
            innovations = [innovation]
            
            node, gene1, gene2 = self.genome1._check_innovation_novel(innovations=innovations,
                                                                      current_innovation=1,
                                                                      current_node_id=8,
                                                                      the_gene=gene)
            assert node.id == 5
            assert gene1.innovation_number == 2
            assert gene2.innovation_number == 3
        
        def test_mutate_add_node(self):
            assert self.genome1.nodes.size == 6
            assert self.genome1.genes.size == 4
            success = self.genome1.mutate_add_node(innovations=[],
                                         current_node_id=2,
                                         current_innovation=0)
            assert success
            assert self.genome1.nodes.size == 7
            assert self.genome1.genes.size == 6
            
        def test_find_first_non_sensor(self):
            self.genome1.nodes = self.nodes[[0,2,4,1,3,5]]
            index = self.genome1._find_first_sensor()
            assert index == 3
        
        def test_select_nodes_for_link(self):
            self.genome1.nodes = self.nodes[[0,2,4,1,3,5]]
            
            for _ in range(10):
                # Not recurrent link
                node1, node2 = self.genome1._select_nodes_for_link( loop_recurrence=False,
                                                                    first_non_sensor=3)
                assert node1
                assert node2.node_type != NodeType.SENSOR
                
                # Recurrent link
                node1, node2 = self.genome1._select_nodes_for_link( loop_recurrence=True,
                                                                    first_non_sensor=3)
                assert node1 == node2
                assert node2.node_type != NodeType.SENSOR
                
        def test_recurrent_link_already_exists(self):
            node1 = self.nodes[0]
            node2 = self.nodes[1]
            threshold = self.nodes.size ** 2
            self.genome1.genesis(network_id=0)
            # Recurrence found
            found, try_count = self.genome1._link_already_exists(try_count=0,
                                                                tries=5,
                                                                threshold=threshold,
                                                                node1=node1,
                                                                node2=node2,
                                                                recurrence=True)
            assert try_count == 5
            assert found
            
            
            node3 = self.nodes[1]
            recurrent_gene = Gene(weight=1.0,
                                  in_node=node3,
                                  out_node=node3,
                                  innovation_number=2,
                                  mutation_number=0,
                                  recurrence=True)
            
            # Non-recurrence not found
            found, try_count = self.genome1._link_already_exists(try_count=0,
                                                                tries=5,
                                                                threshold=threshold,
                                                                node1=node1,
                                                                node2=node2,
                                                                recurrence=False)
            assert not found
            assert try_count == 1
            
            genome2 = Genome(genome_id=1, nodes=[node3],
                             genes=[recurrent_gene])
            genome2.genesis(network_id=1)
            found, try_count = genome2._link_already_exists(try_count=0,
                                                            tries=5,
                                                            threshold=threshold,
                                                            node1=node3,
                                                            node2=node3,
                                                            recurrence=False)
            assert try_count == 5
            assert found
            
            
            
class TestPopulation:
    @pytest.fixture(autouse=True)
    def setup(self):
        sensor_node = Node(node_id=0,
                                node_type=NodeType.SENSOR,
                                node_place=NodePlace.INPUT)
        
        action_node = Node(node_id=1,
                                node_type=NodeType.NEURON,
                                node_place=NodePlace.OUTPUT)
        
        gene1 = Gene(in_node=sensor_node,
                    out_node=action_node,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        sensor_node2 = Node(node_id=2,
                                node_type=NodeType.SENSOR,
                                node_place=NodePlace.INPUT)
        
        action_node2 = Node(node_id=3,
                                node_type=NodeType.NEURON,
                                node_place=NodePlace.OUTPUT)
        
        gene2 = Gene(in_node=sensor_node2,
                    out_node=action_node2,
                    weight=1.0,
                    innovation_number=0,
                    mutation_number=0)
        
        nodes = np.array([sensor_node, action_node, sensor_node2, action_node2])
        genes = np.array([gene1, gene2])
        
        genome = Genome(genome_id=0,
                        nodes=nodes,
                        genes=genes)
        
        genome2 = Genome(genome_id=1,
                         nodes = np.array([sensor_node, action_node]),
                         genes=np.array([gene1]))
        
        self.organisms = np.array([genome, genome2])

    def test_create_population(self):
        population = Population(organisms=self.organisms, species=np.array([]))
        assert population
        
    def test_population_fields(self):
        population = Population(organisms=self.organisms, species=np.array([]))
        assert set(['organisms', 'species', 'size']).issubset(vars(population))
        
    