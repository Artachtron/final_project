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
        
        assert set(['link', 'innovation_number', 'mutation_number','enable', 'frozen']).issubset(vars(gene))
        assert gene.innovation_number == 0
        assert gene.mutation_number == 0
        assert gene.enable == True
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
        
        self.nodes = np.array([sensor_node, action_node, sensor_node2, action_node2])
        self.genes = np.array([gene1, gene2])
        
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
        
        self.organisms = np.array([genome,genome2])

    def test_create_population(self):
        population = Population(organisms=self.organisms, species=np.array([]), size=len(self.organisms))
        assert population
        
    def test_population_fields(self):
        population = Population(organisms=self.organisms, species=np.array([]))
        assert set(['organisms', 'species', 'size']).issubset(vars(population))
        
    