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
            
        
        def test_mutate_links_weight(self):
            """ Config.weight_mutate_prob = 1.0
            Config.new_link_prob = 0.5
            Config.weight_mutate_power = 0.5 """
            
            weights = [gene.weight for gene in self.genome1.link_genes]
            self.genome1._mutate_link_weights()
            new_weights = [gene.weight for gene in self.genome1.link_genes]
            
            assert new_weights[2] != weights[2] 
         
        def test_mutate_add_node(self):
            nodes = {node.id: node for node in self.nodes.values() if node.id > 4}
            links = {link.id: link for link in self.links.values() if link.id > 3}

            genome1 = Genome(genome_id=1,
                             node_genes=nodes,
                             link_genes=links)
                        
            initial_link = genome1.get_last_link_id()
            initial_node = genome1.get_last_node_id()
            
            # Innovation is novel
            assert len(genome1.node_genes) == 2
            assert genome1.n_link_genes == 1
            success = genome1._mutate_add_node()
            assert genome1.link_genes[0].enabled == False
            assert success
            assert genome1.get_last_link_id() == initial_link+2
            assert genome1.get_last_node_id() == initial_node+1
            assert len(genome1.node_genes) == 3
            assert genome1.n_link_genes == 3
            nodes = {node.id: node for node in self.nodes.values() if node.id > 4}
            assert list(set(genome1._node_genes.keys()) - set(nodes.keys()))[0] == 7
            
            # Innovation exists
            links = {link.id: link for link in self.links.values() if link.id > 3}
            genome2 = Genome(genome_id=2,
                             node_genes=nodes,
                             link_genes=links)
                                 
            genome2.link_genes[0].enabled = True
            #assert genome2.get_last_link_id() == initial_innov+2
            new_link = LinkGene(in_node=1,
                                out_node=2)
            assert new_link.id == initial_link+3
            assert len(genome2.node_genes) == 2
            assert genome2.n_link_genes == 1
            success = genome2._mutate_add_node()
            assert success
            assert genome2.get_last_link_id() == initial_link+2
            assert genome2.get_last_node_id() == initial_node+1
            assert len(genome2.node_genes) == 3
            assert genome2.n_link_genes == 3
            

            

            
        