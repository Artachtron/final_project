import pytest
from gene import Gene
from node import Node, NodeType, NodePlace, FuncType
from link import Link
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
            
            self.nodes = np.array([sensor_node, action_node, sensor_node2, action_node2, sensor_node3, action_node3])
            self.genes = np.array([gene0, gene1, gene2, gene3])
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
            self.genome1.nodes = self.genome1.insert_node(nodes_list=self.genome1.nodes,
                                                node=node)
            assert self.genome1.nodes.size == 7
            
            nodes_list = list(self.genome1.nodes)
            nodes_list.insert(3, self.genome1.nodes[3])
            assert self.genome1.nodes.all() == np.array(nodes_list).all()
            
            
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
        
        def test_mutate_add_node(self):
            #self.genome1.mutate_add_node()
            pass

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
        
    