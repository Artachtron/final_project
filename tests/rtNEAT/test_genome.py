import pytest, os, sys
import numpy as np

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..', 'src', 'rtNEAT')))
from project.src.rtNEAT.genome import Genome
from project.src.rtNEAT.genes import NodeGene, LinkGene, reset_innovation_table, NodeType
from project.src.rtNEAT.neat import Config

Config.configure()

class TestGenome:
    def test_create_genome(self):
        genome = Genome(genome_id=0)
        
        assert type(genome) == Genome 
        
    def test_genome_fields(self):
        nodes = {0: NodeGene(0), 1: NodeGene(1)}
        genes = {0: LinkGene(link_id=0,
                            in_node=nodes[0].id,
                            out_node=nodes[1].id)}
        
        genome = Genome(genome_id=0,
                        node_genes=nodes,
                        link_genes=genes)
        
        assert {'id','_node_genes','_link_genes'}.issubset(vars(genome))
        
        assert genome.id == 0
        assert genome._node_genes == nodes
        assert genome._link_genes == genes
        
    def test_genesis(self):
        genome = Genome.genesis(genome_id=0,
                                n_inputs=3,
                                n_outputs=5)
        
        assert genome.n_node_genes == 3 + 5
        assert genome.n_link_genes == 3 * 5
        assert list(genome.size.values()) == [8, 15]
        
        genome2 = Genome.genesis(   genome_id=2,
                                    n_inputs=3,
                                    n_outputs=5)
        
        for node1, node2 in zip(genome.node_genes, genome2.node_genes):
            assert node1.id == node2.id
        
        for link1, link2 in zip(genome.link_genes, genome2.link_genes):
            assert link1.id == link2.id
        
    class TestGenomeMethods:
        @pytest.fixture(autouse=True)
        def setup(self):
            sensor_node = NodeGene(node_type=NodeType.INPUT)
            
            sensor_node2 = NodeGene(node_type=NodeType.INPUT)
   
            sensor_node3 = NodeGene(node_type=NodeType.INPUT)
            
            action_node = NodeGene(node_type=NodeType.OUTPUT)
            
            action_node2 = NodeGene(node_type=NodeType.OUTPUT)
            
            action_node3 = NodeGene(node_type=NodeType.OUTPUT)
            
            gene0 = LinkGene(in_node=sensor_node,
                            out_node=action_node,
                            weight=1.0,
                            mutation_number=0)
            
            gene1 = LinkGene(in_node=sensor_node2,
                            out_node=action_node2,
                            weight=1.0,
                            mutation_number=0)
            
            gene2 = LinkGene(in_node=sensor_node3,
                            out_node=action_node3,
                            weight=1.0,
                            mutation_number=0)
                    
            gene3 = LinkGene(in_node=sensor_node3,
                            out_node=action_node3,
                            weight=1.0,
                            mutation_number=1)
 
            nodes = [sensor_node, action_node, sensor_node2, action_node2, sensor_node3, action_node3]
            genes = [gene0, gene1, gene2, gene3]
            self.nodes = {node.id: node for node in nodes}
            self.links = {gene.id: gene for gene in genes}
            
            self.genome1 = Genome(genome_id=1,
                            node_genes=self.nodes,
                            link_genes=self.links)
            
            self.genome2 = Genome(genome_id=2,
                                node_genes={node.id: node for node in self.nodes.values() if node.id < 5},
                                link_genes={link.id: link for link in self.links.values() if link.id < 3})
            
            self.genome2_extended = Genome(genome_id=2,
                                    node_genes={node.id: node for node in self.nodes.values() if node.id < 5},
                                    link_genes={link.id: link for link in self.links.values() if link.id < 3})
            
            self.genome2_extended.add_node(NodeGene(node_id=1,
                                                    mutation_number=1))
            
            self.genome2_extended.add_link(LinkGene(link_id=1,
                                                    in_node=sensor_node,
                                                    out_node=action_node,
                                                    weight=1.0,
                                                    mutation_number=1))
                
            self.genome3 = Genome(genome_id=3,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in [1,2,3,5,6]},
                                link_genes={link.id: link for link in self.links.values() if link.id < 4})
            
            self.genome4 = Genome(genome_id=4,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(1,7))},
                                link_genes={link.id: link for link in self.links.values() if link.id in list(range(2,5))})
                        
            np.random.seed(1)

            yield
            
            reset_innovation_table()   

        def test_insert_node(self):
            node = NodeGene(node_id=1)
            nodes_dict = Genome.insert_gene_in_dict(genes_dict={},
                                                    gene=node)
            genome = Genome(genome_id=0,
                                 node_genes={},
                                 link_genes={})
            
            assert nodes_dict == {1: node}
            assert genome._node_genes == {}
            
            genome.add_node(node=node)
            assert genome._node_genes == nodes_dict
            
        def test_genetical_gene_distance(self):
            # Node distance
            ## Excess nodes
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome1._node_genes,
                                                    gene_dict2 = self.genome2._node_genes)
            assert dist == 2
            
            ## Disjoint
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome3._node_genes,
                                                    gene_dict2 = self.genome4._node_genes)
            assert dist == 1
                        
            ## Mutation
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome2._node_genes,
                                                    gene_dict2 = self.genome2_extended._node_genes)
            assert dist == 0.5/5
            
            # Link distance
            ## Excess nodes
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome1._link_genes,
                                                    gene_dict2 = self.genome2._link_genes)
            assert dist == 2
            
            ## Disjoint
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome3._link_genes,
                                                    gene_dict2 = self.genome4._link_genes)
            assert dist == 1
                        
            ## Mutation
            dist = Genome._genetical_gene_distance( gene_dict1 = self.genome2._link_genes,
                                                    gene_dict2 = self.genome2_extended._link_genes)
            assert dist == 0.5/3
            
        def test_genetical_distance(self):
            # Full distance
            ## Excess nodes
            dist = Genome.genetical_distance(   genome1 = self.genome1,
                                                genome2 = self.genome2)
            assert dist == 4
            
            ## Disjoint
            dist = Genome.genetical_distance(   genome1 = self.genome3,
                                                genome2 = self.genome4)
            assert dist == 2
                        
            ## Mutation
            dist = Genome.genetical_distance(   genome1 = self.genome2,
                                                genome2 = self.genome2_extended)
            assert dist == 0.5/3 + 0.5/5
            
        
        def test_genome_compatibility(self):
            self.links[3].innovation_number = self.links[2].innovation_number
            # Excess
            genome1 = Genome(   genome_id=0,
                                node_genes=self.nodes,
                                link_genes=self.links)
            
            genome2 = Genome(   genome_id=1,
                                node_genes={node.id: node for node in self.nodes.values() if node.id < 4},
                                link_genes={link.id: link for link in self.links.values() if link.id < 2})
            
            genetical_distance = Genome.genetical_distance( genome1=genome1,
                                                            genome2=genome2)
            assert genetical_distance == 2.0 * Config.excess_coeff
            
            # Disjoint
            genome3 = Genome(   genome_id=2,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in [0,1,4,5]},
                                link_genes=self.links[0:3])
                
            genome4 = Genome(   genome_id=3,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(2,5))},
                                link_genes=self.links[1:3])
                        
            genetical_distance = Genome.genetical_distance(   genome1=genome4,
                                                    genome2=genome3)
            assert genetical_distance == 1.0 * Config.disjoint_coeff
            
            # Mutation
            genome5 = Genome(   genome_id=4,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(2,4))},
                                link_genes=self.links[2:3])
            
            genome6 = Genome(   genome_id=5,
                                node_genes={node.id: node for node in self.nodes.values() if node.id in list(range(4,len(self.nodes)))},
                                link_genes=self.links[3:])
            
            genetical_distance = Genome.genetical_distance(   genome1=genome5,
                                                    genome2=genome6)
            assert genetical_distance == 1.0 * Config.mutation_difference_coeff
            

            

            
        